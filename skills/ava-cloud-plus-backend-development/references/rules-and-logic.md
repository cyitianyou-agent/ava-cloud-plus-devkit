# 业务规则与跨对象逻辑

## 选择机制

| 需求 | 使用机制 |
| --- | --- |
| 单字段必填、去空格、范围约束 | common business rule |
| 同一 BO 内多属性同步计算 | `BusinessRuleCommon` 专用规则 + BO `registerRules()` |
| 保存时校验目标 BO 是否存在 | `BusinessLogic` 合同与检查服务 |
| 保存时更新另一个 BO、库存、金额或引用状态 | `BusinessLogic` + `@LogicContract` |
| 用户主动调用的独立业务动作 | Repository 自定义方法；内部可复用规则/逻辑服务 |

不要把跨对象查询放进属性 setter 或 `BusinessRuleCommon`，也不要把自动随保存发生的影响只写在 REST 方法中。

## 属性级 BusinessRule

专用规则通常继承 `BusinessRuleCommon`：

1. 构造函数接收 `IPropertyInfo<T>`，设置可国际化的规则名称。
2. 把所有读取依赖加入 `getInputProperties()`。
3. 把所有可能写回的属性加入 `getAffectedProperties()`。
4. 在 `execute(BusinessRuleContext)` 中从 context 取输入、处理 null/精度/枚举边界，并只写入必要输出。

计算金额和数量使用项目 decimal 工具，显式处理舍入。双向推导规则要定义“哪个值为空或为零时推导哪个值”，避免多个输出互相振荡。

在 BO `registerRules()` 中返回规则数组。对继承层次中的规则，检查当前基类是否已经组合父规则；不要无依据地丢弃父类规则。

## 跨对象业务逻辑组成

完整逻辑通常包含：

- `I...Contract extends IBusinessLogicContract`：仅声明逻辑所需的最小稳定输入。
- `...Service extends BusinessLogic<Contract, Affected>`：用 `@LogicContract(Contract.class)` 绑定。
- 触发 BO 的 `getContracts()`：返回合同对象，常用匿名实现把当前 BO 字段投影到契约。

一个契约应表达业务含义，而不是暴露整个触发 BO。合同至少提供稳定 `getIdentifiers()`，让逻辑链能够识别新旧合同并执行正向/反向差异。

## BusinessLogic 生命周期

实现关注四个扩展点：

- `checkDataStatus(Object)`：先保留框架对 deleted、canceled、approval、planned 等状态的判断，再增加本逻辑的跳过条件。
- `fetchBeAffected(contract)`：优先查当前事务缓存，再用共享事务 Repository 查询完整受影响对象。
- `impact(contract)`：施加新合同的业务影响。
- `revoke(contract)`：撤销旧合同的同等影响。

正向和反向必须成对设计。数量从 10 改为 15 时，框架可能撤销旧 10 再施加新 15；取消、删除、计划状态和行删除也会影响是否执行或撤销。只实现正向累加会造成重复保存后的数据漂移。

## 事务缓存与跨仓储

- `fetchBeAffected` 先使用框架提供的缓存查找能力，以复用同一逻辑链中已加载对象。
- 缓存没有结果时创建目标模块 Repository，并 `setTransaction(this.getTransaction())`。
- 检查下游 OperationResult 的 error，再取第一项或完整集合。
- 找不到必须存在的对象时抛 `BusinessLogicException`，消息来自 i18n。
- 不在逻辑服务中独立提交事务；受影响对象由逻辑链统一持久化。

## 合同实现

触发 BO 的 `getContracts()` 可以返回多个合同。实现时：

- 从当前 BO/父 BO读取值，不把可变 BO 实例暴露给服务。
- 行需要父单据日期、币种或状态时，确保集合 `afterAddItem` 已建立可靠 parent 引用，并考虑反序列化/加载路径。
- identifiers 必须在同一业务项的修改前后稳定；不要把会变化的数量、金额作为唯一身份。
- canceled/deleted/status 到合同状态的映射应与同类单据一致。

## 必测状态矩阵

按实际需求选择相关项：

- 新建：正向影响一次。
- 重复保存未修改对象：不重复累计。
- 数量/金额修改：撤销旧值并施加新值。
- 根取消、删除：旧影响被撤销。
- 行删除：只撤销目标行。
- PLANNED 与 RELEASED 切换：符合框架状态语义。
- 找不到受影响对象：整体失败且无部分提交。
- 多个合同影响同一对象：缓存与最终结果一致。

不要根据直觉推断 CLOSED、CANCELED、DELETED 的等价性；以目标模块现有逻辑和框架 `checkDataStatus` 的真实行为为准。

