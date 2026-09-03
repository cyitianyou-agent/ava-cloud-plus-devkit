# 可搜索选择输入框

本规范适用于客户编码、供应商编码、物料编码、物料目录编码、单位等字段：用户既可以输入编码或名称的一部分搜索建议，也可以点击值帮助按钮打开完整选择页面。用户确认建议项或弹窗选择后，由 Application 确定最终对象并回填关联字段。

## 一、继承关系和能力边界

```text
sap.m.Input
└─ sap.extension.m.Input
   └─ sap.extension.m.RepositoryInput
      └─ sap.extension.m.SelectionInput
         ├─ UserInput
         ├─ OrganizationInput
         ├─ BusinessObjectInput
         └─ BranchInput
```

### `sap.extension.m.Input`

在 OpenUI5 输入框基础上增加：

- `bindingValue`：Cloud+ 统一绑定值；
- `valueHelpOnly`：是否只能通过选择赋值，默认是 `true`；
- `showValueLink` / `valueLinkRequest`：当前值的业务对象链接；
- `valuePaste`：粘贴事件；
- 删除或退格清除只选值字段；
- 粘贴后触发建议；
- 建议列表只有一项时，回车可直接选中。

普通自由文本仍使用 `sap.extension.m.Input`。只有字段对应可查询 BO 时，才使用 `RepositoryInput` 或 `SelectionInput`。

### `sap.extension.m.RepositoryInput`

增加以下核心配置：

- `repository`：执行建议查询和描述查询的业务仓库；
- `dataInfo.type`：被查询的 BO 类型；
- `dataInfo.key`：真正写入 `bindingValue` 的属性；
- `dataInfo.text`：建议列表的描述属性；
- `criteria`：建议查询和选择的基础过滤条件，可为条件数组、`Criteria` 或动态函数；
- `describeValue`：绑定值回显时是否查询并显示描述，默认是 `true`；
- `showSuggestion`：是否启用输入建议；
- `itemConditions(item)`：把建议项转换成精确查询条件，交给 Application 确认和加载完整 BO。

当同时设置 `showSuggestion: true`、有效 `repository` 和 `dataInfo.type` 时，扩展控件会自动：

1. 把 `valueHelpOnly` 改为 `false`，允许直接输入；
2. 关闭前端本地过滤和自动完成；
3. 输入时调用 Repository 查询；
4. 克隆 `criteria`，避免污染原始条件；
5. 默认设置 `noChilds = true` 和较小的建议结果数；
6. 在 `dataInfo.key` 与 `dataInfo.text` 上追加 `CONTAIN` 条件，两者之间使用 `OR`；
7. 把查询结果转换成建议项，key 为编码、additionalText 为名称；
8. 精确匹配或仅有一条结果时，可自动触发 `suggestionItemSelected`。

因此 View 不应再写一套 key/name 模糊查询。View 只配置基础业务条件，并在选中建议后通知 Application。

### `sap.extension.m.SelectionInput`

它在 `RepositoryInput` 上增加：

- `chooseType`，默认单选；
- 默认 `valueHelpRequest`，可按 `dataInfo.type` 运行 BO 选择服务；
- `afterSelection`，在默认选择完成后返回完整对象集合。

如果选择结果只需要写回一个 key，优先使用 `SelectionInput` 的默认选择能力。如果选择客户或物料后还要同步名称、价格、税组、单位、仓库等关联数据，应使用 Application 管理的选择模式。

## 二、两条用户操作路径

### 路径 A：输入搜索

```text
输入编码/名称
-> RepositoryInput 的 suggest
-> Repository 按基础条件 + key/text 模糊条件查询
-> 用户选择建议项
-> suggestionItemSelected
-> View 将 itemConditions(selectedItem) 传给 Application
-> Application 查询/确认完整 BO，并更新当前主对象或子表行
```

### 路径 B：值帮助选择

```text
点击值帮助按钮
-> valueHelpRequest
-> View 触发 Application 的 choose...Event
-> Application 打开 Choose 服务
-> 用户确认对象
-> Application 更新当前主对象或子表行
```

两条路径原则上汇入同一个 Application 处理方法，保证输入选择和弹窗选择具有相同的业务校验及回填结果。输入建议路径会额外传入 `itemConditions(selectedItem)`；弹窗路径不传该参数，由同一方法展示完整候选范围。

需要特别注意：`RepositoryInput.criteria` 会自动参与输入建议查询；如果 `valueHelpRequest` 被 View 重写为 Application 事件，该 `criteria` 不会自动传给 Application。Application 必须自行构造相同的基础业务条件，或者按接口约定接收 View 传入的动态条件。

## 三、Application 端统一处理范式

主表字段的 Application 方法接收可选的建议筛选条件，把它们与选择服务的基础条件合并：

```ts
private choosePartner(filterConditions?: ibas.ICondition[]): void {
    let conditions: ibas.IList<ibas.ICondition> = partner.app.conditions.partner.create();
    // 输入建议传来精确的 key/text 条件；点击值帮助时没有此参数。
    if (filterConditions instanceof Array && filterConditions.length > 0) {
        if (conditions.length > 1) {
            conditions.firstOrDefault().bracketOpen++;
            conditions.lastOrDefault().bracketClose++;
        }
        conditions.add(filterConditions);
    }
    let that: this = this;
    ibas.servicesManager.runChooseService<partner.bo.IPartner>({
        boCode: partner.bo.Partner.BUSINESS_OBJECT_CODE,
        chooseType: ibas.emChooseType.SINGLE,
        criteria: conditions,
        onCompleted(selecteds: ibas.IList<partner.bo.IPartner>): void {
            let selected: partner.bo.IPartner = selecteds.firstOrDefault();
            if (ibas.objects.isNull(selected)) {
                return;
            }
            // 所有关联字段在这里统一回填，View 不承担此逻辑。
            that.editData.partnerCode = selected.code;
            that.editData.partnerName = selected.name;
            that.editData.currency = selected.currency;
            that.editData.paymentCode = selected.paymentCode;
        }
    });
}
```

子表字段采用同样方式，但还需要当前行，并在 Application 中追加价格清单、仓库、日期、业务用途等条件：

```ts
private chooseLineItem(
    caller: bo.DocumentLine,
    filterConditions?: ibas.ICondition[]
): void {
    let conditions: ibas.IList<ibas.ICondition>
        = materials.app.conditions.product.create(this.editData.documentDate);
    if (filterConditions instanceof Array && filterConditions.length > 0) {
        if (conditions.length > 1) {
            conditions.firstOrDefault().bracketOpen++;
            conditions.lastOrDefault().bracketClose++;
        }
        conditions.add(filterConditions);
    }

    let condition: ibas.ICondition = new ibas.Condition();
    condition.alias = materials.app.conditions.product.CONDITION_ALIAS_SALES_ITEM;
    condition.operation = ibas.emConditionOperation.EQUAL;
    condition.value = ibas.emYesNo.YES.toString();
    conditions.add(condition);

    if (!ibas.objects.isNull(caller) && !ibas.strings.isEmpty(caller.warehouse)) {
        condition = new ibas.Condition();
        condition.alias = materials.app.conditions.product.CONDITION_ALIAS_WAREHOUSE;
        condition.operation = ibas.emConditionOperation.EQUAL;
        condition.value = caller.warehouse;
        conditions.add(condition);
    }

    let that: this = this;
    ibas.servicesManager.runChooseService<materials.bo.IProduct>({
        boCode: materials.bo.BO_CODE_PRODUCT,
        chooseType: ibas.emChooseType.SINGLE,
        criteria: conditions,
        onCompleted(selecteds: ibas.IList<materials.bo.IProduct>): void {
            let selected: materials.bo.IProduct = selecteds.firstOrDefault();
            if (ibas.objects.isNull(selected)) {
                return;
            }
            // caller 为空时是否新建行，由具体 Application 契约决定。
            if (ibas.objects.isNull(caller)) {
                caller = that.editData.documentLines.create();
            }
            caller.itemCode = selected.code;
            caller.itemDescription = selected.name;
            caller.uom = selected.uom;
            caller.price = selected.price;
        }
    });
}
```

上例中的销售物料、仓库、价格等字段是“条件应由 Application 组合”的示范，不是所有物料输入框都必须带这些条件。实际条件必须来自目标业务的 Application 契约。

## 四、主表字段完整示例

以下模式适合 `customerCode`、`supplierCode` 等主表外键。示例只表达通用结构，客户启用条件等应替换为目标业务自己的条件。

```ts
/** 选择业务伙伴；可接收弹窗选择结果或建议项条件 */
choosePartnerEvent: Function;

new sap.extension.m.RepositoryInput("", {
    showValueHelp: true,
    valueHelpRequest: function (): void {
        // 弹窗选择路径：Application 决定如何打开选择服务及回填数据。
        that.fireViewEvents(that.choosePartnerEvent);
    },
    showValueLink: true,
    valueLinkRequest: function (event: sap.ui.base.Event): void {
        ibas.servicesManager.runLinkService({
            boCode: partner.bo.Partner.BUSINESS_OBJECT_CODE,
            linkValue: event.getParameter("value")
        });
    },
    // 编码字段显示编码；名称通常由相邻只读字段显示。
    describeValue: false,
    showSuggestion: true,
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    },
    suggestionItemSelected: function (
        this: sap.extension.m.RepositoryInput,
        event: sap.ui.base.Event
    ): void {
        let selectedItem: sap.ui.core.Item = event.getParameter("selectedItem");
        if (ibas.objects.isNull(selectedItem)) {
            return;
        }
        // 输入建议路径：把建议项转换为精确条件，仍交给同一 Application 方法。
        that.fireViewEvents(
            that.choosePartnerEvent,
            this.itemConditions(selectedItem)
        );
    },
    criteria: [
        new ibas.Condition(
            partner.bo.Partner.PROPERTY_ACTIVATED_NAME,
            ibas.emConditionOperation.EQUAL,
            ibas.emYesNo.YES.toString()
        )
    ]
}).bindProperty("bindingValue", {
    path: "partnerCode",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 20
    })
})
```

与编码相邻的名称通常只读：

```ts
new sap.extension.m.Input("", {
    editable: false
}).bindProperty("bindingValue", {
    path: "partnerName",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 100
    })
})
```

## 五、子表行字段完整示例

以下模式适合 `itemCode`。与主表字段相比，事件必须额外传当前绑定行。

```ts
/** 选择行物料；参数：当前行、其他业务参数、建议项精确条件 */
chooseLineItemEvent: Function;

new sap.extension.m.RepositoryInput("", {
    showValueHelp: true,
    valueHelpRequest: function (this: sap.extension.m.RepositoryInput): void {
        let line: bo.DocumentLine = this.getBindingContext().getObject();
        that.fireViewEvents(that.chooseLineItemEvent, line);
    },
    showValueLink: true,
    valueLinkRequest: function (event: sap.ui.base.Event): void {
        ibas.servicesManager.runLinkService({
            boCode: materials.bo.Material.BUSINESS_OBJECT_CODE,
            linkValue: event.getParameter("value")
        });
    },
    describeValue: false,
    showSuggestion: true,
    repository: materials.bo.BORepositoryMaterials,
    dataInfo: {
        type: materials.bo.Material,
        key: materials.bo.Material.PROPERTY_CODE_NAME,
        text: materials.bo.Material.PROPERTY_NAME_NAME
    },
    suggestionItemSelected: function (
        this: sap.extension.m.RepositoryInput,
        event: sap.ui.base.Event
    ): void {
        let selectedItem: sap.ui.core.Item = event.getParameter("selectedItem");
        if (ibas.objects.isNull(selectedItem)) {
            return;
        }
        let line: bo.DocumentLine = this.getBindingContext().getObject();
        that.fireViewEvents(
            that.chooseLineItemEvent,
            line,
            null,
            this.itemConditions(selectedItem)
        );
    },
    criteria: [
        new ibas.Condition(
            materials.app.conditions.product.CONDITION_ALIAS_SALES_ITEM,
            ibas.emConditionOperation.EQUAL,
            ibas.emYesNo.YES
        )
    ]
}).bindProperty("bindingValue", {
    path: "itemCode",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 50
    })
})
```

事件参数必须以实际 `I...View` 和 Application 方法签名为准。示例中的 `null` 只是表示某些单据方法在建议选择时保留了中间业务参数；不能机械复制到所有页面。

## 六、静态查询条件

业务约束与当前行无关时，使用条件数组：

```ts
criteria: [
    new ibas.Condition(
        bo.Item.PROPERTY_ACTIVATED_NAME,
        ibas.emConditionOperation.EQUAL,
        ibas.emYesNo.YES.toString()
    )
]
```

`RepositoryInput` 会把数组转换为 `Criteria`，建议查询时再克隆并追加 key/text 模糊条件。不要手工加入用户当前输入值。

## 七、动态查询条件

条件依赖当前主对象或子表行时，使用函数。输入建议每次查询前都会重新求值；`SelectionInput` 使用默认值帮助时也会重新求值。自定义 `valueHelpRequest` 必须由 View/Application 显式传递或重建所需条件：

```ts
criteria: function (
    source: sap.extension.m.RepositoryInput
): ibas.ICriteria {
    let criteria: ibas.Criteria = new ibas.Criteria();
    let line: bo.DocumentLine = source.getBindingContext()?.getObject();

    let condition: ibas.ICondition = criteria.conditions.create();
    condition.alias = bo.Item.PROPERTY_ACTIVATED_NAME;
    condition.operation = ibas.emConditionOperation.EQUAL;
    condition.value = ibas.emYesNo.YES.toString();

    if (!ibas.objects.isNull(line) && !ibas.strings.isEmpty(line.warehouse)) {
        condition = criteria.conditions.create();
        condition.alias = materials.app.conditions.product.CONDITION_ALIAS_WAREHOUSE;
        condition.operation = ibas.emConditionOperation.EQUAL;
        condition.value = line.warehouse;
    }
    return criteria;
}
```

优先从 `source.getBindingContext().getObject()` 或页面模型取得依赖值。通过 `form.getContent()[2]` 等数字索引读取其他控件属于脆弱写法，只能在没有模型路径和稳定控件引用时局部使用，不能作为通用示例。

## 八、`itemConditions` 的用途

建议项只保存 key 和显示文本，不一定是完整 BO。`itemConditions(selectedItem)` 会按 `dataInfo` 生成精确条件：

- key 条件：建议项的 `key`；
- 当 key 与 text 不同时，再生成 text 条件；
- 多个条件会组成同一括号组。

因此 Application 可以沿用既有选择方法，根据精确条件重新加载完整 BO，再统一执行权限、状态、单位、价格等业务处理。不要在 View 中把建议项强制转换为完整 BO。

## 九、`describeValue` 的选择

### 使用 `describeValue: false`

适用于绑定字段就是编码，且名称有独立显示字段的场景：

```text
customerCode + customerName
itemCode + itemDescription
```

输入框始终显示编码，`bindingValue` 与可见文本一致。

### 保持默认 `describeValue: true`

适用于只显示一个输入框、希望界面显示名称但模型保存 key 的场景。控件会按 key 查询描述并更新显示文本。此时必须正确配置 `repository`、`dataInfo.key` 和 `dataInfo.text`。

不要同时把名称显示在输入框和旁边的名称字段中，造成重复信息。

## 十、值链接

`RepositoryInput` 在 BO 存在查看服务时可以自动启用值链接，也可以显式配置：

```ts
showValueLink: true,
valueLinkRequest: function (event: sap.ui.base.Event): void {
    ibas.servicesManager.runLinkService({
        boCode: bo.Item.BUSINESS_OBJECT_CODE,
        linkValue: event.getParameter("value")
    });
}
```

只有当前值能够唯一定位 BO 且确有查看服务时才启用。子表的链接目标与绑定值不一致时，应从当前行取得真正的链接 key。

## 十一、何时使用 `SelectionInput`

如果选择后只需把目标 key 写入当前字段，不需要 Application 更新其他字段，可以使用默认选择服务：

```ts
new sap.extension.m.SelectionInput("", {
    showValueHelp: true,
    repository: master.bo.BORepositoryMaster,
    dataInfo: {
        type: master.bo.MasterData,
        key: master.bo.MasterData.PROPERTY_CODE_NAME,
        text: master.bo.MasterData.PROPERTY_NAME_NAME
    },
    criteria: [
        new ibas.Condition(
            master.bo.MasterData.PROPERTY_ACTIVATED_NAME,
            ibas.emConditionOperation.EQUAL,
            ibas.emYesNo.YES.toString()
        )
    ],
    afterSelection: function (event: sap.ui.base.Event): void {
        let selecteds: ibas.IList<any> = event.getParameter("selecteds");
        // 仅处理额外的界面联动；业务处理仍应交给 Application。
    }
}).bindProperty("bindingValue", {
    path: "masterCode",
    type: new sap.extension.data.Alphanumeric()
})
```

客户、供应商、物料等通常需要回填多个业务字段，优先采用前述 Application 管理模式，而不是依赖默认 key 回写。

## 十二、粘贴行为是条件能力

基础 `sap.extension.m.Input` 会在粘贴后触发 suggest，因此普通单值粘贴不需要额外代码。

只有可编辑表格明确支持从 Excel/多行文本批量粘贴时，才处理 `valuePaste`，并使用表格填充工具补行、逐格触发建议。多行粘贴是单据表格的增强能力，不是所有 `RepositoryInput` 的默认写法。

## 十三、实现检查表

- 字段对应可查询 BO，才使用 `RepositoryInput`/`SelectionInput`。
- `repository`、`dataInfo.type/key/text` 与真实 BO 一致。
- 需要输入搜索时设置 `showSuggestion: true`。
- 编码和名称分列显示时设置 `describeValue: false`。
- `criteria` 只放业务基础条件，不重复拼接用户输入的模糊条件。
- 动态条件从模型或当前绑定行读取，避免控件数字索引。
- `valueHelpRequest` 和 `suggestionItemSelected` 汇入同一个 Application 方法。
- 自定义 `valueHelpRequest` 时，由 Application 重建完整基础条件，不能误以为控件的 `criteria` 会自动传入。
- 子表事件传当前行对象。
- 建议项通过 `itemConditions` 交给 Application，不在 View 假装成完整 BO。
- 值链接只在 key 唯一且存在查看服务时启用。
- 多行粘贴只有明确业务需求时实现。
