# AVA Cloud+ 完整功能开发流程

本流程用于需要跨业务对象、Java 后端、TypeScript 前端和数据库交付的功能。局部修复不必机械执行全部阶段，但必须检查直接上下游是否受到影响。

## Skill 顺序

```text
0. delivering-ava-cloud-plus-feature
   建立业务目标、范围、模型变化、验收条件和环境门禁
       ↓
1. generating-ava-cloud-business-objects
   生成或最小更新最终 Domain XML
       ↓
2. generating-ava-cloud-code
   在临时目录生成代码候选并把真实模型增量安全合并
       ↓
3. ava-cloud-plus-backend-development
   完成 Java BO、规则、Logic、Repository、REST、资源和测试
       ↓
4. ava-cloud-plus-frontend-development
   完成 api、borep、bsapp、bsui/c、注册和语言资源
       ↓
   构建门禁：XML、Java、service WAR 和 TypeScript 通过
       ↓
5. evolving-ava-cloud-plus-database
   使用 btulz.transforms 落地结构、初始化 SQL 和必要初始数据
       ↓
6. verifying-ava-cloud-plus-feature
   对照验收条件验证跨层契约、数据库和实际业务行为
```

`converting-crystal-reports-to-jasper` 是独立的报表迁移分支。需求包含报表时，由交付编排 Skill 把报表产物和验证项合并进最终验收，但报表迁移不阻塞无关的业务对象开发阶段。

## 阶段输入与输出

| 阶段 | 主要输入 | 必须交付给下游的结果 |
| --- | --- | --- |
| 交付编排 | 业务描述、目标模块、范围 | 交付契约、验收条件、受影响层和环境条件 |
| 业务建模 | 自然语言或目标 XML | 最终 XML、模型增量、推断和待确认语义 |
| 代码生成 | 最终 XML 或 Excel | 候选目录、合并文件、跳过项和模板遗留项 |
| 后端开发 | 模型、生成骨架、业务规则 | 稳定 BO/Repository/REST 契约、测试和构建结果 |
| 前端开发 | 模型、后端契约、用户流程 | 四层前端实现、注册、语言资源和构建结果 |
| 数据库落地 | 最终 XML、模块 JAR、SQL/数据资源 | 动作结果、结构与元数据后置核验，不含凭据 |
| 跨层验收 | 原始验收条件和全部产物 | 验收矩阵、证据、未运行项和修复责任阶段 |

## 何时跳过阶段

- 需求不改变持久化模型：跳过业务建模、代码生成和数据库落地。
- 模型已经确认且目标代码完整：可跳过代码生成，直接按专用开发 Skill 最小修改。
- 纯后端规则或 Logic：通常跳过前端与数据库，但检查对外错误和返回语义是否变化。
- 纯 PC 布局：只执行前端阶段和相关构建、验收，不修改 API、后端或数据库。
- 只有 XML 或代码审阅：不因完整流程存在而自动连接数据库。

## 构建门禁与数据库门禁

数据库落地前至少满足：

1. 最终 XML 的模型、字段和引用完整。
2. 受影响 Java 核心工程能够测试或编译。
3. service WAR 能够验证 App/Svc、REST 与序列化类型。
4. 受影响 TypeScript 层按依赖顺序构建通过。
5. 最终差异没有未审阅覆盖、凭据和无关生成物。

数据库目标、公司标记和执行范围未明确授权时，到此停止数据库执行，但继续报告已完成的静态与构建验证。不能把这种状态写成完整功能验收通过。

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

- XML、对象关系或类型错误：返回业务对象建模阶段。
- 候选生成物与真实增量不符：返回代码生成阶段。
- BO、Repository、REST、规则或事务错误：返回后端阶段。
- API、borep、Application、View 或注册错误：返回前端阶段。
- 表结构、BO 元数据、初始化 SQL 或初始数据错误：返回数据库阶段。
- 修复上游契约后，重新执行所有直接受影响的下游检查。

最终完成的判定标准是验收条件拥有跨层证据，不是某一个生成、构建或数据库命令退出成功。

