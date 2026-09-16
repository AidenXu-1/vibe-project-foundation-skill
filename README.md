# vibe-project-foundation

为新的 Vibe Coding / 软件产品项目搭建**开发前地基**的 Agent Skill：铺好项目骨架、文档体系、AI 工作入口和 Git 安全网，再进入 Spec 与开发。

它不是用来直接写功能代码的，也不替你决定技术栈——它负责在动手之前，把"想清楚、做出来、长什么样"三件事的位置和规范定下来。

## 它解决什么问题

新项目一上来就写代码，通常会出现：目录乱、AI 每次都要重新交代一遍规则、临时实验混进主分支、Spec 写在哪全靠记性。这个 Skill 把第一次初始化的动作固化下来：

- **统一的目录语义**：`docs/` 想清楚、`app/` 做出来、`design/` 长什么样、`scratch/` 做实验。
- **统一的 AI 入口**：`CLAUDE.md` / `AGENTS.md` 都指向 `docs/agent-guide.md`，换工具不换规则。
- **统一的开发合同**：`docs/spec.md` 是后续开发的唯一准绳，冲突时以它为准。
- **Git 安全网**：初始化即建库并首次提交，`scratch/` 默认被忽略，随时能回滚。

## 安装

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/AidenXu-1/vibe-project-foundation-skill.git ~/.codex/skills/vibe-project-foundation
```

如果当前 Codex 环境不会自动热加载新 Skill，重启或刷新一下。

## 快速开始

### 方式一：让 Agent 调用 Skill

直接对 Codex 说：

```text
帮我给这个新项目搭建一下地基。
```

或：

```text
我要开始一个新的 Vibe Coding 项目，先帮我初始化项目骨架。
```

Skill 会先确认两件事——项目名、一句话说明——然后铺设，不会在地基阶段替你选技术栈。

### 方式二：直接跑脚本

```bash
bash scaffold.sh "/path/to/target" "项目名" "一句话说明"
```

指定日期（默认取系统当天）：

```bash
bash scaffold.sh "/path/to/target" "项目名" "一句话说明" "2026-06-26"
```

> 目标目录必须为空，脚本检测到非空会直接中止，不会覆盖已有项目。

## 会生成什么

```text
<项目>/
├── AGENTS.md       # 通用 Agent 工作入口（Codex / Copilot 等）
├── CLAUDE.md       # AI 工作入口（Claude Code 自动加载）
├── README.md       # 人类入口与导航
├── .gitignore
├── docs/           # 想清楚
│   ├── spec.md         # 开发合同，唯一准绳
│   ├── agent-guide.md  # AI 实现取舍与设计预览规则
│   ├── roadmap.md
│   ├── progress.md
│   ├── conventions.md
│   ├── decisions/      # ADR 决策记录
│   └── spec/           # 分模块 Spec
├── app/            # 做出来（占位，待 Kickoff 后初始化）
├── design/         # 长什么样：references / ui / assets
└── scratch/        # 实验区（git 忽略）
```

脚本同时完成：复制模板 → 替换 `{{PROJECT_NAME}}` / `{{ONE_LINER}}` / `{{DATE}}` 占位符 → `git init` → 首次提交 → 排除 `.DS_Store` 等噪音。

## 适用场景

适合：

- 全新的 Vibe Coding 项目。
- 全新的软件产品 / 互联网产品 / 插件 / 小程序 / 网站系统。
- 需要长期维护、持续迭代的可运行项目。
- 开发前需要先写 Spec、做风险检查、排路线图的项目。

不适合：

- 已经有代码和历史结构的老项目（不要用它覆盖）。
- 知识库搭建、Skill 开发等需要专用组织结构的任务。
- 课程、内容、运营、咨询、调研等非软件项目。
- 只想快速生成一次性 demo 的临时目录。

## 仓库结构

这个仓库只放"能直接用的 Skill"和这份说明，没有多余的脚手架文件：

```text
.
├── SKILL.md            # Skill 的适用范围与执行步骤
├── agents/openai.yaml  # 界面元数据：展示名、默认提示词
├── scaffold.sh         # 一键铺地脚本
├── templates/          # 项目骨架模板
└── README.md           # 本文件
```

改模板只需编辑 `templates/` 下的文件，之后所有新项目都会继承。

## License

本仓库未附带 LICENSE 文件，默认保留所有权利。
