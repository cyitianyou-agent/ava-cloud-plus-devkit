# 基础控件与数据类型

本文件用于选择 PC View 的基础编辑控件和数据类型。模型设置位置、数据形状和刷新规则见 [JSONModel 基础绑定](json-model-bindings.md)。

涉及外部 BO、值帮助或选择输入时读取 [Repository 与选择控件](repository-controls.md)；涉及 ViewView 只读展示、状态、所有人、组织或服务按钮时读取 [只读、状态与服务控件](display-and-state-controls.md)。

## 控件选择

| 字段语义 | 编辑控件 | 列表/表格 | 数据类型 |
| --- | --- | --- | --- |
| 文本、编码 | `sap.extension.m.Input` | `Text` / `DataLink` | `Alphanumeric` |
| 整数、内部主键 | `Input` 或专用控件 | `Text` | `Numeric` |
| 数量 | `Input` | `Text` | `Quantity` |
| 金额、合计 | `Input` | `Text` | `Price` / `Sum` |
| 汇率 | `Input` / 汇率组件 | `Text` | `Rate` |
| 日期、时间 | `DatePicker` / `TimePicker` | `Text` | `Date` / `Time` |
| 是/否 | `CheckBox` / `TipsCheckBox` / `EnumSelect` | `Text` | `YesNo` |
| 枚举和状态 | `EnumSelect` | `Text` | `Enum` 或专用类型 |
| 可配置属性 | `PropertySelect` | `PropertyText` | 与属性一致 |

## 普通输入

```ts
new sap.extension.m.Input("", {
}).bindProperty("bindingValue", {
    path: "name",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 100
    })
})
```

Label 的 `required` 来自 BO 或 Application 的真实约束。已知长度时在数据类型中设置 `maxLength`。

## 日期、时间、是否与枚举

分别使用扩展 `DatePicker`、`TimePicker`、`CheckBox` 和 `EnumSelect`，并绑定匹配的 `Date`、`Time`、`YesNo` 和枚举数据类型。

只有改变状态存在明确风险时使用 `TipsCheckBox`；提示使用国际化键。

## 编号系列

编号输入与 `SeriesSelect` 通常相邻。已有对象不允许切换系列；自动系列启用时通常不允许手工修改编号。对象 code、`series` 和 `isNew` 绑定必须来自真实 BO。

## 可配置属性

编辑使用 `PropertySelect`，列表使用 `PropertyText`。两者的 `dataInfo.code` 和 `propertyName` 必须对应同一业务对象及属性，不用普通枚举控件替代动态属性配置。

## 表格显示

普通字段使用扩展 `Text`；只有链接服务已经注册并可由 PC Navigation 打开时才使用 `DataLink`。行控件继续使用相对属性路径和匹配的数据类型。

## 桌面表格

- ListView、ChooseView 和可编辑子表默认使用 `sap.extension.table.DataTable`。
- ViewView 只读子表默认使用 `sap.extension.m.DataTable`。
- 只有真实层级数据才使用扩展 TreeTable。
- `sap.m.Table` 名称中的 `m` 不表示它只能用于移动端；判断依据是目标 PC 页面结构。
