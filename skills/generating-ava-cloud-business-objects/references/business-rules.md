# AVA Cloud+ 业务对象规则

## 目录

- [规则优先级](#规则优先级)
- [对象类型](#对象类型)
- [强制模板](#强制模板)
- [主键和层级](#主键和层级)
- [命名](#命名)
- [字段推断](#字段推断)
- [枚举](#枚举)
- [索引](#索引)
- [节点顺序](#节点顺序)
- [更新边界](#更新边界)
- [快速检查](#快速检查)

## 规则优先级

依次采用：用户本次明确要求、当前会话已确认信息、上游交付契约中已确认的事实、更新任务的目标 XML、内置模板和规则、默认推断。低优先级资料不得覆盖高优先级的明确业务值。

模板规定的主键、行键和父子关联是结构性不变量，不属于普通默认推断。用户说法与这些不变量冲突时，先指出差异和数据库兼容影响并请求确认；在用户明确要求改变建模约定前，不增加第二套主键或静默覆盖模板。明确批准结构性例外后，把它记录为模型设计变化并要求数据库兼容方案。

目标 XML 只用于更新定位、重复检查和保留原值，不用于单独推断模块简称或新建对象惯例。`${Company}`、`Date/Default`、`Numeric/Quantity` 等历史写法在更新中保留，在新建中不照抄。

独立创建任务不扫描现有模块对象、源码或固定目录来猜测事实。模块简称来自当前会话或上游交付契约中的已确认值；输出位置优先采用用户指定位置或交付契约已确认路径，无法可靠确定时询问用户。

新建对象、新增模型或修正 `Domain.ShortName` 时，把模块简称作为生成前置条件。当前会话和上游交付契约均未提供已确认值，或两者存在冲突时，当前轮次只询问模块简称并停止对应修改，不通过项目检索给出候选简称。

## 对象类型

| 业务特征 | 主表类型 | 行类型 |
|---|---|---|
| 配置、记录、映射关系 | `Simple` | `SimpleLine` |
| 独立编码和名称、长期档案、被其他业务引用 | `MasterData` | `MasterDataLine` |
| 单据编号、日期、状态、明细、上下游单据关系 | `Document` | `DocumentLine` |

判断明确时直接使用并报告依据；两个类型均合理时请求用户确认。

一份新 XML 通常只包含一个主 `BusinessObject`。主表可以有多个子表，子表可以继续包含孙表；所有行关系使用 `OneToMany`。

## 强制模板

| 对象类型 | 模板 |
|---|---|
| 简单对象 | `assets/templates/ds_ud_simple.xml` |
| 主数据 | `assets/templates/ds_ud_masterdata.xml` |
| 单据 | `assets/templates/ds_ud_document.xml` |

创建主表或行表时，复制模板中相同 `ModelType` 的全部 `Property`，保留字段名称、映射、主键、唯一键、声明类型和相对顺序。业务字段追加在强制字段之后。

不要通过一份手写字段清单重建模板。模板文件是强制字段的唯一基准；创建后直接对照模板逐字段自检。

## 主键和层级

| 模型类型 | 主键 | 额外约束 |
|---|---|---|
| `Simple` | `ObjectKey` | 无 |
| `SimpleLine` | `ObjectKey + LineId` | 孙表另加非主键 `ItemId` |
| `MasterData` | `DocEntry` | `Code` 为唯一键，不是主键 |
| `MasterDataLine` | `Code + LineId` | 孙表另加非主键 `ItemId` |
| `Document` | `DocEntry` | 无 |
| `DocumentLine` | `DocEntry + LineId` | 孙表另加非主键 `ItemId` |

孙表 `ItemId` 固定采用：

```xml
<Property Name="ItemId" Description="父级行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="ItemId"/>
```

`ItemId` 紧跟 `LineId`，记录直接父级子表的 `LineId`，不得设置 `PrimaryKey="Yes"`。

层级结构：

```xml
<BusinessObject MappedModel="Main" ShortName="AVA_AA_OBJECT">
  <RelatedBO Relation="OneToMany" MappedModel="Child">
    <RelatedBO Relation="OneToMany" MappedModel="Grandchild"/>
  </RelatedBO>
</BusinessObject>
```

## 命名

### 模块和对象代码

- 新建采用 `AVA_AA_BBB`。
- `AVA` 固定。
- `AA` 使用当前会话或上游交付契约中已经确认的模块简称，长度为 1–5；同时写入 `Domain.ShortName`。
- `BBB` 使用业务对象英文大写，可读缩写后保证完整对象代码不超过 30 位。
- 更新保留现有 `ShortName`，包括 `${Company}` 和旧缩写。

### 表映射

主表表标识使用四位大写字母：`O + 三位业务缩写`。例如生产订单使用 `OPDO`。

```text
主表：AVA_MF_OPDO
子表 1：AVA_MF_PDO1
子表 2：AVA_MF_PDO2
子表 1 的孙表 1：AVA_MF_PDO11
子表 1 的孙表 2：AVA_MF_PDO12
```

同级表按 XML 中的业务顺序从 `1` 开始编号。新建不跳号；更新已有对象时沿用现有索引并选择未占用值。

### 文件、模型和字段

- 文件名：`ds_<模块缩写小写>_<主对象英文名小写>.xml`。
- `Domain.Name`：根据当前会话中的模块名称生成英文名；无法可靠确定时询问用户。
- `Model.Name`：英文 `PascalCase`；子表和孙表名称继续包含父级语义。
- `Property.Name`：语义完整的英文 `PascalCase`。
- `Property.Description`：中文业务名称。
- `Property.Mapped`：默认与 `Name` 相同；过长或冲突时使用可读缩写。
- 同一 `Model` 内的字段 `Name` 和 `Mapped` 都必须唯一。

## 字段推断

根据当前会话中的字段语义推断，并采用以下正式组合：

| `DataType` | 合法 `DataSubType` |
|---|---|
| `Alphanumeric` | `Default`、`Address`、`Phone` |
| `Memo` | `Default` |
| `Numeric` | `Default` |
| `Date` | `Date`、`Time` |
| `Decimal` | `Rate`、`Sum`、`Price`、`Quantity`、`Percentage`、`Measurement` |
| `Bytes` | `Default` |
| `Unknown` | `Default` |

默认长度：

| 语义 | `EditSize` |
|---|---:|
| `Numeric`、`Date`、`Decimal` | 8 |
| 是否或状态枚举 | 1 |
| 普通编码 | 8 |
| 业务对象代码 | 30 |
| 名称、一般短文本 | 100 |
| 较长参考文本 | 200 |
| GUID、动作标识 | 36 |
| 长文本 | 使用 `Memo/Default` |

数量用 `Decimal/Quantity`，金额或合计用 `Decimal/Sum`，单价用 `Decimal/Price`，百分比用 `Decimal/Percentage`，换算率用 `Decimal/Rate`，长度、面积、重量等度量用 `Decimal/Measurement`。

所有默认推断都在完成报告中标注。更新现有字段时只修改用户点名的属性，不顺带统一其他字段。

## 枚举

优先使用当前会话明确给出的枚举或内置模板已有的通用枚举。是否字段优先使用：

```xml
DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo"
```

找不到匹配枚举时，允许生成语义明确的 `DeclaredType`，例如 `emInspectionCycleType`。XML 可以先引用该名称；在完成报告中列入“待补全枚举”。

源码还允许 `Boolean`、`Link`、`Image`、`Email`、`Short`、`Long`。不要自动推断这些扩展值；用户明确指定时允许使用并报告警告。

## 索引

尽量少加索引。

- 主键和模板唯一键按模板生成。
- 用户明确说明字段或字段组合唯一时设置 `UniqueKey="Yes"`。
- 用户明确说明高频查询、筛选或关联条件时生成 `Index`。
- 只有会话明确说明高频查询、筛选或关联条件时才增加相应索引。
- 仅凭字段名称无法确定时，只在结果中提出建议，不写入 XML。
- 每个 `IndexProperty.Name` 必须引用同一 `Model` 已存在字段。

## 节点顺序

1. `Domain` 下先放全部 `Model`，后放 `BusinessObject`。
2. 每个 `Model` 先放模板强制字段，再放业务字段，最后放 `Index`。
3. 孙表 `ItemId` 是唯一允许插入模板字段序列的业务字段，位置紧跟 `LineId`。
4. 更新时保持所有原节点的相对顺序。
5. 新字段优先放在同义字段附近；无法判断时放在最后一个 `Property` 后。

## 更新边界

默认允许：

- 增加字段。
- 修改用户明确指定的字段属性或长度。
- 增加子表、孙表和对应 `RelatedBO`。
- 增加明确必要的少量索引。

默认禁止：

- 删除或重命名现有节点。
- 修改 `Domain`、`BusinessObject` 或 `Model` 属性。
- 迁移历史对象代码和表映射。
- 缩短字段长度。
- 重排或批量格式化 XML。
- 修复与本次需求无关的历史问题。

用户明确要求默认禁止项时，先说明影响，再限定到用户点名的目标。修改已有 `Property` 属性时，记录精确的 `Model.Property.Attribute`，并逐项与原文件对照。

## 快速检查

- [ ] 新建、新增模型或修正简称所需的模块简称来自当前会话或上游交付契约；未确认时已经询问用户。
- [ ] 输出位置来自用户指定位置或上游交付契约；无法判断时已经询问用户。
- [ ] 对象类型有明确语义依据。
- [ ] 所有主表和行表完整复制对应模板字段。
- [ ] 主键、唯一键和孙表 `ItemId` 正确。
- [ ] 新建对象和表映射使用 `AVA`，更新保留历史值。
- [ ] 字段类型和编辑类型属于合法组合。
- [ ] 同一作用域没有重复名称或映射。
- [ ] `RelatedBO` 指向存在且类型正确的 `Model`。
- [ ] 没有添加无法证明必要的索引。
- [ ] 已直接阅读最终 XML，确认标签、属性引号、节点层级和引用关系完整。
- [ ] 实际 diff 没有无关变化。
