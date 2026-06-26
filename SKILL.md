---
name: vibe-project-foundation
description: Use when starting a NEW long-lived Vibe Coding project and the user wants 开发前准备, 搭地基, 项目骨架, 初始化项目, project setup, or scaffold a project foundation before feature work.
---

# vibe-project-foundation

把"开发前准备"沉淀成一次可复用的铺设流程。为一个**全新、长期维护**的 Vibe Coding 项目搭好三层结构 + AI 工作层 + git 安全网,让用户随后能进入 Spec 梳理、风险检查、Kickoff 和小步开发。

## 设计理念(一句话)

> `docs/spec.md` 让人和 AI **对齐唯一开发准绳**,`AGENTS.md` / `CLAUDE.md` + `docs/agent-guide.md` 让不同 Agent **照同一套规矩做**,git + `scratch/` 给**犯错的安全网**。
> 三件事齐了,vibecoding 的地基才完整。

最终铺设出的结构:

```
<项目>/
├── CLAUDE.md     # AI 工作入口(Claude Code 自动加载)
├── AGENTS.md     # 通用 Agent 工作入口(Codex / Copilot 等)
├── README.md     # 人类入口与导航
├── .gitignore
├── docs/         # 想清楚:spec / agent-guide / overview / roadmap / progress / handoff / conventions / decisions/
├── app/          # 做出来(占位,待 Kickoff 后初始化)
├── design/       # 长什么样:references / ui / assets
└── scratch/      # 实验区(git 忽略)
```

## 执行步骤

### 0. 适用性硬闸

本 Skill 只适用于全新、长期维护的可运行软件 / 互联网产品 / Vibe Coding 项目。若用户要做的是课程、内容、运营、咨询、线下交付、调研、内部流程或其他非软件项目,不得创建 `app/`、`design/`、`docs/spec.md` 这套软件地基;应停下来说明本 Skill 不适用,转用对应业务地基 / 现有目录结构 / `agent-team` 的最小业务地基。

### 1. 收集最少必要信息
向用户确认两项(其余一律留占位符 `(待填)`,**不要替用户编需求**):
- **项目名**(`PROJECT_NAME`):默认用目标目录名。
- **项目一句话**(`ONE_LINER`):这个项目是什么。用户说不清就写用户原话或 `(待填:用户暂未说清)`,不要自行补全。

目标目录默认 = 当前工作目录。若当前目录非空或已是别的项目,改用 `<cwd>/<项目名>` 子目录,并和用户确认。目标目录必须是空目录,避免覆盖已有文件。

**不要**在这一步追问技术栈/形态——地基刻意与技术无关。先写 Spec 和做风险检查,再进入 Kickoff 选型。

### 2. 安全检查
若目标目录不是空目录,说明可能已有内容,**停下来问用户**,不要覆盖。(脚本本身也会拦截。)

### 3. 铺设
用脚本一键完成(复制模板 + 替换占位符 + git 初始化 + 首次提交)。`scaffold.sh` 与本 SKILL.md 同目录,用它的**绝对路径**调用:

```bash
bash <本skill目录>/scaffold.sh "<目标目录>" "<项目名>" "<项目一句话>"
```

- `<本skill目录>` = 本 SKILL.md 所在目录的绝对路径。
- 日期默认取系统当天;如需指定,可加第 4 个参数 `YYYY-MM-DD`。
- 占位符 `{{PROJECT_NAME}}` `{{ONE_LINER}}` `{{DATE}}` 由脚本自动替换。
- 脚本对"目标目录非空"会自动中止,防止覆盖已有文件。

若环境不便跑脚本,可手动:`cp -R <本skill目录>/templates/. <目标>/` → 替换三个占位符 → `git init && git add -A && git commit`。

### 4. 验证
- 跑 `git -C <目标> ls-files` 确认文件齐全,尤其确认 `AGENTS.md`、`CLAUDE.md`、`docs/agent-guide.md`、`docs/spec.md` 存在。
- 用 `scratch/` 放一个临时文件,确认被 `.gitignore` 忽略(`git status` 不显示)。

### 5. 收尾汇报
向用户简述:铺了什么、结构长什么样、git 首次提交已完成,并给出**下一步 = 写 Spec v0**。强调技术选型不在地基阶段做,要等 Spec 和风险检查后进入 Kickoff。

## 注意

- 这是**新项目地基**,不是改造已有代码库的工具。已有项目请勿用它覆盖。
- 全程保持技术无关:不预设框架、不建语言相关目录,避免 Spec 未稳定就返工。
- 占位符内容(`(待填)`)是给用户后续填的,不要擅自替用户拍板需求或边界。
- `docs/spec.md` 是后续开发的唯一准绳;`overview.md`、`mvp.md` 等是辅助说明,若冲突以 Spec 为准并提示用户同步修正。
- 模板可按需演进:直接编辑 `templates/` 下文件即可影响以后所有新项目。
