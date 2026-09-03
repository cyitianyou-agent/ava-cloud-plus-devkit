# 四层联动与开发流程

本文件用于新增业务对象、标准功能或跨层修改。它解决的是“改动应该落在哪一层，以及怎样确认整条链没有断”，各层具体写法继续读取对应规范。

## 一、四层不是四份重复代码

```text
api
├─ Data.ts：模块标识、配置键、BO 编码、公共枚举、稳定服务契约
├─ bo/*.ts：BO、子项和集合的公共接口
├─ BORepository.ts：公共仓库接口
└─ index.ts：api 编译引用入口
          ↓ 类型契约
borep
├─ bo/*.ts：具体 BO、集合、默认值和业务规则
├─ BORepository.ts：查询、保存和远程调用实现
├─ DataConverter.ts：远程数据转换和 BOFactory
└─ index.ts：运行时引用及工厂注册
          ↓ 可执行领域层
bsapp
├─ *ListApp / *EditApp / *ChooseApp / *ViewApp
├─ I*View：Application 与 View 的契约
├─ *Func：功能入口
├─ *Service / *Mapping：跨功能服务入口
├─ 功能 index.ts
└─ Console.ts：模块功能、服务和权限注册
          ↓ MVP 契约
bsui/c
├─ *ListView / *EditView / *ChooseView / *ViewView
├─ 功能 index.ts
└─ Navigation.ts：Application ID 到 PC View 的映射
```

各层回答不同问题：

- `api`：其他代码可以依赖什么类型和能力？
- `borep`：BO 在浏览器运行时怎样工作，怎样与后端交换？
- `bsapp`：一个用户操作如何查询、修改、保存并驱动视图？
- `bsui/c`：这些契约在 PC 端怎样呈现和交互？

## 二、依赖方向是硬约束

允许：

```text
api <- borep <- bsapp <- bsui/c
```

不允许：

- `api` 引用 `borep` 的具体类；
- BO 或 Repository 引用某个 Application；
- `bsapp` 创建 OpenUI5 控件；
- View 直接查询、保存 Repository 或执行业务计算；
- 为了让 View 编译而在 `3rdparty` 声明文件中补假类型；
- 当前模块直接修改另一个模块的生成声明产物。

跨模块依赖应通过对方公开的 `index.d.ts` 使用。若目标模块的 `tsconfig.json` 尚未包含该依赖，先确认模块设计确实允许依赖，再更新真实依赖配置；不要用全局 `any` 绕过。

## 三、新增一个标准 BO 功能的联动清单

假设新增 `Sample`，并提供 List、Edit、Choose、View 四类功能。

### 1. `api`

- `Data.ts` 增加唯一的 `BO_CODE_SAMPLE`；需要时增加公共枚举或配置键。
- `api/bo/Sample.ts` 定义 `ISample`；有子项时同时定义 `ISampleLines`、`ISampleLine`。
- 根据对象语义选择 `IBOMasterData`、`IBODocument` 或 `IBOSimple`，子项选择对应 Line 接口。
- `IBORepository<Module>` 增加 `fetchSample`；对象可保存时增加 `saveSample`。
- `api/index.ts` 引用新 BO 文件，并保持 `Data.ts → bo/*.ts → BORepository.ts` 的可解析顺序。

### 2. `borep`

- `borep/bo/Sample.ts` 实现 API 接口，基类与 API 接口完全对应。
- 声明 `BUSINESS_OBJECT_CODE`、所有 `PROPERTY_*_NAME`、getter/setter、集合类、默认值和必要规则。
- `BORepository.ts` 实现 API 新方法；普通查询保存委托基类 `fetch`、`save`。
- `DataConverter.ts` 仅为确实需要特殊序列化的枚举或数据补充对称转换。
- `borep/index.ts` 引用新文件，并向 `boFactory` 注册可由仓库构造的根 BO。

### 3. `bsapp`

- 建立 `sample/index.ts`，引用实际存在的 Function 和 Application。
- ListApp 调用 `fetchSample`，提供新建、查看、编辑、删除流程。
- EditApp 维护 `editData`，重新读取已有对象，调用 `saveSample`，并管理子集合。
- ChooseApp 调用 `fetchSample`，提供 `SampleChooseServiceMapping`。
- ViewApp 调用 `fetchSample`，提供 `SampleLinkServiceMapping`。
- 每个 Application 文件定义对应 `I...View`，事件和 `show...` 方法参数使用具体类型。
- `SampleFunc` 默认返回主要入口 Application。
- `Console.ts` 引用功能目录，注册 Function、Choose/Link/Edit Mapping 和权限元素。

### 4. `bsui/c`

- 实现 Application 所声明的 PC View 接口，不在 View 发明接口外的业务流程。
- 功能 `index.ts` 引用实际 View 文件。
- `Navigation.ts` 为每个可显示 Application ID 创建唯一映射。
- 添加页面所需的国际化键；BO 字段标签与 Application 名称分别放在模块既有语言资源位置。

## 四、从一个字段变化向上下游检查

新增或修改 BO 字段时按下面链路核对：

```text
后端映射名称
    ↕
api 接口属性
    ↕
borep PROPERTY_*_NAME + getter/setter
    ↕
DataConverter（仅特殊类型）
    ↕
Application 条件、赋值和校验
    ↕
View bindingValue 路径和 sap.extension.data 类型
    ↕
国际化标签
```

必须保持三种命名各司其职：

- TypeScript 属性：小驼峰，如 `customerCode`；
- 后端映射常量值：PascalCase，如 `"CustomerCode"`；
- 静态常量名：`PROPERTY_CUSTOMERCODE_NAME`。

不能因为 View 使用小写路径，就把 `PROPERTY_*_NAME` 的远程映射值也改成小写。

## 五、从一个子集合变化向上下游检查

新增 `sampleLines` 时至少同时存在：

```text
api:
ISample.sampleLines: ISampleLines
ISampleLines.create(): ISampleLine
ISampleLine extends 对应 Line 接口

borep:
Sample.sampleLines: SampleLines
SampleLines extends BusinessObjects<SampleLine, Sample>
SampleLines.create(): SampleLine
Sample.init() 中 new SampleLines(this)

bsapp:
IView.showSampleLines(datas: bo.SampleLine[])
新增/删除/选择行事件
使用原集合修改，显示 filterDeleted()

bsui/c:
独立 DataTable
{ rows: datas } JSONModel
行绑定使用真实 SampleLine
```

若子项还有孙集合，API 和 borep 的所有权必须先正确表达，再由 Application 保存当前子项上下文，View 才使用下钻式孙表。

## 六、功能、服务和导航的三类 ID

- `FUNCTION_ID`：模块功能入口，由 `ModuleFunction` 使用，在 Console 中注册。
- `APPLICATION_ID`：Application 与 View Navigation 的对应标识，必须全局稳定且不重复。
- BO code：领域对象标识，用于 Repository、服务映射、数据链接和控件 `dataInfo`。

三者用途不同，不能互换。新增功能后至少检查：

```text
Func.default() -> Application
Console.register(Func / Mapping)
Mapping.create() -> Application
Navigation APPLICATION_ID -> PC View
View.dataInfo.code -> BO BUSINESS_OBJECT_CODE
```

复制已有功能时必须生成新的 Function/Application ID，不能连同旧 ID 一起复制。完成后搜索新旧 ID，确认一个 Application ID 在 PC `Navigation.ts` 中只有一个 `case`。

## 七、修改 View 契约的顺序

`I...View` 位于 `bsapp`，是 Application 和 PC View 的共同边界。新增事件时：

1. 在 `I...View` 声明事件及参数语义。
2. 在 Application `registerView()` 中把方法赋给 View 事件。
3. 在 Application 实现方法，业务行为和 Repository 调用留在这里。
4. 在 PC View 声明事件字段并通过 `fireViewEvents(...)` 触发。

新增显示方法时：

1. 在 `I...View` 声明 `show...` 及具体参数类型。
2. Application 在数据准备完成后调用它。
3. PC View 把数据绑定到最小稳定 Page/Table/Dialog 模型。

不能先在 View 中随意增加回调，再用 `any` 或动态属性规避接口缺失。

## 八、局部修改如何避免过度扩散

- 只改布局：通常不改 API 和 borep，但要读取属性类型与 `I...View`。
- 只改默认值或 BO 规则：通常不改 View；检查页面是否有重复计算，若有应删除 View/Application 的重复职责。
- 只增加 Application 动作：如果不改变公共 BO 或 Repository 契约，不必修改 API。
- 只增加仓库远程方法：API 和 borep 必须同步，View 通常不感知，Application 负责调用。
- 只增加内部临时对象：若不会被其他模块、Repository 或服务契约使用，不要塞入公共 `api`。

判断标准不是“文件在哪”，而是这个变化是否改变了其他层可以依赖的契约。

## 九、编译与排错顺序

目标模块通常以 `bsapp/Console.ts` 作为 TypeScript 根文件，再通过三斜线引用串联 `borep`、`api` 和各功能。编译错误应按依赖层处理：

1. API 名称、接口继承和引用顺序。
2. borep 类是否完整实现 API，Repository 和 converter 是否识别类型。
3. bsapp 泛型、View 接口和注册方法。
4. bsui/c 控件类型、绑定路径和 Navigation 映射。

如果错误来自依赖模块声明，先确认当前模块是否使用了依赖模块尚未发布的源码能力。不要直接编辑 `3rdparty/<module>/index.d.ts`；应更新真实依赖模块并重新生成或刷新声明。

## 十、端到端完成检查

- 新增文件已进入所在层的 `index.ts` 引用链。
- 新 BO code 唯一，并被具体类、Repository、控件和服务映射一致使用。
- API 接口和 borep 实现逐项一致，没有接口字段存在而具体类遗漏。
- 可查询/保存对象在 Repository 接口和实现中同时存在方法。
- 可由远程结果构造的 BO 已在 `boFactory` 注册。
- 特殊枚举转换同时实现发送与接收方向，并保留 `super` 回退。
- Application 和 `I...View` 参数使用具体类型，没有用 `any` 掩盖断层。
- Function、Mapping、Console 和 PC Navigation 注册完整且 ID 不重复。
- View 只处理 PC 控件、模型、选择和事件，不直接保存或查询。
- 主对象、子表和孙表在 API、borep、Application、View 中保持相同归属。
- 新增用户可见文本使用国际化键。
- 目标模块构建通过，且没有触碰 `bsui/m`、`3rdparty` 或生成声明产物。
