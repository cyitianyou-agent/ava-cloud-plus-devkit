# borep 业务对象与仓库规范

`borep` 是前端领域运行时层：实现 `api` 中的 BO 和 Repository 契约，维护 BO 状态、父子集合、默认值、业务规则以及远程数据转换。它不创建 Application，不绘制 OpenUI5 控件。

## 一、标准结构

```text
borep/
├─ bo/
│  ├─ Sample.ts
│  └─ Other.ts
├─ BORepository.ts
├─ DataConverter.ts
└─ index.ts
```

依赖关系：

```text
api 接口 -> borep 具体类 -> bsapp 使用具体类
```

## 二、具体 BO 必须实现 API 接口

基类与 API 接口一一对应：

| API 接口 | borep 基类 |
| --- | --- |
| `IBOMasterData` | `BOMasterData<T>` |
| `IBOMasterDataLine` | `BOMasterDataLine<T>` |
| `IBODocument` | `BODocument<T>` |
| `IBODocumentLine` | `BODocumentLine<T>` |
| `IBOSimple` | `BOSimple<T>` |
| `IBOSimpleLine` | `BOSimpleLine<T>` |

不能让 API 声明为单据，具体类却继承 `BOSimple`；基类决定主键、状态、行关系、criteria 和保存行为。

## 三、属性实现标准

```ts
namespace demo {
    export namespace bo {
        export class Sample extends ibas.BOSimple<Sample> implements ISample {
            /** 业务对象编码 */
            static BUSINESS_OBJECT_CODE: string = BO_CODE_SAMPLE;

            /** 映射的属性名称-名称 */
            static PROPERTY_NAME_NAME: string = "Name";

            get name(): string {
                return this.getProperty<string>(Sample.PROPERTY_NAME_NAME);
            }

            set name(value: string) {
                this.setProperty(Sample.PROPERTY_NAME_NAME, value);
            }
        }
    }
}
```

每个持久化属性保持三项一致：

```text
API:     name: string
常量:    PROPERTY_NAME_NAME = "Name"
运行时:  get/set name -> getProperty/setProperty(PROPERTY_NAME_NAME)
```

规则：

- `PROPERTY_*_NAME` 的值是后端映射名称，通常 PascalCase，不能从 View 的绑定路径猜测大小写。
- getter/setter 使用具体泛型，不能用 `any` 掩盖 API 不一致。
- setter 通过 `setProperty()`，不要直接写私有字段，否则 BO 脏状态、规则和 Bindable 通知不会工作。
- 计算属性若不是持久化字段，应明确其来源，不伪造远程映射常量。
- 静态业务常量可以放在具体类，但跨模块消费者需要使用时应考虑提升为 API 公共常量。

## 四、`init()` 只做对象初始化

```ts
protected init(): void {
    this.sampleLines = new SampleLines(this);
    this.objectCode = ibas.config.applyVariables(
        Sample.BUSINESS_OBJECT_CODE
    );
    this.activated = ibas.emYesNo.YES;
}
```

适合放入 `init()`：

- 用 `new ChildCollection(this)` 创建主对象或子项拥有的集合；
- 对 BO code 应用配置变量；
- 设置确定的领域默认值，如启用状态、当天日期、本位币或初始单据状态。

不适合放入 `init()`：

- Repository 查询；
- 用户确认或消息；
- 依赖某个 View 的默认值；
- 需要异步返回的数据；
- 保存动作或跨 Application 调用。

加载远程对象时框架会经历加载状态。集合 `afterAdd()` 中设置默认值前应判断是否会覆盖远程数据。

## 五、子集合和孙集合

```ts
export class SampleLines extends ibas.BusinessObjects<SampleLine, Sample>
    implements ISampleLines {

    create(): SampleLine {
        let item: SampleLine = new SampleLine();
        this.add(item);
        return item;
    }

    protected afterAdd(item: SampleLine): void {
        super.afterAdd(item);
        if (!this.parent.isLoading && item.isNew) {
            item.visOrder = this.length - 1;
        }
    }
}
```

- 泛型第二项必须是真实父类型。
- `create()` 创建具体行、调用 `add()`，然后返回已经进入集合的对象。
- 父键、行号等框架能维护的字段交给 `BusinessObjects`，不要在 Application 重复模拟。
- 自定义顺序、默认货币等行为只有确属所有新增行的领域规则时才放 `afterAdd()`。
- `afterAdd()` 先调用 `super.afterAdd(item)`。
- 远程加载期间避免重新计算或覆盖后端值，必要时检查 `parent.isLoading` 和 `item.isNew`。

孙集合在子项的 `init()` 中创建：

```ts
export class SampleLine extends ibas.BOSimpleLine<SampleLine>
    implements ISampleLine {

    protected init(): void {
        this.sampleLineValues = new SampleLineValues(this);
    }
}

export class SampleLineValues
    extends ibas.BusinessObjects<SampleLineValue, SampleLine>
    implements ISampleLineValues {
}
```

不能把孙集合错误地以主对象作为父泛型，也不能只在 View 中维护一份脱离 BO 的孙项数组。

## 六、业务规则放在 BO

由属性变化确定、在任何 Application 中都必须成立的计算应注册为 BO 规则：

```ts
protected registerRules(): ibas.IBusinessRule[] {
    return [
        new ibas.BusinessRuleSumElements(
            Sample.PROPERTY_TOTAL_NAME,
            Sample.PROPERTY_SAMPLELINES_NAME,
            SampleLine.PROPERTY_LINETOTAL_NAME
        )
    ];
}
```

行级计算示例：

```ts
protected registerRules(): ibas.IBusinessRule[] {
    return [
        new ibas.BusinessRuleMultiplication(
            SampleLine.PROPERTY_LINETOTAL_NAME,
            SampleLine.PROPERTY_QUANTITY_NAME,
            SampleLine.PROPERTY_PRICE_NAME,
            ibas.config.get(ibas.CONFIG_ITEM_DECIMAL_PLACES_SUM)
        )
    ];
}
```

选择依据：

- 始终成立的属性联动和金额计算：BO 规则或 BO 方法。
- 需要 Repository、用户确认或流程状态的动作：Application。
- 纯显示格式和控件显隐：View formatter。

不要让 View、Application 和 BO 同时计算同一个总计。

## 七、领域方法

可复用且只依赖领域对象的数据赋值，可以放到 BO：

```ts
baseMaterial(source: bo.IMaterial): void {
    if (ibas.objects.isNull(source)) {
        return;
    }
    this.itemCode = source.code;
    this.itemDescription = source.name;
}
```

方法应保持同步、确定，不弹消息、不查询 Repository、不打开服务。需要异步选择数据的流程由 Application 完成，选中后再调用 BO 方法。

## 八、Repository 标准实现

```ts
export class BORepositoryDemo extends ibas.BORepositoryApplication
    implements IBORepositoryDemo {

    protected createConverter(): ibas.IDataConverter {
        return new DataConverter();
    }

    fetchSample(fetcher: ibas.IFetchCaller<bo.Sample>): void {
        super.fetch(bo.Sample.name, fetcher);
    }

    saveSample(saver: ibas.ISaveCaller<bo.Sample>): void {
        super.save(bo.Sample.name, saver);
    }
}
```

- 类名、Repository 名称常量和模块命名空间保持一致。
- API Repository 使用接口类型；实现使用具体 BO 类型。
- 普通查询保存委托 `super.fetch(<BO>.name, ...)` 和 `super.save(...)`。
- 不在每个方法复制 Ajax、token 和 converter 初始化。
- 只读查询类型只实现 fetch；保存方法必须有真实后端能力。

### 自定义远程方法

只有标准 fetch/save 不够时才使用 `BORepositoryAjax.callRemoteMethod()`：

```ts
closeSample(caller: ICloseCaller<bo.Sample>): void {
    let repository: ibas.BORepositoryAjax = new ibas.BORepositoryAjax();
    repository.address = this.address;
    repository.token = this.token;
    repository.converter = this.createConverter();
    repository.callRemoteMethod(
        "closeSample",
        caller.beClosed,
        (opRslt: ibas.IOperationResult<bo.Sample>) => {
            caller.onCompleted.call(
                ibas.objects.isNull(caller.caller) ? caller : caller.caller,
                opRslt
            );
        }
    );
}
```

- 方法名、query 参数和 body 必须匹配真实后端契约，不能从相似模块猜。
- URL 参数中的自由文本使用 `encodeURIComponent()`。
- token、address 和 converter 取当前 Repository 实例。
- 回调使用 caller 指定的上下文约定。
- API caller、实现参数和 Application 回调结果类型必须一致。

上传、下载和文件 URL 复用模块既有 FileRepository 约定；不为单个 View 自行拼地址。

## 九、DataConverter

标准结构：

```ts
export class DataConverter extends ibas.DataConverter4j {
    protected createConverter(): ibas.BOConverter {
        return new BOConverter();
    }
}

export const boFactory: ibas.BOFactory = new ibas.BOFactory();

class BOConverter extends ibas.BOConverter {
    protected factory(): ibas.BOFactory {
        return boFactory;
    }
}
```

### 枚举转换必须双向对称

```ts
protected convertData(boName: string, property: string, value: any): any {
    if (boName === bo.Sample.name
        && property === bo.Sample.PROPERTY_SAMPLESTATUS_NAME) {
        return ibas.enums.toString(bo.emSampleStatus, value);
    }
    return super.convertData(boName, property, value);
}

protected parsingData(boName: string, property: string, value: any): any {
    if (boName === bo.Sample.name
        && property === bo.Sample.PROPERTY_SAMPLESTATUS_NAME) {
        return ibas.enums.valueOf(bo.emSampleStatus, value);
    }
    return super.parsingData(boName, property, value);
}
```

- `convertData` 处理发送方向，`parsingData` 处理接收方向。
- 判断使用 BO 名称和映射属性常量，不用 UI 字段标签。
- 未命中特例必须调用 `super`。
- 普通字符串、数字、日期和框架已经支持的枚举不重复添加转换。
- 新增一边转换时必须检查另一边，不能造成“保存正常、重新查询值错误”。

`customParsing()` 只处理框架工厂无法按标准结构识别的远程结果，不把普通 BO 映射全写成手工解析。

## 十、BOFactory 与 `borep/index.ts`

```ts
/// <reference path="../api/index.ts" />
/// <reference path="./bo/Sample.ts" />
/// <reference path="./DataConverter.ts" />
/// <reference path="./BORepository.ts" />

namespace demo {
    export namespace bo {
        boFactory.register(
            BO_REPOSITORY_DEMO,
            BORepositoryDemo
        );
        boFactory.register(
            Sample.BUSINESS_OBJECT_CODE,
            Sample
        );
    }
}
```

- 先引用 `api`，再引用具体 BO，最后引用 converter 和 Repository。
- Repository 用模块 Repository 名称注册。
- 通过 BO code 从远程数据构造的根 BO必须注册。
- 子行通常由父集合和转换器构造，不机械逐行注册；只有它本身可独立返回并有独立 code 时按模块既有方式注册。
- 查询结果 DTO 若使用按构造函数注册的模式，应保持现有 `boFactory.register(Type)` 约定，不伪造 BO code。

## 十一、重置、克隆和删除语义

- 使用基类 `clone()` 保持 BO 类型和集合语义；不要 JSON 深拷贝。
- 覆盖 `reset()` 时先调用 `super.reset()`，再恢复该 BO 的领域初始状态。
- 已持久化对象/行调用 `delete()` 标记删除；新建行由 Application 从原集合 `remove()`。
- View 只显示 `filterDeleted()`，不能因此改变原集合的保存语义。

## 十二、常见反例

- getter/setter 直接读写字段，绕过 `getProperty()`、`setProperty()`。
- API 是 `IBODocument`，实现却继承 `BOSimple`。
- 主对象声明子集合，但 `init()` 没有 `new Lines(this)`。
- `create()` 返回新行却没有加入集合。
- `afterAdd()` 在远程加载期间覆盖后端值。
- 总计同时在 BO 规则、Application 和 View formatter 中计算。
- Repository API 新增方法，但具体 Repository 漏实现或类型不同。
- 自定义远程方法硬编码另一个模块的地址或 converter。
- 只写 `convertData` 不写 `parsingData`，或命中特例后没有 `super` 回退。
- 新 BO 文件已存在，但未进入 `borep/index.ts` 或未注册 BOFactory。

## 十三、完成检查

- 具体类和 API 接口的基类、属性、集合和方法一致。
- 每个持久化属性都有正确的映射常量与 get/setProperty。
- `init()` 创建所有真实子集合并设置确定的领域默认值。
- 集合父泛型、`create()`、`afterAdd()` 和加载保护正确。
- 通用计算位于 BO 规则或领域方法，不泄漏到 View。
- Repository 实现 API 全部方法，并使用当前模块 converter。
- DataConverter 特例必要、双向、带 `super` 回退。
- Repository 和根 BO 已进入 `borep/index.ts` 引用及工厂注册。
- 没有引用 `bsapp`、`bsui` 或 OpenUI5 控件。
