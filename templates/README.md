# {{PROJECT_NAME}}

> {{ONE_LINER}}

本仓库采用「三层物理隔离 + AI 工作层」的方式管理:把**想清楚 / 做出来 / 长什么样**分开,并为不同 AI agent 提供统一入口。

## 仓库结构

```
{{PROJECT_NAME}}/
├── CLAUDE.md         ← AI 工作入口(Claude Code 自动加载)
├── AGENTS.md         ← 通用 Agent 工作入口(Codex / Copilot 等)
├── README.md         ← 你在这里:项目总入口与导航
├── docs/             ← 规划与管理:spec、agent-guide、overview、roadmap、progress、handoff、决策记录
├── app/              ← 应用本体代码(地基阶段仅占位)
├── design/           ← 设计与 UI 参考
└── scratch/          ← 草稿/实验区(git 忽略)
```

## 三层各管什么

| 文件夹 | 回答的问题 | 谁主要在这里工作 |
|--------|-----------|----------------|
| `docs/` | 我们要做什么、做到什么程度、做到哪了 | 规划 / 决策 / 交接 |
| `app/` | 怎么做出来 | 写代码 |
| `design/` | 它长什么样、参考了谁 | 设计 / 体验 |

## 从哪开始

1. 读 [`docs/spec.md`](docs/spec.md) —— 当前唯一开发准绳。
2. 读 [`docs/agent-guide.md`](docs/agent-guide.md) —— AI 协作规则与安全边界。
3. 读 [`docs/roadmap.md`](docs/roadmap.md) —— 阶段地图。
4. 想了解进展,看 [`docs/progress.md`](docs/progress.md)。
5. 接手项目 / 换设备继续,先读 [`docs/handoff.md`](docs/handoff.md)。

## 当前阶段

🟡 **地基搭建** —— 目录与文档骨架已就位,尚未进入需求与编码。下一步是写 [`docs/spec.md`](docs/spec.md) 的 v0 草案。
