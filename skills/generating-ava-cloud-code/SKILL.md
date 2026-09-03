---
name: generating-ava-cloud-code
description: Use when 需要从已确认的 AVA Cloud+ 业务对象 Excel 或 datastructures XML 调用 btulz.transforms 生成 Java 与 TypeScript PC 代码候选，或把对象、模型、子表和字段对应的生成结果安全合并到已有模块。
---

# 生成 AVA Cloud+ 代码框架

## 目标与边界

把已确认的业务模型机械投影为 Java 和 TypeScript PC 候选代码，并安全合并到目标模块。所有工具输出先进入独立临时目录；已有模块中的人工实现、稳定标识和项目配置优先。

本 Skill 不拥有模型语义。没有可用 `Domain` XML、用户要求根据自然语言改变模型，或 Excel 转换结果尚未确认时，先使用 `generating-ava-cloud-business-objects` 创建、更新或校验 XML，再返回代码生成。

当前插件的实现与验收链只覆盖 PC 前端 `bsui/c`。即使模板产生 `bsui/m`，也不得将移动端候选合并到正式模块；把它列为超出范围的跳过项。

## 执行门禁

开始前确认输入 Excel/XML、正式模块根目录、`btulz.transforms.core-*.jar` 或模板目录，以及用户需要的 Java、TypeScript 和 `bsui/c` 范围。能从会话、上游交付契约或目标项目可靠取得时直接使用；不能可靠判断且会改变结果时询问用户。

目标位于现有项目时，读取其 `AGENTS.md`、后端 `pom.xml` 和前端 `tsconfig.json`。保留工作树已有改动，不修改 `3rdparty` 声明文件。

## 工作流

1. 创建独立临时目录，分别建立 Excel XML 输出目录和代码输出目录；正式模块目录禁止直接传给任何 `-OutputFolder`。
2. 输入为 Excel 时读取 [Excel 转换命令](references/btulz-excel-command.md)，执行 `excel` 并确认至少生成一个非空 XML。
3. 对 Excel 输出目录或多个 XML 运行 `scripts/merge_domain_xml.py <输入目录> <汇总 XML>`，形成单一、去重的候选 XML；冲突时停止。
4. 把候选 XML 交给 `generating-ava-cloud-business-objects` 的“校验转换结果”模式。只有它确认 Domain、模型、键、映射和关系后，才把结果作为代码生成输入；本阶段不自行修正模型语义。
5. 增量任务从用户说明、版本控制差异或旧 XML 确定真实模型增量；不能把候选与手写代码的全部差异视为本次需求。
6. 读取 [代码生成命令](references/btulz-code-command.md)，从目标项目提取稳定参数。已有模块沿用现有 `GroupId`、`ArtifactId`、版本、版权和 `ProjectId`。
7. 对已确认 XML 执行 `code`。模板尚未释放时只在临时工作目录使用 `-Release`。
8. 检查退出码、日志、未替换模板标记和输出结构，并把候选根目录与正式模块根目录对齐。
9. 运行 `scripts/inventory_generated.py <候选根目录> <正式模块根目录>` 盘点 `new`、`changed`、`same` 和 `target-only` 文件；脚本只读。
10. 目标为空时，确认没有源码、构建文件或有效配置后复制完整候选，但不覆盖版本控制元数据。目标已有代码时，读取 [增量合并规则](references/incremental-merge.md)，只复制本次新增的对象专属文件，并对共享或同名文件做最小语义合并。
11. 回查模型增量，排除随机 ID、模板版本、格式化、已有逻辑回退、移动端候选和用户未要求的脚手架。
12. 运行生成阶段可直接证明的静态检查和目标项目构建；业务规则、专用仓储、页面交互和运行验收交给相应开发及最终验收阶段。
13. 仅删除本次创建且已确认的临时路径；用户要求审阅候选时保留并报告。

## 安全边界

- `CodeTransformer` 会直接截断同名文件，已有模块中禁止全量覆盖。
- 候选文件在目标中缺失，不代表它必然属于本次模型增量。
- 不用生成器重新序列化的 XML 覆盖用户维护的源 XML。
- 已有应用 ID、模块 `ProjectId`、对象代码、命名空间、依赖版本和自定义逻辑保持不变。
- `-Domains` 指向目录时只读取直属文件；同名 Domain 会合并但不替对象或模型去重。
- Excel 输出是候选模型；必须经过业务对象阶段确认后才允许生成或复制代码。
- 模板 `TODO` 不等于已完成功能，应交给后端或前端阶段实现或列为未解决项。

## 阶段结果

按以下顺序报告：

1. `status`：`completed`、`partial`、`blocked` 或 `skipped`；
2. 原始输入、已确认 XML、工具/JAR 和模板来源；
3. 临时候选根目录与正式目标根目录；
4. 新增、语义合并、跳过和保留的文件；
5. 真实模型增量对应的代码变化；
6. 静态检查、构建命令和结果；
7. 模板遗留项，以及建议进入后端、前端或停止的原因。
