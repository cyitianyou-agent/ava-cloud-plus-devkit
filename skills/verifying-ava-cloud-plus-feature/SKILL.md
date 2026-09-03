---
name: verifying-ava-cloud-plus-feature
description: Use when 需要在实现阶段和数据库阶段结束后，对 AVA Cloud+ 功能执行最终跨层验收，覆盖 datastructures、Java、REST、TypeScript PC、数据库、业务行为及交付契约中的可选 Jasper 报表；不适用于单独运行构建门禁或检查一个文件。
---

# 验证 AVA Cloud+ 完整功能

## 目标与边界

以交付契约中的业务目标和验收条件为基准，判断模型、Java、REST、TypeScript PC、数据库、业务行为和可选报表是否形成同一条可用链路。本 Skill 只收集证据和作出判定；发现问题时指出断点与责任阶段，不在验收阶段顺手修改产物。

本 Skill 只在各实现阶段已经交付结果后执行一次最终验收。数据库前的静态与构建门禁由交付编排汇总各阶段证据，不重复调用本 Skill。

验收条件所必需的数据库、服务、浏览器或 Jasper 环境未授权或不可用时，保留可复现的未运行项并判定为 `partial`，不能报告完整通过；非必要环境缺失只列为未运行项。

## 开始前收集证据

读取目标项目 `AGENTS.md`、版本控制差异、原始需求或交付契约，以及各阶段统一结果。确认：

- 最终 `Domain` XML 和真实模型增量；
- Java BO、Repository、REST、资源、测试和构建结果；
- TypeScript `api`、`borep`、`bsapp`、`bsui/c`、注册和构建结果；
- 数据库是否应用本次结构、SQL 和初始化内容；
- 交付契约是否包含 Crystal/Jasper 报表，以及其 Report IR、JRXML 和静态检查结果；
- 哪些条件需要数据库、服务、浏览器或 Jasper 运行环境。

按 [跨层验收矩阵](references/acceptance-matrix.md) 选择与契约有关的检查，不为未受影响层制造工作。

## 验收顺序

1. **范围与差异**：区分用户原有改动、本次实现、临时候选和构建产物；排除凭据、`3rdparty` 修改、无关格式化和未审阅覆盖。
2. **模型与代码契约**：从最终 XML 逐项核对 Java 与 TypeScript 的名称、映射、类型、对象 code、主子键、集合、查询保存和序列化注册。
3. **服务与 PC 界面链路**：核对 App/Svc Repository、REST、Resolver、前端 Repository、Application、`I...View`、PC View、Console、Mapping、Navigation 和语言资源。
4. **测试与构建证据**：复核模型、Java 核心、service WAR、TypeScript 各层和最终差异的实际命令及结果；证据缺失时运行目标项目允许的最小充分验证。
5. **数据库与业务行为**：已授权并应用时验证结构、BO 元数据、初始化结果，以及需求对应的查询、保存、重载、规则、影响、撤销和回滚行为。
6. **可选报表**：契约包含报表时，对照 Report IR 验证 JRXML 参数、SQL、字段、分组、区段、元素、UUID、7.x 格式和敏感信息。编译、数据或版式没有运行证据时分别列为未验证。
7. **逐项判定**：为每条验收条件记录涉及层、证据、结论、未运行项和责任阶段。

## 判定规则

- **通过**：验收条件的全部必要层都有一致实现和成功证据。
- **部分通过**：静态契约和可执行验证通过，但必要的数据库、服务、浏览器或 Jasper 运行验证因明确环境条件未执行。
- **失败**：存在契约断链、构建失败、数据库不一致、报表静态转换错误或业务行为不符。
- **不适用**：经交付契约确认该层不受影响；不能用它替代缺少实现。

生成器成功、单层编译成功、JRXML 已生成、HTTP 返回成功或页面可以打开，都不足以单独判定完整功能通过。

## 责任返回

| 问题 | 返回阶段 |
| --- | --- |
| XML、对象关系、键或映射 | 业务对象 |
| 候选代码或增量合并 | 代码生成 |
| Java BO、规则、Logic、Repository、REST | Java 后端 |
| TypeScript 契约、Application、PC View、注册 | TypeScript 前端 |
| 表结构、元数据、SQL、初始化数据 | 数据库 |
| Report IR、JRXML、参数、SQL、布局语义 | 报表迁移 |

修复后只重跑直接受影响的下游门禁与验收项。

## 阶段结果

按 `status`、`verdict`、验收输入、逐项验收矩阵、证据、未运行项、失败责任阶段和剩余风险报告。

- `status` 表示验收工作是否执行完：`completed`、`partial`、`blocked` 或 `skipped`；仅当交付编排判定整个验收阶段不在任务范围且未运行时使用 `skipped`。
- `verdict` 表示交付质量：`passed`、`partially-passed` 或 `failed`。

所有计划检查均已执行时，即使发现缺陷，`status` 也可以是 `completed`，同时 `verdict` 为 `failed`。环境导致必要检查未运行时，`status` 为 `partial`，`verdict` 至多为 `partially-passed`。
