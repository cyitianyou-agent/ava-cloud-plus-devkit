---
name: ava-cloud-plus-backend-development
description: 创建、修改或评审 AVA Cloud+ Java 后端业务模块，覆盖业务对象、集合关系、规则、跨对象逻辑、仓储、REST、初始化资源和测试；不适用于 TypeScript 前端、移动端或 ibas-framework 底层架构修改。
---

# AVA Cloud+ Java 后端开发

AVA Cloud+ 后端以业务对象为中心，不是普通的 Controller、Service、DAO 三层结构。一个可对外使用的标准业务对象通常沿以下链路贯通：

```text
datastructures XML
    ↓
Java BO 接口、实现和父子集合
    ↓
App/Svc 仓储契约与 BORepository 实现
    ↓
REST DataService 与 JAXB Resolver
    ↓
初始化资源、i18n 和测试
```

业务规则在 BO 属性变化时执行；需要随保存事务正向影响、反向撤销其他对象的逻辑，通过业务逻辑契约与 `BusinessLogic` 实现。目标是让数据模型、运行时对象、持久化、服务契约和资源注册保持一致，而不是机械修改每一层。

## 范围与红线

- 处理现有 `ibas.*` 业务模块的 Java 后端及其必要的 Maven、资源、REST 和测试代码。
- `ibas-framework` 只可作为只读参考，用于确认基类、生命周期、事务、权限、规则和序列化行为；不得修改它来适配某个业务需求。
- 不处理 TypeScript `api`、`borep`、`bsapp`、`bsui/c` 或 `bsui/m`，除非用户另行明确要求。
- 不把某个模块的行业定制、兼容代码、拼写历史或特殊单据流程提升为全局规范。
- 不把数据库访问绕过 `BORepository`，不在 REST 层复制持久化和业务逻辑。
- 不在源码、Skill 或结果报告中复制 `app.xml` 的连接信息、口令、客户数据或其他敏感值。
- 不修改编译产物、发布包或依赖缓存来掩盖源码问题。

## 开始前建立事实

先读目标模块本身，再决定修改面。至少确认：

1. 根 `pom.xml`、核心 JAR 子工程与 service WAR 子工程，以及模块间 Maven 依赖。
2. 目标 BO 对应的 `datastructures/ds_*.xml`、Java `bo/<name>/` 包、对象类型、主键、子表和孙表。
3. `IBORepository<Module>App`、`IBORepository<Module>Svc`、`BORepository<Module>` 的现有契约。
4. service 工程中的 `DataService`、`Resolver`，以及目标类型是否已经暴露和注册。
5. `MyConfiguration`、`i18n`、`initialization` 和相关测试中是否存在本功能的配置、关系或行为约束。
6. 邻近且形态相同的实现：简单对象对简单对象、主数据对主数据、单据对单据；有孙表时必须找有孙表的参照。

只有目标模块无法解释基类行为时，才读取 `ibas-framework` 中对应的最小源码。框架代码用于解释，不作为修改目标。

## 按任务读取规范

- 涉及模块结构、依赖或完整开发链路时，读 [模块结构与变更流程](references/module-architecture.md)。
- 新增或修改 BO、字段、枚举、子集合、默认值时，读 [业务对象与集合](references/business-objects.md)。
- 新增查询、保存、自定义远程方法或 REST 服务时，读 [仓储与 REST](references/repository-and-rest.md)。
- 涉及校验、计算、状态联动、库存/金额影响或跨对象更新时，读 [业务规则与跨对象逻辑](references/rules-and-logic.md)。
- 涉及配置、初始化数据、关系、国际化、Maven 或测试时，读 [资源、构建与验证](references/resources-and-validation.md)。

局部修复只读受影响规范及直接上下游；新增完整业务对象通常需要全部读取。

## 决定改动面

| 需求 | 通常涉及 |
| --- | --- |
| 新增或改变持久化字段、对象层级 | `datastructures` + BO 接口/实现/集合，并检查仓储、REST、初始化与客户端契约 |
| 只改默认值、属性校验或派生计算 | BO `initialize()` / `registerRules()` 或专用 `rules` 类，并补行为测试 |
| 新增标准查询与保存 | App/Svc 接口 + Repository + DataService + Resolver |
| 新增非 BO 返回值或专用查询 | `data` DTO/枚举 + App/Svc 接口 + Repository + DataService，按序列化需求更新 Resolver |
| 保存时影响其他对象 | 逻辑 Contract + `@LogicContract` 服务 + BO `getContracts()` + 正向/反向测试 |
| 多对象原子操作 | Repository 自定义方法 + 显式事务边界；跨仓储共享同一事务 |
| 新增配置、模块注册或对象关系 | `MyConfiguration` + `initialization` 对应资源 + i18n/测试 |
| 只改 REST 路径或认证参数 | DataService，并核对 Svc 契约、token 处理和现有调用方 |

不要为追求“完整链路”改动没有受影响的文件，但任何契约变化都必须检查直接上下游。

## 生成骨架与手工代码

`datastructures` 模型可被项目的转换模板用于生成 BO、仓储和 REST 标准骨架，但成熟模块会在骨架上加入大量手工逻辑。

- 若目标工程已有明确的生成命令且用户允许生成，先保留工作树差异，生成后逐文件审查；不得接受对无关对象、业务规则、集合关联或自定义仓储方法的覆盖。
- 若没有可验证的生成入口，不臆造命令。按同模块、同对象类型的现有文件做最小修改。
- 生成模板中的集合关联占位逻辑不是完成品；父子键、孙表 `ItemId`、查询条件和父属性传播必须结合真实层级实现。
- 不仅修改生成后的 Java 而遗漏数据结构 XML；也不只修改 XML 而假设运行时代码已经自动同步。
- 历史代码与当前模板不一致时，以目标模块当前可运行的约定为准，并保持改动最小。

## 默认实施顺序

1. 明确对象类型、数据关系、业务状态和对外契约。
2. 更新数据结构及 Java BO 契约，保持属性名、映射、类型和集合层级一致。
3. 补齐集合关联、默认值、规则和业务逻辑契约。
4. 更新 App/Svc 仓储接口和 Repository，实现权限、错误与事务语义。
5. 更新 REST 端点和 JAXB 注册；只在需要时增加 DTO、配置和初始化资料。
6. 增加针对可观察业务行为的测试，覆盖新建、修改、删除/取消、正向影响、反向撤销和失败回滚中与需求相关的场景。
7. 从核心 JAR 到 service WAR 执行目标模块的最小充分构建和测试，并检查最终差异。

局部修复可以从直接故障点开始，但完成前要沿链路上下各核对一次。

## 完成标准

- 没有修改 `ibas-framework`，且没有把框架职责复制到业务模块。
- 数据结构、BO 接口、实现、集合和数据库映射一致；主子键与孙表关联可查询、可传播。
- `initialize()` 保留 `super.initialize()`，默认值和对象编码符合目标模块现行约定。
- 属性规则注册完整；跨对象逻辑具备稳定契约、正向 `impact`、反向 `revoke` 和同事务访问。
- App 接口使用 BO 接口类型，Svc/REST 使用可序列化具体类型，Repository 同时实现两套契约。
- 标准操作委托框架 `fetch`/`save`；自定义操作正确处理 token、`OperationResult`、异常与事务。
- DataService、Resolver、i18n、initialization 和 Maven 依赖没有遗漏或无关扩张。
- 测试验证业务结果和回滚语义，而非只验证方法可以被调用。
- 核心 JAR 与受影响的 service WAR 构建通过，最终差异无凭据、生成物或无关格式化。
