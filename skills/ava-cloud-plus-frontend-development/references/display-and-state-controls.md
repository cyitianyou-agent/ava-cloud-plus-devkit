# 只读、状态与服务控件

用于 ViewView、ObjectPage、状态控制、所有人、组织以及通用业务服务入口。

## 对象页只读控件

- 普通属性：`ObjectAttribute`。
- 外部 BO 说明：`RepositoryObjectAttribute`，其 Repository 与 `dataInfo` 必须有效。
- 是否和单据状态：`ObjectYesNoStatus`、`ObjectDocumentStatus` 或相应 `ObjectEnumStatus`。
- 数量和金额：`ObjectNumber`，`number` 与 `unit` 分别绑定数值和单位/币种。
- 可配置属性：`PropertyObjectAttribute`。

只读控件仍使用真实 BO 属性和匹配的数据类型。Repository 或链接服务不存在时不声明远程说明或链接能力。

## 所有人与组织

编辑所有人使用 `DataOwnerInput`，并绑定当前组织；查看使用 `UserObjectAttribute` 和 `OrganizationObjectAttribute`。数据类型通常分别为 `Numeric` 和 `Alphanumeric`，但以真实 BO 契约为准。

## 属性状态

单一状态可以直接绑定 `isNew` 等属性；多个状态使用 `parts` formatter。formatter 必须确定、无副作用，只返回显示、可编辑或启用状态，不能调用服务、修改 BO、触发事件或执行业务计算。

## 通用服务按钮

只有当前对象或选择集合真实支持服务代理时才显示服务按钮。ListView 传选中集合，EditView/ViewView 传当前页面 BO，并使用当前模块 `DataConverter`。

服务发现为空时安静返回；有服务时用 ActionSheet 显示国际化名称和图标。按钮事件只负责调用服务管理器，不在 View 内实现具体业务动作。

## 完成检查

- 只读控件与字段语义、数据类型和已有服务能力匹配。
- 所有人和组织使用专用控件并保持组织上下文。
- formatter 没有副作用。
- 服务按钮传递正确对象和转换器，不复制业务逻辑。
