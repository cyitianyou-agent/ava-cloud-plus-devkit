# api 公共契约规范

`api` 是业务模块提供给本模块其他层及外部前端模块使用的 TypeScript 公共面。它主要定义“可以依赖什么”，不负责创建具体 BO、发送 Repository 请求、驱动页面或实现 PC 控件。部分成熟模块也在 `Data.ts` 提供公共 ServiceProxy、条件构造器等可执行帮助代码；只有确实需要跨功能复用时才采用这种形式。

## 一、标准结构

```text
api/
├─ Data.ts
├─ bo/
│  ├─ Sample.ts
│  └─ Other.ts
├─ BORepository.ts
└─ index.ts
```

- `Data.ts`：模块元数据、配置键、BO code、公共枚举、稳定服务契约和公共条件构造器。
- `bo/*.ts`：BO、子项、集合及少量领域能力的接口。
- `BORepository.ts`：仓库公共接口和自定义调用参数接口。
- `index.ts`：用三斜线引用导出 API 文件。

## 二、`Data.ts` 放什么

### 模块元数据

```ts
namespace demo {
    /** 模块标识 */
    export const CONSOLE_ID: string = "00000000-0000-0000-0000-000000000000";
    /** 模块名称 */
    export const CONSOLE_NAME: string = "Demo";
    /** 模块版本 */
    export const CONSOLE_VERSION: string = "0.1.0";
}
```

ID 必须使用真实新值；名称应与模块仓库名、语言资源和 Repository 名称保持既有约定。

### 模块配置

```ts
export namespace config {
    export const CONFIG_ITEM_ENABLE_SAMPLE: string = "enableSample";

    export function get<T>(key: string, defalut?: T): T {
        return ibas.config.get(
            ibas.strings.format("{0}|{1}", CONSOLE_ID, key),
            defalut
        );
    }

    export function isEnableSample(): boolean {
        return get(CONFIG_ITEM_ENABLE_SAMPLE, false);
    }
}
```

配置键属于公共契约时才放这里。一个页面内部的临时开关、选中页签或对话框状态不属于模块配置。

### Repository 名称和 BO code

```ts
export namespace bo {
    export const BO_REPOSITORY_DEMO: string = ibas.strings.format(
        ibas.MODULE_REPOSITORY_NAME_TEMPLATE,
        CONSOLE_NAME
    );

    export const BO_CODE_SAMPLE: string = "${Company}_DM_SAMPLE";
}
```

- 每个可识别业务对象只有一个 code 定义源。
- 具体 BO 类的 `BUSINESS_OBJECT_CODE` 引用这里的常量，不重复写字面值。
- 不复制另一个 BO code 后只改常量名而忘记改字符串。
- 变更既有 BO code 会影响持久化、服务发现和链接，不能作为普通重命名处理。

### 公共枚举

```ts
export namespace bo {
    export enum emSampleStatus {
        NEW,
        PROCESSING,
        FINISHED
    }
}
```

枚举应表达稳定业务语义。仅服务某个 View 的颜色、页签或控件状态不要放入 BO 公共枚举。新增枚举后检查后端传输值以及 `DataConverter` 是否需要字符串与枚举的双向转换。

### 公共服务契约和代理

跨功能或跨模块调用需要稳定类型时，可在 `app` 命名空间声明：

```ts
export namespace app {
    export interface ISampleServiceContract extends ibas.IServiceContract {
        objectKey: number;
    }

    export class SampleServiceProxy extends ibas.ServiceProxy<ISampleServiceContract> {
    }
}
```

只有调用方确实需要依赖的契约才进入 API。Application 私有状态、某个 View 的内部行结构和一次性回调对象留在 `bsapp` 或 View 文件中。

### 可复用查询条件

当多个 Application 或 RepositoryInput 必须遵循同一业务过滤规则时，可以公开条件构造器：

```ts
export namespace app {
    export namespace conditions {
        export namespace sample {
            export function create(): ibas.IList<ibas.ICondition> {
                let conditions: ibas.IList<ibas.ICondition> =
                    new ibas.ArrayList<ibas.ICondition>();
                let condition: ibas.ICondition = new ibas.Condition();
                condition.alias = "Activated";
                condition.operation = ibas.emConditionOperation.EQUAL;
                condition.value = ibas.emYesNo.YES.toString();
                conditions.add(condition);
                return conditions;
            }
        }
    }
}
```

条件构造器应无 UI 依赖、无 Repository 查询、每次返回独立条件对象。当前模块整体编译且已有约定时，也可以使用具体 BO 的 `PROPERTY_*_NAME` 避免硬编码别名；但不能让 BO 接口或 Repository 公共签名暴露 borep 私有实现。只被一个 Application 使用的简单条件可以留在该 Application，不必扩大公共 API。

## 三、BO 接口选择正确基类

先按业务身份选择，不按“字段多少”选择：

| BO 语义 | 主对象接口 | 子项接口 | 常见标识 |
| --- | --- | --- | --- |
| 主数据 | `ibas.IBOMasterData` | `ibas.IBOMasterDataLine` | `code`、`name` |
| 单据 | `ibas.IBODocument` | `ibas.IBODocumentLine` | `docEntry`、`docNum`、单据状态 |
| 简单对象 | `ibas.IBOSimple` | `ibas.IBOSimpleLine` | `objectKey` 或业务自定义键 |

需要用户字段时，在真实支持用户字段的对象上附加 `ibas.IBOUserFields`。不要为了复用几个字段错误继承另一类 BO。

## 四、BO 接口示例

```ts
namespace demo {
    export namespace bo {
        /** 示例对象 */
        export interface ISample extends ibas.IBOSimple {
            objectKey: number;
            objectCode: string;
            name: string;
            activated: ibas.emYesNo;
            remarks: string;
            sampleLines: ISampleLines;
        }

        /** 示例对象行集合 */
        export interface ISampleLines extends ibas.IBusinessObjects<ISampleLine> {
            create(): ISampleLine;
        }

        /** 示例对象行 */
        export interface ISampleLine extends ibas.IBOSimpleLine {
            objectKey: number;
            lineId: number;
            visOrder: number;
            value: string;
        }
    }
}
```

规则：

- TypeScript 属性使用小驼峰；类型保持明确，日期用 `Date`，是非值和状态用对应枚举。
- 主接口的集合属性使用集合接口，不直接写普通数组。
- 集合接口继承 `IBusinessObjects<T>` 并提供 `create()`。
- 子项接口使用与主对象匹配的 Line 类型，除非既有数据模型明确采用其他类型。
- 接口只声明消费者可用的属性和方法，不包含 `PROPERTY_*_NAME`、默认值或 UI 展示信息。
- 注释说明业务语义，不重复类型本身。

### 孙表

孙表仍是子项自己的集合：

```ts
export interface ISampleLine extends ibas.IBOSimpleLine {
    values: ISampleLineValues;
}

export interface ISampleLineValues extends ibas.IBusinessObjects<ISampleLineValue> {
    create(): ISampleLineValue;
}
```

不能为了界面方便把孙集合提升到主接口，或在 Application 中临时拼出一个不符合 BO 所有权的平级数组。

## 五、Repository 公共接口

```ts
export interface IBORepositoryDemo extends ibas.IBORepositoryApplication {
    fetchSample(fetcher: ibas.IFetchCaller<bo.ISample>): void;
    saveSample(saver: ibas.ISaveCaller<bo.ISample>): void;
}
```

公共接口使用 BO 接口类型，具体 `borep` 实现使用具体类类型：

```text
api:   IFetchCaller<ISample>
borep: IFetchCaller<Sample>
```

只读查询对象不需要机械增加 `save...`。可持久化对象的 fetch/save 方法应成对且命名一致。

### 自定义远程方法

标准 `fetch`、`save` 无法表达时，定义具名 caller：

```ts
export interface ICloseCaller<T> extends ibas.IMethodCaller<T> {
    beClosed: T;
    onCompleted(opRslt: ibas.IOperationResult<T>): void;
}

export interface IBORepositoryDemo extends ibas.IBORepositoryApplication {
    closeSample(caller: ICloseCaller<bo.ISample>): void;
}
```

- 参数名表达业务含义，不把多个无关值塞进 `any`。
- 返回 `IOperationResult<T>` 还是 `IOperationMessage` 应与真实后端契约一致。
- caller 保留可选的 `caller` 上下文，并由实现用正确上下文调用 `onCompleted`。
- 不在 API 接口中写 Ajax 地址、token 拼接或序列化实现。

## 六、`api/index.ts` 引用顺序

```ts
/// <reference path="./Data.ts" />
/// <reference path="./bo/Sample.ts" />
/// <reference path="./bo/Other.ts" />
/// <reference path="./BORepository.ts" />
```

一般先让模块常量和枚举可见，再加载 BO 接口，最后加载引用这些接口的 Repository。新增文件未进入 `api/index.ts`，即使编辑器能定位，也可能不会进入 `outFile` 和声明输出。

## 七、API 稳定性

`api` 会进入模块声明并被其他模块编译引用，因此修改要比内部实现谨慎：

- 新增属性前确认后端和 borep 能提供它。
- 删除或重命名属性前搜索跨模块引用。
- 不把具体 View 类、OpenUI5 控件或本模块内部 Application 放入 BO 接口和 Repository 公共签名。
- 不暴露尚未稳定、只有单处调用的临时数据结构。
- BO 接口和 Repository 公共签名只使用接口及框架公共类型；公共帮助函数内部若沿用当前模块已有的 `PROPERTY_*_NAME` 约定，必须保持在整体编译可解析的范围内。
- 不通过编辑已经生成到 `3rdparty` 的声明来发布变化。

## 八、常见反例

- API 声明了 `saveSample`，borep 没有实现。
- BO 接口新增 `status`，具体类没有 getter/setter。
- 主接口写 `lines: ISampleLine[]`，丢失 `BusinessObjects` 的父子关系和 `create()`。
- 在 API 中导入或创建 `sap.m.*` 控件。
- 把某个 EditView 的临时选择状态放入 `Data.ts`。
- 只改 `3rdparty/demo/index.d.ts`，真实模块源码没有变化。
- 公共枚举改了成员顺序或传输值，却没有检查转换器和后端。

## 九、完成检查

- `Data.ts` 中 BO code、枚举和配置键唯一且命名一致。
- BO 接口选择了正确的主对象和 Line 基类。
- 属性类型、集合归属和 `create()` 契约完整。
- Repository 接口使用 BO 接口类型，自定义 caller 没有滥用 `any`。
- 新文件已加入 `api/index.ts` 且引用顺序可解析。
- API 没有依赖 `borep`、`bsapp` 或 `bsui`。
- 每项 API 变化都能在 borep 找到对应实现，或明确属于纯公共契约。
- 没有直接修改任何 `3rdparty` 声明文件。
