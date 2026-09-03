# Crystal → JasperReports 7.x 转换规则

## 数据库与 SQL

1. 从 Crystal 元数据识别当前报表的数据库类型，只接受 `sqlServer`、`mysql` 或 `unknown`。
2. `sqlServer` 继续使用 SQL Server SQL，`mysql` 继续使用 MySQL SQL。`unknown` 不猜测。
3. 保存原 SQL 的完整字符序列，只扫描已提取参数的精确名称。未加引号的 `{?Name}` 替换为 `$P{Name}`。
4. Crystal 字符串值参数若以独立 SQL 字符串字面量出现，即完整形式为 `'{?Name}'`，替换时必须同时移除这一对单引号，生成 `$P{Name}`。JasperReports 会把 `$P{Name}` 转成 JDBC `?`；若生成 `'$P{Name}'`，数据库收到的是字符串常量 `'?'`，PreparedStatement 无法绑定该参数。
5. 仅当单引号内的完整内容恰好是一个已知参数时应用上一条规则。`'%{?Name}%'`、`'prefix{?Name}'` 等参数与其他文本混合的复合字面量不得机械去引号或改写；记录为未确定 SQL 参数表达式并停止该报表，避免改变 SQL Server 或 MySQL 语义。
6. 除第 4 条所述 JDBC 值参数边界外，其他字符、空白、换行、大小写、引号、函数和注释保持不变。
7. 不把 Crystal 值参数映射为 `$P!{Name}`。已有原 SQL 若本来含动态拼接，只原样保留并提示风险。
8. Crystal Record Selection 不在 SQL 中时，仅把确定的简单布尔条件映射为 `filterExpression`；不得为了“合并条件”改写原 SQL。

## 参数类型

| Crystal 类型 | Java class |
|---|---|
| StringField、文本 | `java.lang.String` |
| Int8sField、Int8uField、Int16sField、Int16uField | `java.lang.Integer` |
| Int32sField、Int32uField、IntegerField | `java.lang.Long` |
| NumberField、CurrencyField、DecimalField | `java.math.BigDecimal` |
| DateField | `java.sql.Date` |
| DateTimeField、TimeStampField | `java.sql.Timestamp` |
| TimeField | `java.sql.Time` |
| BooleanField | `java.lang.Boolean` |
| 未知 | `java.lang.String`，并记录推断警告 |

参数 `name` 逐字复制。显示提示可另用描述文本，但不得借此重命名参数。

## 区段

| Crystal | JasperReports 7.x | 处理 |
|---|---|---|
| Report Header | `title` | 单 band，height 位于 `title` |
| Page Header | `pageHeader` | 单 band |
| Group Header | `group/groupHeader/band` | 需要明确 group expression |
| Details | `detail/band` | 多个 Details 区段可生成多个 band |
| Group Footer | `group/groupFooter/band` | 汇总变量按组 reset |
| Page Footer | `pageFooter` | 单 band |
| Report Footer | `summary` | 单 band |
| 无数据区段 | `noData` | 仅原报表有等价语义时生成 |

Crystal “Suppress” 公式只有在能可靠转换成 Java 布尔表达式时才变成取反后的 `printWhenExpression`。New Page Before/After 需根据区段语义选择 group 分页属性或 break 元素；不确定时报告，不能猜测。

## 对象

| Crystal 对象 | Jasper 7.x |
|---|---|
| TextObject | `element kind="staticText"` + `text` |
| DatabaseFieldObject | `element kind="textField"` + `$F{...}` expression |
| ParameterFieldObject | `element kind="textField"` + `$P{...}` expression |
| FormulaFieldObject | `textField`；仅转换已确认的 Java 等价表达式 |
| LineObject | `element kind="line"` |
| BoxObject | `element kind="rectangle"` |
| BlobFieldObject/PictureObject | `element kind="image"` |
| SubreportObject | `element kind="subreport"`；前提是参数和连接映射完整 |
| 未知/OLE/复杂图表 | 不静默丢弃；进入 unsupported/warning |

## 坐标与尺寸

- 保留对象相对其 Crystal 区段的层级和顺序。
- 若元数据明确单位是 twip，使用 `round(twip / 20)` 转为 Jasper 整数单位。
- 若提取器已经输出 point/pixel，直接使用；不得再次除以 20。
- 负坐标、超出 band、宽高为零、对象重叠都应在问题清单中说明。除防止 XML 无法表达外，不自动“美化”布局。

## 公式

- 可直接映射：字段/参数引用、字符串/数字常量、明确的算术和布尔运算、简单 null 判断。
- 需要报告：Crystal 专用函数、共享变量、running total、复杂日期/字符串语义、动态数组、打印状态函数、跨区段引用。
- 不能确定时保留原公式文本到内部问题记录，不把原 Crystal 公式直接写成 Java expression。

## 生成后对照

逐项比较：参数集合与引用、SQL 除占位符及其独立字符串字面量外层引号外的字符序列、字段集合、group 与 section 数量、对象类型与几何、样式、未支持项、数据库类型以及敏感值。额外扫描 SQL，确认不存在 `'$P{Name}'` 形式的 JDBC 值参数。任何缺失或新增都必须能追溯到输入或明确的降级决定。
