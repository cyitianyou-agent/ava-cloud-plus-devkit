# 资源、构建与验证

## MyConfiguration

模块配置类通常提供：

- 唯一 `MODULE_ID`。
- root、data、bo、service 命名空间。
- 模块配置键和带默认值的读取方法。
- 对业务对象代码、表名或 token 的模块统一处理。

新增配置时先检查 `initialization/configs` 是否需要对应默认值或管理项。配置键使用稳定 camelCase 字符串；不要把环境地址、数据库口令或客户值写成代码常量。

## i18n

- 面向用户的规则、逻辑和仓储错误使用 `I18N.prop(...)`。
- 同时维护模块默认语言与已有的语言变体，保持 key 一致。
- key 使用模块简称和语义命名，先搜索是否已有可复用消息。
- 日志中的纯技术诊断可参数化，但不得记录 token、连接串或业务敏感正文。

## initialization

初始化资源按用途最小变更：

- `bo.applicationmodule*.xml`：模块标识和平台声明。
- `configs/bo.applicationconfig.*.xml`：可管理的模块配置。
- `relations/bo.borelationship.*.xml`：单据引用、转换或其他 BO 关系。
- 其他 `bo.*.xml`：模块启动所需的真实业务初始数据。

新增关系时核对源对象 code、关联集合属性、目标对象 code 和关系类型。对象 code 中的 `${Company}` 等变量要与 BO 和数据结构采用同一约定。

不要为了新增普通字段修改模块注册；不要复制邻近初始化文件后只改文件名而遗漏内部 code。

## Maven 与服务工程

- 新跨模块 Java 引用只有在目标核心 JAR 的 `pom.xml` 已有或确需新增依赖时才成立。
- service WAR 依赖目标核心 JAR；REST DTO 若放在核心 JAR，通常无需额外复制到 service。
- 保持父版本、模块版本和项目现行 Java 级别，不在功能修改中顺手升级插件或依赖。
- 核心逻辑测试优先运行 JAR 子工程；涉及 JAXB/Jersey/打包再构建 service WAR。

根据目标模块实际 Maven 结构选择命令。常见最小验证形态是：

```powershell
mvn -pl ibas.<module> -am test
mvn -pl ibas.<module>.service -am package -DskipTests
```

不要原样套用占位模块名。若父工程没有声明 `<modules>`，进入相应子工程运行 Maven，或遵循模块已有编译脚本。不要用跳过编译、删除测试或修改依赖版本来掩盖失败。

## 测试策略

测试应针对公共行为而不是内部实现：

- BO：默认值、规则、主子键传播、孙表 Criteria、序列化往返。
- Repository：标准保存/查询、自定义 Criteria、权限错误、OperationResult。
- Logic：新建、修改、取消/删除、行状态、正反向影响和事务回滚。
- REST：路径、token 选择、具体请求/响应类型和 Resolver 注册。
- 初始化：配置 key、对象 code、关系 target 与模块 ID 的一致性。

优先复用目标模块的测试基类、数据准备方法和仓储清理方式。集成测试需要数据库或外部环境时，先运行不依赖环境的编译/单元测试，并明确报告未运行项及所需条件；不要伪造通过结果。

## 完成前检查

1. 运行目标核心 JAR 测试或至少编译。
2. 构建受影响 service WAR，捕获接口/具体类型和 JAXB 注册错误。
3. 搜索新 BO/方法名，确认数据结构、接口、实现、REST、Resolver 和测试中的拼写一致。
4. 搜索新增 i18n key 和配置 key，确认定义与使用成对存在。
5. 检查 `git diff --check` 与 `git status --short`。
6. 审查差异中是否包含本地配置、凭据、构建产物、批量生成覆盖或无关格式化。

结果报告应列出：修改层次、关键业务约束、运行的命令、通过项、未验证项和剩余风险。

