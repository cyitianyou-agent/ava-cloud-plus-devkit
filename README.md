# AVA Cloud+ Devkit

`ava-cloud-plus-devkit` 是一个面向 Codex 的 Git marketplace 插件，把多项 AVA Cloud+ 开发技能打包为一次安装、统一更新的工具集。

## 按开发流程使用 Skill

| 阶段 | Skill | 用途 |
| --- | --- | --- |
| 0. 完整交付编排 | `delivering-ava-cloud-plus-feature` | 从业务需求建立交付契约，路由后续阶段并追踪整体完成度 |
| 1. 业务模型确认 | `generating-ava-cloud-business-objects` | 创建、局部更新，或校验修正 Excel 转换得到的 `datastructures` XML |
| 2. 代码框架生成 | `generating-ava-cloud-code` | 使用 `btulz.transforms` 从已确认模型生成 Java 与 TypeScript PC 骨架并安全合并 |
| 3a. Java 后端开发 | `ava-cloud-plus-backend-development` | 联动 BO、规则、逻辑、仓储、REST、初始化资源和测试 |
| 3b. TypeScript PC 前端开发 | `ava-cloud-plus-frontend-development` | 联动 `api`、`borep`、`bsapp` 与 `bsui/c` |
| 3c. 可选报表旁路 | `converting-crystal-reports-to-jasper` | 将 Crystal Reports RPT/RptToXml 元数据迁移为 JasperReports Library 7.x JRXML |
| 4. 数据库落地 | `evolving-ava-cloud-plus-database` | 使用 `ds`、`dsJar`、`sql` 和 bobas `ds/init` 落地结构与初始化数据 |
| 5. 最终跨层验收 | `verifying-ava-cloud-plus-feature` | 汇总模型、Java、REST、TypeScript PC、数据库、业务行为和可选报表证据 |

标准链路是按需求裁剪的分支图；局部需求只使用真正受影响的阶段：

```text
交付契约
    ├── 业务模型确认 → 代码候选 → Java / TypeScript PC
    │                                  ↓
    │                            构建门禁 → 数据库落地或跳过 ──┐
    └── Crystal/RptToXml → JRXML → 报表静态检查（可选）───────┤
                                                               ↓
                                                          最终跨层验收
```

数据库操作会改变外部状态。插件可以在未连接数据库时完成规划、输入检查和构建门禁，但只有用户明确授权目标环境后才执行数据库命令。报表迁移默认只提供静态转换证据，编译、数据和版式需要相应运行环境。完整的阶段输入、输出和返回规则见 [AVA Cloud+ 完整功能开发流程](docs/DEVELOPMENT_WORKFLOW.md)。

八个 Skill 的引用文档、模板、辅助脚本和代理界面配置均随插件发布，不依赖作者电脑上的原始目录。

## 安装

要求使用支持 `codex plugin` 命令的 Codex 客户端。

先注册这个 GitHub 仓库作为 marketplace：

```powershell
codex plugin marketplace add cyitianyou-agent/ava-cloud-plus-devkit --ref main
```

再安装插件：

```powershell
codex plugin add ava-cloud-plus-devkit@ava-cloud-plus-devkit
```

安装完成后请新建一个 Codex 任务，使新 Skill 被完整加载。也可以在 Codex 客户端的 Plugins 页面中找到已注册 marketplace 下的 `AVA Cloud+ Devkit` 并安装。

更详细的安装、更新和故障排查见 [安装与更新指南](docs/INSTALLATION.md)。

## 更新

插件跟随 Git marketplace 的 `main` 分支发布。作者推送新提交后，Codex 需要刷新 marketplace 快照才能取得新版本；客户端是否在后台自动刷新由 Codex 版本和客户端策略决定。需要立即更新时运行：

```powershell
codex plugin marketplace upgrade ava-cloud-plus-devkit
codex plugin add ava-cloud-plus-devkit@ava-cloud-plus-devkit
```

然后新建一个 Codex 任务。第二条命令用于确保已安装插件重新指向最新快照，重复执行是安全的。

## 使用示例

- “从这项业务需求开始，帮我完成 AVA Cloud+ 的建模、前后端开发、数据库落地和验收。”
- “帮我在 AVA Cloud+ 的库存模块里新增一个 PC 端编辑功能。”
- “帮我在 AVA Cloud+ 的销售模块新增一个 Java 后端业务逻辑，并补齐仓储、REST 和测试。”
- “模块简称是 `MM`，请根据描述生成一个主数据业务对象 XML，输出到指定目录。”
- “使用这份业务对象 Excel 或 XML 调用 btulz.transforms 生成代码，并把新增对象安全合并到现有模块。”
- “使用模块 JAR 中的数据结构和初始化 SQL 更新已授权的测试数据库，并核验结果。”
- “按需求验收这个功能的 XML、Java、REST、TypeScript、数据库和保存重载行为。”
- “把这份 RptToXml XML 转为 JasperReports 7.x JRXML。”

也可以显式指定 Skill，例如：

```text
使用 $generating-ava-cloud-business-objects 根据下面的业务描述生成数据结构 XML。
```

## 仓库结构

```text
ava-cloud-plus-devkit/
├── .agents/plugins/marketplace.json  # Git marketplace 清单
├── .codex-plugin/plugin.json         # Codex 插件 manifest
├── skills/                           # 八个可独立触发、可按流程协作的 Skill
├── scripts/                          # 本地校验与版本更新脚本
├── docs/                             # 安装、发布与维护文档
├── VERSION                           # 唯一发布版本号
└── CHANGELOG.md                      # 版本变更记录
```

## 本地校验

本仓库的校验脚本只依赖 Python 标准库：

```powershell
python scripts/validate.py
```

发布版本时使用：

```powershell
python scripts/bump_version.py 0.2.0
```

脚本会同步 `VERSION` 与 `.codex-plugin/plugin.json`。随后维护 `CHANGELOG.md`、提交并创建对应的 `v0.2.0` 标签。完整流程见 [发布指南](docs/RELEASING.md)。

## 贡献

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。提交前必须运行仓库校验，并确保每个 Skill 的目录名与其 `SKILL.md` frontmatter 中的 `name` 一致。

## 许可证

[MIT](LICENSE)
