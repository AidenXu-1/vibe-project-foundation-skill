# Vibe 项目地基

给从零开始、需要长期维护的软件项目搭地基。把你已经说清的使用场景、验收办法和下一步留在项目里，换一次对话，下一位助手也能接着做。

[下载 v1.2.0 安装包](https://github.com/AidenXu-1/vibe-project-foundation-skill/releases/download/v1.2.0/vibe-project-foundation-v1.2.0.zip) · [版本说明](https://github.com/AidenXu-1/vibe-project-foundation-skill/releases/tag/v1.2.0)

## 安装到 Codex

解压安装包，将其中的 `vibe-project-foundation` 文件夹放进 `~/.codex/skills/`。安装完成后，在下一轮对话中用 `$vibe-project-foundation` 调用。升级已有安装时，先将旧文件夹移到 Skills 目录外，再放入新版。

生成项目需要本机可用的 Bash、Python 3 和 Git。本版在 macOS、Python 3.9.6、Git 2.54.0 的环境中实测。

## 第一次使用

在一个独立的新项目目录中，对 Codex 说：

> 用 $vibe-project-foundation 给我搭一个 Mac 备课夹的地基。我想把讲义关联到一节课，完全退出再打开，从那节课还能找到原讲义。这次先只搭地基。

助手会把“退出、重开、回到同一节课、打开原讲义”写成后续开发可以照做的验收步骤。交接前，它会从本地保存的版本中重新读出需求和进度。此时 `app/` 里只有说明文件。等你要求继续开发，助手会从项目自己的工作入口接着做。

| 你想知道什么 | 去哪里看 |
| --- | --- |
| 产品要做什么，怎样算做成 | [需求模板](templates/docs/spec.md)生成的 `docs/spec.md` |
| 上次做到哪一步，接下来做什么 | [进度模板](templates/docs/progress.md)生成的 `docs/progress.md` |
| 换一个 AI 助手，从哪里接手 | 项目根目录的 `AGENTS.md` 和 `CLAUDE.md` 都指向[同一份工作规则](templates/docs/agent-guide.md) |
| 哪里放临时样本和实验记录 | `scratch/`，其中的实验文件会被 Git 忽略 |

## 直接运行生成脚本

如果只需铺设项目文件，也可以在终端运行：

```bash
bash ~/.codex/skills/vibe-project-foundation/scaffold.sh ~/Projects/备课夹 "备课夹" "按课程保存和找回讲义"
```

脚本会在目标目录保存并核对 21 个模板文件。它可以新建目录，也能复用尚无提交、暂存内容和其他文件的独立空 Git 仓库。目标须位于其他仓库之外，已有文件会保留。

如果脚本中途中断，解决提示的问题后，用同一版 Skill、同一目标和原参数重试。脚本已成功、只差整理需求时，直接接着交接。

这个 Skill 适用于持续迭代的软件、插件、小程序和网站。项目已经有合适的工程骨架时，直接沿用。[完整使用说明](SKILL.md)

## 许可

本仓库未附带 LICENSE 文件，默认保留所有权利。
