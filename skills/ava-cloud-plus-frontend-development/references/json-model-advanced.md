# JSONModel 局部与高级模式

仅在 Dialog、Popover、同一控件树的多上下文、小型组合模型或已确认的特殊刷新需求中使用。本文件建立在 [JSONModel 基础绑定](json-model-bindings.md) 之上。

## Dialog 与 Popover

临时编辑一个对象时，把对象模型绑定到局部容器，不覆盖主 Page：

```ts
dialog.setModel(
    new sap.extension.model.JSONModel(data)
);
```

局部模型只服务该交互，并在容器关闭或销毁后结束生命周期。维护主 BO 内真实行对象时直接绑定该行；只有取消操作必须放弃修改时才创建临时副本，并由 Application 定义确认后的合并协议。

ActionSheet 可以直接绑定短生命周期的服务数组，因为其聚合使用模型根 `/`；不要把这种形状推广到业务 DataTable。

## 命名模型

只有同一控件树必须同时访问两个独立对象时才使用命名模型。名称表达业务上下文，如 `role`，绑定路径显式写成 `role>/property`。

- 不用 `model1` 等无语义名称。
- 不用多个命名模型替代本可独立绑定的多个 Table。
- 不把同一对象同时放入默认模型和命名模型。
- 模型设置在能覆盖所有使用者的最近共同容器上。

## 小型组合模型

局部控件确实需要“集合 + 少量共同上下文”时可以使用：

```ts
this.table.setModel(new sap.extension.model.JSONModel({
    rows: datas,
    currency: currency
}));
```

该模型必须只绑定局部容器，附加字段直接参与显示、数量少且不重复主 BO，`rows` 保留真实行对象，数据由 Application 或 `show...` 参数提供。

如果组合模型逐渐包含用户、权限、按钮状态、多个集合和查询结果，应重新拆分边界或把业务状态交回 Application。

## 手工刷新

只在以下情况考虑 `model.refresh(...)`：

- 普通数组原地变化且没有 `ibas.Bindable` 通知；
- formatter 依赖多个值而既有控件没有重新求值；
- 树、拖拽或分组结构原地重排；
- 既有组件契约明确要求刷新。

`setForcedRefresh(true)` 仅用于已验证自动刷新不足的局部模型，不在按键或 formatter 中强制刷新整页。

## 常见失控形状

- 页面级总模型同时包含主对象、多个集合、查询结果和 UI 状态。
- 给同一组子控件重复设置同一模型，而不是设置在共同父容器。
- 已有独立 `showLines()` 契约，却让 Table 深层绑定 Page 的 `/orderLines`。
- View 查询 Repository 后把结果塞入总模型。

这些形状会扩大刷新范围、混淆职责，并削弱扩展模型对直接 BO 和浅层数组的监听能力。
