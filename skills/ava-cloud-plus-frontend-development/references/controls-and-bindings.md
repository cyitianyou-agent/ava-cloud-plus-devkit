# 常用控件与代码示例

本文件是 PC View 的控件配方。示例中的 BO、属性名和国际化键需要替换，控件组合和绑定方式可直接沿用。

本文件说明“字段用什么控件和类型”；模型绑定在哪个控件、使用什么数据形状以及何时刷新，读取 [JSONModel 数据绑定与模型边界](json-model-bindings.md)。

## 一、控件选择表

| 字段语义 | 编辑控件 | 列表/表格 | ViewView | 数据类型 |
| --- | --- | --- | --- | --- |
| 文本、编码 | `sap.extension.m.Input` | `Text` / `DataLink` | `ObjectAttribute` | `Alphanumeric` |
| 整数、内部主键 | `Input` 或专用选择控件 | `Text` | `ObjectAttribute` | `Numeric` |
| 数量 | `Input` | `Text` | `ObjectNumber` | `Quantity` |
| 金额、合计 | `Input` | `Text` | `ObjectNumber` | `Price` / `Sum` |
| 汇率 | `Input` / 汇率组件 | `Text` | `ObjectNumber` | `Rate` |
| 日期 | `DatePicker` | `Text` | `ObjectAttribute` | `Date` |
| 时间 | `TimePicker` | `Text` | `ObjectAttribute` | `Time` |
| 是/否 | `CheckBox` / `TipsCheckBox` / `EnumSelect` | `Text` | `ObjectYesNoStatus` | `YesNo` |
| 枚举 | `EnumSelect` | `Text` | `ObjectEnumStatus` | `Enum` 或专用类型 |
| 单据状态 | `EnumSelect` | `Text` | `ObjectDocumentStatus` | `DocumentStatus` |
| 可配置属性 | `PropertySelect` | `PropertyText` | `PropertyObjectAttribute` | 与属性一致 |
| 外部 BO | `RepositoryInput` / `SelectionInput` | `RepositoryText` | `RepositoryObjectAttribute` | 与外键一致 |
| 所有人 | `DataOwnerInput` | `UserText` | `UserObjectAttribute` | 通常 `Numeric` |
| 组织 | 组织输入控件 | `OrganizationText` | `OrganizationObjectAttribute` | 通常 `Alphanumeric` |

## 二、普通输入

```ts
new sap.m.Label("", {
    text: ibas.i18n.prop("bo_item_name"),
    required: true
}),
new sap.extension.m.Input("", {
}).bindProperty("bindingValue", {
    path: "name",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 100
    })
})
```

`required` 必须来自 BO/Application 的真实约束。已知长度时把 `maxLength` 写入数据类型。

## 三、日期和时间

```ts
new sap.extension.m.DatePicker("", {
}).bindProperty("bindingValue", {
    path: "documentDate",
    type: new sap.extension.data.Date()
}),
new sap.extension.m.TimePicker("", {
}).bindProperty("bindingValue", {
    path: "startTime",
    type: new sap.extension.data.Time()
})
```

## 四、是/否与枚举

```ts
new sap.extension.m.CheckBox("", {
}).bindProperty("bindingValue", {
    path: "activated",
    type: new sap.extension.data.YesNo()
}),
new sap.extension.m.EnumSelect("", {
    enumType: ibas.emDocumentStatus
}).bindProperty("bindingValue", {
    path: "documentStatus",
    type: new sap.extension.data.DocumentStatus()
})
```

需要提示改变状态的风险时才用 `TipsCheckBox`：

```ts
new sap.extension.m.TipsCheckBox("", {
    text: ibas.i18n.prop("bo_item_canceled"),
    tipsOnSelection: ibas.i18n.prop([
        "shell_data_cancel",
        "shell_data_status"
    ])
}).bindProperty("bindingValue", {
    path: "canceled",
    type: new sap.extension.data.YesNo()
})
```

## 五、编号系列

```ts
new sap.extension.m.Input("", {
}).bindProperty("bindingValue", {
    path: "docNum",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 20
    })
}).bindProperty("editable", {
    path: "series",
    formatter(data: number): boolean {
        return data > 0 ? false : true;
    }
}),
new sap.extension.m.SeriesSelect("", {
    objectCode: bo.Item.BUSINESS_OBJECT_CODE
}).bindProperty("bindingValue", {
    path: "series",
    type: new sap.extension.data.Numeric()
}).bindProperty("editable", {
    path: "isNew",
    formatter(data: boolean): boolean {
        return data === true;
    }
})
```

编号与系列通常相邻出现。已有对象不允许切换系列；选择自动系列后不允许手工改编号。

## 六、可配置属性

```ts
new sap.extension.m.PropertySelect("", {
    dataInfo: {
        code: bo.Item.BUSINESS_OBJECT_CODE
    },
    propertyName: "category"
}).bindProperty("bindingValue", {
    path: "category",
    type: new sap.extension.data.Alphanumeric({
        maxLength: 30
    })
})
```

列表显示：

```ts
new sap.extension.m.PropertyText("", {
    dataInfo: {
        code: bo.Item.BUSINESS_OBJECT_CODE
    },
    propertyName: "category"
}).bindProperty("bindingValue", {
    path: "category",
    type: new sap.extension.data.Alphanumeric()
})
```

## 七、业务仓库选择和显示

当字段既允许直接输入关键字搜索，又允许点击值帮助弹窗选择时，必须继续读取 [可搜索选择输入框](searchable-inputs.md)。其中包含 `RepositoryInput` 的完整配置、静态/动态查询条件、主表字段和子表行字段示例，以及输入建议与 Application 回填的职责边界。

输入并触发 Application 选择事件：

```ts
new sap.extension.m.RepositoryInput("", {
    showValueHelp: true,
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    },
    valueHelpRequest: function (): void {
        that.fireViewEvents(that.choosePartnerEvent);
    }
}).bindProperty("bindingValue", {
    path: "partnerCode",
    type: new sap.extension.data.Alphanumeric()
})
```

带固定过滤条件的通用选择：

```ts
new sap.extension.m.SelectionInput("", {
    showValueHelp: true,
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    },
    criteria: [
        new ibas.Condition(
            partner.bo.Partner.PROPERTY_DELETED_NAME,
            ibas.emConditionOperation.NOT_EQUAL,
            ibas.emYesNo.YES.toString()
        )
    ]
}).bindProperty("bindingValue", {
    path: "partnerCode",
    type: new sap.extension.data.Alphanumeric()
})
```

列表描述：

```ts
new sap.extension.m.RepositoryText("", {
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    }
}).bindProperty("bindingValue", {
    path: "partnerCode",
    type: new sap.extension.data.Alphanumeric()
})
```

## 八、值帮助的行对象

子表选择必须传当前行：

```ts
new sap.extension.m.Input("", {
    showValueHelp: true,
    valueHelpRequest(this: sap.extension.m.Input): void {
        let line: bo.ItemLine = this.getBindingContext().getObject();
        that.fireViewEvents(that.chooseLineItemEvent, line);
    }
}).bindProperty("bindingValue", {
    path: "itemCode",
    type: new sap.extension.data.Alphanumeric()
})
```

选择约束复杂并被多个页面复用时，使用模块已有 `component.*` 控件；不要在多个 View 中复制同一套 Repository 和条件逻辑。

## 九、表格显示控件

普通文本：

```ts
new sap.extension.m.Text("", {
}).bindProperty("bindingValue", {
    path: "name",
    type: new sap.extension.data.Alphanumeric()
})
```

业务对象链接：

```ts
new sap.extension.m.DataLink("", {
    objectCode: bo.Item.BUSINESS_OBJECT_CODE
}).bindProperty("bindingValue", {
    path: "code",
    type: new sap.extension.data.Alphanumeric()
})
```

只有链接服务存在时使用 `DataLink`。

## 十、对象页只读控件

普通属性：

```ts
new sap.extension.m.ObjectAttribute("", {
    title: ibas.i18n.prop("bo_item_reference"),
    bindingValue: {
        path: "reference",
        type: new sap.extension.data.Alphanumeric()
    }
})
```

Repository 属性：

```ts
new sap.extension.m.RepositoryObjectAttribute("", {
    title: ibas.i18n.prop("bo_item_partner"),
    repository: partner.bo.BORepositoryPartner,
    dataInfo: {
        type: partner.bo.Partner,
        key: partner.bo.Partner.PROPERTY_CODE_NAME,
        text: partner.bo.Partner.PROPERTY_NAME_NAME
    },
    bindingValue: {
        path: "partnerCode",
        type: new sap.extension.data.Alphanumeric()
    }
})
```

状态：

```ts
new sap.extension.m.ObjectDocumentStatus("", {
    title: ibas.i18n.prop("bo_item_documentstatus"),
    enumValue: {
        path: "documentStatus",
        type: new sap.extension.data.DocumentStatus()
    }
}),
new sap.extension.m.ObjectYesNoStatus("", {
    title: ibas.i18n.prop("bo_item_canceled"),
    negative: true,
    enumValue: {
        path: "canceled",
        type: new sap.extension.data.YesNo()
    }
})
```

数量或金额：

```ts
new sap.extension.m.ObjectNumber("", {
    textAlign: sap.ui.core.TextAlign.Right,
    number: {
        path: "documentTotal",
        type: new sap.extension.data.Sum()
    },
    unit: {
        path: "documentCurrency",
        type: new sap.extension.data.Alphanumeric()
    }
})
```

## 十一、所有人和组织

编辑：

```ts
new sap.extension.m.DataOwnerInput("", {
    showValueHelp: true,
    organization: {
        path: "organization",
        type: new sap.extension.data.Alphanumeric()
    }
}).bindProperty("bindingValue", {
    path: "dataOwner",
    type: new sap.extension.data.Numeric()
})
```

查看：

```ts
new sap.extension.m.UserObjectAttribute("", {
    title: ibas.i18n.prop("bo_item_dataowner"),
    bindingValue: {
        path: "dataOwner",
        type: new sap.extension.data.Numeric()
    }
}),
new sap.extension.m.OrganizationObjectAttribute("", {
    title: ibas.i18n.prop("bo_item_organization"),
    bindingValue: {
        path: "organization",
        type: new sap.extension.data.Alphanumeric()
    }
})
```

## 十二、属性状态绑定

单属性控制：

```ts
enabled: {
    path: "isNew",
    formatter(data: boolean): boolean {
        return data !== true;
    }
}
```

多状态控制：

```ts
editable: {
    parts: [
        {
            path: "approvalStatus",
            type: new sap.extension.data.ApprovalStatus()
        },
        {
            path: "documentStatus",
            type: new sap.extension.data.DocumentStatus()
        }
    ],
    formatter(
        approvalStatus: ibas.emApprovalStatus,
        documentStatus: ibas.emDocumentStatus
    ): boolean {
        if (approvalStatus === ibas.emApprovalStatus.PROCESSING) {
            return false;
        }
        if (documentStatus === ibas.emDocumentStatus.CLOSED) {
            return false;
        }
        return true;
    }
}
```

formatter 只用于展示状态，必须确定、无副作用。不能在 formatter 中调用服务、修改 BO、触发事件或执行业务计算。

## 十三、通用服务按钮

```ts
new sap.m.Button("", {
    type: sap.m.ButtonType.Transparent,
    icon: "sap-icon://action",
    press: function (event: sap.ui.base.Event): void {
        ibas.servicesManager.showServices({
            proxy: new ibas.BOServiceProxy({
                data: that.table.getSelecteds(),
                converter: new bo.DataConverter()
            }),
            displayServices(services: ibas.IServiceAgent[]): void {
                if (ibas.objects.isNull(services) || services.length === 0) {
                    return;
                }
                let sheet: sap.m.ActionSheet = new sap.m.ActionSheet("", {
                    placement: sap.m.PlacementType.Bottom
                });
                for (let service of services) {
                    sheet.addButton(new sap.m.Button("", {
                        text: ibas.i18n.prop(service.name),
                        icon: service.icon,
                        type: sap.m.ButtonType.Transparent,
                        press: function (): void {
                            service.run();
                        }
                    }));
                }
                sheet.openBy(event.getSource());
            }
        });
    }
})
```

ListView 传选中集合，ViewView/EditView 传当前页面模型对象。没有服务或接口不需要时，不生成此按钮。

## 十四、桌面表格选择

- ListView、ChooseView、可编辑子表：默认 `sap.extension.table.DataTable`。
- ViewView 内只读子表：默认 `sap.extension.m.DataTable`。
- 层级数据：才使用扩展 TreeTable。
- 不因为 `sap.m.Table` 名称带 `m` 就认定它是移动端专用；判断依据是其在 PC ObjectPage 中的嵌入用途。
