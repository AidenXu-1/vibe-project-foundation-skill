"""在空项目中铺设模板并核对首次 Git 提交。"""

import argparse
from contextlib import contextmanager
import datetime
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile


class Refusal(Exception):
    """目标已有工作，不能继续初始化。"""


def git(target, *args, check=True, index=None, extra_env=None, input_data=None):
    # 保留用户签名、忽略规则等设置，但不接受外层仓库传来的目录或索引。
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
                "GIT_IMPLICIT_WORK_TREE", "GIT_PREFIX"):
        env.pop(key, None)
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(["git", "-C", str(target), *args], env=env, input=input_data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def paths(output):
    return {os.fsdecode(p) for p in output.split(b"\0") if p}


def render_templates(name, purpose, date):
    source = Path(__file__).resolve().parent / "templates"
    replacements = {"PROJECT_NAME": name, "ONE_LINER": purpose, "DATE": date}
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.name != ".DS_Store":
            data = path.read_bytes()
            if path.suffix == ".md" or path.name == ".gitignore":
                value = re.sub(r"\{\{(PROJECT_NAME|ONE_LINER|DATE)\}\}",
                               lambda m: replacements[m[1]], data.decode("utf-8"))
                data = value.encode("utf-8")
            files[str(path.relative_to(source))] = (data, path.stat().st_mode & 0o777)
    required = {"AGENTS.md", "CLAUDE.md", "docs/agent-guide.md", "docs/spec.md"}
    if not required.issubset(files):
        raise ValueError("模板缺少必需的 AI 入口或需求文件。")
    return files


@contextmanager
def complete_file(directory, data, mode):
    handle = tempfile.NamedTemporaryFile(dir=directory, prefix=".vibe-foundation-", delete=False)
    path = Path(handle.name)
    try:
        with handle:
            handle.write(data)
            os.fchmod(handle.fileno(), mode)
        yield path
    finally:
        path.unlink(missing_ok=True)


def publish_new_file(source, destination):
    try:
        os.link(source, destination)
        return
    except OSError as exc:
        if exc.errno not in (errno.EPERM, errno.ENOTSUP, errno.ENOSYS):
            raise

    # 外置卷可能没有硬链接。使用系统的“不覆盖目标”改名操作。
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    src, dst = os.fsencode(source), os.fsencode(destination)
    if sys.platform == "darwin":
        result = libc.renamex_np(src, dst, 0x00000004)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        result = libc.renameat2(-100, src, -100, dst, 1)  # AT_FDCWD, RENAME_NOREPLACE
    else:
        raise OSError(errno.ENOTSUP, "此卷不支持安全放入新文件", str(destination))
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def write_templates(root, files, staged, git_dir=None):
    if git_dir is None:
        git_dir = Path(os.fsdecode(git(root, "rev-parse", "--absolute-git-dir").stdout.rstrip(b"\n")))
    metadata_device = git_dir.stat().st_dev
    for name, (data, mode) in files.items():
        path = root / name
        if path.resolve() != path:
            raise Refusal(f"项目路径经过符号链接，已保留：{name}")
        if path.exists():
            if not path.is_file() or path.read_bytes() != data:
                raise Refusal(f"文件内容已改变，已保留：{name}")
        elif name in staged:
            raise Refusal(f"已暂存的文件后来被移走，已保留当前状态：{name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            directory = git_dir if path.parent.stat().st_dev == metadata_device else path.parent
            with complete_file(directory, data, mode) as prepared:
                publish_new_file(prepared, path)


def save_pending(marker, state):
    with complete_file(marker.parent, json.dumps(state).encode("utf-8"), 0o600) as prepared:
        os.replace(prepared, marker)


def object_id(root, revision):
    result = git(root, "rev-parse", "--verify", "--quiet", revision,
                 check=False)
    if result.returncode == 1:
        return None
    result.check_returncode()
    return result.stdout.decode("ascii").strip()


def checked_tree(root, commit, files):
    parents = git(root, "rev-list", "--parents", "-n1", commit).stdout.split()
    names = paths(git(root, "ls-tree", "-rz", "--name-only", commit).stdout)
    if len(parents) != 1 or names != set(files):
        raise Refusal("待保存的版本包含其他历史或文件清单不符，已保留原仓库。")
    return object_id(root, commit + "^{tree}")


def confirm_working_changes(root, files, index):
    indexed = paths(git(root, "ls-files", "-z", index=index).stdout)
    extra = indexed - set(files)
    if extra:
        git(root, "update-index", "--force-remove", "--", *sorted(extra), index=index)
    changed = set(files) - indexed
    changed.update(paths(git(root, "diff", "--name-only", "-z", index=index).stdout))
    if changed:
        named = sorted(changed)
        approved = paths(git(root, "ls-files", "-z", "--", *named).stdout)
        if approved != changed or git(root, "diff", "--quiet", "--", *named, check=False).returncode:
            ask_to_stage(named)
        git(root, "add", "-f", "--", *named, index=index)


def ask_to_stage(names):
    command = shlex.join(["git", "add", "--", *sorted(names)])
    raise Refusal(f"工作文件有尚未纳入版本的改动。请检查后在项目目录运行 {command}，再重试。")


def reference_transaction(phase):
    # Git 已锁住分支。先让团队自己的事务钩子处理完整输入，再检查即将公布的对象。
    records = sys.stdin.buffer.read()
    original = Path(os.environ["VPF_TEAM_HOOKS"]) / "reference-transaction"
    if original.is_file() and os.access(original, os.X_OK):
        result = subprocess.run([str(original), phase], input=records)
        if result.returncode:
            sys.exit(result.returncode)
    root = Path(os.environ["VPF_TARGET"])
    marker = Path(os.environ["VPF_MARKER"])
    state = json.loads(marker.read_text())
    updates = [line.split(b" ", 2) for line in records.splitlines()]
    branch = os.fsencode(state["branch"])
    commits = {new for old, new, ref in updates if ref in (branch, b"HEAD") and not old.strip(b"0")}
    if not any(ref in (branch, b"HEAD") for _, _, ref in updates):
        return
    if len(commits) != 1:
        raise Refusal("分支历史已变化，已保留。")
    commit = commits.pop().decode("ascii")
    files = json.loads(os.environ["VPF_FILES"])
    tree = checked_tree(root, commit, files)
    index = Path(os.environ["GIT_INDEX_FILE"])
    changed = paths(git(root, "diff", "--name-only", "-z", commit, "--", *files, index=index).stdout)
    if changed:
        ask_to_stage(changed)
    state["commit"] = commit
    save_pending(marker, state)
    # 只合并模板路径，同时保留其他窗口的暂存项。Git 将在本钩子返回后公布版本。
    git(root, "read-tree", "-i", "-m", state["base"], tree)


def prepare_hooks(root, stage, marker, files):
    owner = git(root, "rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout
    owner = Path(os.fsdecode(owner.rstrip(b"\n")))
    hooks = stage / "hooks"
    hooks.mkdir(exist_ok=True)
    # 钩子仍在真实项目中运行。还原 hooksPath，供钩子自己的 Git 命令使用。
    parameter = "'core.hooksPath'='" + str(owner).replace("'", "'\\''") + "'"
    env = {"VPF_TEAM_HOOKS": str(owner), "VPF_RESTORE_HOOKS": parameter,
           "VPF_PYTHON": sys.executable, "VPF_SCAFFOLD": str(Path(__file__).resolve()),
           "VPF_TARGET": str(root), "VPF_MARKER": str(marker), "VPF_FILES": json.dumps(list(files))}
    shim = ("#!/bin/sh\n"
            'export GIT_CONFIG_PARAMETERS="${GIT_CONFIG_PARAMETERS-} $VPF_RESTORE_HOOKS"\n'
            'hook=${0##*/}\n'
            'if [ "$hook" = reference-transaction ] && [ "$1" = prepared ]; then\n'
            '  exec "$VPF_PYTHON" "$VPF_SCAFFOLD" --reference-transaction "$@"\n'
            'fi\n[ -x "$VPF_TEAM_HOOKS/$hook" ] || exit 0\nexec "$VPF_TEAM_HOOKS/$hook" "$@"\n')
    enabled = {"reference-transaction"}
    if owner.is_dir():
        enabled.update(p.name for p in owner.iterdir() if not p.name.endswith(".sample") and p.is_file() and os.access(p, os.X_OK))
    for old in hooks.iterdir():
        if old.name not in enabled:
            old.unlink()
    for hook in enabled:
        entry = hooks / hook
        with complete_file(hooks, shim.encode(), 0o700) as prepared:
            os.replace(prepared, entry)
    return hooks, env


def first_commit(root, name, files, git_dir, marker, state, legacy_tree, staged):
    stage_name = state.get("stage")
    if stage_name is None:
        if legacy_tree and git(root, "write-tree").stdout.decode().strip() != legacy_tree:
            raise Refusal("上次初始化后暂存内容已变化，已保留。")
        if staged and (staged != set(files) or git(root, "diff", "--quiet", check=False).returncode):
            raise Refusal("目标仓库已有其他暂存或修改，已保留。")
        state["base"] = legacy_tree or git(root, "mktree", input_data=b"").stdout.decode().strip()
        state["branch"] = git(root, "symbolic-ref", "HEAD").stdout.decode().strip()
        stage_name = state["stage"] = Path(tempfile.mkdtemp(prefix="vibe-stage-", dir=git_dir)).name
        save_pending(marker, state)
    if not isinstance(stage_name, str) or not stage_name.startswith("vibe-stage-") or Path(stage_name).name != stage_name:
        raise Refusal("未完成记录中的暂存目录无效。")
    stage = git_dir / stage_name
    if stage.is_symlink() or git(root, "symbolic-ref", "HEAD").stdout.decode().strip() != state["branch"]:
        raise Refusal("上次初始化后仓库位置或分支已改变，已保留当前状态。")
    head = object_id(root, "HEAD")
    if head is None:
        index = stage / "index"
        if not index.exists():
            write_templates(root, files, staged, git_dir)
            git(root, "add", "-f", "--", *files, index=index)
        else:
            confirm_working_changes(root, files, index)
        hooks, env = prepare_hooks(root, stage, marker, files)
        options = ["-c", f"core.hooksPath={hooks}"]
        for setting, key, fallback in (("user.name", "GIT_AUTHOR_NAME", "dev"),
                                       ("user.email", "GIT_AUTHOR_EMAIL", "dev@local")):
            if not git(root, "config", "--get", setting, check=False).stdout.strip():
                options.extend(["-c", f"{setting}={os.environ.get(key) or fallback}"])
        try:
            git(root, *options, "commit", "-q", "-m", f"chore: 搭建开发前地基({name})",
                index=index, extra_env=env)
        except subprocess.CalledProcessError:
            published = object_id(root, "HEAD")
            if published and published != json.loads(marker.read_text()).get("commit"):
                raise Refusal("其他操作已先保存版本，当前历史和文件均已保留。")
            raise
        state = json.loads(marker.read_text())
        head = object_id(root, "HEAD")
    if not head or state.get("commit") != head:
        raise Refusal("已有版本与本次初始化不一致，已保留。")
    if stage.exists():
        shutil.rmtree(stage)


def initialize(root, name, purpose, requested_date):
    dotgit = root / ".git"
    existing_files = {p.name for p in root.iterdir()} - {".git", ".DS_Store"}
    if dotgit.is_symlink():
        raise Refusal("Git 目录是符号链接，已保留。")
    if not dotgit.exists():
        if existing_files:
            raise Refusal("目标目录已有内容，已保留。")
        git(root, "init", "-q")
    top = git(root, "rev-parse", "--show-toplevel", check=False)
    if top.returncode or Path(os.fsdecode(top.stdout.rstrip(b"\n"))).resolve() != root:
        raise Refusal("目标并非独立工作仓库的根目录。")
    git_dir = Path(os.fsdecode(git(root, "rev-parse", "--absolute-git-dir").stdout.rstrip(b"\n")))
    marker = git_dir / "vibe-foundation-pending.json"
    resume = marker.is_file()
    if existing_files and not resume:
        raise Refusal("目标目录已有项目文件，已保留。")
    staged = paths(git(root, "ls-files", "-z").stdout)
    if staged and not resume:
        raise Refusal("目标仓库已有暂存内容，已保留。")
    has_head = git(root, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0
    has_refs = bool(git(root, "for-each-ref", "--count=1", "--format=%(refname)").stdout)
    if (has_head and not resume) or (has_refs and not has_head):
        raise Refusal("目标仓库已有版本历史，已保留。")

    previous = json.loads(marker.read_text()) if resume else {}
    date = requested_date or previous.get("date") or datetime.date.today().isoformat()
    files = render_templates(name, purpose, date)
    digest = hashlib.sha256()
    for filename, (data, mode) in files.items():
        digest.update(os.fsencode(filename) + b"\0")
        digest.update(str(mode).encode("ascii") + b"\0")
        digest.update(hashlib.sha256(data).digest())
    state = {"date": date, "name": name, "templates": digest.hexdigest()}
    legacy_tree = previous.pop("tree", None)
    if resume:
        if any(previous.get(key) != value for key, value in state.items()):
            raise Refusal("项目参数或模板已变化，保留上次未完成的初始化。")
        state = previous
    else:
        save_pending(marker, state)

    if has_head and not state.get("stage"):
        head = object_id(root, "HEAD")
        if not legacy_tree or checked_tree(root, head, files) != legacy_tree:
            raise Refusal("已有版本与本次初始化不一致，已保留。")
    else:
        first_commit(root, name, files, git_dir, marker, state, legacy_tree, staged)
    marker.unlink()
    print(f"✅ 地基已铺设到: {root}")
    print("\n".join(files))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("name")
    parser.add_argument("purpose")
    parser.add_argument("date", nargs="?")
    args = parser.parse_args()
    if not args.target or not args.name or not args.purpose:
        parser.error("需要目标目录、项目名和一句话简介。")
    if args.date:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.date):
            parser.error("日期格式必须是 YYYY-MM-DD。")
        datetime.date.fromisoformat(args.date)
    root = Path(args.target).resolve()
    if root.exists() and not root.is_dir():
        raise Refusal("目标路径已有文件，已保留。")
    ancestor = root.parent
    while not ancestor.is_dir():
        ancestor = ancestor.parent
    if git(ancestor, "rev-parse", "--git-dir", check=False).returncode == 0:
        raise Refusal("目标位于已有 Git 仓库内，请使用新项目自己的仓库根目录。")
    root.mkdir(parents=True, exist_ok=True)
    fd = os.open(root, os.O_RDONLY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refusal("另一个窗口正在为这个目录搭地基，请稍后重试。") from None
        initialize(root, args.name, args.purpose, args.date)
    finally:
        os.close(fd)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "--reference-transaction":
            reference_transaction(sys.argv[2])
        else:
            main()
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    except subprocess.CalledProcessError as exc:
        print(os.fsdecode(exc.stderr).strip() or f"Git 退出状态 {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
