# 业务对象与集合

## 对象类型

先从目标数据结构和同模块代码确定对象类型：

| 类型 | 根接口 | 行接口 | 常见根键 |
| --- | --- | --- | --- |
| 简单对象 | `IBOSimple` | `IBOSimpleLine` | `ObjectKey` |
| 主数据 | `IBOMasterData` | `IBOMasterDataLine` | `Code` |
| 单据 | `IBODocument` | `IBODocumentLine` | `DocEntry` |

附加能力接口如 `IBOSeriesKey`、`IBOUserFields`、数据所有权、取消/删除/引用标记等，只按数据结构和同类对象的真实语义实现，不按名称猜测。

## 接口与实现

一个标准 BO 需要保持以下契约一致：

- `I<Object>` 声明与对象类型匹配的父接口、属性 getter/setter 和子集合 getter。
- `<Object>` 继承 `BusinessObject<<Object>>`，实现对应接口及必要能力接口。
- 根 BO 使用 JAXB 类型/根元素注解和 `@BusinessObjectUnit`；行对象遵循同模块的 JAXB 约定。
- `DB_TABLE_NAME`、`BUSINESS_OBJECT_CODE`、`BUSINESS_OBJECT_NAME` 与数据结构一致。
- 每个持久化属性同时具有属性名常量、`@DbField`、`IPropertyInfo<T>`、`@XmlElement` getter 和 setter。
- Java 类型、`DataType`、`EditType`、主键/唯一键信息、数据库列名与 XML 定义一致。
- 枚举放在模块 `data` 包，沿用 `em...` 命名和目标模块的序列化方式。
- 金额、价格和数量使用项目的 decimal 工具与 `BigDecimal`，避免 `double` 运算；若同类对象提供字符串/数值重载，保持一致。

不要只增加字段和 getter/setter 而遗漏 `IPropertyInfo`，规则、Criteria 和客户端都依赖稳定的属性元数据名称。

## 初始化

`initialize()` 的基本不变量：

1. 首先调用 `super.initialize()`。
2. 创建所有一对多集合，并把 `this` 作为 parent。
3. 创建数据模型要求的一对一子对象。
4. 按目标模块现行写法设置已应用变量的对象编码。
5. 只设置业务上明确的默认值。

单据通常初始化日期和 `RELEASED` 状态，主数据通常初始化 `Activated=YES`；以同模块同类型对象为准。不要在初始化中访问仓储或执行跨对象持久化。

如果单据实现 `reset()`，必须先调用 `super.reset()`，再恢复根与行的默认状态；不要清掉框架需要保留的身份、跟踪或集合信息。

## 子集合

集合通常：

- 继承 `BusinessObjects<I<Line>, I<Parent>>`。
- 提供无参和带 parent 构造方法。
- `getElementType()` 返回具体行类。
- `create()` 创建具体行并通过 `add()` 加入。
- 自定义 `afterAddItem`、`afterRemoveItem`、`getElementCriteria`、`onParentPropertyChanged` 时先调用 `super`，除非已确认基类没有对应语义。

框架集合已负责常规 `LineId` 分配、根主键传播、父状态传播、脏标记和基础子查询条件。不要重复实现这些逻辑。只有业务额外值、特殊关联或孙表键才覆盖扩展点。

## 孙表

孙表不仅依赖根主键，还要通过 `ItemId` 指向父行：

- `afterAddItem` 设置孙项 `ItemId = parent.LineId`。
- `getElementCriteria` 同时限制根键和 `ItemId`。
- `onParentPropertyChanged` 在父行 `LineId` 或根键变化时传播到已有孙项。
- 父行 `initialize()` 创建孙集合并绑定 parent。

不能直接复用普通一层行集合的 Criteria，否则不同父行的孙项可能被混载。

## 属性规则

BO 在 `registerRules()` 返回 `IBusinessRule[]`：

- 必填、去空格、最小/最大值等通用约束优先使用已有 common rule。
- 多字段推导或模块语义放入 `rules` 专用类。
- 规则的 input properties 是触发/取值依赖，affected properties 是可能写回的属性；两者应准确，避免递归和漏触发。
- 规则错误使用 i18n，不硬编码面向用户的消息。

规则只处理单个 BO 图内的同步属性行为。查询或保存其他 BO 的逻辑应使用业务逻辑契约或 Repository，而不是从 rule 中打开仓储。

## 修改自检

- XML 模型、Java 接口和实现是否三方一致。
- 新字段是否具有正确映射、类型、序列化和属性元数据。
- 集合是否在初始化时绑定 parent。
- 新建、加载、修改根键和删除行时，主子键是否正确。
- 孙表是否同时按根键和 `ItemId` 查询。
- 默认值是否只在新对象初始化时生效，未覆盖加载值。
- 自定义规则是否声明完整 input/affected 属性并有边界测试。

