# EditView 规范与完整骨架

## 一、上中下三区是默认页面骨架

标准 EditView 使用 `sap.extension.m.DataPage`，内容按业务阅读顺序组织：

```text
sap.extension.m.DataPage
├─ subHeader: 保存、删除、新建/克隆、业务动作、服务
└─ content
   ├─ formTop：主表身份、编号、日期、状态、关键字段
   ├─ formMiddle：业务明细、子表、可选 IconTabBar
   └─ formBottom：合计、所有人、组织、分支、项目、备注
```

这是一种语义分区，不要求每个页面机械出现三个非空控件：

- 简单主数据字段很少：可只保留 `formTop` 和 `formBottom`。
- 没有补充字段：可以省略 `formBottom`。
- 不允许创建空 `SimpleForm` 或空 `IconTabFilter` 凑结构。

## 二、中区何时使用 `sap.m.IconTabBar`

满足任一条件时，优先在 `formMiddle` 中使用页签：

- 主表字段形成两个以上清晰业务组，例如常规、库存、采购、销售、计划；
- 存在两个以上需要独立操作的子表；
- 一个子表与一组复杂业务字段并存，直接纵向堆叠会明显降低定位效率；
- 页面需要把低频设置与主流程字段隔离。

不满足上述条件时直接放置一个表单或子表，不为了字段数量的绝对阈值创建页签。页签按业务概念命名，不用“页签1/页签2”。

页签骨架：

```ts
let formMiddle: sap.ui.layout.form.SimpleForm = new sap.ui.layout.form.SimpleForm("", {
    editable: true,
    content: [
        new sap.m.IconTabBar("", {
            headerBackgroundDesign: sap.m.BackgroundDesign.Transparent,
            backgroundDesign: sap.m.BackgroundDesign.Transparent,
            expandable: false,
            items: [
                new sap.m.IconTabFilter("", {
                    text: ibas.i18n.prop("demo_title_general"),
                    content: [
                        new sap.ui.layout.form.SimpleForm("", {
                            editable: true,
                            content: [
                                // 此处放同一业务组的 Label + 编辑控件
                            ]
                        })
                    ]
                }),
                new sap.m.IconTabFilter("", {
                    text: ibas.i18n.prop("bo_itemline"),
                    content: [
                        this.tableLines
                    ]
                })
            ]
        })
    ]
});
```

## 三、完整页面骨架

```ts
/** 编辑视图-示例对象 */
export class ItemEditView extends ibas.BOEditView implements app.IItemEditView {
    /** 删除数据事件 */
    deleteDataEvent: Function;
    /** 新建数据事件，参数：是否克隆 */
    createDataEvent: Function;
    /** 添加子项事件 */
    addItemLineEvent: Function;
    /** 删除子项事件，参数：子项集合 */
    removeItemLineEvent: Function;
    /** 选择子项物料事件，参数：当前子项 */
    chooseLineMaterialEvent: Function;

    draw(): any {
        let that: this = this;
        let formTop: sap.ui.layout.form.SimpleForm = new sap.ui.layout.form.SimpleForm("", {
            editable: true,
            content: [
                new sap.ui.core.Title("", {
                    text: ibas.i18n.prop("demo_title_general")
                }),
                new sap.m.Label("", {
                    text: ibas.i18n.prop("bo_item_code")
                }),
                new sap.extension.m.Input("", {
                }).bindProperty("bindingValue", {
                    path: "code",
                    type: new sap.extension.data.Alphanumeric({
                        maxLength: 20
                    })
                }).bindProperty("editable", {
                    path: "series",
                    formatter(data: number): boolean {
                        return data > 0 ? false : true;
                    }
                }),
                new sap.extension.m.SeriesSelect("", {
                    objectCode: bo.Item.BUSINESS_OBJECT_CODE
                }).bindProperty("bindingValue", {
                    path: "series",
                    type: new sap.extension.data.Numeric()
                }).bindProperty("editable", {
                    path: "isNew",
                    formatter(data: boolean): boolean {
                        return data === true;
                    }
                }),
                new sap.m.Label("", {
                    text: ibas.i18n.prop("bo_item_name")
                }),
                new sap.extension.m.Input("", {
                }).bindProperty("bindingValue", {
                    path: "name",
                    type: new sap.extension.data.Alphanumeric({
                        maxLength: 100
                    })
                })
            ]
        });

        this.tableLines = this.createLineTable();
        let formMiddle: sap.ui.layout.form.SimpleForm = new sap.ui.layout.form.SimpleForm("", {
            editable: true,
            content: [
                new sap.ui.core.Title("", {
                    text: ibas.i18n.prop("bo_itemline")
                }),
                this.tableLines
            ]
        });

        let formBottom: sap.ui.layout.form.SimpleForm = new sap.ui.layout.form.SimpleForm("", {
            editable: true,
            content: [
                new sap.ui.core.Title("", {
                    text: ibas.i18n.prop("demo_title_others")
                }),
                new sap.m.Label("", {
                    text: ibas.i18n.prop("bo_item_dataowner")
                }),
                new sap.extension.m.DataOwnerInput("", {
                    showValueHelp: true
                }).bindProperty("bindingValue", {
                    path: "dataOwner",
                    type: new sap.extension.data.Numeric()
                }),
                new sap.m.Label("", {
                    text: ibas.i18n.prop("bo_item_remarks")
                }),
                new sap.extension.m.TextArea("", {
                    rows: 3
                }).bindProperty("bindingValue", {
                    path: "remarks",
                    type: new sap.extension.data.Alphanumeric({
                        maxLength: 200
                    })
                })
            ]
        });

        return this.page = new sap.extension.m.DataPage("", {
            showHeader: false,
            dataInfo: {
                code: bo.Item.BUSINESS_OBJECT_CODE
            },
            subHeader: this.createToolbar(),
            content: [
                formTop,
                formMiddle,
                formBottom
            ]
        });
    }

    private page: sap.extension.m.Page;
    private tableLines: sap.extension.table.Table;

    private createToolbar(): sap.m.Toolbar {
        let that: this = this;
        return new sap.m.Toolbar("", {
            content: [
                new sap.m.Button("", {
                    text: ibas.i18n.prop("shell_data_save"),
                    type: sap.m.ButtonType.Transparent,
                    icon: "sap-icon://save",
                    press: function (): void {
                        that.fireViewEvents(that.saveDataEvent);
                    }
                }),
                new sap.m.Button("", {
                    text: ibas.i18n.prop("shell_data_delete"),
                    type: sap.m.ButtonType.Transparent,
                    icon: "sap-icon://delete",
                    enabled: {
                        path: "isNew",
                        formatter(data: boolean): boolean {
                            return data !== true;
                        }
                    },
                    press: function (): void {
                        that.fireViewEvents(that.deleteDataEvent);
                    }
                }),
                new sap.m.ToolbarSeparator(""),
                new sap.m.MenuButton("", {
                    text: ibas.strings.format(
                        "{0}/{1}",
                        ibas.i18n.prop("shell_data_new"),
                        ibas.i18n.prop("shell_data_clone")
                    ),
                    icon: "sap-icon://create",
                    type: sap.m.ButtonType.Transparent,
                    menu: new sap.m.Menu("", {
                        items: [
                            new sap.m.MenuItem("", {
                                text: ibas.i18n.prop("shell_data_new"),
                                press: function (): void {
                                    that.fireViewEvents(that.createDataEvent, false);
                                }
                            }),
                            new sap.m.MenuItem("", {
                                text: ibas.i18n.prop("shell_data_clone"),
                                press: function (): void {
                                    that.fireViewEvents(that.createDataEvent, true);
                                }
                            })
                        ]
                    })
                }),
                new sap.m.ToolbarSpacer("")
            ]
        });
    }

    private createLineTable(): sap.extension.table.DataTable {
        let that: this = this;
        return new sap.extension.table.DataTable("", {
            enableSelectAll: false,
            visibleRowCount: sap.extension.table.visibleRowCount(8),
            dataInfo: {
                code: bo.Item.BUSINESS_OBJECT_CODE,
                name: bo.ItemLine.name
            },
            rows: "{/rows}",
            toolbar: new sap.m.Toolbar("", {
                content: [
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_add"),
                        icon: "sap-icon://add",
                        type: sap.m.ButtonType.Transparent,
                        press: function (): void {
                            that.fireViewEvents(that.addItemLineEvent);
                        }
                    }),
                    new sap.m.Button("", {
                        text: ibas.i18n.prop("shell_data_remove"),
                        icon: "sap-icon://less",
                        type: sap.m.ButtonType.Transparent,
                        press: function (): void {
                            that.fireViewEvents(
                                that.removeItemLineEvent,
                                that.tableLines.getSelecteds()
                            );
                        }
                    })
                ]
            }),
            columns: [
                new sap.extension.table.DataColumn("", {
                    label: ibas.i18n.prop("bo_itemline_itemcode"),
                    template: new sap.extension.m.Input("", {
                        showValueHelp: true,
                        valueHelpRequest(this: sap.extension.m.Input): void {
                            that.fireViewEvents(
                                that.chooseLineMaterialEvent,
                                this.getBindingContext().getObject()
                            );
                        }
                    }).bindProperty("bindingValue", {
                        path: "itemCode",
                        type: new sap.extension.data.Alphanumeric({
                            maxLength: 50
                        })
                    })
                }),
                new sap.extension.table.DataColumn("", {
                    label: ibas.i18n.prop("bo_itemline_quantity"),
                    template: new sap.extension.m.Input("", {
                    }).bindProperty("bindingValue", {
                        path: "quantity",
                        type: new sap.extension.data.Quantity()
                    })
                })
            ],
            sortProperty: "visOrder",
            sortIntervalStep: 1
        });
    }

    showItem(data: bo.Item): void {
        this.page.setModel(new sap.extension.model.JSONModel(data));
        sap.extension.pages.changeStatus(this.page);
    }

    showItemLines(datas: bo.ItemLine[]): void {
        this.tableLines.setModel(
            new sap.extension.model.JSONModel({ rows: datas })
        );
    }
}
```

## 四、主表字段分组

### 主数据上区

通常放编码、系列、名称、启用状态和最常用分类。编码在自动编号系列下不可编辑；系列通常仅新对象可编辑。

### 单据上区

通常分成“一般”和“状态”两组：

- 一般：业务伙伴、价格清单、引用、来源；
- 状态：`docEntry`、`docNum + SeriesSelect`、单据状态、取消/打印标记、单据日期、交付日期。

### 下区

通常放合计、分支、所有人、组织、项目、备注。只有 BO 实际存在且业务启用时才显示分支、成本中心等配置字段。

## 五、子表规则

- 可编辑子表使用 `sap.extension.table.DataTable` 与 `DataColumn`。
- 常见行数为约 8 行，允许页面为上下区保留空间；不是固定值，复杂页面可根据现有布局调整。
- 子表工具栏只包含该子表动作，如添加、删除、复制、上移、下移。
- 行级选择事件必须传当前绑定行对象。
- 只有 BO 确实有 `visOrder` 等排序属性时才设置 `sortProperty` 和 `sortIntervalStep`。
- 数量、金额等计算结果应由 BO/Application 产生，View 只用类型控件显示或编辑。
- 当子项本身拥有需要维护的孙集合时，不要把两个表格直接按普通子表并列处理。先判断是否满足下钻式编辑条件；满足时继续读取 [包含孙表的 EditView](nested-child-edit-view.md)。

## 六、状态控制

`show<BO>` 设置模型后必须调用：

```ts
sap.extension.pages.changeStatus(this.page);
```

它负责主数据、单据在新增、已保存、关闭、取消、删除等状态下的通用编辑控制。额外业务限制再通过 `editable`、`enabled` 或 `visible` 的绑定补充，不要用零散代码替代框架状态处理。

formatter 只能计算表现状态，不查询 Repository、不修改 BO、不执行保存或金额计算。
