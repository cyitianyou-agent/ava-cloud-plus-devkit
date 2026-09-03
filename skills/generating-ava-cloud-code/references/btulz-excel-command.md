# `btulz.transforms excel` 命令

## 参数与调用

| 参数 | 行为 |
| --- | --- |
| `-ExcelFile` | 要解析的 `.xls` 或 `.xlsx` 文件 |
| `-OutputFolder` | XML 输出目录；必须位于本次临时目录 |
| `-IgnoreSheet=yes` | 默认行为，忽略名称以 `!--` 开头的工作表 |
| `-IgnoreSheet=no` | 解析这些注释/模板工作表，只在用户明确需要时使用 |
| `-Release` | 只释放 JAR 内的 `templates/`，解析已有 Excel 并不依赖它，通常省略 |

```powershell
$excelArgs = @(
    '-Dfile.encoding=utf-8'
    '-jar'
    $jarPath
    'excel'
    "-ExcelFile=$excelPath"
    "-OutputFolder=$xmlFolder"
    "-IgnoreSheet=$ignoreSheet"
)
Push-Location $tempPath
try {
    & java @excelArgs
    if ($LASTEXITCODE -ne 0) {
        throw "btulz.transforms excel failed: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
```

退出码为 0 仍可能没有输出，例如所有工作表都以 `!--` 开头且保持默认忽略。执行后必须枚举输出目录，确认至少存在一个非空 XML，并逐个解析根节点。

## 源码决定的输出

- Domain 名称取 Excel 文件名去扩展名、去最后一个下划线后的版本，再取前一个下划线后的片段。例如 `Domain_Models_Materials_v1.0.xlsx` 得到 `Materials`。
- Domain 简称由该名称中的非小写字符拼成；文件命名不符合约定时结果可能错误，转换后必须核对 `Domain.Name` 和 `Domain.ShortName`。
- 名称以 `!--` 开头的工作表默认跳过；其他工作表都交给默认解析器，在第一列为“表名”或“对象名”的区域读取模型和业务对象。
- 输出按业务对象分组，每个对象通常生成 `ds_<域简称>_<对象名>.xml`，其中只带该对象递归引用的模型。
- 多个 XML 可能重复包含共享模型。不要直接把输出目录交给 `code`；先用 `scripts/merge_domain_xml.py` 合并并去重。

## 转换后复核

Excel 解析器是格式驱动的，不等价于业务规则校验。至少核对：

- Domain 名称与简称、对象代码、表映射和对象层级。
- 模型类型、主键、唯一键、属性类型、子类型、长度、声明类型和映射。
- 所有 `MappedModel` 指向唯一存在的模型。
- 主数据主表的 `Code` 主键。当前解析源码把主数据主表的主键判断写成了 `DocEntry`，因此转换结果可能只有 `Code` 唯一键而缺少主键。
- 子表/孙表关系。解析器创建的 Excel 子表关系能力有限，复杂层级不能仅凭成功日志判断。

发现问题时，在临时汇总 XML 中按 `generating-ava-cloud-business-objects` 的规则做最小修正并记录；不要修改用户原 Excel，除非用户明确要求回写。
