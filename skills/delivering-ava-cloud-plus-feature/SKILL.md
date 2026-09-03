---
name: delivering-ava-cloud-plus-feature
description: Use when 需要从一项 AVA Cloud+ 业务需求出发，协调业务模型、生成代码、Java 后端、TypeScript PC 前端、数据库、可选报表和最终验收；不适用于只改一个已明确文件的局部任务。
---

# 交付 AVA Cloud+ 完整功能

## 目标

把业务需求转换为可追踪的交付契约，按依赖关系路由专用 Skill，并用阶段证据判断整体状态。本 Skill 不复制各阶段实现规范，也不直接拥有 XML、Java、TypeScript、数据库或 JRXML 产物。

完整流程是有条件分支，不是要求每个任务机械经过全部阶段：

```text
交付契约
    ├── 业务功能主链
    │   业务模型确认 → 代码候选 → Java / TypeScript PC
    │                                  ↓
    │                            静态与构建门禁
    │                                  ↓
    │                     数据库落地或按范围跳过 ──────┐
    └── 报表旁路（报表需求才进入）
        Crystal RPT/RptToXml → JRXML → 报表静态检查 ──┤
                                                      ↓
                                                 最终跨层验收
```

前端涉及 REST、Repository 或服务返回契约时，先稳定对应后端契约；纯 PC 页面、绑定或本地应用行为可以在模型确认后直接进入前端阶段。

## 开始前建立交付契约

读取目标项目的 `AGENTS.md` 和版本控制状态，再按 [交付契约与阶段门禁](references/delivery-contract.md) 建立本轮契约。至少明确业务目标、范围、可观察验收条件、受影响层、目标模块和现有改动。

只有缺失信息会改变业务模型、目标模块、数据库目标、报表输入或最终判定时才询问用户。交付契约中已确认的模块简称、路径和模型事实可直接交给后续 Skill，不要求后续阶段重复询问。

## 阶段所有权

| 阶段 | 唯一拥有的决策或产物 | 发现上游问题时 |
| --- | --- | --- |
| 业务对象 | `Domain` XML 的结构、语义、映射和真实模型增量 | 在本阶段修正并重新确认 |
| 代码生成 | Excel/XML 转换、候选代码和最小语义合并 | 返回业务对象阶段，不自行定义模型语义 |
| Java 后端 | Java BO、规则、Logic、Repository、REST、资源和测试 | 返回模型或生成阶段 |
| TypeScript 前端 | `api`、`borep`、`bsapp`、`bsui/c`、注册和语言资源 | 返回后端契约、模型或生成阶段 |
| 报表迁移 | Report IR、JRXML 和静态转换问题清单 | 返回报表输入确认或转换阶段 |
| 数据库 | 已授权环境中的结构、元数据、SQL 和初始化数据落地 | 返回模型、制品或数据库编排阶段 |
| 最终验收 | 验收证据、逐项结论和整体 `verdict` | 指向拥有缺陷产物的阶段，不在验收阶段顺手修复 |

## 阶段路由

1. 新对象、新模型、字段、索引、映射或关系变化，以及 Excel 转换模型的校验修正，使用 `generating-ava-cloud-business-objects`。
2. 已确认模型需要投影为 Java 或 TypeScript 骨架时，使用 `generating-ava-cloud-code`。已有代码完整时可以跳过生成。
3. 使用 `ava-cloud-plus-backend-development` 完成受影响的 Java 后端；使用 `ava-cloud-plus-frontend-development` 完成受影响的 TypeScript PC 前端。两者按实际契约依赖排序。
4. 需求包含 Crystal RPT/RptToXml 迁移时，使用 `converting-crystal-reports-to-jasper` 形成独立旁路产物；它不阻塞无关业务模块开发。
5. 汇总各实现阶段的静态检查、测试和构建结果，形成构建门禁。失败时返回产物所属阶段修复。
6. 模型、兼容 SQL 或初始化内容变化时，使用 `evolving-ava-cloud-plus-database`。目标环境和范围未明确授权时只规划，不连接数据库。
7. 所有可执行阶段完成后，使用 `verifying-ava-cloud-plus-feature` 对照原始契约进行一次最终验收。

## 构建门禁

数据库落地前至少确认最终 XML 可解析、受影响 Java 核心工程与 service WAR 可构建、受影响 TypeScript 层可构建，并且最终差异没有未审阅覆盖、凭据和无关生成物。

构建门禁由交付 Skill 汇总模型、生成、后端和前端阶段已经产生的证据；不把最终验收 Skill 当作数据库前的重复构建步骤。

## 变更传播

- XML 的模型、字段或映射变化，重新检查生成代码、Java、TypeScript 和数据库范围。
- Java App/Svc 或 REST 契约变化，重新检查前端 Repository 与调用方。
- TypeScript `api` 或 `I...View` 变化，重新检查实现、Application、PC View 和注册入口。
- 数据库结构或初始化数据变化，重新执行后置核验和相关集成测试。
- 报表参数、SQL、字段或布局语义变化，重新执行 Report IR 到 JRXML 的静态对照。
- 上游假设失效时更新交付契约，并重新判断直接下游范围。

## 完成与交接

每个阶段按统一结构返回：`status`、输入基线、产出或修改文件、真实语义增量、验证证据、未解决项和建议下一阶段。`status` 只使用 `completed`、`partial`、`blocked` 或 `skipped`。

最终完成要求每项验收条件都有实现位置与证据。验收条件所必需的数据库、服务、浏览器或 Jasper 运行环境缺失时判定 `partial`，不能写成完整交付通过；非必要环境缺失只列为未运行项。
