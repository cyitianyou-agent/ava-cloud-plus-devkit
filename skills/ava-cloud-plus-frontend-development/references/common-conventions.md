# 通用架构与界面风格

## 一、MVP 职责边界

页面运行链路为：

```text
bsapp Application -> bsui/c Navigation -> PC View
```

Application 负责业务动作，在 `registerView()` 中把方法赋给 View 事件；View 负责控件、绑定和用户交互，通过 `fireViewEvents(...)` 把操作交还 Application。

标准对应关系：

| 页面目的 | View 基类 | 常用根控件 |
| --- | --- | --- |
| 列表查询 | `ibas.BOListView` | `sap.extension.m.Page` |
| 数据选择 | `ibas.BOChooseView` | `sap.m.Dialog` |
| 数据编辑 | `ibas.BOEditView` | `sap.extension.m.DataPage` |
| 数据查看 | `ibas.BOViewView` | `sap.extension.uxap.DataObjectPageLayout` |
| 自定义完整页面 | `ibas.View` 或查询类基类 | `sap.extension.m.Page` |
| 自定义弹窗 | `ibas.DialogView` | `sap.m.Dialog` |

`app.I...View` 是 View 的直接契约。实现前必须核对：

- Application 注册了哪些事件；
- Application 调用了哪些 `show...` 方法；
- 事件接收单对象、对象集合还是附加参数；
- 页面是否继承查询、选择、编辑或查看生命周期。

接口和 Application 注册方式示例：

```ts
export interface IItemEditView extends ibas.IBOEditView {
    /** 显示示例对象 */
    showItem(data: bo.Item): void;
    /** 删除数据事件 */
    deleteDataEvent: Function;
    /** 新建数据事件，参数：是否克隆 */
    createDataEvent: Function;
}

protected registerView(): void {
    super.registerView();
    this.view.deleteDataEvent = this.deleteData;
    this.view.createDataEvent = this.createData;
}
```

`saveDataEvent`、`fetchDataEvent`、`chooseDataEvent` 等事件由相应基类注册时，具体 Application 不需要重复注册，但 View 仍按基类契约触发它们。

View 中只声明并触发事件：

```ts
/** 编辑数据，参数：目标数据 */
editDataEvent: Function;

press: function (): void {
    that.fireViewEvents(
        that.editDataEvent,
        that.table.getSelecteds().firstOrDefault()
    );
}
```

不要在 View 中直接创建 Repository 查询、保存 BO 或实现业务计算。

## 二、文件结构

标准类保持三层命名空间：

```ts
namespace demo {
    export namespace ui {
        export namespace c {
            export class ItemListView extends ibas.BOListView implements app.IItemListView {
            }
        }
    }
}
```

标准文件命名：

- `ItemListView.ts`
- `ItemEditView.ts`
- `ItemChooseView.ts`
- `ItemViewView.ts`

同一功能目录的 `index.ts` 使用三斜线引用：

```ts
/// <reference path="./ItemChooseView.ts" />
/// <reference path="./ItemEditView.ts" />
/// <reference path="./ItemListView.ts" />
/// <reference path="./ItemViewView.ts" />
```

PC 导航映射：

```ts
case app.ItemListApp.APPLICATION_ID:
    view = new c.ItemListView();
    break;
case app.ItemChooseApp.APPLICATION_ID:
    view = new c.ItemChooseView();
    break;
case app.ItemEditApp.APPLICATION_ID:
    view = new c.ItemEditView();
    break;
case app.ItemViewApp.APPLICATION_ID:
    view = new c.ItemViewView();
    break;
```

## 三、Cloud+ PC 端视觉语言

### 强共性

- 页面以业务数据为中心，信息密度较高，不使用大面积装饰性留白。
- 标准完整页面通常 `showHeader: false`，操作放在 `subHeader` 的透明工具栏。
- 列表、选择、编辑子表优先使用 `sap.extension.table.DataTable`，这是面向 PC 的密集表格。
- 标签统一使用 `ibas.i18n.prop(...)`，不硬编码用户可见文字。
- 标准按钮使用 `sap.m.ButtonType.Transparent` 和 SAP 图标。
- BO 值优先绑定到扩展控件的 `bindingValue`，并声明 `sap.extension.data.*` 类型。
- 对象元数据、用户字段、Repository 描述、链接服务、状态显示优先使用 `sap.extension.*` 能力。

### 默认间距和分组

- 主要依靠 `SimpleForm`、`ToolbarSeparator`、`ToolbarSpacer`、`ObjectPageSection` 和 `IconTabFilter` 形成层次。
- 只在相邻控件确实需要间隔时使用 `sapUiTinyMargin...`、`sapUiSmallMargin...`。
- 不在单个标准页中发明新的颜色、阴影、卡片或栅格体系。
- 表格列宽只给长文本、描述、备注等需要稳定空间的列设置；不为每一列机械设置宽度。

## 四、标准按钮语义

| 动作 | 国际化键 | 图标 |
| --- | --- | --- |
| 新建 | `shell_data_new` | `sap-icon://create` |
| 查看 | `shell_data_view` | `sap-icon://display` |
| 编辑 | `shell_data_edit` | `sap-icon://edit` |
| 保存 | `shell_data_save` | `sap-icon://save` |
| 删除 | `shell_data_delete` | `sap-icon://delete` |
| 克隆 | `shell_data_clone` | `sap-icon://copy` |
| 通用服务 | 按服务名称 | `sap-icon://action` |

默认顺序：主要动作在左，相关动作连续排列；删除等动作使用分隔符隔开；通用服务放在 `ToolbarSpacer` 之后的右侧。若 Application 不支持某动作，不生成空按钮。

## 五、模型和显示方法

本节只列默认形状；模型作用域、分页追加、局部模型、刷新方式和反例必须继续读取 [JSONModel 数据绑定与模型边界](json-model-bindings.md)。

主对象直接作为根模型：

```ts
showItem(data: bo.Item): void {
    this.page.setModel(new sap.extension.model.JSONModel(data));
}
```

独立表格集合使用统一的 `/rows`：

```ts
showItemLines(datas: bo.ItemLine[]): void {
    this.tableLines.setModel(
        new sap.extension.model.JSONModel({ rows: datas })
    );
}
```

绑定路径必须与模型形状一致。一个页面内不要无理由混用 BO 根模型、`{ data: bo }` 和 `{ rows: datas }`。

只有后续方法需要访问的控件才声明为字段：

```ts
private page: sap.extension.m.Page;
private table: sap.extension.table.Table;
private tableLines: sap.extension.table.Table;
```

## 六、`that` 与控件上下文

普通回调需要访问 View 时，使用：

```ts
let that: this = this;
```

当 OpenUI5 明确把 `this` 绑定为控件时，可使用具名 `this` 类型取得行绑定对象：

```ts
valueHelpRequest(this: sap.extension.m.Input): void {
    that.fireViewEvents(
        that.chooseItemEvent,
        this.getBindingContext().getObject()
    );
}
```

不要混淆 View 的 `this` 和控件的 `this`。

## 七、规则取舍

以下属于条件变体，不是默认结构：

- `IconTabBar`：主表字段或子表存在多个清晰业务组时使用；不是每个 EditView 都必须有。
- 树表：数据本身具有层级关系时使用。
- 内嵌查询面板：Application 提供查询面板契约时使用。
- 卡片、看板、时间轴、图表：业务任务以该表达形式为核心时使用。
- 嵌套 `NavContainer`：页面确实需要内部钻取且 Application/View 生命周期支持时使用。

判断不了时，优先保持标准骨架，不能从一个特殊页面推导新的全局规则。

## 八、集成检查

- 文件名、导出类名、`I...View` 名称一致。
- View 触发的每个事件都存在于接口，并由 Application 或基类注册。
- Application 调用的每个 `show...` 方法均已实现，参数类型一致。
- `index.ts` 已引用新增 PC View。
- `Navigation.ts` 的 Application ID 与 View 一一对应，没有重复 case。
- 没有修改 `bsui/m` 和 `3rdparty`。
