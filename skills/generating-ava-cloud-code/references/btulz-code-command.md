# `btulz.transforms code` 命令

## 源码行为

`code` 子命令由 `Command4Code` 创建 `CodeTransformer`。模板目录依次按“参数中的现有目录”、“`<工作目录>/code/<TemplateFolder>`”、“JAR 资源”解析。打包资源通常不能作为普通目录遍历，使用默认模板时应在独立临时工作目录通过 `-Release` 释放，不能释放到正式模块或工具源码仓库。

| 参数 | 取值原则 |
| --- | --- |
| `-TemplateFolder` | 默认通常为 `ibas_classic`，也可传绝对模板目录 |
| `-OutputFolder` | 本次临时目录下的新目录 |
| `-GroupId` | 已有项目从 `pom.xml` 与包名取得 |
| `-ArtifactId` | 常见为 `ibas`，以目标实际值为准 |
| `-ProjectVersion`、`-ProjectUrl` | 沿用目标项目 |
| `-Domains` | 单个 XML 或目录；增量任务优先传确切 XML，目录读取不递归 |
| `-Parameters` | JSON 数组，核对 `Company`、`Copyright`、`ibasVersion`、`ibasIfVersion`、`ProjectId` |
| `-Release` | 仅在临时工作目录需要内置模板时使用 |

已有模块的 `ProjectId` 可从前端 `CONSOLE_ID` 或初始化资源 `ModuleId` 核对，不得重新生成。运行时 `ID` 会为部分新文件产生 UUID/long；只接受真正新增文件中的标识。

## PowerShell 形态

`-Dfile.encoding=utf-8` 必须位于 `-jar` 之前：

```powershell
$taskArgs = @(
    '-Dfile.encoding=utf-8'
    '-jar'
    $jarPath
    'code'
    '-TemplateFolder=ibas_classic'
    "-OutputFolder=$outputPath"
    "-GroupId=$groupId"
    "-ArtifactId=$artifactId"
    "-ProjectVersion=$projectVersion"
    "-ProjectUrl=$projectUrl"
    "-Domains=$xmlPath"
    "-Parameters=$parameterJson"
    '-Release'
)
Push-Location $tempPath
try {
    & java @taskArgs
    if ($LASTEXITCODE -ne 0) {
        throw "btulz.transforms code failed: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
```

JSON 应由结构化数据序列化，避免手工拼接转义字符。

## 输出规则

- 每个 Domain 输出到 `<OutputFolder>/<Domain.Name>/`。
- 普通 `Template_` 文件按 Domain 生成一次，可能汇总全部对象或模型。
- `Template_BO_` 按顶层业务对象生成；`Template_BOModel_` 为对象及递归子项的模型生成；`Template_BOItem_` 只为递归 `OneToMany` 子项生成。
- `putout_domain_models.txt` 会输出重新序列化的数据结构 XML，非模板文件会直接复制。
- 同名输出通过 `FileOutputStream` 重写，没有冲突检测、备份或三方合并。

日志中的部分变量警告可能来自模板内有意保留的 Shell 环境变量。仍要检查源码、配置和路径中是否残留 `$BEGIN_`、`$END_` 或业务模板变量，不能只看退出码。
