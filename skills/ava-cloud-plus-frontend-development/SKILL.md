---
name: ava-cloud-plus-frontend-development
description: Use when 需要创建、修改或评审 AVA Cloud+ TypeScript PC 前端业务模块，涉及 api、borep、bsapp、bsui/c、业务对象、仓库、Application 或 View；不适用于移动端或 Java 后端。
---

# AVA Cloud+ 前端业务模块开发

使用本 Skill 完成一个业务功能时，四层代码应形成同一条可追踪的契约链：

```text
api 公共契约
    ↓
borep 业务对象与仓库运行时
    ↓
bsapp 应用编排与 View 接口
    ↓
bsui/c PC 端界面实现
```

目标不是机械地让四个目录都有改动，而是保证本次需求涉及的契约、运行时、Application 和 PC View 相互一致，没有把职责放错层，也没有遗漏引用、工厂、服务或导航注册。

## 开发流程位置

本 Skill 消费已经确认的业务模型；涉及远程调用时还必须消费已经稳定的服务端契约：

```text
已确认模型与代码候选
    ├── Java 后端契约（远程调用变化时先稳定）
    └── ava-cloud-plus-frontend-development（当前）
                    ↓
              静态与构建门禁
                    ↓
     数据库落地（按需）→ 最终跨层验收
```

纯 PC 页面、绑定或本地应用行为可以直接进入本阶段；跨前后端功能先稳定受影响的后端 App/Svc 与 REST 契约。完成后交付四层契约、注册入口、语言资源和 TypeScript 构建结果，由交付编排汇总构建门禁，最终验收再核对数据库与实际业务行为。

## 范围与红线

- 处理业务模块中的 `api`、`borep`、`bsapp`、`bsui/c` 及其必要的模块入口、语言资源和 TypeScript 引用。
- 不读取、不生成、不修改 `bsui/m`；本 Skill 的 UI 规范只针对 PC 端。
- 不处理 Java 后端、数据库脚本或服务端业务逻辑，除非用户另行明确要求。
- `api` 是可被其他前端模块引用的 TypeScript 公共契约，不是 REST 控制器或后端接口实现。
- 代码依赖方向只能是 `api ← borep ← bsapp ← bsui/c`，也就是右侧层可以使用左侧层，左侧层不能反向依赖右侧层。BO 不得引用 Application 或 View。
- Repository 查询、保存和远程方法由 `borep` 提供，由 `bsapp` 调用；View 不直接承担业务持久化。
- 使用全局 `namespace`、三斜线引用和 `outFile` 编译模式，不改造成 ESM。
- 不修改当前模块或依赖模块的 `3rdparty` 声明产物。
- 不把一个模块的定制逻辑、行业覆盖或历史兼容写法提升为全局规范。

## 规则强度

1. **硬约束**：层间依赖方向、接口与实现一致、BO 基类和集合归属、Repository 契约、MVP 边界、注册入口、PC 范围。
2. **标准骨架**：常规 BO、Repository、List/Edit/Choose/View Application 和 PC View 的默认结构。
3. **条件变体**：孙表、用户字段、自定义远程方法、服务代理、行业覆盖、树表和复杂页面；只在数据或业务契约明确要求时使用。
4. **业务特例**：局部计算、特殊转换、动态列和专用弹窗；不得反向改变标准层次。

## 开始前必须建立的事实

先读取目标模块自己的代码，不能只凭文件名生成：

1. 模块 `tsconfig.json`、`api/index.ts`、`borep/index.ts`、`bsapp/Console.ts` 和 `bsui/c/Navigation.ts`。
2. 目标 BO 在 `api/bo` 的接口、`borep/bo` 的实现以及 Repository 的查询保存方法。
3. 目标功能目录中的 Application、`I...View` 和 PC View。
4. 跨模块类型、选择服务或 Repository 控件所依赖的 `3rdparty/<module>/index.d.ts`。
5. 需求究竟改变公共契约、BO 运行时、应用流程、界面，还是其中若干层。

读取结果至少列出：BO 类型、主键、子集合、Repository 方法、Application 基类、View 事件、`show...` 方法、功能/服务映射和 PC 导航映射。

## 按任务读取规范

### 跨层开发或新增完整功能

先读 [四层联动与开发流程](references/module-lifecycle.md)，再按实际改动读取下面各层规范。新增 BO 或标准功能通常四份都要读；局部修复只读被影响层及其直接上下游。

### `api`

读取 [api 公共契约规范](references/api-layer.md)，用于模块元数据、BO 编码、枚举、BO 接口、Repository 接口、服务契约和 `api/index.ts`。

### `borep`

读取 [borep 业务对象与仓库规范](references/borep-layer.md)，用于具体 BO、集合、默认值、业务规则、Repository、DataConverter、BOFactory 和 `borep/index.ts`。

### `bsapp`

先读 [bsapp 公共契约](references/bsapp-layer.md)，再按页面能力读取 [ListApp](references/bsapp-list.md)、[EditApp](references/bsapp-edit.md) 或 [ChooseApp、ViewApp 与服务映射](references/bsapp-services.md)。自定义应用只读取直接相关的公共约束和服务映射。

### `bsui/c`

必读 [PC View 通用架构与风格](references/common-conventions.md)，再只读取当前页面类型：

- [ListView 规范与完整骨架](references/list-view.md)
- [EditView 规范与完整骨架](references/edit-view.md)
  - BO 存在真实“主表 → 子表 → 孙表”集合并需要同页维护时，再读 [包含孙表的 EditView](references/nested-child-edit-view.md)
- [ChooseView 规范与完整骨架](references/choose-view.md)
- [ViewView 规范与完整骨架](references/view-view.md)

涉及常规 View 数据绑定时读 [JSONModel 基础绑定](references/json-model-bindings.md)；只有 Dialog、Popover、命名模型、组合模型或特殊刷新时再读 [JSONModel 高级模式](references/json-model-advanced.md)。基础字段先读 [基础控件与数据类型](references/controls-and-bindings.md)；外部 BO 或值帮助再读 [Repository 与选择控件](references/repository-controls.md)；ViewView、状态、所有人、组织或服务按钮再读 [只读、状态与服务控件](references/display-and-state-controls.md)。字段同时支持输入搜索和弹窗选择时读 [可搜索选择输入框](references/searchable-inputs.md)。只有非标准页面、查询面板或行业覆盖才读 [非标准页面与行业扩展](references/custom-and-extensions.md)。

## 决定需要改哪些层

| 需求变化 | 通常涉及 |
| --- | --- |
| 新增公开 BO、属性、枚举或集合 | `api` + `borep`，并检查 `bsapp`、View 和转换器 |
| 只调整 BO 默认值、规则或集合行为 | `borep`，检查现有 Application/View 是否依赖旧行为 |
| 新增查询、保存或远程仓库方法 | `api/BORepository.ts` + `borep/BORepository.ts`，调用方在 `bsapp` |
| 新增 List/Edit/Choose/View 功能 | `bsapp` + `bsui/c`，并检查 BO/Repository 契约是否已存在 |
| 新增选择或链接服务 | `bsapp` Application + Mapping + Console 注册 + PC Navigation/View |
| 只改 PC 布局或控件 | `bsui/c`，但必须先核对 `I...View` 和 BO 属性类型 |
| 修改 View 事件参数或 `show...` 方法 | 先改 `bsapp` 接口与 Application，再同步 `bsui/c` |
| 新增业务对象编码 | `api/Data.ts` + 具体 BO 的 `BUSINESS_OBJECT_CODE` + BOFactory 注册 |
| 新增可序列化枚举 | `api/Data.ts`，并检查 `borep/DataConverter.ts` 是否需要双向转换 |

不要为了“层次完整”去改没有受到影响的文件；也不能因为界面先能运行，就省略已经发生变化的公共接口、工厂或服务注册。

## 实施顺序

对新增或跨层功能，默认按依赖方向实施：

1. 明确 BO 形态和对外契约。
2. 更新 `api`，让属性、集合和 Repository 方法先有稳定类型。
3. 更新 `borep`，实现 BO、集合、转换和仓库调用，并完成工厂注册。
4. 更新 `bsapp`，实现查询、保存、选择、业务动作以及 View 接口。
5. 更新 `bsui/c`，只根据 `I...View` 契约绘制和绑定 PC 页面。
6. 更新各层 `index.ts`、`Console.ts`、服务 Mapping、PC `Navigation.ts` 和语言资源。
7. 运行目标模块构建，从最底层错误开始修复，不用 `any` 或绕过注册掩盖断链。

局部修复不强制从第一层开始，但完成前必须沿链路向上、向下各检查一次直接影响。

## 自包含要求

- 本 Skill 的架构、代码骨架和控件示例全部位于本目录。
- 不依赖个人 profile、外部网页、绝对路径文档或其他 Skill 才能理解规范。
- 实施时读取目标模块源码，是为了取得本次功能的真实名称、类型和契约，不属于外部规范依赖。

## 完成标准

- 四层职责和依赖方向正确，没有 BO 引用 Application、View 访问 Repository 等倒置。
- API 接口与 borep 实现的属性、集合、参数和返回类型一致。
- BO 编码、具体类、Repository、转换器及 BOFactory 注册完整。
- Application 使用具体 BO 和 Repository，实现错误、busy、消息与刷新流程。
- `I...View` 的事件和 `show...` 方法与 Application、PC View 完全一致。
- Function、服务 Mapping、Console、各层 `index.ts` 和 PC Navigation 没有漏注册或重复 ID。
- PC View 符合页面类型、控件和 JSONModel 规范；未触碰移动端。
- 国际化键、BO 属性名、Repository 方法名和业务对象编码在各层拼写一致。
- 目标模块 TypeScript 构建通过；没有修改 `3rdparty` 或生成产物来规避错误。

## 阶段结果

按 `status`、输入模型与后端契约、修改文件、TypeScript 契约与交互增量、构建证据、未解决项及建议下一阶段的顺序报告。`status` 只使用 `completed`、`partial`、`blocked` 或 `skipped`；前端完成不等于完整功能验收通过。
