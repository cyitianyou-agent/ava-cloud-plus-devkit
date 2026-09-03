# AVA Cloud+ Devkit

`ava-cloud-plus-devkit` 是一个面向 Codex 的 Git marketplace 插件，把多项 AVA Cloud+ 开发技能打包为一次安装、统一更新的工具集。

## 包含的技能

| Skill | 用途 |
| --- | --- |
| `ava-cloud-plus-frontend-development` | 创建、修改或评审 AVA Cloud+ TypeScript 前端业务模块，联动 `api`、`borep`、`bsapp` 与 `bsui/c` |
| `ava-cloud-plus-backend-development` | 创建、修改或评审 AVA Cloud+ Java 后端业务模块，联动 BO、规则、逻辑、仓储、REST 与初始化资源 |
| `generating-ava-cloud-business-objects` | 根据自然语言创建或局部更新 AVA Cloud+ `datastructures` XML |
| `converting-crystal-reports-to-jasper` | 将 Crystal Reports RPT/RptToXml 元数据迁移为 JasperReports Library 7.x JRXML |

四个 Skill 的引用文档、模板和代理界面配置均随插件发布，不依赖作者电脑上的原始目录。

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

- “帮我在 AVA Cloud+ 的库存模块里新增一个 PC 端编辑功能。”
- “帮我在 AVA Cloud+ 的销售模块新增一个 Java 后端业务逻辑，并补齐仓储、REST 和测试。”
- “模块简称是 `MM`，请根据描述生成一个主数据业务对象 XML，输出到指定目录。”
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
├── skills/                           # 四个可独立触发的 Skill
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
