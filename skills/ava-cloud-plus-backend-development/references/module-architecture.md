# 模块结构与变更流程

## 典型工程结构

一个传统 AVA Cloud+ 业务模块通常包含：

```text
ibas.<module>/
├── pom.xml                         Maven 父工程与公共依赖/插件
├── ibas.<module>/                  后端核心 JAR
│   ├── pom.xml
│   ├── app.xml                     本地运行配置，不复制其中敏感值
│   └── src/
│       ├── main/java/.../<module>/
│       │   ├── MyConfiguration.java
│       │   ├── bo/<object>/
│       │   ├── data/
│       │   ├── logic/
│       │   ├── repository/
│       │   └── rules/
│       ├── main/resources/
│       │   ├── datastructures/
│       │   ├── i18n/
│       │   └── initialization/
│       └── test/java/
└── ibas.<module>.service/          REST 与 Web 资源 WAR
    ├── pom.xml
    └── src/main/
        ├── java/.../service/rest/
        └── webapp/WEB-INF/
```

实际模块可能省略某些目录。不得为了匹配示意结构创建空层。

## 核心职责

- `bo`：运行时业务对象、接口、集合、默认值和属性规则。
- `data`：模块枚举、非持久化 DTO、数据转换辅助类型。
- `rules`：可复用的属性级校验或推导规则。
- `logic`：保存事务中的跨对象业务影响，通过契约发现并支持正向与反向执行。
- `repository`：模块对内 App 契约、对外 Svc 契约及其统一实现。
- `service/rest`：把 Svc 能力映射为 HTTP/JAX-RS，不承载重复业务逻辑。
- `datastructures`：持久化模型与对象关系的模型来源。
- `initialization`：模块、配置和业务对象关系等启动初始化数据。
- `i18n`：规则、逻辑和仓储错误消息。

## 依赖方向

通常的代码依赖方向为：

```text
framework / 基础业务模块
          ↑
目标模块核心 JAR
          ↑
目标模块 service WAR
```

service 依赖核心 JAR；核心 JAR 不得反向依赖 service。目标模块可以通过 Maven 依赖使用基础业务模块的公开 BO 接口、Repository、规则或逻辑契约，但先确认依赖已经存在，避免仅为复用一个小实现造成新的模块环。

## 事实采集清单

开始修改前记录：

- Maven artifact、Java 版本、模块依赖和受影响构建单元。
- `MyConfiguration.MODULE_ID`、命名空间和已有配置键。
- BO 类型：Simple、MasterData 或 Document。
- 根对象、行对象、孙表对象的主键与集合属性。
- `BUSINESS_OBJECT_CODE`、`DB_TABLE_NAME` 和变量替换方式。
- 仓储三件套已有方法及自定义方法命名。
- REST 基础路径、认证参数、JAXB Resolver 注册类型。
- 相关初始化文件、i18n key 和现有测试基类。

## 选择参照实现

参照优先级：

1. 目标模块中同类型、同层级、近期维护的对象。
2. 目标模块中的仓储、REST、配置和测试既有风格。
3. 直接依赖模块中与当前需求相同的机制。
4. `ibas-framework` 中相应基类的只读实现，仅用于解释行为。

不要从名称相似但对象类型不同的代码复制主键和状态逻辑。单据、主数据和简单对象的基础字段、行接口与默认状态不同。

## 变更控制

- 先检查 `git status`，保留用户已有改动。
- 对生成式变更先确认生成范围；生成后以差异为准逐文件清理，不提交无关重排。
- 新增依赖前检查当前依赖树能否满足需求，并确认不会形成环。
- 不修改本地数据库连接、部署地址或真实 token 作为功能实现的一部分。
- 不在核心 JAR 中引入 servlet/JAX-RS 层职责。

