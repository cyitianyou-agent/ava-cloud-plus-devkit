---
name: converting-crystal-reports-to-jasper
description: Use when converting Crystal Reports RPT or RptToXml metadata into portable JasperReports Library 7.x JRXML, especially parameterized SQL Server or MySQL reports.
---

# Crystal Reports 转 JasperReports 7.x

将 Crystal 报表语义迁移为 JasperReports Library 7.x 的 Jackson XML 格式。Skill 自带规范与模板，不依赖创建它的电脑、源码目录、Python、PowerShell、数据库连接或 Jasper 编译环境。

## 开发流程位置

本 Skill 是报表迁移的独立分支，不属于“业务对象建模 → 代码生成 → 前后端开发 → 数据库 → 验收”的标准功能链。只有完整功能明确包含 Crystal 报表迁移时，才由 `delivering-ava-cloud-plus-feature` 把它作为并行交付项纳入最终验收。

## 选择输入

- 优先使用已经提取的 RptToXml XML；读取前先按 [`references/crystal-xml-map.md`](references/crystal-xml-map.md) 清除凭据、服务器、连接串、保存数据和当前参数值。
- 输入为 `.rpt` 时，只使用目标环境已经具备的只读提取能力。不要下载安装组件，不要修改源 RPT。无法读取二进制 RPT 时，停止该文件并说明需要用户提供 RptToXml XML。
- 单文件与批量均可；批量按文件名稳定排序，单项失败后继续。

## 转换

1. 读取 [`references/report-ir-contract.md`](references/report-ir-contract.md)，在上下文中建立脱敏 Report IR；不要把 IR 写入正式输出目录。
2. 读取 [`references/conversion-rules.md`](references/conversion-rules.md)，保留数据库类型、参数原名、SQL 方言、字段、分组、区段、坐标和样式。不能确定的内容进入问题清单，禁止虚构。
3. 生成前读取 [`references/jrxml-7-core.md`](references/jrxml-7-core.md)；涉及图片、形状、子报表或复杂元素时再读取 [`references/jrxml-7-elements.md`](references/jrxml-7-elements.md)。
4. 选择 [`assets/jrxml7-base.jrxml`](assets/jrxml7-base.jrxml)、[`assets/jrxml7-parameterized-sql.jrxml`](assets/jrxml7-parameterized-sql.jrxml) 或 [`assets/jrxml7-grouped-report.jrxml`](assets/jrxml7-grouped-report.jrxml) 作为结构起点，并为报表和元素生成互不重复的 UUID。

## 不可变约束

- 只生成 JasperReports 7.x 新格式：`<query>`、直接 band、`<element kind="...">`、`<expression>`；不得混入 6.x 的 `<queryString>`、`<reportElement>`、嵌套 `<staticText>` 或 `<textField>` 结构。
- 参数名与 Crystal 完全一致，不改大小写、空格、下划线或命名风格。SQL 中只转换已知参数：`{?Name}` 变为 `$P{Name}`；独立字符串参数 `'{?Name}'` 必须连同外层单引号一起变为 `$P{Name}`，不得生成 `'$P{Name}'`。
- 一个报表只保留原 SQL Server 或 MySQL 方言。不得格式化、翻译或优化 SQL；不得把值参数改为 `$P!{}`。
- 不连接数据库、不执行 SQL、不编译 `.jasper`、不声称数据或版式已验证。

## 复查与修复

输出前由模型对照 IR 复查参数集合、SQL、字段、分组、区段、元素、UUID 和敏感信息，并检查 XML 声明、标签闭合、属性转义及 CDATA。SQL 复查必须确认所有 `$P{Name}` 都是可绑定的 JDBC 值参数，禁止出现 `'$P{Name}'`；若 Crystal 原文是独立的 `'{?Name}'`，只允许移除包裹该参数的这一对单引号。只修复确定的问题，最多两轮；修复不得顺便改 SQL、参数名或布局。两轮后仍不确定则停止该文件并报告。

## 输出

JRXML 文件必须是 UTF-8 纯 XML，不加 Markdown 围栏或说明文字。单文件只生成一个 `.jrxml`，问题在回复中列出；批量生成成功的 `.jrxml` 和唯一 `conversion-report.json`。默认不覆盖已有文件。完整契约见 [`references/output-contract.md`](references/output-contract.md)。规范来源说明见 [`references/source-provenance.md`](references/source-provenance.md)。
