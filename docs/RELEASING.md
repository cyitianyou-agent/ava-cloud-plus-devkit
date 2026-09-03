# 发布指南

本项目使用语义化版本 `MAJOR.MINOR.PATCH`，以根目录 `VERSION` 和 `.codex-plugin/plugin.json` 中的 `version` 为准，两者必须一致。

## 版本选择

- `PATCH`：修正文档、规则或模板，不引入不兼容行为。
- `MINOR`：新增 Skill、模板或向后兼容能力。
- `MAJOR`：删除 Skill、改变关键工作流或引入需要迁移的不兼容变更。

## 发布步骤

1. 从最新 `main` 创建发布分支。
2. 运行 `python scripts/bump_version.py X.Y.Z`。
3. 把 `CHANGELOG.md` 的 `[Unreleased]` 内容移动到 `[X.Y.Z] - YYYY-MM-DD`。
4. 运行 `python scripts/validate.py`。
5. 提交并合并到 `main`。
6. 创建并推送带注释标签：`git tag -a vX.Y.Z -m "Release vX.Y.Z"`。
7. 运行 `git push origin main --follow-tags`。

`release.yml` 会验证标签与 `VERSION` 一致，并用 `CHANGELOG.md` 自动创建 GitHub Release。普通用户跟随 `main`；要求可复现的用户可以把 marketplace 固定到版本标签。

## 发布前检查

- 八个 Skill 均有合法 frontmatter，且目录内引用文件完整。
- 没有本机绝对路径、凭据、连接串或临时输出进入仓库。
- `VERSION`、manifest、Git 标签三者一致。
- README 中的安装命令与实际 GitHub owner、仓库名一致。
- 新版本已记录所有用户可见变化。
