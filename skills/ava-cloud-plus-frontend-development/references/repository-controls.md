# Repository 与选择控件

用于外部业务对象、关键字建议、值帮助和行级选择。字段同时支持输入搜索和弹窗选择时，还必须读取 [可搜索选择输入框](searchable-inputs.md)。

## RepositoryInput

`RepositoryInput` 负责按输入值提供 Repository 建议，并通过 `valueHelpRequest` 把弹窗选择请求交给 Application：

```ts
new sap.extension.m.RepositoryInput("", {
    showValueHelp: true,
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    },
    valueHelpRequest: function (): void {
        that.fireViewEvents(that.choosePartnerEvent);
    }
}).bindProperty("bindingValue", {
    path: "partnerCode",
    type: new sap.extension.data.Alphanumeric()
})
```

Repository、BO 类型、key、text 和绑定字段必须形成同一契约。复杂的静态/动态条件、`describeValue` 与建议行为由 `searchable-inputs.md` 定义。

## SelectionInput

需要通用固定条件选择时使用 `SelectionInput`，通过 `criteria` 提供明确的 `ibas.Condition`。不要把依赖当前行或页面状态的动态条件固化在 View 构造函数中。

## RepositoryText

列表中需要把外键解析为说明时使用 `RepositoryText`，并复用与输入控件一致的 Repository 和 `dataInfo`。不需要说明或远程查询时使用普通 `Text`。

## 行级值帮助

子表选择事件必须传递当前真实行对象：

```ts
valueHelpRequest(this: sap.extension.m.Input): void {
    let line: bo.ItemLine = this.getBindingContext().getObject();
    that.fireViewEvents(that.chooseLineItemEvent, line);
}
```

不要按表格索引回查行。选择结果由 Application 回填到该行；View 不查询后直接修改其他业务对象。

选择约束被多个页面复用时，采用模块已有 `component.*` 控件，不在多个 View 复制 Repository 和条件逻辑。

## 完成检查

- Repository、BO 类型、key、text 和绑定字段匹配。
- 输入建议与值帮助两条路径都能回到同一 Application 契约。
- 行级事件携带真实行对象。
- 选择 Mapping 已在 Console 注册，移动端代码未被引入。
