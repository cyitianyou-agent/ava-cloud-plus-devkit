# AVA Cloud+ 数据结构 XML 模型

## 目录

- [节点层级](#节点层级)
- [Domain](#domain)
- [Model](#model)
- [Property](#property)
- [Index](#index)
- [IndexProperty](#indexproperty)
- [BusinessObject](#businessobject)
- [RelatedBO](#relatedbo)
- [枚举](#枚举)
- [源码能力与推荐用法](#源码能力与推荐用法)

本文已整理生成业务对象所需的 XML 节点与属性能力，可独立使用。XML 属性名区分大小写。

## 节点层级

```text
Domain
├── Model *
│   ├── Property *
│   └── Index *
│       └── IndexProperty *
└── BusinessObject *
    └── RelatedBO *
        └── RelatedBO * ...
```

`Domain` 结构允许多个 `BusinessObject`，AVA Cloud+ 新建文件通常只放一个主对象。`RelatedBO` 可以递归嵌套。

## Domain

| 属性 | 类型 | 说明 |
|---|---|---|
| `Name` | 字符串 | 领域或模块名称，例如 `Manufacturing` |
| `ShortName` | 字符串 | 模块缩写；生成时只使用当前会话或上游交付契约中已经确认的值 |
| `Description` | 字符串 | 可选描述 |

子节点：零到多个 `Model`，零到多个 `BusinessObject`。业务数据结构至少各需要一个。

## Model

| 属性 | 类型 | 说明 |
|---|---|---|
| `Name` | 字符串 | 模型名称，也是业务对象映射引用键 |
| `Description` | 字符串 | 中文业务描述 |
| `ModelType` | `emModelType` | 模型类型 |
| `Mapped` | 字符串 | 数据库表映射 |
| `Entity` | 布尔 | 可选；源码默认 `true` |

子节点：零到多个 `Property`，零到多个 `Index`。

`ModelType`：

- `Unspecified`
- `MasterData`
- `MasterDataLine`
- `Document`
- `DocumentLine`
- `Simple`
- `SimpleLine`

## Property

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Name` | 字符串 | 无 | 代码属性名 |
| `Description` | 字符串 | 无 | 中文描述 |
| `DeclaredType` | 字符串 | 无 | Java/TypeScript 声明类型或枚举名 |
| `PrimaryKey` | 是否 | `No` | 主键标识 |
| `UniqueKey` | 是否 | `No` | 唯一键标识 |
| `SearchKey` | 是否 | `No` | 搜索键标识 |
| `DataType` | `emDataType` | `Alphanumeric` | 数据类型 |
| `DataSubType` | `emDataSubType` | `Default` | 数据编辑子类型 |
| `EditSize` | 整数 | `8` | 编辑或存储长度 |
| `Mapped` | 字符串 | 无 | 数据库列映射 |
| `Linked` | 字符串 | 无 | 可选关联信息 |
| `DefaultValue` | 字符串 | 无 | 可选默认值 |

模板使用 `Yes` 表示 `PrimaryKey`、`UniqueKey` 等是否属性为真。

## Index

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Name` | 字符串 | 无 | 可选完整名称 |
| `ShortName` | 字符串 | 无 | 索引短名；常用于生成最终索引名 |
| `Description` | 字符串 | 无 | 描述 |
| `IndexType` | `emIndexType` | `NonClustered` | 索引类型 |

子节点：一个或多个 `IndexProperty`。如果省略 `IndexType`，源码按 `NonClustered` 处理。

## IndexProperty

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Name` | 字符串 | 无 | 必须引用同一 `Model` 的 `Property.Name` |
| `Direction` | 字符串 | `ASC` | `ASC` 或 `DESC` |

## BusinessObject

| 属性 | 类型 | 说明 |
|---|---|---|
| `Name` | 字符串 | 可选；未写时源码使用 `MappedModel` |
| `Description` | 字符串 | 可选描述 |
| `ShortName` | 字符串 | 业务对象代码 |
| `MappedModel` | 字符串 | 必须引用一个 `Model.Name` |

子节点：零到多个 `RelatedBO`。

## RelatedBO

`RelatedBO` 继承 `BusinessObject` 的 `Name`、`Description`、`ShortName` 和 `MappedModel`，并增加：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Relation` | `emBORelation` | `OneToMany` 或 `OneToOne` |

行模型通常使用 `OneToMany`；当映射模型是主表类型时，源码可以推导为 `OneToOne`。AVA Cloud+ 的子表和孙表统一明确写 `OneToMany`。

## 枚举

### emDataType

```text
Unknown
Alphanumeric
Memo
Numeric
Date
Decimal
Bytes
Boolean
```

### emDataSubType

```text
Default
Address
Phone
Date
Time
Rate
Sum
Price
Quantity
Percentage
Measurement
Link
Image
Email
Short
Long
```

### emIndexType

```text
NonClustered
Clustered
Unique
UniqueClustered
```

### emBORelation

```text
OneToMany
OneToOne
```

### emYesNo

```text
No
Yes
```

## 源码能力与推荐用法

Java 枚举只说明解析器能够表示这些值，不代表用户自定义界面允许任意组合。

新建字段采用界面正式组合：

```text
Alphanumeric → Default, Address, Phone
Memo         → Default
Numeric      → Default
Date         → Date, Time
Decimal      → Rate, Sum, Price, Quantity, Percentage, Measurement
Bytes        → Default
Unknown      → Default
```

扩展组合仅在用户明确指定时使用：

```text
Boolean      → Default
Alphanumeric → Link, Image, Email
Numeric      → Short, Long
```

目标 XML 可能包含 `Date/Default`、`Numeric/Quantity` 等历史例外。更新时保留这些原值；新增字段不要模仿。
