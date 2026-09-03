# btulz.transforms 数据库命令

以下命令以已构建的工具 JAR 为准。版本号、路径、模板和连接值必须从当前环境取得，不照抄示例。

## Core `ds`

从一个 `Domain` XML 或目录直属的 `ds_*.xml` 创建缺失结构并注册 BO 元数据：

```powershell
java -jar <core-jar> ds `
  -TemplateFile=<ds-template> `
  -Company=<company> `
  -DbServer=<server> `
  -DbPort=<port> `
  -DbSchema=<schema> `
  -DbName=<database> `
  -DbUser=<user> `
  -DbPassword=<password> `
  -Domains=<domain-xml-or-directory>
```

无绝对模板路径时，可先在独立工作目录使用 `-Release` 释放 JAR 内的 `ds/` 模板。目录输入只读取直属、名称符合 `ds_*.xml` 的文件，不递归读取。

## Core `dsJar`

从模块 JAR 先应用 `datastructures`，再执行匹配过滤标记的 `datastructures/sql_*.xml`：

```powershell
java -jar <core-jar> dsJar `
  -DsTemplate=<ds-template> `
  -SqlFilter=<database-filter> `
  -JarFile=<module-jar> `
  -Company=<company> `
  -DbServer=<server> `
  -DbPort=<port> `
  -DbSchema=<schema> `
  -DbName=<database> `
  -DbUser=<user> `
  -DbPassword=<password>
```

`SqlFilter` 应与项目资源命名保持一致，例如模块实际采用的 `sql_mssql_` 或 `sql_mysql_` 标记。先确认 JAR 中包含本次最终 XML 和初始化资源。

## Core `sql`

执行一个 SQL 编排 XML。为避免误执行同目录其他 XML，优先传精确文件：

```powershell
java -jar <core-jar> sql `
  -SqlFile=<orchestration-xml> `
  -Company=<company> `
  -DbServer=<server> `
  -DbPort=<port> `
  -DbSchema=<schema> `
  -DbName=<database> `
  -DbUser=<user> `
  -DbPassword=<password>
```

Core `sql` 没有命令行过滤参数；传目录时会处理目录直属的所有 XML。SQL 文件应是工具支持的 `Action > Step > Script` 编排，而不是普通 `.sql` 文件。

## BOBAS `ds`

从 `app.xml` 和数据库值映射取得连接、模板及 SQL 过滤设置，可接受 XML 或 JAR：

```powershell
java -jar <bobas-jar> ds `
  -data=<domain-xml-or-module-jar> `
  -config=<app-xml> `
  -dbSign=<database-sign>
```

只有需要覆盖配置推断时才提供 `-template`、`-sql` 或 `-dbValue`。`-ignore` 会让处理在部分错误后继续，默认不要使用。

当 `data` 是 JAR 时，该命令同时处理数据结构和匹配的初始化 SQL；当 `data` 是 XML 时，只应用数据结构。

## BOBAS `init`

从数据 JAR 导入初始化业务数据：

```powershell
java -jar <bobas-jar> init `
  -data=<module-jar> `
  -config=<app-xml> `
  -classes=<dependency-jars>
```

依赖类库用分号分隔，也可以传包含 JAR 的目录。`-test` 只测试类加载，不导入数据；`-force` 替换已存在数据；`-ignore` 忽略单项错误。后两项必须与用户意图一致。

## 数据库类型

工具的经典映射覆盖 MSSQL、MySQL、PostgreSQL、HANA、SQLite、Sybase 和 DM8。是否能执行还取决于当前 JAR 中的模板、数据库值映射与 JDBC 驱动，不能仅凭文件名判断环境已经可用。

