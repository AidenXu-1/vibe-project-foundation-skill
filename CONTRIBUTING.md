# 贡献指南

谢谢你愿意改进 `vibe-project-foundation`。

这是一个 Codex Skill，不是普通项目模板。它的目标是帮新项目搭地基，而不是替用户决定需求、技术栈或产品方向。

## 修改原则

- 不要让它覆盖已有项目。
- 不要在地基阶段预设技术栈。
- 不要把非软件项目强行导向 `app/`、`design/`、`docs/spec.md` 这套软件结构。
- 不要在模板里替用户编需求。
- `docs/spec.md` 必须保持唯一开发准绳。
- `scratch/` 必须保持 Git 忽略。
- 修改模板后要运行验证脚本。

## 本地验证

```bash
bash scripts/verify_scaffold.sh
```

推荐同时运行：

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .
```

## Pull Request 检查清单

- [ ] 我运行过 `bash scripts/verify_scaffold.sh`。
- [ ] 我没有提交 `.DS_Store`、`__pycache__`、`.env` 或私有项目资料。
- [ ] 我没有让脚本覆盖非空目录。
- [ ] 我没有把需求判断、技术选型或产品方向写死进模板。
- [ ] 如果改了模板结构，我同步更新了验证脚本。
