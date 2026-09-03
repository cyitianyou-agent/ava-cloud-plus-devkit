# JasperReports 7.x JRXML 核心格式

本规范从 JasperReports Library 7.0.3 源码及其 demo JRXML 提炼。7.x 使用 Jackson XML 持久化，不能把 6.x JRXML 当作兼容模板。

## 根元素

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport name="SalesOrder" language="java"
              pageWidth="595" pageHeight="842" columnWidth="555"
              leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20"
              uuid="5af94bc1-f2e7-4a93-9d0a-19a53b9fd705">
  ...
</jasperReport>
```

- 官方 7.0.3 示例的根节点不带旧版 `xmlns`、`xsi:schemaLocation`。
- `name` 必填；页面尺寸、栏宽和边距使用整数。
- `uuid` 使用标准 UUID 字符串；每个报表和元素使用不同值。

## 推荐顺序

按 7.0.3 示例的对象模型顺序组织：

1. `property`、`template`、`style`
2. `subDataset`
3. `parameter`
4. `query`
5. `field`、`sortField`
6. `variable`
7. `filterExpression`
8. `group`
9. `background`、`title`、`pageHeader`、`columnHeader`
10. `detail`
11. `columnFooter`、`pageFooter`、`lastPageFooter`、`summary`、`noData`

## 参数、SQL、字段

```xml
<parameter name="Order_No" class="java.lang.String"/>
<query language="sql"><![CDATA[SELECT * FROM SalesOrder WHERE OrderNo = $P{Order_No}]]></query>
<field name="OrderNo" class="java.lang.String"/>
```

- 查询节点是 `<query language="sql">`，不是 `<queryString>`。
- `$P{Name}` 是 JDBC 值参数；本 Skill 禁止把 Crystal 值参数变成 `$P!{Name}`。
- `$F{Name}` 引用字段，`$V{Name}` 引用变量，`$P{Name}` 引用参数。
- 表达式和 SQL 优先放入 CDATA；不得在 CDATA 中出现未拆分的 `]]>`。

## 样式

```xml
<style name="Base" default="true" fontName="SansSerif" fontSize="10.0"/>
<style name="Bold" style="Base" bold="true"/>
```

字体、字号、粗体、斜体、颜色可直接放在 `style` 或元素属性中。可移植模板优先使用 Java 逻辑字体 `SansSerif`；只有目标环境明确提供 Jasper 字体扩展时才使用特定字体。不要生成本机字体路径。

## 分组与变量

```xml
<variable name="AmountSum" resetType="Group" calculation="Sum"
          resetGroup="OrderGroup" class="java.math.BigDecimal">
  <expression><![CDATA[$F{Amount}]]></expression>
</variable>
<group name="OrderGroup" reprintHeaderOnEachPage="true">
  <expression><![CDATA[$F{OrderNo}]]></expression>
  <groupHeader>
    <band height="20">...</band>
  </groupHeader>
  <groupFooter>
    <band height="20">...</band>
  </groupFooter>
</group>
```

7.x 分组表达式节点为 `<expression>`，不是旧写法 `<groupExpression>`。

## Band

`title`、`pageHeader`、`columnHeader`、`columnFooter`、`pageFooter`、`summary` 等单 band 区段直接使用 `height`：

```xml
<title height="30">
  <element kind="staticText" uuid="..." x="0" y="0" width="555" height="24">
    <text><![CDATA[Sales Order]]></text>
  </element>
</title>
```

`detail` 和 group header/footer 包含一个或多个 `<band>`：

```xml
<detail>
  <band height="18">
    <element kind="textField" uuid="..." x="0" y="0" width="120" height="18">
      <expression><![CDATA[$F{OrderNo}]]></expression>
    </element>
  </band>
</detail>
```

## 条件

数据集级过滤：

```xml
<filterExpression><![CDATA[$F{Status}.equals($P{Status})]]></filterExpression>
```

Band 或元素显示条件：

```xml
<printWhenExpression><![CDATA[Boolean.TRUE.equals($P{ShowDetail})]]></printWhenExpression>
```

只有在 Crystal 公式语义确定、Java 类型明确时才转换；否则保留内容并报告。

## 7.x 与旧格式边界

| 7.x | 不要生成的旧结构 |
|---|---|
| `<query language="sql">` | `<queryString>` |
| `<title height="...">` | `<title><band ...>` |
| `<element kind="staticText" ...>` | `<staticText><reportElement ...>` |
| `<element kind="textField" ...>` | `<textField><reportElement ...>` |
| `<expression>` | `<textFieldExpression>`、`<groupExpression>` |
| 元素几何属性直接位于 `element` | `<reportElement x="..." ...>` |
