# JasperReports 7.x 元素速查

所有例子均采用 JasperReports 7.0.3 的 `<element kind="...">` 结构。几何、颜色、对齐、伸展和分页相关属性直接位于 `element`。

## 文本

```xml
<element kind="staticText" uuid="..." x="0" y="0" width="120" height="18" style="Bold">
  <text><![CDATA[Order No.]]></text>
</element>
<element kind="textField" uuid="..." x="120" y="0" width="160" height="18"
         blankWhenNull="true" textAdjust="StretchHeight">
  <expression><![CDATA[$F{OrderNo}]]></expression>
</element>
```

静态文字使用 `<text>`，动态值使用 `<expression>`。不要生成 `<textElement>` 或 `<textFieldExpression>`。

## 线、矩形和椭圆

```xml
<element kind="line" uuid="..." x="0" y="20" width="555" height="1">
  <pen lineWidth="0.5" lineStyle="Solid"/>
</element>
<element kind="rectangle" uuid="..." x="0" y="0" width="555" height="20" backcolor="#EEEEEE">
  <pen lineWidth="1.0"/>
</element>
<element kind="ellipse" uuid="..." x="0" y="0" width="20" height="20"/>
```

Crystal Box 优先映射为 `rectangle`；只有原对象是椭圆时使用 `ellipse`。

## Frame

```xml
<element kind="frame" uuid="..." x="0" y="0" width="555" height="20">
  <element kind="staticText" uuid="..." x="0" y="0" width="100" height="20">
    <text><![CDATA[Header]]></text>
  </element>
  <box><pen lineWidth="1.0"/></box>
</element>
```

Frame 内部元素坐标相对 Frame。不要把 Crystal 区段整体无条件包成 Frame；仅在需要共同边框、背景或相对定位时使用。

## 图片

```xml
<element kind="image" uuid="..." x="0" y="0" width="120" height="40" scaleImage="RetainShape">
  <expression><![CDATA[$P{LogoImage}]]></expression>
</element>
```

图片表达式可以是参数、字段或目标环境可访问的相对资源。不得写创建者电脑上的绝对路径。嵌入图片数据无法可靠迁移时报告，不虚构路径。

## 子报表

```xml
<parameter name="OrderLinesReport" class="net.sf.jasperreports.engine.JasperReport"/>
<element kind="subreport" uuid="..." x="0" y="0" width="555" height="20">
  <connectionExpression><![CDATA[$P{REPORT_CONNECTION}]]></connectionExpression>
  <expression><![CDATA[$P{OrderLinesReport}]]></expression>
  <parameter name="Order_No">
    <expression><![CDATA[$P{Order_No}]]></expression>
  </parameter>
</element>
```

只有子报表来源、参数映射和连接语义都明确时才生成。否则主报表中放置最小可识别占位元素会掩盖错误，应改为报告未支持项。

## 常用属性

| 目的 | 7.x 属性/子节点 |
|---|---|
| 水平/垂直对齐 | `hTextAlign`, `vTextAlign` |
| 文本自动增高 | `textAdjust="StretchHeight"`、常配 `positionType="Float"` |
| 空值不显示 | `blankWhenNull="true"` |
| 背景填充 | `mode="Opaque"` + `backcolor` |
| 边框 | `<box>`、`<pen>`、`<topPen>` 等 |
| 数字/日期格式 | `pattern` 或 `<patternExpression>` |
| 条件显示 | `<printWhenExpression>` |
| 图片缩放 | `scaleImage="Clip|FillFrame|RetainShape|RealHeight|RealSize"` |

## 高级组件

图表、交叉表、条码、地图、HTML/OLE、复杂子报表和自定义组件需要各自扩展模块。除非 RptToXml 元数据足够且当前任务明确需要，否则不要凭常识拼装；在单文件回复或批量报告中记录组件类型、位置和未迁移原因。
