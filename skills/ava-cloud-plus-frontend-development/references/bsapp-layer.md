# bsapp Application 与 View 公共契约

`bsapp` 是 MVP 应用编排层：调用 `borep` Repository 和 BO，处理查询、保存、选择、业务动作、消息与生命周期，并通过 `I...View` 驱动界面。它不能创建 OpenUI5 控件，也不能依赖 `bsui/c` 的具体 View。

## 文件与职责

```text
bsapp/sample/
├─ SampleFunc.ts
├─ SampleListApp.ts
├─ SampleEditApp.ts
├─ SampleChooseApp.ts
├─ SampleViewApp.ts
└─ index.ts
```

只创建真实能力需要的文件。只读对象不需要空 EditApp；没有选择、链接或编辑服务时不增加对应 Application 和 Mapping。

页面类型的专用流程按需读取：

- 列表查询、分页和批量删除：[ListApp](bsapp-list.md)
- 编辑、重载、保存、克隆和子集合：[EditApp](bsapp-edit.md)
- 选择、只读查看及服务映射：[ChooseApp、ViewApp 与服务映射](bsapp-services.md)

## Application 标识

每个 Application 使用独立、稳定的 `APPLICATION_ID`、国际化 `APPLICATION_NAME` 和正确的 `BUSINESS_OBJECT_CODE`。复制现有 Application 后必须替换 ID、名称、BO code、泛型和 Repository 方法；这些值还要与 Function、Mapping 和 PC Navigation 保持一致。

## `I...View` 契约

接口与 Application 放在同一个 `bsapp` 文件中，并继承匹配的框架 View 接口：

```ts
export interface ISampleEditView extends ibas.IBOEditView {
    showSample(data: bo.Sample): void;
    showSampleLines(datas: bo.SampleLine[]): void;

    addSampleLineEvent: Function;
    removeSampleLineEvent: Function;
}
```

- `show...` 参数使用当前模块的具体 borep BO 类型。
- 事件注释说明单对象、集合、克隆和可选参数语义。
- 接口不暴露 OpenUI5 控件，也不因当前只实现 PC View 而命名为 PC 接口。
- View 事件、接口声明、`registerView()` 赋值和 Application 方法必须一致。

## 事件注册

```ts
protected registerView(): void {
    super.registerView();
    this.view.addSampleLineEvent = this.addSampleLine;
    this.view.removeSampleLineEvent = this.removeSampleLine;
}
```

先调用 `super.registerView()`，只注册本 Application 实际实现的附加事件，并保持模块已有的方法绑定方式。

## Function、Mapping 与 Console

- 菜单直接进入的功能注册 `ModuleFunction`。
- 供其他功能调用的选择、链接、编辑或业务服务注册对应 Mapping。
- 没有跨功能调用需求时不增加 ServiceProxy 和 Mapping。
- `Console.registers()` 只注册真实存在且可运行的 Function、Mapping 和权限元素。
- `Console.run()` 保留既有语言资源、平台 UI 库和 Navigation 初始化，不改变移动平台分支。

`SampleFunc.default()` 创建 Application 并传递 navigation；Mapping 的 `create()` 返回与其契约匹配的 Application 或 Service。Application 本身不能直接当作 Function 或 Mapping 注册。

## 引用链

功能 `index.ts` 引用实际存在的 Func、Application 和 View 契约文件，`bsapp/Console.ts` 再引用功能目录。模块采用 `outFile` 时，遗漏三斜线引用可能导致文件完全不进入编译结果。

## 异步、错误与消息

- 查询或保存前 `busy(true)`，成功和失败路径都恢复 busy。
- `resultCode !== 0` 按失败处理，不继续显示或替换数据。
- 空查询结果是信息；保存空结果可能表示删除成功，要按方法语义判断。
- 业务前置条件不足用 WARNING 并立即返回。
- 删除、放弃脏数据等易丢失动作先用 QUESTION 确认。
- 消息使用国际化键，不硬编码用户文字。

## 完成检查

- Application 基类、BO 类型、ID、名称和 code 匹配。
- `I...View`、事件注册、Application 方法和 PC View 契约一致。
- Repository、busy、错误和消息流程完整。
- Function、Mapping、Console、功能 `index.ts` 和 Navigation 没有漏项或重复 ID。
- `bsapp` 没有 OpenUI5 控件代码，也不依赖 `bsui/c`。
