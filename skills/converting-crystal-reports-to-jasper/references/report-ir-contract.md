# Report IR 上下文契约

Report IR 是模型在当前任务上下文中维护的脱敏中间结构，不是正式输出文件，也不需要任何脚本或 JSON Schema 运行时。

```json
{
  "source": {"name": "SalesOrder.rpt"},
  "report": {
    "name": "SalesOrder",
    "pageWidth": 595,
    "pageHeight": 842,
    "columnWidth": 555,
    "margins": {"left": 20, "right": 20, "top": 20, "bottom": 20}
  },
  "database": {
    "type": "sqlServer",
    "originalSql": "SELECT ... WHERE OrderNo = {?Order_No}",
    "jasperSql": "SELECT ... WHERE OrderNo = $P{Order_No}",
    "dialectChanged": false
  },
  "parameters": [
    {"name": "Order_No", "crystalType": "StringField", "javaClass": "java.lang.String", "usage": ["query"]}
  ],
  "fields": [],
  "groups": [],
  "sections": [],
  "unsupported": [],
  "issues": []
}
```

## 必备不变量

- `database.type` 只能是 `sqlServer`、`mysql`、`unknown`。
- `originalSql` 是脱敏元数据中的原始字符序列；`jasperSql` 只替换已知参数占位符。
- `dialectChanged` 必须为 `false`；否则停止生成。
- 参数同时保留 Crystal 类型与 Java 类型；`name` 不标准化。
- 每个 section 保留原名称、语义类型、高度、分页/抑制属性和对象列表。
- 每个对象保留来源类型、位置、尺寸、内容/表达式、样式及转换决定。
- `unsupported` 和 `issues` 只保存非敏感摘要，不保存凭据或连接信息。

## 使用方式

先建立报表/数据库/参数/字段，再建立分组/区段/对象。生成 JRXML 后逐项回填迁移状态：`mapped`、`degraded`、`unsupported`。Report IR 仅用于推理和复查，单文件模式不得另行输出；批量报告只取其非敏感摘要。
