# bsapp EditApp

EditApp 以一个 `editData` 根 BO 为保存单位，负责重载、新建、克隆、保存以及子集合操作。

## 显示与重载

`viewShowed()` 先调用父实现。没有 `editData` 时由 Application 创建新 BO；随后分别调用主对象和各子集合的 `show...` 方法。集合显示使用 `filterDeleted()`，保存仍使用包含删除标记的 BO 原集合。

已持久化对象默认按自身 `criteria()` 重新查询，避免直接编辑列表中的不完整或过期对象：

```text
新对象 -> 直接作为 editData 并显示
已有对象且 criteria 有效 -> Repository 重载 -> 替换 editData -> 显示
无法重新取得 -> 提示已失效
其他调用形式 -> 交给 super.run(...)
```

## 保存

- 保存前设置 busy，并把唯一 `editData` 交给 Repository。
- `resultCode !== 0` 时保留原 `editData` 并报告错误。
- 成功后使用 Repository 返回的新实例替换 `editData`。
- 删除成功返回空集合时释放 `editData`。
- 成功消息区分保存和删除，随后统一回到 `viewShowed()`。
- 包含孙表时同时清理已经失效的当前子项上下文。

```ts
protected saveData(): void {
    this.busy(true);
    let that: this = this;
    let repository: bo.BORepositoryDemo = new bo.BORepositoryDemo();
    repository.saveSample({
        beSaved: this.editData,
        onCompleted(opRslt: ibas.IOperationResult<bo.Sample>): void {
            try {
                if (opRslt.resultCode !== 0) {
                    throw new Error(opRslt.message);
                }
                // 必须使用服务端返回实例，确保主键、版本和默认值与持久化结果一致。
                that.editData = opRslt.resultObjects.firstOrDefault();
                that.viewShowed();
            } catch (error) {
                that.messages(error);
            } finally {
                that.busy(false);
            }
        }
    });
}
```

删除成功是否返回空集合取决于目标 Repository 契约；采用此骨架前先核对并在空结果时显式释放 `editData`。

## 新建与克隆

- 当前对象为脏数据时，先询问是否放弃修改。
- 新建使用具体 BO 构造函数。
- 克隆使用 BO 的 `clone()`，不用 JSON 深拷贝。
- 替换根对象后调用 `viewShowed()` 刷新所有局部模型。

## 子集合

Application 修改 BO 原集合，View 只接收过滤后的结果。新增使用集合 `create()`；删除新行时从原集合移除，删除已持久化行时调用 `delete()`。

孙表由 Application 保存当前父子项上下文，并根据父子键创建、筛选和刷新；View 不直接创建脱离 BO 的孙项数组。真实存在孙表时继续读取 [包含孙表的 EditView](nested-child-edit-view.md)。

## 完成检查

- `editData` 始终是唯一保存根对象。
- 已有对象重载后再编辑，新建和克隆不丢失 BO 类型。
- 保存成功替换实例，失败保留实例，所有路径恢复 busy。
- 子集合操作修改 BO 原集合，删除语义和 `filterDeleted()` 正确。
