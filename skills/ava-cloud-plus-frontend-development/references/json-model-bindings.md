# JSONModel 数据绑定与模型边界

Cloud+ PC View 的常规绑定方式不是构造一个覆盖整页所有数据和状态的 ViewModel，而是围绕**可独立显示、刷新和替换的控件单元**建立小模型。

最稳定的默认关系是：

```text
一个 Page / ObjectPage       -> 当前主 BO
一个业务 Table              -> { rows: 当前集合 }
一个独立 Dialog / Popover    -> 当前对象或一个小型临时结构
一个分页 ListView/ChooseView -> 表格自己的 { rows: 已加载结果 }
```

这些模型可以同时存在。子控件从最近的模型继承数据，表格自己的模型会自然隔离表格行数据，不需要把整页数据拼成一个总对象。

## 一、默认使用 Cloud+ 扩展 JSONModel

业务 View 优先使用：

```ts
new sap.extension.model.JSONModel(data)
```

不要在标准页面中无理由换成：

```ts
new sap.ui.model.json.JSONModel(data)
```

`sap.extension.model.JSONModel` 继承 OpenUI5 原生 `JSONModel`，并补充了 Cloud+ BO 所需的行为：

- 对直接绑定的 `ibas.Bindable` 注册属性变化监听；
- 对直接绑定的数组成员注册变化监听；
- 对 `{ rows: datas }` 这类浅层结构中的 Bindable 和数组成员注册监听；
- BO 属性变化时自动刷新绑定；
- 提供 `addData()`，用于分页表格向 `/rows` 追加数据；
- 提供 `size()`、`setForcedRefresh()` 等扩展能力；
- 模型销毁时移除已注册的 BO 监听。

这意味着模型中应保留真实 BO 实例，不要先做 JSON 深拷贝：

```ts
// 正确：保留 BO 身份、状态和属性变化通知。
new sap.extension.model.JSONModel(data)

// 不推荐：丢失 BO 类型、方法、状态以及 Bindable 通知能力。
new sap.extension.model.JSONModel(
    JSON.parse(JSON.stringify(data))
)
```

只有目标控件或既有第三方组件明确要求原生 `sap.ui.model.json.JSONModel`，且不需要 Cloud+ BO 监听和扩展方法时，才局部使用原生模型。历史自定义页面中的原生模型不是标准 View 的默认写法。

## 二、先确定模型边界，再写绑定路径

使用以下顺序判断：

1. 哪个控件是一组数据的稳定显示边界？通常是 `Page`、`ObjectPageLayout`、`Table`、`Dialog` 或局部容器。
2. 这个控件一次只显示一个对象，还是一个集合？
3. 这组数据是否会独立刷新或替换？如果会，就应有独立模型。
4. 子控件是否只需要这一组数据？如果是，让它继承最近的模型。
5. 只有同一控件树确实需要同时访问两个独立对象时，才考虑命名模型。

### 默认决策表

| 显示单元 | 模型数据 | 聚合绑定 | 字段绑定 |
| --- | --- | --- | --- |
| EditView 主 Page | `bo.Root` | 无 | `path: "name"` |
| ViewView ObjectPage | `bo.Root` | 无 | `path: "name"` |
| ListView/ChooseView 表格 | `{ rows: bo.Root[] }` | `rows: "{/rows}"` | `path: "name"` |
| EditView 可编辑子表 | `{ rows: bo.Line[] }` | `rows: "{/rows}"` | `path: "itemCode"` |
| ViewView 只读子表 | `{ rows: bo.Line[] }` | `items.path: "/rows"` | `path: "itemCode"` |
| 孙表下钻页 | `{ rows: bo.GrandLine[] }` | `rows: "{/rows}"` | `path: "value"` |
| 独立对象对话框 | 当前对象 | 无 | `path: "/content"` 或按现有控件约定使用相对路径 |
| 临时选择列表 | `{ rows: items }` | `/rows` | 行内相对路径 |

表中的模型数据都是浅层形状。`{ rows: datas }` 只是集合的统一入口，不是将业务数据重新映射成 DTO。

## 三、主 Page 直接绑定当前 BO

EditView 和 ViewView 的主控件直接绑定 Application 传入的当前 BO：

```ts
private page: sap.extension.m.Page;

showOrder(data: bo.Order): void {
    this.page.setModel(
        new sap.extension.model.JSONModel(data)
    );
    sap.extension.pages.changeStatus(this.page);
}
```

字段使用主对象属性名，不额外增加 `data`、`root`、`current` 等包装层：

```ts
new sap.extension.m.Input("", {
}).bindProperty("bindingValue", {
    path: "customerCode",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 20
    })
})
```

避免以下形状：

```ts
// 不推荐：只为主对象增加一层无意义路径。
this.page.setModel(new sap.extension.model.JSONModel({
    data: data
}));

// 随后的所有绑定被迫写成 data/customerCode。
```

主 Page 模型的职责是表达“当前正在编辑或查看的对象”。页面状态控制也依赖这个模型中的 `isNew`、`isDirty`、单据状态等 BO 属性。

## 四、每个业务表格绑定自己的 `/rows`

PC 编辑表、列表表和选择表通常使用：

```ts
this.table = new sap.extension.table.DataTable("", {
    rows: "{/rows}",
    columns: [
        new sap.extension.table.DataColumn("", {
            label: ibas.i18n.prop("bo_orderline_itemcode"),
            template: new sap.extension.m.Input("", {
            }).bindProperty("bindingValue", {
                path: "itemCode",
                type: new sap.extension.data.Alphanumeric({
                    maxLength: 50
                })
            })
        })
    ]
});

showOrderLines(datas: bo.OrderLine[]): void {
    this.table.setModel(
        new sap.extension.model.JSONModel({ rows: datas })
    );
}
```

`/rows` 是模型根上的集合路径；进入某一行后，单元格模板获得该行的绑定上下文，所以字段继续写相对路径 `itemCode`，不要写 `/rows/0/itemCode`。

ViewView 中的 `sap.extension.m.DataTable` 使用同一模型形状，只是聚合名不同：

```ts
this.table = new sap.extension.m.DataTable("", {
    items: {
        path: "/rows",
        template: new sap.extension.m.ColumnListItem("", {
            cells: [
                new sap.extension.m.ObjectAttribute("", {
                    bindingValue: {
                        path: "itemCode",
                        type: new sap.extension.data.Alphanumeric()
                    }
                })
            ]
        })
    }
});
```

### 多个子表

一个 EditView 或 ViewView 有多个子集合时，每张表维护自己的模型：

```ts
showOrderLines(datas: bo.OrderLine[]): void {
    this.tableLines.setModel(
        new sap.extension.model.JSONModel({ rows: datas })
    );
}

showOrderDocuments(datas: bo.OrderDocument[]): void {
    this.tableDocuments.setModel(
        new sap.extension.model.JSONModel({ rows: datas })
    );
}
```

不要为了少写两次 `setModel()` 构造：

```ts
// 不推荐：页面级大模型混合主对象、多个集合和界面状态。
{
    order: data,
    lines: lines,
    documents: documents,
    users: users,
    busy: false,
    selectedTab: "lines"
}
```

独立表格模型带来的约束是刻意的：Application 调用哪个 `show...`，View 就只刷新哪个视觉单元。

## 五、`show...` 方法应与模型边界一一对应

一个稳定模型边界通常有一个语义明确的显示方法：

```ts
showOrder(data: bo.Order): void;
showOrderLines(datas: bo.OrderLine[]): void;
showOrderDocuments(datas: bo.OrderDocument[]): void;
```

实现要求：

- 方法参数使用真实 BO 或 BO 数组类型；
- 主对象设置到 Page；
- 集合设置到对应 Table；
- 方法只负责模型替换、必要的容器切换和 busy 状态，不查询 Repository；
- 不在一个 `showAll(data)` 中自行拆分所有集合，除非 Application 接口本来只提供这个契约；
- 子表显示编辑数据时使用 `filterDeleted()` 后的数组，但数组成员仍是原 BO 行对象。

典型 Application 调用：

```ts
this.view.showOrder(this.editData);
this.view.showOrderLines(
    this.editData.orderLines.filterDeleted()
);
this.view.showOrderDocuments(
    this.editData.orderDocuments.filterDeleted()
);
```

这种划分也让行业扩展可以只覆盖某个表格或显示方法，不必理解一个私有的总 ViewModel。

## 六、列表和选择页的分页追加

ListView、ChooseView 常常分批查询。第一次返回时创建表格模型，后续批次复用模型并调用 `addData()`：

```ts
showData(datas: bo.Order[]): void {
    let model: sap.ui.model.Model = this.table.getModel();
    if (model instanceof sap.extension.model.JSONModel) {
        model.addData(datas);
    } else {
        this.table.setModel(
            new sap.extension.model.JSONModel({ rows: datas })
        );
    }
    this.table.setBusy(false);
}
```

新查询开始前清除旧模型，并回到第一行：

```ts
query(criteria: ibas.ICriteria): void {
    super.query(criteria);
    if (this.isDisplayed) {
        this.table.setBusy(true);
        this.table.setFirstVisibleRow(0);
        this.table.setModel(null);
    }
}
```

规则：

- 同一查询的下一批结果使用 `addData(datas)`，不要覆盖已加载结果；
- 查询条件改变时先 `setModel(null)`，否则新旧条件结果会混在 `/rows`；
- `addData()` 在未指定路径时默认识别扩展模型的 `rows` 集合；
- 分页状态、下一页条件保留在 ListView 基类或 Application，不塞入表格模型；
- 普通 EditView 子表刷新是整体替换，不使用分页追加模式。

## 七、BO 修改、集合变化与刷新

### BO 属性修改

输入控件绑定真实 BO 属性。用户编辑或 Application 回填属性时，`sap.extension.model.JSONModel` 通过 `ibas.Bindable` 监听刷新相关绑定，通常不需要手工调用 `refresh(true)`。

```ts
selectedLine.itemCode = selected.code;
selectedLine.itemDescription = selected.name;
```

不要为了让界面变化而重新创建一份普通对象。若 Application 回填后需要切换整个对象，调用对应 `show...` 方法替换局部模型。

### 集合结构变化

集合新增、移除、过滤或重新排序后，重新调用对应显示方法最清晰：

```ts
this.editData.orderLines.create();
this.view.showOrderLines(
    this.editData.orderLines.filterDeleted()
);
```

删除遵循 BO 原集合语义，显示层只接收过滤后的集合：

```ts
if (item.isNew) {
    this.editData.orderLines.remove(item);
} else {
    item.delete();
}
this.view.showOrderLines(
    this.editData.orderLines.filterDeleted()
);
```

### 手工刷新是条件手段

仅在这些情况下考虑 `model.refresh(...)`：

- View 自己维护的普通数组发生原地变更，没有 `ibas.Bindable` 通知；
- formatter 依赖的多个值发生变化，但既有控件没有重新求值；
- 树、拖拽、分组等自定义结构在原地重排；
- 既有组件契约明确要求刷新模型。

`setForcedRefresh(true)` 也只用于已经验证普通自动刷新不足的局部模型，不是每个表格的默认设置。不要在每次按键或每个 formatter 中强制刷新整个 Page。

## 八、独立 Dialog、Popover 和局部容器

临时编辑某一个对象时，把对象绑定到对话框，而不是覆盖主 Page 模型：

```ts
let dialog: sap.m.Dialog = new sap.m.Dialog("", {
    content: [
        new sap.extension.m.TextArea("", {
        }).bindProperty("bindingValue", {
            path: "/content",
            type: new sap.extension.data.Alphanumeric({
                maxLength: 500
            })
        })
    ]
});
dialog.setModel(
    new sap.extension.model.JSONModel(data)
);
dialog.open();
```

局部模型遵循两个条件：

- 数据只服务这个局部交互；
- 关闭或销毁容器后，不再需要这份显示状态。

如果弹窗维护的是主 BO 内的真实行对象，仍直接绑定该行对象，让修改落回原 BO。只有“取消时必须放弃修改”的交互才创建临时副本，并由 Application 决定确认后如何合并；View 不自行设计复制和提交协议。

服务 `ActionSheet` 把服务数组直接作为模型，是因为它的列表聚合直接绑定模型根 `/`。这种小型、只服务一个瞬时控件的根数组不应推广到业务 `DataTable`；业务表格继续统一使用 `{ rows: datas }`。

## 九、命名模型只用于同一控件树的真实多上下文

标准页面通常不需要命名模型。只有同一 Page 的某个区域必须同时保留主对象模型和另一个独立对象模型时才使用：

```ts
showContact(data: bo.Contact): void {
    this.page.setModel(
        new sap.extension.model.JSONModel(data)
    );
}

showRole(data: bo.ContactRole): void {
    this.page.setModel(
        new sap.extension.model.JSONModel(data),
        "role"
    );
}
```

命名模型的绑定路径必须显式带名称：

```ts
new sap.extension.m.Input("", {
}).bindProperty("bindingValue", {
    path: "role>/interactionSummary",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 500
    })
})
```

使用限制：

- 名称表达业务上下文，如 `role`、`overview`，不要使用 `model1`；
- 不要用多个命名模型替代本可独立绑定的多个 Table；
- 不要把同一对象同时放入默认模型和命名模型；
- 不要依赖控件树外部某个同名模型；模型应设置在能完整覆盖使用者的最近共同容器上。

## 十、允许的小型组合模型

默认形状是单对象或 `{ rows: datas }`。只有一个局部控件确实需要“集合 + 少量共同上下文”时，才使用浅层组合：

```ts
this.table.setModel(new sap.extension.model.JSONModel({
    rows: datas,
    currency: currency
}));
```

它必须同时满足：

- 只绑定在该 Table 或局部容器，不绑定整页；
- 附加字段直接参与这一控件树的显示；
- 字段数量少、语义单一，不重复整个主 BO；
- `rows` 仍保留真实 BO 行对象；
- Application 或 `show...` 参数清楚提供数据，不由 View 查询拼装。

如果附加字段逐渐变成用户、权限、按钮状态、多个业务集合和查询结果的混合体，说明模型边界已经失控，应重新拆分控件模型或把业务状态交回 Application。

## 十一、绑定路径规范

- Page 直接绑定主 BO：字段路径使用 BO 属性名，如 `name`、`documentDate`。
- `DataTable` 聚合绑定根集合：`rows: "{/rows}"`。
- `sap.extension.m.DataTable` 聚合：`items: { path: "/rows", ... }`。
- 行模板字段使用相对路径，如 `itemCode`，由行绑定上下文定位对象。
- 独立对话框直接绑定对象时，可使用根绝对路径 `/content`；同一局部区域保持一致。
- 命名模型路径使用 `role>/property`，不能省略模型名。
- 一个模型内不要混用 `{ data: bo }`、`{ rows: datas }` 和根数组，除非各自属于不同局部控件且聚合契约确实不同。
- formatter 只转换表现值或控件状态，不修改模型，不触发事件，不查询服务。

在表格事件中通过行上下文取得真实对象：

```ts
valueHelpRequest(this: sap.extension.m.Input): void {
    let line: bo.OrderLine = this.getBindingContext().getObject();
    that.fireViewEvents(that.chooseLineItemEvent, line);
}
```

不要从 `/rows` 再按当前索引手工查找对象；排序、筛选和滚动后，界面行索引不一定等于原集合索引。

## 十二、常见反例

### 页面级总模型

```ts
// 不推荐
this.page.setModel(new sap.extension.model.JSONModel({
    data: order,
    rows: order.orderLines,
    documents: order.orderDocuments,
    choices: choices,
    ui: {
        busy: false,
        selected: undefined
    }
}));
```

问题：路径过深、刷新范围过大、主从对象责任混杂，而且扩展模型只对直接成员和直接数组成员注册监听，深层嵌套结构容易破坏 BO 自动刷新预期。

### 所有控件重复设置同一模型

```ts
// 不推荐
this.formTop.setModel(model);
this.formMiddle.setModel(model);
this.formBottom.setModel(model);
```

模型设置在它们最近的共同父控件 Page 上即可，子控件通过继承取得模型。

### 表格绑定 Page 的深层子集合

```ts
// 不作为标准写法
rows: "{/orderLines}"
```

标准 EditView 已通过 `showOrderLines(datas)` 建立表格刷新契约时，表格应使用自己的 `{ rows: datas }`。只有目标页面明确采用单模型整体绑定、Application 没有独立显示契约且集合生命周期完全跟随主对象时，才保留既有深层路径，不要机械重构。

### View 内查询后塞入总模型

View 不应为了补齐 `choices`、`users`、`warehouses` 等字段直接查询 Repository。查询由 Application 执行，再通过事件、`show...` 方法或专用扩展控件交给 View。

## 十三、完成检查

- 标准业务绑定使用 `sap.extension.model.JSONModel`。
- 主 Page 直接绑定当前 BO，没有无意义的 `data` 包装层。
- 每张独立业务表格使用自己的 `{ rows: datas }` 模型。
- 表格聚合绑定 `/rows`，行字段使用相对属性路径。
- 多子表页面没有构造包含所有集合和 UI 状态的页面级总模型。
- `show...` 方法与 Page、Table、Dialog 等模型边界对应。
- ListView、ChooseView 的下一批数据使用 `addData()`；新查询开始前清除旧模型。
- 编辑模型保留真实 BO 实例，没有 JSON 深拷贝。
- BO 普通属性变化依赖扩展模型自动刷新，不滥用 `refresh(true)` 或 `setForcedRefresh(true)`。
- 集合新增、删除、过滤后刷新对应表格，不刷新无关页面区域。
- 命名模型只用于同一控件树的真实多上下文，并在绑定路径中显式写模型名。
- Dialog、Popover 的临时模型只绑定局部容器，不覆盖主 Page 模型。
- View 没有通过模型拼装承担 Repository 查询、业务计算或保存职责。
