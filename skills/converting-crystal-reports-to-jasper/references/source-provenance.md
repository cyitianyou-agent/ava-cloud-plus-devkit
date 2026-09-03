# JasperReports 7.0.3 源码依据

本 Skill 的 JRXML 规范与模板从 JasperReports Library 7.0.3 源码提炼。这里记录仓库相对路径，Skill 运行时不读取、不依赖这些源码文件或创建者电脑。

| 依据 | 源码仓库相对路径 | 提炼内容 |
|---|---|---|
| 7.0.0 兼容性说明 | `README.md` | 7.x 用 Jackson XML 替换 Digester，6.x JRXML 不再由 7.x Library 单独兼容 |
| 参数化 SQL、字段、标准区段 | `demo/samples/subreport/reports/AddressReport.jrxml` | `parameter`、`query`、`field`、直接 band、`element kind` |
| 样式、变量、分组、表达式 | `demo/samples/jasper/reports/FirstJasper.jrxml` | `style`、`variable`、`group/expression`、group header/footer |
| Filter 与文本元素 | `demo/samples/query/reports/QueryReport.jrxml` 及 datasource 示例 | `filterExpression`、textField、line、page footer |
| 线、矩形、椭圆 | `demo/samples/shapes/reports/ShapesReport.jrxml` | `line`、`rectangle`、`ellipse`、`pen` |
| 子报表 | `demo/samples/subreport/reports/MasterReport.jrxml` | `element kind="subreport"`、参数与连接表达式 |
| XML 写出配置 | `core/src/main/java/net/sf/jasperreports/engine/xml/JRXmlWriter.java` | JRXML 写出及 UUID 排除配置的存在 |
| XML 对象模型 | `core/src/main/java/net/sf/jasperreports/engine/**` | Jackson XML 属性、元素名和对象关系 |

模板是针对 Crystal 迁移场景重新编写的最小示例，不复制完整官方 demo。目标基线固定为 JasperReports Library 7.0.3；未来升级到新的 7.x 小版本时，应重新对照该版本源码示例再更新规范。
