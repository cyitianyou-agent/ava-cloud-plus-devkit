# 输出契约

## 单文件

- 正式产物只有 `<source-name>.jrxml`。
- 回复中列出数据库类型、参数名、SQL 占位符迁移、未支持项和不确定项。
- 不输出 Crystal XML、Report IR、临时文件、验证脚本或额外报告。
- 同名文件存在时默认停止，不覆盖。

## 批量

- 每个成功输入生成一个同名 `.jrxml`。
- 整批只额外生成一个 `conversion-report.json`；失败项没有伪造的 JRXML。
- 单项失败不终止后续项；按文件名稳定顺序处理。

```json
{
  "schemaVersion": "1.0",
  "summary": {"total": 3, "succeeded": 2, "failed": 1},
  "reports": [
    {
      "source": "A.rpt",
      "output": "A.jrxml",
      "status": "GENERATED",
      "databaseType": "sqlServer",
      "parametersPreserved": true,
      "sqlPreserved": true,
      "reviewRounds": 1,
      "warnings": []
    }
  ]
}
```

状态使用 `GENERATED`、`GENERATED_WITH_WARNINGS`、`INPUT_UNREADABLE`、`SANITIZATION_STOPPED`、`GENERATION_STOPPED`。由于本 Skill 不连接数据库、不编译 Jasper、不运行外部验证器，禁止使用暗示已编译或已运行验证的状态名。

## JRXML 文件要求

- UTF-8 XML 声明。
- 只含一个 `jasperReport` 根元素，不带 Markdown 围栏。
- 不包含凭据、服务器、连接串、保存数据、本机绝对路径、内部推理或问题说明。
- 使用 JasperReports 7.x 新结构；UUID 互不重复。
- 不承诺数据库执行、Jasper 编译、数据正确性或视觉一致性。
