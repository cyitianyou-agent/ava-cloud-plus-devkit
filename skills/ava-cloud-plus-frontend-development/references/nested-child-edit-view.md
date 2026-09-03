# 包含孙表的 EditView

本规范是标准 EditView 的**条件变体**，只处理以下真实数据关系：

```text
主对象 Root
└─ 子集合 children: Child[]
   └─ 每个 Child 各自拥有孙集合 grandChildren: GrandChild[]
```

孙表必须属于某一个具体子项。若第二张表只是主对象的另一个平级集合，应使用 `IconTabBar` 分页签，不应套用本规范。

## 一、默认交互：在中区下钻，不同时铺开两张表

Cloud+ PC 端对于“先选子项，再维护该子项的孙项”的常见结构是：

```text
sap.extension.m.DataPage
├─ formTop：主表关键字段
├─ formMiddle
│  ├─ 动态标题：子项 / 孙项
│  └─ sap.m.NavContainer
│     ├─ 第 1 页：子表 DataTable
│     │  └─ 行尾箭头：进入当前子项的孙表
│     └─ 第 2 页：孙表 DataTable
│        └─ 工具栏右侧返回：回到子表
└─ formBottom：所有者、组织、备注等
```

这样组织的理由是：

- 子表选择通常还承担批量删除，不能把“选中行”含糊地等同于“进入孙表”；
- 孙表只有在确定当前子项后才有意义，下钻能够清楚表达上下文；
- 两张可编辑表格不同时占据纵向空间，仍保持标准 EditView 的上、中、下三区密度；
- 返回后仍处于同一 EditView，不建立新的保存边界，最终仍保存完整主对象。

### 适用条件

同时满足以下条件时，默认使用 `NavContainer` 下钻：

- BO 明确定义了 `Root.children`，且 `Child.grandChildren` 是子项自己的集合；
- 孙项的新增、删除或编辑必须知道当前 `Child`；
- 子表与孙表都适合表格批量维护；
- 用户通常先定位一个子项，再连续维护它的孙项；
- 子表和孙表不需要持续并排对照。

### 不适用条件

- 两个集合都直接属于主对象：使用 `IconTabBar` 的两个业务页签。
- 孙项只有一两个简单字段：可考虑直接在子表列中表达，前提是 BO 和交互都清晰。
- 孙项是复杂独立对象，拥有自己的保存、校验或大量表单字段：使用独立编辑 Application、对话框或页面。
- 业务要求同时对照子项与孙项：可使用主从分栏，但这是业务特例，不是默认骨架。
- 只是为了展示详情而没有孙集合：不要虚构下钻层级。

## 二、职责与契约

### View 负责

- 创建子表、孙表和 `NavContainer`；
- 从行操作取得当前绑定的子项并触发事件；
- 把选中行集合交给删除事件；
- 切换容器页面、标题和对应表格模型；
- 继续用 `show<Root>` 设置主对象模型和页面状态。

### Application 负责

- 持有当前正在维护孙表的子项；
- 从正确的父集合创建、删除孙项；
- 阻止没有父上下文时新增或删除孙项；
- 刷新 `filterDeleted()` 后的子集合或孙集合；
- 主对象被新建、克隆、重新查询或保存替换后，清理过期的当前子项上下文；
- 处理业务校验、选择服务和持久化。

### BO 负责

- 定义真实的主从集合归属；
- 在集合 `create()`、`afterAdd()` 或属性逻辑中处理默认值、顺序和联动；
- 维护 `isNew`、删除标记、脏数据等对象状态。

View 不应保存 `currentChild` 并直接调用 `currentChild.grandChildren.create()`；否则层级状态、业务校验和刷新逻辑会绕过 Application。

## 三、事件与 `show...` 方法

接口至少应明确以下契约，名称替换成实际 BO 语义：

```ts
export interface IRootEditView extends ibas.IBOEditView {
    showRoot(data: bo.Root): void;
    showChildren(datas: bo.Child[]): void;
    showGrandChildren(datas: bo.GrandChild[]): void;

    addChildEvent: Function;
    removeChildEvent: Function;

    /** 参数：进入孙表时传 Child；返回子表时不传参数。 */
    editChildEvent: Function;
    addGrandChildEvent: Function;
    removeGrandChildEvent: Function;
}
```

`editChildEvent` 使用一个对称约定：

- `editChildEvent(child)`：Application 记录 `child`，显示其孙集合；
- `editChildEvent()`：Application 清空当前子项，显示主对象的子集合。

这不是业务“编辑子项”的保存动作，而是切换当前层级上下文。若现有接口已经使用 `openChildDetailsEvent`、`showChildValuesEvent` 等更清晰名称，保持现有命名即可，不必为了模板改名。

## 四、View 完整结构示例

下面示例省略普通主表字段和页面主工具栏，只完整展示孙表相关结构。示例中的 `Root`、`Child`、`GrandChild` 均应替换为真实 BO 类型。

```ts
export class RootEditView extends ibas.BOEditView implements app.IRootEditView {
    addChildEvent: Function;
    removeChildEvent: Function;
    editChildEvent: Function;
    addGrandChildEvent: Function;
    removeGrandChildEvent: Function;

    private page: sap.extension.m.Page;
    private tableTitle: sap.ui.core.Title;
    private container: sap.m.NavContainer;
    private tableChild: sap.extension.table.Table;
    private tableGrandChild: sap.extension.table.Table;

    draw(): any {
        let that: this = this;

        this.tableChild = this.createChildTable();
        this.tableGrandChild = this.createGrandChildTable();

        let formMiddle: sap.ui.layout.form.SimpleForm = new sap.ui.layout.form.SimpleForm("", {
            editable: true,
            content: [
                this.tableTitle = new sap.ui.core.Title("", {
                    text: ibas.i18n.prop("bo_child")
                }),
                this.container = new sap.m.NavContainer("", {
                    height: ibas.strings.format(
                        "{0}rem",
                        sap.extension.table.visibleRowCount(8) * 3
                    ),
                    pages: [
                        this.tableChild,
                        this.tableGrandChild
                    ]
                })
            ]
        });

        return this.page = new sap.extension.m.DataPage("", {
            showHeader: false,
            dataInfo: {
                code: bo.Root.BUSINESS_OBJECT_CODE
            },
            subHeader: this.createToolbar(),
            content: [
                this.createTopForm(),
                formMiddle,
                this.createBottomForm()
            ]
        });
    }

    private createChildTable(): sap.extension.table.DataTable {
        let that: this = this;
        return new sap.extension.table.DataTable("", {
            enableSelectAll: false,
            visibleRowCount: sap.extension.table.visibleRowCount(8),
            dataInfo: {
                code: bo.Root.BUSINESS_OBJECT_CODE,
                name: bo.Child.name
            },
            rows: "{/rows}",
            toolbar: new sap.m.Toolbar("", {
                content: [
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_add"),
                        type: sap.m.ButtonType.Transparent,
                        icon: "sap-icon://add",
                        press: function (): void {
                            that.fireViewEvents(that.addChildEvent);
                        }
                    }),
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_remove"),
                        type: sap.m.ButtonType.Transparent,
                        icon: "sap-icon://less",
                        press: function (): void {
                            that.fireViewEvents(
                                that.removeChildEvent,
                                that.tableChild.getSelecteds()
                            );
                        }
                    })
                ]
            }),
            rowActionCount: 1,
            rowActionTemplate: new sap.ui.table.RowAction("", {
                items: [
                    new sap.ui.table.RowActionItem("", {
                        icon: "sap-icon://slim-arrow-right",
                        press: function (): void {
                            that.fireViewEvents(
                                that.editChildEvent,
                                this.getBindingContext().getObject()
                            );
                        }
                    })
                ]
            }),
            columns: [
                new sap.extension.table.DataColumn("", {
                    label: ibas.i18n.prop("bo_child_name"),
                    template: new sap.extension.m.Input("", {
                    }).bindProperty("bindingValue", {
                        path: "name",
                        type: new sap.extension.data.Alphanumeric({
                            maxLength: 100
                        })
                    }),
                    width: "100%"
                })
            ],
            sortProperty: "visOrder",
            sortIntervalStep: 1
        });
    }

    private createGrandChildTable(): sap.extension.table.DataTable {
        let that: this = this;
        return new sap.extension.table.DataTable("", {
            enableSelectAll: false,
            visibleRowCount: sap.extension.table.visibleRowCount(8),
            dataInfo: {
                code: bo.Root.BUSINESS_OBJECT_CODE,
                name: bo.GrandChild.name
            },
            rows: "{/rows}",
            toolbar: new sap.m.Toolbar("", {
                content: [
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_add"),
                        type: sap.m.ButtonType.Transparent,
                        icon: "sap-icon://add",
                        press: function (): void {
                            that.fireViewEvents(that.addGrandChildEvent);
                        }
                    }),
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_remove"),
                        type: sap.m.ButtonType.Transparent,
                        icon: "sap-icon://less",
                        press: function (): void {
                            that.fireViewEvents(
                                that.removeGrandChildEvent,
                                that.tableGrandChild.getSelecteds()
                            );
                        }
                    }),
                    new sap.m.ToolbarSpacer(""),
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_back"),
                        type: sap.m.ButtonType.Transparent,
                        icon: "sap-icon://nav-back",
                        press: function (): void {
                            that.fireViewEvents(that.editChildEvent);
                        }
                    })
                ]
            }),
            columns: [
                new sap.extension.table.DataColumn("", {
                    label: ibas.i18n.prop("bo_grandchild_value"),
                    template: new sap.extension.m.Input("", {
                    }).bindProperty("bindingValue", {
                        path: "value",
                        type: new sap.extension.data.Alphanumeric({
                            maxLength: 100
                        })
                    }),
                    width: "100%"
                })
            ]
        });
    }

    showRoot(data: bo.Root): void {
        this.page.setModel(new sap.extension.model.JSONModel(data));
        sap.extension.pages.changeStatus(this.page);
    }

    showChildren(datas: bo.Child[]): void {
        this.tableTitle.setText(ibas.i18n.prop("bo_child"));
        this.container.backToTop();
        this.tableChild.setModel(
            new sap.extension.model.JSONModel({ rows: datas })
        );
    }

    showGrandChildren(datas: bo.GrandChild[]): void {
        this.tableTitle.setText(ibas.i18n.prop("bo_grandchild"));
        this.container.to(this.tableGrandChild.getId());
        this.tableGrandChild.setModel(
            new sap.extension.model.JSONModel({ rows: datas })
        );
    }
}
```

### 结构细节

- 子表通过 `rowActionTemplate` 的 `slim-arrow-right` 下钻；不要用双击，因为双击在选择表、编辑表等页面中含义不稳定。
- 批量删除仍读取 `getSelecteds()`；“选择行”和“进入孙表”是两个独立动作。
- 孙表的返回按钮位于孙表工具栏最右侧，前面使用 `ToolbarSpacer`，不占用页面主工具栏。
- `showChildren` 使用 `backToTop()`，确保无论容器历史如何都回到第一个页面。
- `showChildren`、`showGrandChildren` 分别给各自表格设置 `{ rows: datas }` 模型，不把孙表绑定到主页面的绝对深层路径。
- 动态标题必须随层级切换，避免用户进入孙表后仍看到子表标题。
- 两个容器页保持相同高度，避免下钻时整个 EditView 跳动。8 行表格通常可使用约 `24rem`，也可按模块已有密度用 `visibleRowCount(8) * 3` 计算；这不是固定尺寸。
- 只有对应 BO 确实存在排序属性时才配置 `sortProperty` 和 `sortIntervalStep`。

## 五、Application 完整上下文示例

```ts
export class RootEditApp extends ibas.BOEditApplication<IRootEditView, bo.Root> {
    /** 当前孙表所属的子项；只在 Application 保存层级上下文。 */
    private currentChild: bo.Child;

    protected registerView(): void {
        super.registerView();
        this.view.addChildEvent = this.addChild;
        this.view.removeChildEvent = this.removeChild;
        this.view.editChildEvent = this.editChild;
        this.view.addGrandChildEvent = this.addGrandChild;
        this.view.removeGrandChildEvent = this.removeGrandChild;
    }

    protected viewShowed(): void {
        super.viewShowed();
        if (ibas.objects.isNull(this.editData)) {
            this.editData = new bo.Root();
        }
        this.currentChild = undefined;
        this.view.showRoot(this.editData);
        this.view.showChildren(this.editData.children.filterDeleted());
    }

    private addChild(): void {
        this.editData.children.create();
        this.view.showChildren(this.editData.children.filterDeleted());
    }

    private removeChild(items: bo.Child[]): void {
        if (!(items instanceof Array)) {
            items = [items];
        }
        if (items.length === 0) {
            return;
        }
        for (let item of items) {
            if (this.editData.children.indexOf(item) < 0) {
                continue;
            }
            if (item.isNew) {
                this.editData.children.remove(item);
            } else {
                item.delete();
            }
            if (item === this.currentChild) {
                this.currentChild = undefined;
            }
        }
        this.view.showChildren(this.editData.children.filterDeleted());
    }

    private editChild(item?: bo.Child): void {
        if (ibas.objects.isNull(item)) {
            this.currentChild = undefined;
            this.view.showChildren(this.editData.children.filterDeleted());
            return;
        }
        if (this.editData.children.indexOf(item) < 0 || item.isDeleted) {
            this.currentChild = undefined;
            this.view.showChildren(this.editData.children.filterDeleted());
            return;
        }
        this.currentChild = item;
        this.view.showGrandChildren(
            this.currentChild.grandChildren.filterDeleted()
        );
    }

    private addGrandChild(): void {
        if (ibas.objects.isNull(this.currentChild)) {
            this.proceeding(
                ibas.emMessageType.WARNING,
                ibas.i18n.prop(
                    "shell_please_chooose_data",
                    ibas.i18n.prop("bo_child")
                )
            );
            return;
        }
        this.currentChild.grandChildren.create();
        this.view.showGrandChildren(
            this.currentChild.grandChildren.filterDeleted()
        );
    }

    private removeGrandChild(items: bo.GrandChild[]): void {
        if (ibas.objects.isNull(this.currentChild)) {
            this.proceeding(
                ibas.emMessageType.WARNING,
                ibas.i18n.prop(
                    "shell_please_chooose_data",
                    ibas.i18n.prop("bo_child")
                )
            );
            return;
        }
        if (!(items instanceof Array)) {
            items = [items];
        }
        if (items.length === 0) {
            return;
        }
        for (let item of items) {
            if (this.currentChild.grandChildren.indexOf(item) < 0) {
                continue;
            }
            if (item.isNew) {
                this.currentChild.grandChildren.remove(item);
            } else {
                item.delete();
            }
        }
        this.view.showGrandChildren(
            this.currentChild.grandChildren.filterDeleted()
        );
    }
}
```

### 上下文不变量

实现时必须维持以下关系：

```text
当前显示孙表
    => currentChild 不为空
    => currentChild 仍属于 editData.children
    => 所有孙表增删都作用于 currentChild.grandChildren
```

在这些时机清空 `currentChild` 并回到子表：

- 新建或克隆主对象；
- 保存后 Repository 返回了新的主对象实例；
- 重新查询并替换主对象；
- 删除了当前子项；
- 用户点击孙表返回按钮。

如果 Application 的 `viewShowed()` 会在以上流程后统一执行，可在 `viewShowed()` 中集中清空；否则必须在具体替换点处理。

## 六、刷新与删除规则

每一次结构变化后都刷新当前层级，统一使用过滤删除标记后的集合：

```ts
this.view.showChildren(this.editData.children.filterDeleted());

this.view.showGrandChildren(
    this.currentChild.grandChildren.filterDeleted()
);
```

删除仍遵循 Cloud+ BO 的两类语义：

```ts
if (item.isNew) {
    collection.remove(item);
} else {
    item.delete();
}
```

- 新建未保存的数据从集合移除；
- 已持久化数据只标记删除，交由主对象保存流程处理；
- 删除前确认对象确实属于当前集合，特别是孙表不能接受另一个子项的旧选择；
- 不直接对 `filterDeleted()` 返回的数组执行 `remove()`，修改的必须是 BO 原集合。

## 七、与 `IconTabBar` 的组合

如果 EditView 中区还有其他独立业务组，可以先用 `IconTabBar` 分组，再把整个主从下钻区域放进一个页签：

```text
IconTabBar
├─ 常规页签：主表业务字段
├─ 明细页签：Title + NavContainer(子表, 孙表)
└─ 其他设置页签：另一个平级业务组
```

不要把“子表”和“孙表”拆成两个可随意点击的平级页签。这样会失去当前孙表属于哪个子项的明确入口，也容易在切换子项后显示旧孙表数据。

## 八、不得从示例泛化的特例

以下写法取决于具体业务，不属于包含孙表页面的通用要求：

- 根据条件类型动态替换列模板；
- 在孙表单元格中打开 SQL 或代码编辑器；
- 子表内再打开所有者维护对话框；
- 审批关系、括号计数、条件运算符等专用控件；
- 子表新增时复制选中行、建立树形父级或按十递增顺序；
- 在 View 中查询元数据并据此生成可选项。

只有目标 Application、BO 和既有模块约定明确要求时才实现这些行为。尤其是 Repository 查询原则上应留在 Application；历史页面存在的 View 内查询不能作为新页面默认写法。

## 九、完成检查

- BO 确实是主表、子表、孙表三级归属，而不是两个平级子集合。
- 中区保持标准 EditView 结构，孙表只作为条件变体加入。
- 子表行尾箭头传递当前绑定对象，批量选择仍只服务删除等批量动作。
- Application 持有当前子项，View 不直接修改集合。
- 无父上下文时不能新增、删除或选择孙项数据。
- 返回、主对象替换、删除当前子项后不会保留过期上下文。
- 子表和孙表都用独立 `{ rows: datas }` 模型并显示 `filterDeleted()` 结果。
- 孙表增删修改的是 `currentChild.grandChildren`，不是主对象或其他子项的集合。
- `dataInfo.name`、列绑定类型和排序属性与实际 BO 一致。
- 页面主保存动作仍保存完整主对象，没有为孙表建立第二套保存流程。
- 未把审批条件、SQL 编辑等单页特例写成通用实现。
