---
name: generating-ava-cloud-code
description: Use when 需要从 AVA Cloud+ 业务对象 Excel 或 datastructures XML 调用 btulz.transforms 生成 Java 与 TypeScript 代码框架，或把新增对象、模型、子表、字段对应的生成结果安全增量合并到已有模块。
---

# 生成 AVA Cloud+ 代码框架

## 目标

接受业务对象 Excel 或 XML。Excel 先由 `btulz.transforms excel` 转成并汇总为单一 XML，再统一交给 `btulz.transforms code`；所有中间产物和代码始终先进入独立临时目录，最后根据目标模块状态执行全量复制或最小语义合并。已有模块中的人工实现、稳定标识和项目配置优先。

如果用户既没有 Excel 也没有可用的 `Domain` XML，或要求根据自然语言修改模型，先使用 `generating-ava-cloud-business-objects` 完成 XML，再返回本流程。不要为了让代码生成通过而擅自改变业务模型。

## 开发流程位置

本 Skill 位于业务对象建模之后、手工业务开发之前：

```text
业务对象 XML
    ↓
generating-ava-cloud-code（当前）
    ↓
ava-cloud-plus-backend-development
    ↓
ava-cloud-plus-frontend-development
    ↓
构建门禁 → 数据库落地 → 跨层验收
```

它负责把已确认模型机械投影为候选骨架并安全合并，不负责把模板占位、业务规则、专用仓储方法或页面交互判定为已经实现。完整功能任务中，将新增与合并文件、跳过项和模板遗留项交给后端、前端及验证阶段。

## 执行门禁

开始前确认输入 Excel/XML、正式模块根目录、`btulz.transforms.core-*.jar` 或模板目录，以及用户需要的后端、前端、`bsui/c`、`bsui/m` 范围。能从会话或目标项目可靠取得时直接使用；不能可靠判断且会改变结果时再询问用户。

目标位于现有项目时，先读取其 `AGENTS.md`、后端 `pom.xml` 和前端 `tsconfig.json`。保留工作树中的已有改动，不修改 `3rdparty` 声明文件。

## 工作流

1. 创建独立临时目录，把它作为进程工作目录，并分别建立 Excel XML 输出目录和代码输出目录。正式模块目录禁止直接传给任何 `-OutputFolder`。
2. 输入是 Excel 时阅读 [btulz-excel-command.md](references/btulz-excel-command.md)，先执行 `excel` 命令；不能只检查退出码，必须确认至少生成一个非空 XML。运行 `scripts/merge_domain_xml.py <Excel XML 目录> <汇总 XML>`，把同一 Domain 的分对象 XML 去重汇总；冲突时停止。
3. 直接输入 XML 时以它作为后续 XML；输入目录或多个 XML 时也先用 `merge_domain_xml.py` 生成单一、去重的临时 XML。不要让 `code` 命令自行盲目合并重复模型。
4. 读取最终 XML，确认 `Domain.Name`、全部 `BusinessObject`、`Model`、`RelatedBO`、字段和引用完整。Excel 转换结果还必须按 `generating-ava-cloud-business-objects` 的业务规则复核并修正转换器缺陷，再进入代码生成。
5. 增量任务从用户说明、版本控制差异或旧 XML 确定真实模型增量；不能把“生成结果与手写代码不同”等同于本次需求。
6. 阅读 [btulz-code-command.md](references/btulz-code-command.md)，从目标项目提取稳定参数。已有模块必须沿用现有 `GroupId`、`ArtifactId`、版本、版权和 `ProjectId`。
7. 对最终 XML 执行 `code` 命令。模板尚未释放时在临时工作目录使用 `-Release`；使用已存在的绝对模板目录时可省略它。
8. 检查退出码、日志、未替换的模板标记和输出结构。候选根目录通常是 `<OutputFolder>/<Domain.Name>/`，与正式模块根目录对齐后再比较。
9. 运行 `scripts/inventory_generated.py <候选根目录> <正式模块根目录>` 盘点 `new`、`changed`、`same` 和 `target-only` 文件。脚本只读，不复制或覆盖。
10. 按目标状态处理：
   - 目标为空：确认没有源码、构建文件或有效配置后，把候选根目录下的全部内容复制进去，包括隐藏文件。版本控制元数据和空目录不算业务代码，但绝不能被覆盖或删除。
   - 目标已有代码：阅读 [incremental-merge.md](references/incremental-merge.md)，只复制本次新增且目标不存在的对象专属文件；共享文件和同名文件以候选为参考，用最小补丁合并所需成员。
11. 逐项回查 XML 增量。不要复制随机 ID 变化、模板版本差异、格式化变化、已有代码回退或用户未要求的 PC/移动端框架。
12. 按目标项目说明完成前后端验证，并检查 `git diff --check`、`git diff` 和 `git status --short`。模板遗留的 `TODO` 必须实现或明确报告。
13. 只能删除本次创建且已确认的临时路径；用户要求审阅候选结果时保留并报告路径。

## 安全边界

- `CodeTransformer` 会直接截断同名文件，没有增量合并能力；已有模块中禁止全量覆盖。
- 不因候选文件在目标中缺失就自动复制模块级脚手架，先判断它是否属于本次对象和目标范围。
- 不用生成器重新序列化的 XML 覆盖用户维护的源 XML。
- 已有应用 ID、模块 `ProjectId`、对象代码、命名空间、依赖版本和自定义逻辑保持不变。
- `-Domains` 指向目录时只读取直属文件；同名 Domain 会合并但不替对象或模型去重。优先传本次确切 XML。
- Excel 生成的 XML 是中间模型，不因转换成功就视为业务结构正确；确认后才允许生成或复制代码。

## 结果报告

说明原始输入类型和路径、Excel 生成及汇总的 XML、工具/JAR 与模板来源、临时候选根目录和正式目标根目录；列出新增与修改文件、跳过的生成物、保留的自定义代码、未解决的 `TODO`、验证命令及结果。
