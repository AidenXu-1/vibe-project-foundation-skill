# docs —— 规划与管理

这里是项目的「大脑」。所有**不是代码、但决定代码怎么写**的东西都放这。

## 文件导航

| 文件 | 作用 | 多久更新一次 |
|------|------|------------|
| [`spec.md`](spec.md) | 当前唯一开发准绳:产品意图、技术路线、验收标准 | 经常,每次范围或路线变化时 |
| [`agent-guide.md`](agent-guide.md) | 所有 AI Agent 共用的协作规则 | 偶尔,规则变化时 |
| [`overview.md`](overview.md) | 项目总览:是什么、为谁做、为什么 | 很少,方向变了才改 |
| [`spec/`](spec/) | 单个功能的细分规格模板 | 需要拆复杂功能时 |
| [`mvp.md`](mvp.md) | MVP 辅助说明:第一个能用的版本是什么样 | 很少,以 spec.md 为准 |
| [`roadmap.md`](roadmap.md) | 里程碑 / 路线图 | 每个阶段结束时 |
| [`progress.md`](progress.md) | 进度日志:做了什么、卡在哪 | 经常(每次有进展) |
| [`handoff.md`](handoff.md) | 交接文档:换人 / 换设备如何续上 | 每次要中断时 |
| [`conventions.md`](conventions.md) | 编码约定与护栏 | 选型后补充 |
| [`decisions/`](decisions/) | 架构决策记录(ADR):为什么这么选 | 每做一个重要技术决策 |

## 一条原则

> 开发时以 `spec.md` 为准。其他文档如果和 Spec 冲突,先更新 Spec,再同步相关文档。
