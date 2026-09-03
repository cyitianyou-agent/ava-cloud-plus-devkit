# 仓储与 REST

## 仓储三件套

模块通常由三个类型共同构成一个仓储：

| 类型 | 面向对象 | 签名特点 |
| --- | --- | --- |
| `IBORepository<Module>App` | 核心 Java 调用方 | `IOperationResult<IObject>`，使用 BO 接口，不显式传 token |
| `IBORepository<Module>Svc` | 对外服务 | `OperationResult<Object>`，使用可序列化具体类型并显式传 token |
| `BORepository<Module>` | 两套契约的实现 | 继承 `BORepositoryServiceApplication`，同时实现 App 与 Svc |

标准 BO 的典型能力是：

- Svc `fetchObject(ICriteria, String token)` 委托框架 `fetch(Object.class, criteria, token)`。
- App `fetchObject(ICriteria)` 使用已设置的 `getUserToken()` 调用 Svc 版本，并转换为接口结果。
- Svc `saveObject(Object, String token)` 委托框架 `save(bo, token)`。
- App `saveObject(IObject)` 使用已设置的 token 调用 Svc 版本。

复制签名时核对目标模块的泛型和参数顺序，不要把 App 的接口类型与 Svc 的具体类型混用。

## token 与权限

`BORepositoryServiceApplication` 提供用户认证和数据权限语义。业务模块应通过公开/受保护的框架入口保存和查询，不绕过权限层。

- Java 内部调用先 `setUserToken(...)`，再使用 App 方法。
- REST 同时接收 `Authorization` header 和兼容 query token 时，统一通过模块现有的 `MyConfiguration.optToken(...)` 选择 token。
- 不记录完整 token，不把系统用户作为普通业务请求的默认身份。
- 测试若确需系统用户，限制在测试仓储构造范围并说明原因。

## 自定义仓储方法

非标准方法仍应同时回答四个问题：

1. App 与 Svc 是否都需要它，返回类型分别是什么。
2. Criteria 或 DTO 的允许输入是什么，空条件是否安全。
3. 错误如何进入 `OperationResult`，调用方如何判断 `getError()`。
4. 操作是否需要与其他查询/保存共享事务。

默认做法：设置 token、验证输入、使用 BO 属性元数据构造 Criteria、调用现有 Repository、检查下游 `getError()`、把异常包装进 OperationResult。只有现有 BO 查询无法表达且同模块已有可靠先例时才使用直接 SQL；必须参数化并保留权限、事务和数据库兼容性。

## 事务

单次标准 `save` 使用框架事务语义。一个自定义方法包含多个持久化动作时：

- 仅由最外层操作决定 begin/commit/rollback。
- `beginTransaction()` 的返回值可能表示当前是否新开事务；只提交或回滚自己开启的事务。
- 创建跨模块 Repository 时，用 `setTransaction(this.getTransaction())` 共享当前事务。
- 任一下游 OperationResult 含错误时立即抛出或转交统一失败路径，不继续提交部分数据。
- Repository 使用 try-with-resources 关闭；共享事务的子仓储不得提前提交父事务。

测试至少覆盖成功提交和中途失败回滚。

## REST DataService

`DataService` 通常位于 service WAR，使用模块既有 `@Path("data")`，继承模块 Repository：

- BO 查询与保存通常是 JSON `POST`。
- REST 参数使用具体 `Criteria`、具体 BO 或具体 DTO，确保 JAXB/Jersey 可实例化。
- 方法只做协议适配、token 选择和对 Repository 的委托。
- 路径、方法名和 Svc 方法保持一致，除非明确需要兼容旧 API。
- 不在 REST 方法里复制 Criteria 改写、事务或业务规则。

新增文件上传下载只沿用已有 FileService 机制，并单独处理媒体类型、文件名、大小和路径安全；不要把文件二进制接口塞入普通 JSON BO 方法。

## JAXB Resolver

Resolver 的 `JAXBContext` 至少包含框架通用类型以及所有从 REST 根部序列化/反序列化的具体 BO/DTO。

- 新增 BO 后检查 Resolver，而不是假设 Jersey 会发现接口类型。
- 子对象通常可通过根 BO 注解到达，但目标模块如果显式列出子类，应保持其风格。
- 自定义 DTO 若作为请求或响应根类型，确认 JAXB 注解并注册。
- 注册遗漏常表现为服务编译成功、运行时序列化失败，必须通过服务层测试或最小请求验证。

## REST 自检

- App/Svc/实现/DataService 四处的方法名、参数和返回类型一致。
- token 优先级与模块现有实现一致。
- Resolver 包含新增根类型。
- `web.xml` 的 provider package 能扫描新增 REST 类；一般不需要为同包 DataService 方法改配置。
- 自定义 endpoint 没有绕过 Repository 权限与事务。
- 错误仍以模块标准 OperationResult 形态返回。

