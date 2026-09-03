# ChooseView 规范与完整骨架

## 一、标准结构

```text
sap.m.Dialog
├─ content: sap.extension.table.DataTable
└─ buttons: 新建（可选）、选择、退出
```

ChooseView 是紧凑的选择弹窗，不复制 ListView 的删除、编辑、服务工具栏，也不放完整对象详情。列只解决“选中的是谁”以及“如何区分相似对象”。

## 二、完整可改名骨架

```ts
/** 选择视图-示例对象 */
export class ItemChooseView extends ibas.BOChooseView implements app.IItemChooseView {
    get queryTarget(): any {
        return bo.Item;
    }

    draw(): any {
        let that: this = this;
        this.table = new sap.extension.table.DataTable("", {
            chooseType: this.chooseType,
            visibleRowCount: sap.extension.table.visibleRowCount(15),
            dataInfo: this.queryTarget,
            rows: "{/rows}",
            columns: [
                new sap.extension.table.DataColumn("", {
                    label: ibas.i18n.prop("bo_item_code"),
                    template: new sap.extension.m.Text("", {
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
            },
            rowDoubleClick(event: sap.ui.base.Event): void {
                let row: sap.ui.table.Row = event.getParameter("row");
                let data: bo.Item = row?.getBindingContext()?.getObject();
                that.fireViewEvents(that.chooseDataEvent, data);
            }
        });
        return new sap.m.Dialog("", {
            title: this.title,
            type: sap.m.DialogType.Standard,
            state: sap.ui.core.ValueState.None,
            horizontalScrolling: true,
            verticalScrolling: true,
            content: [
                this.table
            ],
            buttons: [
                new sap.m.Button("", {
                    text: ibas.i18n.prop("shell_data_new"),
                    type: sap.m.ButtonType.Transparent,
                    visible: this.mode === ibas.emViewMode.VIEW ? false : true,
                    press: function (): void {
                        that.fireViewEvents(that.newDataEvent);
                    }
                }),
                new sap.m.Button("", {
                    text: ibas.i18n.prop("shell_data_choose"),
                    type: sap.m.ButtonType.Transparent,
                    press: function (): void {
                        that.fireViewEvents(
                            that.chooseDataEvent,
                            that.table.getSelecteds()
                        );
                    }
                }),
                new sap.m.Button("", {
                    text: ibas.i18n.prop("shell_exit"),
                    type: sap.m.ButtonType.Transparent,
                    press: function (): void {
                        that.fireViewEvents(that.closeEvent);
                    }
                })
            ]
        }).addStyleClass("sapUiNoContentPadding");
    }

    private table: sap.extension.table.Table;

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

    query(criteria: ibas.ICriteria): void {
        super.query(criteria);
        if (this.isDisplayed) {
            this.table.setBusy(true);
            this.table.setFirstVisibleRow(0);
            this.table.setModel(null);
        }
    }
}
```

## 三、选择行为

- 表格必须设置 `chooseType: this.chooseType`，由选择服务决定单选或多选。
- “选择”按钮始终传 `getSelecteds()`，基类服务统一处理结果。
- 双击行传单个绑定对象，用于快速完成选择。
- 双击不能替代“选择”按钮，因为多选场景仍需显式确认。
- 退出必须触发 `closeEvent`，不直接销毁 Dialog。
- 只有 Application 支持新建时才显示“新建”；只读模式隐藏它。

## 四、列和尺寸

- 首列通常是编码/单号，第二列是名称/业务伙伴。
- 再补充状态、日期、规格等必要区分字段。
- 不展示大量审计字段和低频备注。
- 宽表允许水平滚动；内容贴近边缘时使用 `sapUiNoContentPadding`。

## 五、条件变体

只有选择过程必须显示复杂查询条件时，才使用带内嵌查询面板的查询对话框基类。普通 ChooseView 不自行在表格上方拼查询表单。
