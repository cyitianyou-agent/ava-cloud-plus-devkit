# 已有模块的增量合并

## 确定模型增量

候选目录是完整模板投影，不是补丁。先比较新旧 XML，区分新增顶层 `BusinessObject`、新增 `Model/RelatedBO`、新增 `Property` 和属性元数据变化。旧 XML 优先取用户基线，其次取版本控制基线；没有可靠基线时用现有代码验证，仍无法区分则询问用户。

## 文件矩阵

| 类别 | 典型路径 | 处理 |
| --- | --- | --- |
| 后端对象专属 | `<core>/src/main/java/**/bo/<bo>/{I<Model>,<Model>,I<Item>s,<Item>s}.java` | 新对象/模型且目标不存在时复制；同名按成员合并 |
| 后端对象测试 | `<core>/src/test/java/**/Test<BO>.java` | 范围包含测试时复制并补足有效断言 |
| 后端共享 | `<core>/src/main/java/**/repository/{IBORepository*App,IBORepository*Svc,BORepository*}.java` | 新对象时合并 import、fetch、save 契约与实现 |
| REST 共享 | `<service>/src/main/java/**/service/rest/DataService.java` | 新对象时合并 import 与 fetch/save 端点 |
| 前端对象契约/实现 | `api/bo/<BO>.ts`、`borep/bo/<BO>.ts` | 新对象可复制；新增字段只合并接口属性和实现属性块 |
| 前端应用/视图 | `bsapp/<bo>/**`、`bsui/c/<bo>/**` | 仅处理 PC 端；同名保留布局和定制逻辑，移动端候选列为跳过 |
| 前端共享注册 | `api/{Data,BORepository,index}.ts`、`borep/{BORepository,index}.ts`、`bsapp/Console.ts` | 新对象时合并对象代码、仓储、引用、工厂、功能和服务注册 |
| 前端导航 | `bsui/c/Navigation.ts` | 新对象时合并 PC 引用与 `switch` 分支；不合并移动端导航 |
| 语言资源 | `resources/languages/{bos,<domain>}*.json` | 合并对象、应用、关系和实际展示字段文案，保持 JSON 有效 |
| 模块脚手架 | 根/项目 `pom.xml`、`.settings`、构建脚本、Web 配置、`MyConfiguration` | 已有模块通常跳过，不因缺失就认定属于对象增量 |
| 生成的 XML | `<core>/src/main/resources/datastructures/*.xml` | 不覆盖源 XML，仅用于核对 |

## 按变更类型处理

新增对象时，复制不存在的对象专属文件，审阅包名、依赖、模板缺陷和新应用 ID；随后在共享仓储、REST、前端注册、Console、Navigation 和语言文件中按对象块最小插入。不要替换整个共享文件。

新增或修改字段时：

1. 在后端 `I<Model>.java` 合并 getter/setter 契约，在 `<Model>.java` 合并属性常量、`@DbField`、注册、getter/setter 和必要重载。
2. 在 `api/bo/<BO>.ts` 的正确接口加入字段，在 `borep/bo/<BO>.ts` 的正确类加入属性常量、getter、setter。
3. 只有用户要求展示/编辑，或现有页面明确维护全部业务字段时，才把候选控件或列适配到已有 `Choose/List/View/EditView`；禁止覆盖定制页面。
4. 为实际使用字段的 UI 合并 `bos*.json`。单纯字段变化不修改仓储方法、REST、Console 或 Navigation。

新增子表或孙表时，复制新模型 Java 类/接口和 `OneToMany` 集合类/接口；在父模型 Java 与 TypeScript 中合并关系属性和初始化；按范围合并编辑应用事件、显示方法、视图表格与语言资源。集合模板中的关联赋值和查询条件常有 `TODO`，应根据父子键实现或明确报告。

字段变化可能还需要数据库落地，但 `code` 命令不负责。完整功能任务应在构建门禁通过后使用 `evolving-ava-cloud-plus-database`；用户未授权数据库任务时只报告。

## 冲突规则

- 目标不存在且确属本次对象专属文件：复制后审阅。
- 目标存在且相同：不改；存在且不同：只提取 XML 增量对应代码块。
- 差异不对应 XML 增量：保留目标。
- 已有同名对象、字段、方法、注册或语言键：语义一致则跳过，不一致则最小解决并报告。
- UUID、serialVersionUID、格式化、模板版本、版权差异不属于既有文件的有效增量。

最后搜索新对象名、模型名、字段名和对象代码，核对后端契约/实现、前端契约/实现、仓储/REST、注册/导航及所需 UI 没有漏项或重复。
