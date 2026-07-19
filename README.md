# Vibe Project Foundation Skill

为新的 Vibe Coding / 软件产品项目搭建“开发前地基”的 Codex Skill。

它不是用来直接写功能代码的，而是在正式开发前先铺好项目骨架、文档体系、AI 工作入口和 Git 安全网，让后续 Spec、风险检查、Kickoff、小步开发都有统一准绳。

## 这个 Skill 做什么

它会把一个空目录初始化成适合长期维护的项目结构：

```text
<项目>/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── .gitignore
├── docs/
│   ├── spec.md
│   ├── agent-guide.md
│   ├── overview.md
│   ├── roadmap.md
│   ├── progress.md
│   ├── handoff.md
│   ├── conventions.md
│   ├── decisions/
│   └── spec/
├── app/
├── design/
└── scratch/
```

并自动完成：

- 复制模板。
- 替换项目名、一句话说明、日期占位符。
- 初始化 Git。
- 创建首次提交。
- 保护非空目录，避免覆盖已有项目。
- 排除 `.DS_Store` 等 macOS 元数据噪音。

## 适用场景

适合：

- 全新的 Vibe Coding 项目。
- 全新的软件产品 / 互联网产品。
- 需要长期维护的可运行项目。
- 开发前需要先写 Spec、风险检查、路线图和协作规则的项目。

不适合：

- 已经有代码和历史结构的老项目。
- 课程、内容、运营、咨询、线下交付、调研、内部流程等非软件项目。
- 只想快速生成一个临时 demo 的一次性目录。

非软件项目建议使用对应业务地基，或使用 `agent-team` 的最小业务地基能力。

## 安装到 Codex

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/AidenXu-1/vibe-project-foundation-skill.git ~/.codex/skills/vibe-project-foundation
```

如果当前 Codex 环境不会自动热加载新 Skill，请重启或刷新 Codex。

## 触发方式

你可以对 Codex 说：

```text
帮我给这个新项目搭建一下地基。
```

或：

```text
我要开始一个新的 Vibe Coding 项目，先帮我初始化项目骨架。
```

Skill 应先确认项目名和一句话说明，不应在地基阶段替用户决定技术栈。

## 直接运行脚本

```bash
bash scaffold.sh "/path/to/target" "项目名" "一句话说明"
```

指定日期：

```bash
bash scaffold.sh "/path/to/target" "项目名" "一句话说明" "2026-06-26"
```

注意：目标目录必须为空，否则脚本会中止。

## 验证

运行回归验证：

```bash
bash scripts/verify_scaffold.sh
```

运行 Skill 基础校验：

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .
```

期望结果：

```text
OK: vibe-project-foundation scaffold verified
Skill is valid!
```

## 仓库结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── scaffold.sh
├── scripts/verify_scaffold.sh
├── templates/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── .github/
```

其中真正的 Skill 运行资源是：

- `SKILL.md`
- `agents/openai.yaml`
- `scaffold.sh`
- `scripts/verify_scaffold.sh`
- `templates/`

其他文件是 GitHub 开源展示、协作和自动验证用途。

## License

MIT License. See [LICENSE](LICENSE).
