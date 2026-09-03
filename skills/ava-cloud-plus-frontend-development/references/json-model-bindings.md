# JSONModel 基础绑定与模型边界

Cloud+ PC View 围绕可独立显示、刷新和替换的控件单元建立小模型：

```text
Page / ObjectPage       -> 当前主 BO
业务 Table              -> { rows: 当前集合 }
分页 ListView/ChooseView -> Table 自己的 { rows: 已加载结果 }
```

Dialog、Popover、命名模型、小型组合模型和特殊刷新另见 [JSONModel 局部与高级模式](json-model-advanced.md)。

## 扩展 JSONModel

业务 View 默认使用 `sap.extension.model.JSONModel`。它保留 `ibas.Bindable` 监听，支持 BO 属性自动刷新、浅层数组成员监听和分页 `addData()`。模型中保留真实 BO 实例，不做 JSON 深拷贝。

只有目标第三方控件明确要求原生 `sap.ui.model.json.JSONModel`，并且不需要 Cloud+ BO 监听时，才局部使用原生模型。

## 边界决策

先判断哪个控件是稳定显示边界、它显示对象还是集合、是否需要独立刷新。子控件只需要同一数据时，从最近父容器继承模型。

| 显示单元 | 模型数据 | 聚合 | 字段路径 |
| --- | --- | --- | --- |
| EditView Page | `bo.Root` | 无 | `name` |
| ViewView ObjectPage | `bo.Root` | 无 | `name` |
| List/Choose Table | `{ rows: bo.Root[] }` | `/rows` | 行内相对路径 |
| EditView 子表 | `{ rows: bo.Line[] }` | `/rows` | 行内相对路径 |
| ViewView 只读子表 | `{ rows: bo.Line[] }` | `/rows` | 行内相对路径 |
| 孙表下钻 Table | `{ rows: bo.GrandLine[] }` | `/rows` | 行内相对路径 |

`{ rows: datas }` 只是统一集合入口，不把真实 BO 重新映射为 DTO。

## 主对象

主 Page 直接绑定 Application 传入的当前 BO：

```ts
showOrder(data: bo.Order): void {
    this.page.setModel(
        new sap.extension.model.JSONModel(data)
    );
    sap.extension.pages.changeStatus(this.page);
}
```

字段使用 BO 属性名，不增加 `data`、`root` 或 `current` 包装层。页面状态可以直接绑定 `isNew`、`isDirty` 或业务状态属性。

## 业务表格

每张表维护自己的模型：

```ts
showOrderLines(datas: bo.OrderLine[]): void {
    this.tableLines.setModel(
        new sap.extension.model.JSONModel({ rows: datas })
    );
}
```

聚合绑定 `/rows`，单元格使用 `itemCode` 等相对路径。多个子表分别设置到各自 Table，不构造包含主对象、多个集合和 UI 状态的页面级总模型。

## `show...` 契约

一个稳定模型边界对应一个显示方法：主对象设置到 Page，集合设置到对应 Table。方法只负责模型替换、必要容器切换和 busy 状态，不查询 Repository，也不自行拆分所有业务集合。

Application 传入 `filterDeleted()` 后的集合用于显示，但数组成员仍是原 BO 行对象。

## 列表分页

ListView 和 ChooseView 第一次返回时创建 `{ rows: datas }`，同一查询的后续批次复用扩展模型并调用 `addData(datas)`。查询条件变化时先清除旧模型并回到第一行，避免新旧结果混合。

分页状态和下一页条件留在基类或 Application；EditView 子表刷新使用整体替换，不使用分页追加。

## BO 与集合变化

BO 属性变化由扩展模型的 `ibas.Bindable` 监听刷新。Application 回填属性时直接修改真实 BO；需要切换对象时调用对应 `show...` 替换局部模型。

集合新增、删除、过滤或重排后，重新调用对应显示方法。删除新行时从 BO 原集合移除，删除持久化行时标记删除，再显示 `filterDeleted()`。

## 绑定路径

- Page 主 BO：相对属性路径。
- DataTable 聚合：`/rows`；行字段：相对属性路径。
- 表格事件：通过 `this.getBindingContext().getObject()` 取得真实行对象。
- formatter 只转换表现值或控件状态，不修改 BO、不触发事件、不查询服务。

不要按可见行索引回查 `/rows`；排序、筛选和滚动后，可见索引不保证等于原集合索引。

## 完成检查

- 使用扩展 JSONModel 并保留真实 BO。
- 主 Page 直接绑定主对象，每张业务表格使用独立 `{ rows }`。
- `show...` 方法与 Page、Table 等模型边界对应。
- 分页追加和新查询清理语义正确。
- BO 属性依赖自动刷新，集合变化只刷新对应表格。
- View 没有通过模型拼装承担查询、业务计算或保存职责。
