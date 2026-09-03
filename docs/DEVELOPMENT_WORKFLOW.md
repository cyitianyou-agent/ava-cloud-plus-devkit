# AVA Cloud+ 完整功能开发流程

本流程用于需要跨业务模型、Java 后端、TypeScript PC 前端、数据库或报表交付的功能。局部修复不必机械执行全部阶段，但必须检查直接上下游。

## 流程拓扑

```text
0. delivering-ava-cloud-plus-feature
   建立业务目标、范围、验收条件、受影响层和环境门禁
       ├── 业务功能主链
       │   1. generating-ava-cloud-business-objects（模型变化或待校验时）
       │      创建、最小更新或校验修正最终 Domain XML
       │          ↓
       │   2. generating-ava-cloud-code（需要机械投影时）
       │      在临时目录生成代码候选并安全合并真实模型增量
       │          ├── 3a. ava-cloud-plus-backend-development
       │          └── 3b. ava-cloud-plus-frontend-development
       │                          ↓
       │      静态与构建门禁：XML、Java、service WAR 和 TypeScript
       │                          ↓
       │   4. evolving-ava-cloud-plus-database（按需且需授权）
       │      落地结构、兼容 SQL、BO 元数据和初始化数据 ──┐
       │      无数据库变化时按范围跳过 ───────────────────┤
       └── 报表旁路（报表需求才进入）
           3c. converting-crystal-reports-to-jasper
               Report IR → JasperReports 7.x JRXML → 静态检查 ─┤
                                                               ↓
5. verifying-ava-cloud-plus-feature
   汇总主链与可选旁路，对照最初契约执行一次最终验收
```

后端和前端是共享模型后的两条实现分支。前端涉及 REST、Repository 或服务返回契约时，先稳定对应后端契约；纯 PC 页面、绑定或本地应用行为可以直接进入前端。报表是可选旁路，不阻塞无关业务模块开发。

## 阶段所有权与交接

| 阶段 | 拥有的产物 | 必须交给下游的结果 |
| --- | --- | --- |
| 交付编排 | 交付契约和阶段状态 | 验收条件、受影响层、确认事实和环境条件 |
| 业务模型 | 最终 `Domain` XML 语义 | XML、真实模型增量、推断和待确认项 |
| 代码生成 | 候选代码和最小合并 | 候选目录、合并文件、跳过项和模板遗留项 |
| Java 后端 | Java 运行时与服务契约 | BO/Repository/REST/行为、测试和构建结果 |
| TypeScript 前端 | TypeScript PC 契约与界面 | 四层实现、注册、语言资源和构建结果 |
| 报表迁移 | Report IR 与 JRXML | 静态对照证据及未验证的编译、数据、版式项 |
| 数据库 | 已授权环境中的落地结果 | 动作、结构、元数据和数据核验，不含凭据 |
| 最终验收 | 验收矩阵和判定 | 证据、未运行项、剩余风险和责任阶段 |

每个阶段统一报告 `status`、输入基线、产出或修改文件、真实语义增量、验证证据、未解决项和下一阶段。`status` 使用 `completed`、`partial`、`blocked` 或 `skipped`；单阶段 `completed` 不等于完整功能通过。

## 何时跳过阶段

- 不改变持久化模型：跳过业务模型、代码生成和数据库落地。
- 模型已确认且目标代码完整：跳过代码生成，直接最小修改对应实现。
- 纯后端规则或 Logic：通常跳过前端和数据库，但检查对外错误与返回语义。
- 纯 PC 布局：只执行前端、相关构建和验收，不修改 API、后端或数据库。
- 没有报表需求：跳过 Crystal/Jasper 分支。
- 只有 XML 或代码审阅：不因完整流程存在而自动连接数据库。

当前插件不实现或验收 `bsui/m`。生成模板出现移动端候选时只记录为跳过，不合并到正式模块。

## 构建与数据库门禁

数据库落地前至少满足：

1. 最终 XML 的模型、字段、键和引用完整。
2. 受影响 Java 核心工程能够测试或编译。
3. service WAR 能验证 App/Svc、REST 与序列化类型。
4. 受影响 TypeScript 层按依赖顺序构建通过。
5. 最终差异没有未审阅覆盖、凭据、移动端候选和无关生成物。

该门禁由交付编排汇总业务功能主链的实现证据，不调用最终验收 Skill 做重复构建。报表旁路单独执行 JRXML 与 Report IR 静态检查，不阻塞无关数据库落地。

数据库目标、公司标记和执行范围未明确授权时，到此停止数据库执行，但继续记录静态与构建结果。不能把这种状态写成完整功能验收通过。

## 数据库执行路径

| 输入或目标 | 推荐路径 |
| --- | --- |
| 开发期最终 XML | core `ds` |
| 最终模块 JAR 的结构与初始化 SQL | core `dsJar` |
| 独立 SQL 编排 XML | core `sql` |
| 使用 `app.xml` 解析数据库配置 | bobas `ds` |
| 导入初始化业务数据 | bobas `init` |

经典 DS 模板主要负责创建缺失结构和登记 BO 元数据。既有字段的类型、长度、默认值、重命名、删除或数据回填需要显式兼容 SQL 和单独核验。

## 问题返回规则

- XML、对象关系、键、类型或映射错误：返回业务模型阶段。
- 候选生成物或语义合并错误：返回代码生成阶段。
- Java BO、Repository、REST、规则或事务错误：返回后端阶段。
- TypeScript API、borep、Application、PC View 或注册错误：返回前端阶段。
- Report IR、JRXML、参数、SQL 或布局语义错误：返回报表迁移阶段。
- 表结构、BO 元数据、SQL 或初始数据错误：返回数据库阶段。

修复上游契约后，重新执行直接受影响的下游门禁。最终完成以验收条件拥有必要证据为准，不以某个生成、构建、数据库或报表命令成功为准。
