# 跨层验收矩阵

## 字段链路

| 层 | 核对项 |
| --- | --- |
| datastructures | `Property.Name`、`Mapped`、类型、子类型、长度、键和默认值 |
| Java BO | 属性常量、`@DbField`、注册、getter/setter、规则 |
| Repository/REST | 查询条件、App/Svc 类型、具体序列化类型、Resolver |
| TypeScript api | 接口属性、枚举、集合类型和 Repository 契约 |
| TypeScript borep | 映射常量、getter/setter、转换和工厂注册 |
| Application/View | 条件、赋值、绑定路径、控件数据类型和语言键 |
| 数据库 | 实际列、类型、长度、默认值、索引和 BO 字段元数据 |

字段只在实际受影响层检查。例如纯内部字段不要求生成页面控件，但仍要检查会读取或序列化该对象的上下游是否兼容。

## 对象与集合链路

| 语义 | 核对项 |
| --- | --- |
| 对象标识 | XML `BusinessObject.ShortName`、Java/TypeScript code、Repository、控件 `dataInfo` |
| 模型映射 | XML `Model.Mapped`、Java 数据表常量、数据库表 |
| 主子关系 | `RelatedBO`、Java 集合父属性、TypeScript 集合所有权、编辑应用和数据库键 |
| 孙表关系 | `ItemId`、父 `LineId`、Criteria、上下文切换、保存后重新加载 |
| 查询保存 | App/Svc 契约、Repository 实现、REST、前端 Repository 和 Application |
| 注册入口 | Resolver、BOFactory、Console、Function/Mapping、PC Navigation |

## 行为场景

按需求选取，不机械要求全部执行：

- 新建最小有效对象并保存；
- 按主键或业务条件查询并重新加载；
- 修改字段和子集合后再次保存；
- 删除、取消或关闭操作；
- 无效值、无权限和重复数据错误；
- 规则计算和默认值；
- 跨对象正向影响与反向撤销；
- 事务失败后的回滚；
- List、Edit、Choose、View 及服务 Mapping 的实际入口；
- PC View 的字段绑定、子孙表切换、busy、错误消息和刷新。

## 可选 Jasper 报表

仅在交付契约包含 Crystal/Jasper 报表时使用：

| 层次 | 核对项 |
| --- | --- |
| 输入与 IR | 输入已脱敏；参数、SQL、字段、分组、区段、元素和布局语义可追踪 |
| JRXML 静态结构 | JasperReports 7.x 元素格式、XML、UUID、表达式和参数引用有效 |
| SQL 与参数 | 保留原数据库方言；参数名一致；没有 `'$P{Name}'` 或错误的 `$P!{}` |
| 编译 | 只有实际 Jasper 编译成功才标记通过；环境缺失时标记未运行 |
| 数据 | 只有使用授权数据执行并核对结果后才标记通过 |
| 版式 | 只有实际渲染并对照后才标记通过；JRXML 已生成不等于版式通过 |

报表转换 Skill 默认只能提供前三项证据。编译、数据和版式是否属于必要验收条件，以交付契约为准。

## 验收记录

结果使用以下字段，保持简洁且可追踪：

| 验收条件 | 涉及层 | 证据 | 结论 | 剩余事项 |
| --- | --- | --- | --- | --- |
| 用户可观察结果 | 模型/后端/前端/数据库 | 命令、测试或运行结果 | 通过/部分通过/失败/不适用 | 条件或修复阶段 |

自动化测试优先验证业务结果，不把“方法可调用”作为唯一断言。手工运行验证要记录可复现步骤和实际结果，但不记录凭据或客户数据。
