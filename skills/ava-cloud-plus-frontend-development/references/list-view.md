# ListView 规范与完整骨架

## 一、标准结构

ListView 的默认页面结构只有两层：

```text
sap.extension.m.Page
├─ subHeader: sap.m.Toolbar
└─ content: sap.extension.table.DataTable
```

它是全屏列表，不在表格上方加入编辑表单，不把每行改成卡片，也不使用 `IconTabBar` 分页展示同一查询结果。

标准职责：查询、增量加载、展示、选择行，并触发新建、查看、编辑、删除和通用服务事件。

## 二、完整可改名骨架

```ts
namespace demo {
    export namespace ui {
        export namespace c {
            /** 列表视图-示例对象 */
            export class ItemListView extends ibas.BOListView implements app.IItemListView {
                /** 返回查询对象 */
                get queryTarget(): any {
                    return bo.Item;
                }

                /** 编辑数据，参数：目标数据 */
                editDataEvent: Function;
                /** 删除数据，参数：目标数据集合 */
                deleteDataEvent: Function;

                /** 绘制视图 */
                draw(): any {
                    let that: this = this;
                    this.table = new sap.extension.table.DataTable("", {
                        enableSelectAll: false,
                        visibleRowCount: sap.extension.table.visibleRowCount(15),
                        visibleRowCountMode: sap.ui.table.VisibleRowCountMode.Interactive,
                        dataInfo: this.queryTarget,
                        rows: "{/rows}",
                        columns: [
                            new sap.extension.table.DataColumn("", {
                                label: ibas.i18n.prop("bo_item_code"),
                                template: new sap.extension.m.DataLink("", {
                                    objectCode: bo.Item.BUSINESS_OBJECT_CODE,
                                }).bindProperty("bindingValue", {
                                    path: "code",
                                    type: new sap.extension.data.Alphanumeric()
                                })
                            }),
                            new sap.extension.table.DataColumn("", {
                                label: ibas.i18n.prop("bo_item_name"),
                                template: new sap.extension.m.Text("", {
                                }).bindProperty("bindingValue", {
                                    path: "name",
                                    type: new sap.extension.data.Alphanumeric()
                                }),
                                width: "14rem"
                            })
                        ],
                        nextDataSet(event: sap.ui.base.Event): void {
                            let data: any = event.getParameter("data");
                            if (ibas.objects.isNull(data)) {
                                return;
                            }
                            if (ibas.objects.isNull(that.lastCriteria)) {
                                return;
                            }
                            let criteria: ibas.ICriteria = that.lastCriteria.next(data);
                            if (ibas.objects.isNull(criteria)) {
                                return;
                            }
                            that.fireViewEvents(that.fetchDataEvent, criteria);
                        }
                    });
                    return new sap.extension.m.Page("", {
                        showHeader: false,
                        subHeader: new sap.m.Toolbar("", {
                            content: [
                                new sap.m.Button("", {
                                    text: ibas.i18n.prop("shell_data_new"),
                                    type: sap.m.ButtonType.Transparent,
                                    icon: "sap-icon://create",
                                    press: function (): void {
                                        that.fireViewEvents(that.newDataEvent);
                                    }
                                }),
                                new sap.m.Button("", {
                                    text: ibas.i18n.prop("shell_data_edit"),
                                    type: sap.m.ButtonType.Transparent,
                                    icon: "sap-icon://edit",
                                    press: function (): void {
                                        that.fireViewEvents(
                                            that.editDataEvent,
                                            that.table.getSelecteds().firstOrDefault()
                                        );
                                    }
                                }),
                                new sap.m.ToolbarSeparator(""),
                                new sap.m.Button("", {
                                    text: ibas.i18n.prop("shell_data_delete"),
                                    type: sap.m.ButtonType.Transparent,
                                    icon: "sap-icon://delete",
                                    press: function (): void {
                                        that.fireViewEvents(
                                            that.deleteDataEvent,
                                            that.table.getSelecteds()
                                        );
                                    }
                                }),
                                new sap.m.ToolbarSpacer("")
                            ]
                        }),
                        content: [
                            this.table
                        ]
                    });
                }

                private table: sap.extension.table.Table;

                /** 显示数据；翻页时追加 */
                showData(datas: bo.Item[]): void {
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

                /** 新查询时清除旧数据，区别于翻页追加 */
                query(criteria: ibas.ICriteria): void {
                    super.query(criteria);
                    if (this.isDisplayed) {
                        this.table.setBusy(true);
                        this.table.setFirstVisibleRow(0);
                        this.table.setModel(null);
                    }
                }
            }
        }
    }
}
```

## 三、列组织规则

默认顺序：

1. 主键、编号或单号；
2. 名称、业务伙伴、物料等主要描述；
3. 日期、状态、数量、金额等业务字段；
4. 所有人、组织、备注等次要字段。

主键存在链接服务时使用 `DataLink`；没有链接服务时使用 `Text`。外键编码需要显示描述时使用 `RepositoryText`，配置属性使用 `PropertyText`，不要在 formatter 中临时查 Repository。

## 四、操作栏规则

- 单对象动作传 `firstOrDefault()`。
- 批量动作传 `getSelecteds()`。
- 是否提供查看、编辑、删除，以 View 接口和 Application 注册事件为准。
- 通用服务按钮放在右侧；没有服务需求时，不生成空的 action 按钮。
- `enableSelectAll: false` 是增量加载列表的默认选择，避免“全选”被误解为全量数据。

## 五、分页不变量

新查询和下一页必须区分：

- 新查询：保存条件、清空模型、回到第一行、设置 busy；
- 下一页：用 `lastCriteria.next(data)` 生成条件；
- 返回结果：已有模型则 `addData`，首次结果才新建 `{ rows: datas }`；
- 无数据、无上次条件、无下一页条件时直接返回。

## 六、条件变体

只有 Application 明确提供内嵌查询面板时，才改用 `ibas.BOQueryViewWithPanel` 并实现 `embedded(view)`。树形业务对象才使用 TreeTable。二者都不是标准 ListView 的默认写法。
