# Repository Guidelines

## 项目定位

本仓库是 `ava-cloud-plus-devkit` 的源码仓库，同时也是可被 Codex 注册的 Git marketplace。仓库根目录本身构成一个 Codex 插件，集中发布 AVA Cloud+ 开发、业务对象建模和报表迁移相关 Skill。

## 目录与权威来源

- `.codex-plugin/plugin.json`：插件名称、版本、作者、能力和展示信息的权威 manifest。
- `.agents/plugins/marketplace.json`：Git marketplace 清单；当前插件源必须继续指向仓库根目录 `./`。
- `skills/<skill-name>/SKILL.md`：每个 Skill 的入口；目录名必须与 frontmatter 的 `name` 完全一致。
- `skills/<skill-name>/references/`：较长的规则和参考资料，仅由对应 Skill 按需读取。
- `skills/<skill-name>/assets/`：模板和其他必须随插件分发的资源。
- `VERSION`：当前发布版本；必须与插件 manifest 中的 `version` 一致。
- `CHANGELOG.md`：所有用户可见变更的版本记录。
- `docs/`：安装、更新、维护和发布说明。

## 修改约束

- Skill 必须自包含，只使用仓库内的相对路径引用，不依赖个人 profile、本机绝对路径或未随插件发布的文件。
- 不要把凭据、数据库连接串、服务器信息、客户数据、未脱敏报表或其他敏感内容提交到仓库。
- 修改模板或参考资料时保持原有格式、编码和领域约束；不要顺便重排或批量格式化无关内容。
- 新增、删除或重命名 Skill 时，同步检查插件 manifest、README、CHANGELOG 和 `scripts/validate.py` 中的数量及名称约束。
- 不添加 `.mcp.json`、`.app.json` 或相应 manifest 字段，除非该集成已经真实实现并经过验证。
- 不手工修改 Codex 的个人 marketplace、全局配置或插件缓存来替代仓库内的正确实现。

## 写作与代码风格

- 面向维护者的说明优先使用中文；代码、命令、标识符和官方字段名保留英文。
- 新增变量优先使用简洁的 camelCase 名称，通常控制为一到两个英文单词。
- 每行只写一条语句，避免把多条操作堆叠在同一行。
- 新增代码注释应说明意图、约束、边界条件和关键步骤，不重复代码字面行为。
- Markdown 链接优先使用相对路径，确保 GitHub 与本地克隆都能正确访问。

## 验证要求

修改后至少在仓库根目录运行：

```powershell
python scripts/validate.py
```

提交前还应检查：

```powershell
git diff --check
git status --short
```

校验失败时应先修复根因，不得通过删除必要规则、跳过文件或放宽约束来掩盖问题。

## 版本与发布

- 遵循语义化版本 `MAJOR.MINOR.PATCH`。
- 只有明确准备发布时才运行 `python scripts/bump_version.py X.Y.Z`；普通文档或维护提交不要擅自升级版本。
- 用户可见行为、Skill、模板或安装方式发生变化时，更新 `CHANGELOG.md` 的 `[Unreleased]`。
- 标签、Release 和完整发布步骤遵循 `docs/RELEASING.md`。

## Git 工作流

- 默认分支为 `main`，远程仓库使用 SSH：`git@github.com:cyitianyou-agent/ava-cloud-plus-devkit.git`。
- 提交信息采用 Conventional Commits，例如 `feat:`、`fix:`、`docs:` 或 `chore:`。
- 保留用户已有改动，不重置、不覆盖、不删除与当前任务无关的文件。
- 未经明确要求，不创建标签、不发布 Release、不推送远程，也不使用强制推送。
