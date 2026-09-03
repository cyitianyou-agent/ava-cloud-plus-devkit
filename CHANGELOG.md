# Changelog

本项目的显著变更记录在此文件中，格式参考 Keep a Changelog，版本号遵循语义化版本。

## [Unreleased]

### Added

- `ava-cloud-plus-backend-development` Skill，覆盖 AVA Cloud+ Java 后端业务对象、规则、跨对象逻辑、仓储、REST、初始化资源和测试。
- `generating-ava-cloud-code` Skill，使用 `btulz.transforms` 从业务对象 Excel 或 XML 隔离生成前后端代码；Excel 会先转换、校验并去重汇总为 XML，再按空模块、新增对象、新增模型或新增字段执行安全复制与增量合并。

## [0.1.0] - 2026-09-02

### Added

- 初始 Codex 插件与 Git marketplace manifest。
- `ava-cloud-plus-frontend-development` Skill。
- `generating-ava-cloud-business-objects` Skill。
- `converting-crystal-reports-to-jasper` Skill。
- 安装、更新、贡献、安全与发布文档。
- 本地校验、语义化版本更新和 GitHub Actions 工作流。

[Unreleased]: https://github.com/cyitianyou-agent/ava-cloud-plus-devkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cyitianyou-agent/ava-cloud-plus-devkit/releases/tag/v0.1.0
