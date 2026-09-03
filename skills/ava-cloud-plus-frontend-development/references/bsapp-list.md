# bsapp ListApp

ListApp 负责查询、打开新建/查看/编辑应用、批量删除和业务列表动作。

## 查询

`fetchData(criteria)` 在查询前设置 busy，使用当前模块 Repository，检查 `resultCode`，首次需要时显示 View，再把结果交给 `view.showData()`。空结果显示信息而不是异常；所有路径恢复 busy。

```ts
protected fetchData(criteria: ibas.ICriteria): void {
    this.busy(true);
    let that: this = this;
    let repository: bo.BORepositoryDemo = new bo.BORepositoryDemo();
    repository.fetchSample({
        criteria: criteria,
        onCompleted(opRslt: ibas.IOperationResult<bo.Sample>): void {
            try {
                if (opRslt.resultCode !== 0) {
                    throw new Error(opRslt.message);
                }
                if (!that.isViewShowed()) {
                    that.show();
                }
                if (opRslt.resultObjects.length === 0) {
                    that.proceeding(
                        ibas.emMessageType.INFORMATION,
                        ibas.i18n.prop("shell_data_fetched_none")
                    );
                }
                that.view.showData(opRslt.resultObjects);
            } catch (error) {
                that.messages(error);
            } finally {
                // 查询成功、业务失败和异常都必须结束 busy，避免页面永久锁定。
                that.busy(false);
            }
        }
    });
}
```

列表分页由 View 的表格模型追加，Application 继续通过基类 criteria 查询下一页，不在 Application 拼接 UI 数组。

## 打开子 Application

打开 EditApp 或 ViewApp 前检查目标对象，再传递 `navigation`、`viewShower` 和真实 BO。已有对象的重新加载规则由目标 Application 负责。

## 批量删除

- 用 `ibas.arrays.create(data)` 统一单对象和数组。
- 空选择提示并返回。
- 标记删除后询问用户。
- 使用同一 Repository 按框架队列逐项保存。
- 每项失败保留具体对象和错误信息，不显示假成功。
- busy 在队列完成或失败后恢复。

## 完成检查

- 查询条件、Repository 方法和结果 BO 类型一致。
- 首次显示、空结果、错误和分页追加语义正确。
- 子 Application 获得 navigation 与 viewShower。
- 批量删除覆盖空选择、确认、部分失败和 busy 恢复。
