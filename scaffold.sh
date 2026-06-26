#!/usr/bin/env bash
# 把 templates/ 铺设到目标目录,替换占位符,并 git 初始化。
# 用法: scaffold.sh <目标目录> <项目名> <项目一句话> [日期YYYY-MM-DD]
set -euo pipefail

TARGET="${1:?需要目标目录}"
NAME="${2:?需要项目名}"
ONELINER="${3:?需要项目一句话}"
DATE="${4:-$(date +%F)}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPL="$SKILL_DIR/templates"

[ -d "$TPL" ] || { echo "找不到模板目录: $TPL" >&2; exit 1; }

for cmd in git perl find cp python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "缺少依赖命令: $cmd" >&2; exit 1; }
done

if [[ ! "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "日期格式必须是 YYYY-MM-DD: $DATE" >&2
  exit 1
fi
if ! python3 - "$DATE" <<'PY' >/dev/null 2>&1
import datetime
import sys

datetime.date.fromisoformat(sys.argv[1])
PY
then
  echo "日期必须是真实存在的日历日期: $DATE" >&2
  exit 1
fi

CREATED_TARGET=0
if [ ! -e "$TARGET" ]; then
  CREATED_TARGET=1
fi

cleanup_on_error() {
  local code=$?
  if [ "$CREATED_TARGET" -eq 1 ] && [ -d "$TARGET" ]; then
    rm -rf "$TARGET"
    echo "铺设失败,已清理本次创建的目标目录: $TARGET" >&2
  else
    echo "铺设失败,目标目录可能已留下部分文件,请检查: $TARGET" >&2
  fi
  exit "$code"
}
trap cleanup_on_error ERR

mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"

# 安全检查:目标目录非空时中止,避免覆盖用户已有文件
if [ -n "$(find "$TARGET" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "⚠ 目标目录不是空目录,已中止以防覆盖已有文件。" >&2
  echo "  如需搭地基,请换一个空目录,或先手动整理目标目录。" >&2
  exit 2
fi

# 复制整棵模板树(含 .gitignore 等隐藏文件),排除 macOS 元数据噪音
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude '.DS_Store' "$TPL"/ "$TARGET"/
else
  cp -R "$TPL"/. "$TARGET"/
  find "$TARGET" -name '.DS_Store' -type f -delete
fi

# 占位符替换(用环境变量传值,避免特殊字符破坏正则)
export NAME ONELINER DATE
find "$TARGET" -type f \( -name '*.md' -o -name '.gitignore' \) -print0 \
  | while IFS= read -r -d '' f; do
      perl -i -pe '
        s/\{\{PROJECT_NAME\}\}/$ENV{NAME}/g;
        s/\{\{ONE_LINER\}\}/$ENV{ONELINER}/g;
        s/\{\{DATE\}\}/$ENV{DATE}/g;
      ' "$f"
    done

# git 初始化 + 首次提交
cd "$TARGET"
if [ ! -d .git ]; then
  git init -q
fi
git add -A
if git diff --cached --quiet; then
  echo "没有可提交的变更(可能已初始化过)。"
else
  git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name 2>/dev/null || echo dev)}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email 2>/dev/null || echo dev@local)}" \
      commit -q -m "chore: 搭建开发前地基($NAME)

- docs/: Spec、Agent 规则、总览、路线图、进度、交接、规格模板、ADR 决策记录、约定
- design/: 竞品参考、UI 稿、素材
- app/: 占位(待 Spec 和风险检查后 Kickoff 初始化)
- AGENTS.md + CLAUDE.md + agent-guide + scratch/ + .gitignore: 接入 vibecoding 工作流"
fi

echo "✅ 地基已铺设到: $(pwd)"
echo "--- 文件清单 ---"
# 此处 cwd 已是目标目录(上面 cd 过),直接 ls-files,避免相对路径下 git -C 解析错误
git ls-files
trap - ERR
