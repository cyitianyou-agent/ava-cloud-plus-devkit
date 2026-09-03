# RptToXml 元数据读取与脱敏

RptToXml 不同分支的节点层级可能略有差异。按 XML 的本地名称和语义读取，不依赖创建者电脑的路径或固定命名空间。

## 必须先清除

在任何模型分析之前，删除或遮蔽名称忽略大小写、空格、连字符和下划线后等价于下列项目的属性或节点：

- `UserName`、`Password`
- `ServerName`、`DataSource`、`ConnectionString`
- `ParameterCurrentValue(s)`、`ParameterInitialValue(s)`
- `SavedData`、`SavedRecord(s)`、`DataSnapshot`

`HasSavedData` 设为 `False`。若无法判断某段连接/保存数据是否已清除，停止当前报表；不要把原 XML 复制到问题报告。

## 语义定位

| 语义 | 常见节点/关键字 | 缺失时 |
|---|---|---|
| 报表属性 | `Report`, `ReportOptions`, `PrintOptions` | 使用安全页面默认值并提示 |
| 原始 SQL | `Database/Command`, `CommandText`, `SQLQueryString` | 不虚构 SQL；提示需补充 |
| 数据库类型 | `Database`, `DatabaseName`, `Provider`, `DLL`, `ConnectionInfo` | 标记 `unknown` |
| 参数 | `ParameterFieldDefinitions`, `ParameterFieldDefinition` | 参数列表为空 |
| 字段 | `DatabaseFieldDefinitions`, `FieldDefinitions`, `DatabaseFieldDefinition` | 不虚构字段 |
| 分组/排序 | `GroupNameFields`, `SortFields`, `Groups` | 不生成 group |
| 记录筛选 | `RecordSelectionFormula` | 无过滤表达式 |
| 区段 | `Areas/Sections` | 生成最小 detail 并提示 |
| 对象 | `Sections/ReportObjects` | 区段保持为空并提示 |
| 子报表 | `SubreportObject`, `Subreports` | 不生成子报表 |

## 数据库识别

- 元数据明确出现 Microsoft SQL Server、SQL Server、MSSQL 或对应 provider 时记为 `sqlServer`。
- 元数据明确出现 MySQL 或对应 provider/driver 时记为 `mysql`。
- 连接信息被脱敏后仍无法判断时记为 `unknown`；不得从 SQL 函数风格反向猜数据库。

连接属性只能用于识别数据库家族，不能进入 JRXML、Report IR、回复或批量报告。
