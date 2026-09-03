# bsapp Application 与 View 契约规范

`bsapp` 是 MVP 中的应用编排层。它调用 `borep` Repository 和 BO，处理查询、保存、选择、业务动作、消息与页面生命周期，并通过 `I...View` 驱动界面。它不能创建 OpenUI5 控件，也不能依赖某个 PC 或移动端 View 实现。

## 一、标准功能目录

```text
bsapp/sample/
├─ SampleFunc.ts
├─ SampleListApp.ts
├─ SampleEditApp.ts
├─ SampleChooseApp.ts
├─ SampleViewApp.ts
└─ index.ts
```

根据真实能力创建文件。只读查询对象不必生成 EditApp；没有链接服务需求不必生成 ViewApp；不要为了目录看起来完整保留空 Application。

## 二、Application 公共标识

```ts
export class SampleListApp
    extends ibas.BOListApplication<ISampleListView, bo.Sample> {

    static APPLICATION_ID: string = "00000000-0000-0000-0000-000000000001";
    static APPLICATION_NAME: string = "demo_app_sample_list";
    static BUSINESS_OBJECT_CODE: string = bo.Sample.BUSINESS_OBJECT_CODE;

    constructor() {
        super();
        this.id = SampleListApp.APPLICATION_ID;
        this.name = SampleListApp.APPLICATION_NAME;
        this.boCode = SampleListApp.BUSINESS_OBJECT_CODE;
        this.description = ibas.i18n.prop(this.name);
    }
}
```

- 每个 Application 使用独立、稳定的 ID。
- `APPLICATION_NAME` 是国际化键，不能直接写用户可见中文。
- 标准 BO Application 的 `BUSINESS_OBJECT_CODE` 引用具体 BO。
- 复制 Application 后必须替换 ID、名称、BO code、泛型和 Repository 方法。

## 三、`I...View` 是跨端契约

接口与 Application 放在同一 `bsapp` 文件中：

```ts
export interface ISampleEditView extends ibas.IBOEditView {
    showSample(data: bo.Sample): void;
    showSampleLines(datas: bo.SampleLine[]): void;

    deleteDataEvent: Function;
    createDataEvent: Function;
    addSampleLineEvent: Function;
    removeSampleLineEvent: Function;
    chooseLineItemEvent: Function;
}
```

规则：

- 接口继承与 Application 类型匹配的框架 View 接口。
- `show...` 参数使用具体 borep BO 类型，因为 Application 和 View 都在当前模块运行时工作。
- 事件注释写清参数语义，尤其是单对象、对象集合、是否克隆和可选参数。
- View 接口不暴露 OpenUI5 控件。
- 不因本 Skill 排除移动端就把接口命名为 PC 接口；Application 仍保持与平台无关。

## 四、事件注册

```ts
protected registerView(): void {
    super.registerView();
    this.view.deleteDataEvent = this.deleteData;
    this.view.createDataEvent = this.createData;
    this.view.addSampleLineEvent = this.addSampleLine;
    this.view.removeSampleLineEvent = this.removeSampleLine;
    this.view.chooseLineItemEvent = this.chooseLineItem;
}
```

- 先调用 `super.registerView()`，保留基类的保存、查询、选择等标准事件。
- 只注册本 Application 实际实现的附加事件。
- View 声明的事件、接口事件、`registerView()` 赋值和实现方法必须四处一致。
- 不把 Application 方法包成无意义匿名函数；保持框架既有方法绑定方式。

## 五、ListApp

标准职责：查询、打开新建/查看/编辑应用、批量删除以及业务列表动作。

```ts
protected fetchData(criteria: ibas.ICriteria): void {
    this.busy(true);
    let that: this = this;
    let repository: bo.BORepositoryDemo = new bo.BORepositoryDemo();
    repository.fetchSample({
        criteria: criteria,
        onCompleted(opRslt: ibas.IOperationResult<bo.Sample>): void {
            try {
                that.busy(false);
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
                that.busy(false);
                that.messages(error);
            }
        }
    });
    this.proceeding(
        ibas.emMessageType.INFORMATION,
        ibas.i18n.prop("shell_fetching_data")
    );
}
```

打开子 Application 时传递环境：

```ts
protected editData(data: bo.Sample): void {
    if (ibas.objects.isNull(data)) {
        this.messages(
            ibas.emMessageType.WARNING,
            ibas.i18n.prop(
                "shell_please_chooose_data",
                ibas.i18n.prop("shell_data_edit")
            )
        );
        return;
    }
    let app: SampleEditApp = new SampleEditApp();
    app.navigation = this.navigation;
    app.viewShower = this.viewShower;
    app.run(data);
}
```

批量删除：

- 用 `ibas.arrays.create(data)` 统一单对象和数组。
- 空选择先提示并返回。
- 标记删除后询问用户。
- 使用同一 Repository 按框架队列逐项保存。
- 每项失败保留具体对象和错误消息，不显示假成功。
- busy 必须在成功和失败路径最终恢复。

列表分页由 View 的表格模型追加，Application 继续通过基类 criteria 的下一页条件查询，不在 Application 拼接 UI 数组。

## 六、EditApp

### 页面显示

```ts
protected viewShowed(): void {
    super.viewShowed();
    if (ibas.objects.isNull(this.editData)) {
        this.editData = new bo.Sample();
        this.proceeding(
            ibas.emMessageType.WARNING,
            ibas.i18n.prop("shell_data_created_new")
        );
    }
    this.view.showSample(this.editData);
    this.view.showSampleLines(
        this.editData.sampleLines.filterDeleted()
    );
}
```

- `editData` 是唯一待保存根对象。
- 新对象在 Application 创建，不由 View 创建。
- 主对象和各子集合通过独立 `show...` 方法传给 View。
- 显示集合用 `filterDeleted()`；保存的仍是包含删除标记的 BO 原集合。

### 运行已有对象

已持久化对象默认按自身 `criteria()` 重新查询，避免直接编辑 ListView 中可能不完整或过期的对象：

```text
新对象 -> 直接作为 editData 并 show
已有对象且 criteria 有效 -> Repository 重新 fetch -> 替换 editData -> show
无法重新取得 -> 提示数据已失效，再决定是否显示空页面
其他调用形式 -> 交给 super.run(...)
```

不要把传入对象无条件直接作为已有对象编辑，也不要在 View 中重新查询。

### 保存

```ts
protected saveData(): void {
    this.busy(true);
    let that: this = this;
    let repository: bo.BORepositoryDemo = new bo.BORepositoryDemo();
    repository.saveSample({
        beSaved: this.editData,
        onCompleted(opRslt: ibas.IOperationResult<bo.Sample>): void {
            try {
                that.busy(false);
                if (opRslt.resultCode !== 0) {
                    throw new Error(opRslt.message);
                }
                if (opRslt.resultObjects.length === 0) {
                    that.editData = undefined;
                } else {
                    that.editData = opRslt.resultObjects.firstOrDefault();
                }
                that.viewShowed();
            } catch (error) {
                that.busy(false);
                that.messages(error);
            }
        }
    });
}
```

- 保存后使用 Repository 返回的新实例替换 `editData`，不能继续保留旧实例。
- 删除成功可能返回空集合，此时释放 `editData`。
- 成功消息区分保存和删除；示例省略了文字，不代表可以不反馈。
- 刷新统一回到 `viewShowed()`，包含孙表时同时清理过期的当前子项上下文。
- 失败不能替换 `editData`，busy 必须关闭。

### 新建与克隆

- 当前对象脏时先询问是否放弃未保存修改。
- 新建使用 `new bo.Sample()`。
- 克隆使用 BO 的 `clone()`，不使用 JSON 深拷贝。
- 替换后调用 `viewShowed()`，刷新主对象和所有局部表格。

### 子集合

```ts
private addSampleLine(): void {
    this.editData.sampleLines.create();
    this.view.showSampleLines(
        this.editData.sampleLines.filterDeleted()
    );
}

private removeSampleLine(items: bo.SampleLine[]): void {
    if (!(items instanceof Array)) {
        items = [items];
    }
    for (let item of items) {
        if (this.editData.sampleLines.indexOf(item) < 0) {
            continue;
        }
        if (item.isNew) {
            this.editData.sampleLines.remove(item);
        } else {
            item.delete();
        }
    }
    this.view.showSampleLines(
        this.editData.sampleLines.filterDeleted()
    );
}
```

Application 修改 BO 原集合，View 只接收结果。孙表还要由 Application 保存当前父子项，不能让 View 直接创建孙项。

## 七、ChooseApp

```ts
export class SampleChooseApp
    extends ibas.BOChooseService<ISampleChooseView, bo.Sample> {
}
```

查询成功后的标准分支：

- 返回一条、允许自动选择且 View 尚未显示：直接 `chooseData(resultObjects)`。
- 否则先显示 View，再 `showData(resultObjects)`。
- 无结果显示信息，不作为异常。
- Repository 错误交给消息处理。

新建动作通常先销毁当前 ChooseApp，再打开 EditApp，避免残留选择对话框：

```ts
protected newData(): void {
    this.destroy();
    let app: SampleEditApp = new SampleEditApp();
    app.navigation = this.navigation;
    app.viewShower = this.viewShower;
    app.run();
}
```

选择服务映射：

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

Mapping 必须在 Console 注册，否则 `RepositoryInput` 或选择服务按 BO code 查找时无法发现它。

## 八、ViewApp 与链接服务

```ts
export class SampleViewApp
    extends ibas.BOViewService<ISampleViewView, bo.Sample> {
}
```

标准职责：

- `fetchData(criteria | string)` 将字符串转成主键条件并限制结果数。
- Repository 查询后设置 `viewData`。
- `viewShowed()` 调用 View 的主对象和子集合显示方法。
- 编辑事件打开 EditApp，并传递 navigation、viewShower。
- 不在只读 Application 中修改 BO。

链接映射：

```ts
export class SampleLinkServiceMapping extends ibas.BOLinkServiceMapping {
    constructor() {
        super();
        this.id = SampleViewApp.APPLICATION_ID;
        this.name = SampleViewApp.APPLICATION_NAME;
        this.boCode = SampleViewApp.BUSINESS_OBJECT_CODE;
        this.description = ibas.i18n.prop(this.name);
    }

    create(): ibas.IBOLinkService {
        return new SampleViewApp();
    }
}
```

只有存在可用的 ViewApp 和 PC View 时注册链接服务；不能让 DataLink 指向没有 Navigation 映射的 Application。

## 九、EditServiceMapping 与通用 ServiceMapping

BO 需要被其他流程作为编辑服务打开时使用：

```ts
export class SampleEditServiceMapping extends ibas.BOEditServiceMapping {
    constructor() {
        super();
        this.id = SampleEditApp.APPLICATION_ID;
        this.name = SampleEditApp.APPLICATION_NAME;
        this.boCode = SampleEditApp.BUSINESS_OBJECT_CODE;
        this.description = ibas.i18n.prop(this.name);
    }

    create(): ibas.IService<ibas.IBOEditServiceCaller<bo.Sample>> {
        return new SampleEditApp();
    }
}
```

非 BO 标准选择/查看/编辑服务使用 `ServiceMapping`，并将 API 中的 Proxy 与 bsapp 中的 Service 对应：

```ts
export class SampleServiceMapping extends ibas.ServiceMapping {
    constructor() {
        super();
        this.id = SampleService.APPLICATION_ID;
        this.name = SampleService.APPLICATION_NAME;
        this.description = ibas.i18n.prop(this.name);
        this.proxy = SampleServiceProxy;
    }

    create(): ibas.IService<ibas.IServiceContract> {
        return new SampleService();
    }
}
```

没有跨功能调用需求时，不增加 ServiceProxy 和 Mapping。

## 十、Function 与 Console

功能入口：

```ts
export class SampleFunc extends ibas.ModuleFunction {
    static FUNCTION_ID: string = "00000000-0000-0000-0000-000000000002";
    static FUNCTION_NAME: string = "demo_func_sample";

    constructor() {
        super();
        this.id = SampleFunc.FUNCTION_ID;
        this.name = SampleFunc.FUNCTION_NAME;
        this.description = ibas.i18n.prop(this.name);
    }

    default(): ibas.IApplication<ibas.IView> {
        let app: SampleListApp = new SampleListApp();
        app.navigation = this.navigation;
        return app;
    }
}
```

`Console.registers()` 中按真实能力注册：

```ts
this.register(new SampleFunc());
this.register(new SampleChooseServiceMapping());
this.register(new SampleLinkServiceMapping());
```

- 用户从菜单直接进入的功能注册 Function。
- 供其他功能调用的选择、链接、编辑或业务服务注册 Mapping。
- 权限元素在实际受权限控制时注册。
- 条件配置关闭的功能遵循模块已有 config 判断。
- 不把 Application 本身直接当 Function 或 Mapping 注册。

Console 的 `run()` 负责语言资源、平台 UI 库和 Navigation 初始化。PC 功能开发不要改变手机平台分支，也不要删除现有平台选择逻辑。

## 十一、功能 `index.ts`

```ts
/// <reference path="./SampleFunc.ts" />
/// <reference path="./SampleListApp.ts" />
/// <reference path="./SampleChooseApp.ts" />
/// <reference path="./SampleEditApp.ts" />
/// <reference path="./SampleViewApp.ts" />
```

还要在 `bsapp/Console.ts` 顶部引用功能目录：

```ts
/// <reference path="./sample/index.ts" />
```

由于模块常以 `Console.ts` 作为 `tsconfig.json` 的根文件，漏掉任一引用都可能导致代码根本没有进入编译结果。

## 十二、错误、busy 和消息

- 发起异步查询/保存前 `busy(true)`。
- 成功和失败路径都必须恢复 busy。
- `resultCode !== 0` 作为操作失败，不继续显示或替换数据。
- 空查询结果是信息；保存空结果可能表示删除成功，要按方法语义判断。
- 业务前置条件不足用 WARNING 并立即返回。
- 删除、放弃脏数据等不可逆或易丢失动作先用 QUESTION 确认。
- 消息使用国际化键，不硬编码用户文字。

## 十三、常见反例

- Application 中创建 `sap.m.Dialog` 或 `DataTable`。
- View 中实例化 Repository 保存 BO。
- 忘记 `super.registerView()` 或 `super.viewShowed()`。
- 接口事件存在，但 Application 未注册；Application 调用 `show...`，View 接口未声明。
- 已有对象直接编辑而不按 criteria 重新读取。
- 保存成功后仍使用旧 `editData` 实例。
- 子行直接从 `filterDeleted()` 返回数组移除，而不是修改 BO 原集合。
- Choose/Link Mapping 已编写但没有在 Console 注册。
- Application ID 在 PC Navigation 中重复或没有映射。
- 为没有业务入口的空 Application 机械创建 Function。

## 十四、完成检查

- Application 基类和 BO 类型匹配。
- ID、名称、BO code 唯一且在 Function、Mapping、Navigation 中一致。
- `I...View`、注册事件、Application 方法和 PC View 四处契约一致。
- Repository 调用、错误检查、busy 和消息流程完整。
- EditApp 正确处理重新查询、新建、克隆、保存替换和删除。
- 子集合由 Application 修改，显示使用 `filterDeleted()`。
- ChooseApp、ViewApp 及 Mapping 只在真实需要时存在并已注册。
- 功能 `index.ts` 和 `Console.ts` 已进入完整引用链。
- `bsapp` 没有 OpenUI5 控件代码，也没有依赖 `bsui/c`。
