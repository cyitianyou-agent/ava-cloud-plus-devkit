# bsapp ChooseApp、ViewApp 与服务映射

## ChooseApp

ChooseApp 使用 `BOChooseService`。查询成功后：

- 返回一条、允许自动选择且 View 尚未显示时，直接选择；
- 其他情况先显示 View，再显示结果；
- 无结果显示信息，Repository 错误交给统一消息处理。

新建动作通常先销毁当前 ChooseApp，再打开 EditApp，避免残留选择对话框。

`BOChooseServiceMapping` 的 ID、名称和 BO code 来自 ChooseApp，`create()` 返回该 Application，并在 Console 注册，否则 RepositoryInput 无法按 BO code 发现选择服务。

```ts
export class SampleChooseServiceMapping
    extends ibas.BOChooseServiceMapping {

    constructor() {
        super();
        this.id = SampleChooseApp.APPLICATION_ID;
        this.name = SampleChooseApp.APPLICATION_NAME;
        this.boCode = SampleChooseApp.BUSINESS_OBJECT_CODE;
        this.description = ibas.i18n.prop(this.name);
    }

    create(): ibas.IBOChooseService<bo.Sample> {
        return new SampleChooseApp();
    }
}
```

## ViewApp 与链接服务

ViewApp 使用 `BOViewService`，负责把 criteria 或字符串主键转换为查询、设置 `viewData`，并通过主对象和子集合 `show...` 驱动只读 View。编辑事件打开 EditApp 并传递 navigation 与 viewShower；只读 Application 不修改 BO。

只有存在可用 ViewApp、PC View 和 Navigation 映射时才注册 `BOLinkServiceMapping`，否则 DataLink 不能声明链接能力。

## 编辑与通用服务映射

- BO 需要被其他流程打开编辑时使用 `BOEditServiceMapping`。
- 非 BO 标准服务使用 `ServiceMapping`，把 API Proxy 与 bsapp Service 对应。
- 没有跨功能调用需求时不增加 Proxy 或 Mapping。
- Mapping 的泛型、`create()` 返回值、ID、名称和 Console 注册必须一致。

## 完成检查

- ChooseApp 的自动选择、显示、空结果和新建流程明确。
- Choose、Link、Edit 和通用 Mapping 只在真实能力存在时注册。
- ViewApp 不修改 BO，且查询、显示、编辑跳转和 PC Navigation 完整。
- RepositoryInput、DataLink 或服务按钮引用的 Mapping 实际可发现。
