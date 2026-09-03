# 非标准页面与行业扩展

## 一、非标准页面不是第五种固定模板

先根据 Application 生命周期选择基类：

| 页面需求 | 通常使用 |
| --- | --- |
| 无标准 CRUD 生命周期的完整工作页 | `ibas.View` |
| 聚焦操作的弹窗 | `ibas.DialogView` |
| 带内嵌查询面板的完整页面 | `ibas.BOQueryViewWithPanel` |
| 带内嵌查询面板的弹窗 | `ibas.BOQueryDialogViewWithPanel` |
| 常驻工具或面板 | `ibas.ResidentView`、`BarView` 或已有专用基类 |
| 外部 URL 内容 | `ibas.UrlView` |

文件名包含 List、Edit、Choose、View，不代表一定使用对应标准基类；以 `I...View` 和 Application 注册事件为准。

## 二、自定义页面仍遵守的共性

- 页面级工作区使用 `sap.extension.m.Page`，聚焦操作使用 `sap.m.Dialog`。
- 所有业务动作仍通过事件交给 Application。
- 查询基类仍要实现 `query(criteria)`；带面板基类还要实现 `embedded(view)`。
- 复杂页面的临时选中项、展开状态、当前页签可放 View 字段；业务状态必须留在 BO/Application。
- 内嵌子 View 必须保留其显示、关闭、销毁生命周期，不能只抽取控件后遗弃 View。
- 新页面仍需加入功能 `index.ts` 和 PC `Navigation.ts`。

## 三、何时允许特殊布局

只有业务信息结构本身要求时才采用：

- 树表：存在真正父子层级；
- 看板/卡片：核心任务是按状态或类别浏览对象；
- 图表：核心任务是趋势、结构或比较分析；
- 日历/时间轴：核心任务是排程或时间分布；
- `NavContainer`：一个应用内确实需要钻取到次级操作页；
- 分栏：用户需要同时对照两个持续可见的数据区域。

这些布局只约束该功能，不反向改变 List/Edit/Choose/ViewView 的标准骨架。

## 四、行业包覆盖

行业包通过 `ibas.ViewExtendedNavigation` 截获标准模块 Application ID，并返回行业 View。

推荐顺序：

1. 行业 View 继承标准模块 View。
2. 优先调用 `super.draw()`，只添加或替换行业需要的区域。
3. 覆盖 `show...` 时通常先调用 `super.show...`，再绑定行业字段或刷新行业控件。
4. 在行业 PC `Navigation` 中把外部模块的 `APPLICATION_ID` 映射到行业 View。
5. 未处理的 ID 返回 `null`，让扩展导航链继续。

示例：

```ts
export class ItemEditView extends standard.ui.c.ItemEditView {
    draw(): any {
        let page: any = super.draw();
        if (!(page instanceof sap.m.Page)) {
            return page;
        }
        // 仅添加行业页签或控件，不复制整个标准页面。
        return page;
    }

    showItem(data: standard.bo.Item): void {
        super.showItem(data);
        // 刷新仅属于行业包的显示状态。
    }
}
```

扩展导航：

```ts
if (id === standard?.app?.ItemEditApp?.APPLICATION_ID) {
    view = new c.ItemEditView();
}
```

## 五、覆盖风险

通过 `getContent()[0]` 等数字索引遍历标准页面控件树非常脆弱。没有稳定扩展点且必须使用时：

- 每一层先用 `instanceof` 校验；
- 找不到目标结构时安全返回；
- 把遍历集中在一个方法；
- 注释说明依赖的标准页面结构；
- 不复制整个上游 View 来增加一个页签或一列。

局部声明标准 View 的成员签名，只用于依赖声明未暴露但继承确实需要的成员；声明必须与实际基类一致，不能借此绕过类型错误。

## 六、避免把个例泛化

遇到特殊页面写法时，只有同时满足以下条件才提炼成共性：

- 至少在多个无继承关系的业务功能中重复出现；
- 解决的是相同的信息结构或交互问题；
- 不与四类标准页骨架冲突；
- 能明确说明启用条件和不启用条件。

否则把它保留为该功能的局部实现。
