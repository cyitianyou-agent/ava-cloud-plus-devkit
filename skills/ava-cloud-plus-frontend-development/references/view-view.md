# ViewView 规范与完整骨架

## 一、标准结构

```text
sap.extension.uxap.DataObjectPageLayout
├─ headerTitle
│  ├─ 对象标题/副标题
│  ├─ navigationBar：编辑、通用服务
│  └─ actions：状态、关键金额或数量
├─ headerContent：关键日期、伙伴、引用、分类
└─ sections
   ├─ 一般信息
   ├─ 子表/业务明细
   └─ 其他信息：所有人、组织等
```

ViewView 是只读对象页，不复用 EditView 的 Input 和 SimpleForm 伪装只读界面。

## 二、完整可改名骨架

```ts
/** 查看视图-示例对象 */
export class ItemViewView extends ibas.BOViewView implements app.IItemViewView {
    draw(): any {
        let that: this = this;
        this.tableLines = new sap.extension.m.DataTable("", {
            dataInfo: {
                code: bo.Item.BUSINESS_OBJECT_CODE,
                name: bo.ItemLine.name
            },
            columns: [
                new sap.extension.m.Column("", {
                    header: new sap.m.Label("", {
                        text: ibas.i18n.prop("bo_itemline_itemcode")
                    })
                }),
                new sap.extension.m.Column("", {
                    header: new sap.m.Label("", {
                        text: ibas.i18n.prop("bo_itemline_quantity")
                    }),
                    hAlign: sap.ui.core.TextAlign.Right
                })
            ],
            items: {
                path: "/rows",
                template: new sap.m.ColumnListItem("", {
                    cells: [
                        new sap.extension.m.ObjectIdentifier("", {
                            title: {
                                path: "itemCode",
                                type: new sap.extension.data.Alphanumeric()
                            },
                            titleActive: true,
                            titlePress(this: sap.extension.m.ObjectIdentifier): void {
                                let code: string = this.getTitle();
                                if (!ibas.strings.isEmpty(code)) {
                                    ibas.servicesManager.runLinkService({
                                        boCode: bo.Item.BUSINESS_OBJECT_CODE,
                                        linkValue: code
                                    });
                                }
                            }
                        }),
                        new sap.extension.m.ObjectNumber("", {
                            number: {
                                path: "quantity",
                                type: new sap.extension.data.Quantity()
                            },
                            unit: {
                                path: "uom",
                                type: new sap.extension.data.Alphanumeric()
                            }
                        })
                    ]
                })
            }
        });

        return this.page = new sap.extension.uxap.DataObjectPageLayout("", {
            dataInfo: {
                code: bo.Item.BUSINESS_OBJECT_CODE
            },
            headerTitle: new sap.uxap.ObjectPageHeader("", {
                objectTitle: {
                    path: "name",
                    type: new sap.extension.data.Alphanumeric()
                },
                objectSubtitle: {
                    path: "code",
                    type: new sap.extension.data.Alphanumeric()
                },
                navigationBar: new sap.m.Bar("", {
                    contentLeft: [
                        new sap.m.Button("", {
                            text: ibas.i18n.prop("shell_data_edit"),
                            type: sap.m.ButtonType.Transparent,
                            icon: "sap-icon://edit",
                            visible: this.mode === ibas.emViewMode.VIEW ? false : true,
                            press: function (): void {
                                that.fireViewEvents(that.editDataEvent);
                            }
                        })
                    ],
                    contentRight: [
                        // 按需放置当前 BO 的通用服务按钮
                    ]
                }),
                actions: [
                    new sap.extension.m.ObjectYesNoStatus("", {
                        title: ibas.i18n.prop("bo_item_activated"),
                        enumValue: {
                            path: "activated",
                            type: new sap.extension.data.YesNo()
                        }
                    })
                ]
            }),
            headerContent: [
                new sap.extension.m.ObjectAttribute("", {
                    title: ibas.i18n.prop("bo_item_description"),
                    bindingValue: {
                        path: "description",
                        type: new sap.extension.data.Alphanumeric()
                    }
                })
            ],
            sections: [
                new sap.uxap.ObjectPageSection("", {
                    title: ibas.i18n.prop("demo_title_general"),
                    subSections: [
                        new sap.uxap.ObjectPageSubSection("", {
                            blocks: [
                                new sap.extension.m.PropertyObjectAttribute("", {
                                    title: ibas.i18n.prop("bo_item_category"),
                                    dataInfo: {
                                        code: bo.Item.BUSINESS_OBJECT_CODE
                                    },
                                    propertyName: "category",
                                    bindingValue: {
                                        path: "category",
                                        type: new sap.extension.data.Alphanumeric()
                                    }
                                })
                            ]
                        })
                    ]
                }),
                new sap.uxap.ObjectPageSection("", {
                    title: ibas.i18n.prop("bo_itemline"),
                    subSections: [
                        new sap.uxap.ObjectPageSubSection("", {
                            blocks: [
                                this.tableLines
                            ]
                        })
                    ]
                }),
                new sap.uxap.ObjectPageSection("", {
                    title: ibas.i18n.prop("demo_title_others"),
                    subSections: [
                        new sap.uxap.ObjectPageSubSection("", {
                            blocks: [
                                new sap.extension.m.UserObjectAttribute("", {
                                    title: ibas.i18n.prop("bo_item_dataowner"),
                                    bindingValue: {
                                        path: "dataOwner",
                                        type: new sap.extension.data.Numeric()
                                    }
                                }),
                                new sap.extension.m.OrganizationObjectAttribute("", {
                                    title: ibas.i18n.prop("bo_item_organization"),
                                    bindingValue: {
                                        path: "organization",
                                        type: new sap.extension.data.Alphanumeric()
                                    }
                                })
                            ]
                        })
                    ]
                })
            ]
        });
    }

    private page: sap.extension.uxap.ObjectPageLayout;
    private tableLines: sap.extension.m.Table;

    showItem(data: bo.Item): void {
        this.page.setModel(new sap.extension.model.JSONModel(data));
    }

    showItemLines(datas: bo.ItemLine[]): void {
        this.tableLines.setModel(
            new sap.extension.model.JSONModel({ rows: datas })
        );
    }
}
```

## 三、主数据与单据的差异

### 主数据

- `objectTitle`：名称；`objectSubtitle`：编码。
- `actions`：启用、冻结、删除等少量状态。
- `headerContent`：分类、条码、简述等关键识别信息。
- `sections`：一般属性和其他/归属信息。

### 单据

- `objectTitle`：通常显示 `# docEntry` 或单号。
- `actions`：`ObjectDocumentStatus`、取消状态、单据总额等。
- `headerContent`：单据日期、交付日期、业务伙伴、引用。
- `sections`：单据行、物流/财务等业务区、其他信息。

不要在标题、头部和第一个 section 重复展示同一批字段。

## 四、只读子表选择

ObjectPage 内的只读明细默认优先 `sap.extension.m.DataTable`、`sap.extension.m.Column`、`sap.m.ColumnListItem`，便于嵌入对象页。只有列非常多、必须依赖桌面网格排序/固定列，或同模块明确采用桌面表格时，才使用 `sap.extension.table.DataTable`。

## 五、链接和状态

- 只有存在相应 BO 链接服务时，标识才设为可点击。
- `negative: true` 仅用于“是”代表负面状态的字段，例如取消、删除、冻结。
- 编辑按钮在 `mode === ibas.emViewMode.VIEW` 时隐藏，只触发 `editDataEvent`，不在 View 中创建 Edit Application。
