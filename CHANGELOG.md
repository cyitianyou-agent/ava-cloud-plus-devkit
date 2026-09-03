# Changelog

本项目的显著变更记录在此文件中，格式参考 Keep a Changelog，版本号遵循语义化版本。

## [Unreleased]

## [0.2.0] - 2026-09-03

### Added

- `delivering-ava-cloud-plus-feature` Skill，建立交付契约并按业务建模、代码生成、后端、前端、数据库和验收阶段编排完整功能。
- `evolving-ava-cloud-plus-database` Skill，基于 `btulz.transforms` 的 core `ds`、`dsJar`、`sql` 与 bobas `ds/init` 命令落地数据结构、初始化 SQL 和初始业务数据，并执行后置核验。
- `verifying-ava-cloud-plus-feature` Skill，按验收条件检查 datastructures、Java、REST、TypeScript、数据库和实际业务行为的一致性。
- 完整功能开发流程文档，明确 Skill 顺序、阶段交接、构建与数据库门禁及失败返回规则。
- `ava-cloud-plus-backend-development` Skill，覆盖 AVA Cloud+ Java 后端业务对象、规则、跨对象逻辑、仓储、REST、初始化资源和测试。
- `generating-ava-cloud-code` Skill，使用 `btulz.transforms` 从业务对象 Excel 或 XML 隔离生成前后端代码；Excel 会先转换、校验并去重汇总为 XML，再按空模块、新增对象、新增模型或新增字段执行安全复制与增量合并。

### Changed

- 现有建模、代码生成、后端、前端和报表 Skill 增加其在完整开发流程中的位置与交接边界。
- 将完整功能流程重编排为条件分支：后端、TypeScript PC 前端和可选报表共享已确认模型，并在构建门禁后按需进入数据库和最终验收。
- 统一阶段所有权和交接结果；业务对象 Skill 现在同时负责创建、更新和校验 Excel 转换模型，代码生成不再自行定义模型语义。
- 当前前端生成、实现和验收范围统一为 `bsui/c` PC 端；模板产生的 `bsui/m` 候选明确跳过。
- 最终验收与数据库前构建门禁分离，并补充 JasperReports 静态、编译、数据和版式验收边界。
- 统一主数据键规则：主表以 `DocEntry` 为主键、`Code` 为唯一键，行表以 `Code + LineId` 为联合主键。
- 按 Application 类型、JSONModel 使用场景和控件类别拆分前端参考资料，减少局部任务加载无关规范和示例。

## [0.1.0] - 2026-09-02

### Added

- 初始 Codex 插件与 Git marketplace manifest。
- `ava-cloud-plus-frontend-development` Skill。
- `generating-ava-cloud-business-objects` Skill。
- `converting-crystal-reports-to-jasper` Skill。
- 安装、更新、贡献、安全与发布文档。
- 本地校验、语义化版本更新和 GitHub Actions 工作流。

[Unreleased]: https://github.com/cyitianyou-agent/ava-cloud-plus-devkit/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/cyitianyou-agent/ava-cloud-plus-devkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cyitianyou-agent/ava-cloud-plus-devkit/releases/tag/v0.1.0
