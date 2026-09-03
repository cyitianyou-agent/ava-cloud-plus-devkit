# 完整示例：单据、子表和孙表

本例展示销售模块的“渠道报价单”。主表使用 `AVA_SL_OCQT`，第一个子表使用 `AVA_SL_CQT1`，该子表的第一个孙表使用 `AVA_SL_CQT11`。孙表以 `DocEntry + LineId` 为联合主键，并用非主键 `ItemId` 记录所属报价明细的 `LineId`。

示例没有增加索引，因为需求没有明确高频查询条件。`emChannelQuoteExpenseType` 是允许先在 XML 中声明、后续代码生成阶段补全的枚举。

```xml
<?xml version="1.0" encoding="utf-8"?>

<Domain Name="Sales" ShortName="SL">
  <Model Name="ChannelQuote" Description="渠道报价单" ModelType="Document" Mapped="AVA_SL_OCQT">
    <Property Name="DocEntry" Description="凭证编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="DocEntry" PrimaryKey="Yes"/>
    <Property Name="DocNum" Description="期间编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="DocNum"/>
    <Property Name="Period" Description="期间" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Period"/>
    <Property Name="Series" Description="编号系列" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Series"/>
    <Property Name="Canceled" Description="取消" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Canceled"/>
    <Property Name="ObjectCode" Description="类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="Object"/>
    <Property Name="LogInst" Description="实例号（版本）" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="LogInst"/>
    <Property Name="DataSource" Description="数据源" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="DataSource"/>
    <Property Name="Transfered" Description="是否结转" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Transfered"/>
    <Property Name="Status" Description="状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emBOStatus" Mapped="Status"/>
    <Property Name="CreateDate" Description="创建日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="CreateDate"/>
    <Property Name="CreateTime" Description="创建时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="CreateTime"/>
    <Property Name="UpdateDate" Description="修改日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="UpdateDate"/>
    <Property Name="UpdateTime" Description="修改时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="UpdateTime"/>
    <Property Name="CreateUserSign" Description="创建用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Creator"/>
    <Property Name="UpdateUserSign" Description="修改用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Updator"/>
    <Property Name="CreateActionId" Description="创建动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="CreateActId"/>
    <Property Name="UpdateActionId" Description="更新动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="UpdateActId"/>
    <Property Name="DataOwner" Description="数据所有者" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="DataOwner"/>
    <Property Name="TeamMembers" Description="团队成员" DataType="Alphanumeric" DataSubType="Default" EditSize="100" Mapped="TeamMembers"/>
    <Property Name="Organization" Description="数据所属组织" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OrgCode"/>
    <Property Name="ApprovalStatus" Description="审批状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emApprovalStatus" Mapped="ApvlStatus"/>
    <Property Name="DocumentStatus" Description="单据状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emDocumentStatus" Mapped="DocStatus"/>
    <Property Name="PostingDate" Description="过账日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="DocDate"/>
    <Property Name="DeliveryDate" Description="到期日" DataType="Date" DataSubType="Date" EditSize="8" Mapped="DocDueDate"/>
    <Property Name="DocumentDate" Description="凭证日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="TaxDate"/>
    <Property Name="Reference1" Description="参考1" DataType="Alphanumeric" DataSubType="Default" EditSize="100" Mapped="Ref1"/>
    <Property Name="Reference2" Description="参考2" DataType="Alphanumeric" DataSubType="Default" EditSize="200" Mapped="Ref2"/>
    <Property Name="Remarks" Description="备注" DataType="Memo" DataSubType="Default" EditSize="8" Mapped="Remarks"/>
    <Property Name="CustomType" Description="自定义类型" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="CusType"/>
    <Property Name="Referenced" Description="已引用" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Refed"/>
    <Property Name="Deleted" Description="删除的" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Deleted"/>
    <Property Name="ChannelCustomerCode" Description="渠道客户编码" DataType="Alphanumeric" DataSubType="Default" EditSize="20" Mapped="ChannelCustomerCode"/>
    <Property Name="ChannelCustomerName" Description="渠道客户名称" DataType="Alphanumeric" DataSubType="Default" EditSize="100" Mapped="ChannelCustomerName"/>
    <Property Name="ValidDate" Description="有效期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="ValidDate"/>
  </Model>
  <Model Name="ChannelQuoteItem" Description="渠道报价单-明细" ModelType="DocumentLine" Mapped="AVA_SL_CQT1">
    <Property Name="DocEntry" Description="编码" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="DocEntry" PrimaryKey="Yes"/>
    <Property Name="LineId" Description="行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="LineId" PrimaryKey="Yes"/>
    <Property Name="VisOrder" Description="显示顺序" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="VisOrder"/>
    <Property Name="ObjectCode" Description="类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="Object"/>
    <Property Name="LogInst" Description="实例号（版本）" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="LogInst"/>
    <Property Name="DataSource" Description="数据源" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="DataSource"/>
    <Property Name="Canceled" Description="取消" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Canceled"/>
    <Property Name="Status" Description="状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emBOStatus" Mapped="Status"/>
    <Property Name="LineStatus" Description="单据状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emDocumentStatus" Mapped="LineStatus"/>
    <Property Name="CreateDate" Description="创建日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="CreateDate"/>
    <Property Name="CreateTime" Description="创建时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="CreateTime"/>
    <Property Name="UpdateDate" Description="修改日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="UpdateDate"/>
    <Property Name="UpdateTime" Description="修改时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="UpdateTime"/>
    <Property Name="CreateUserSign" Description="创建用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Creator"/>
    <Property Name="UpdateUserSign" Description="修改用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Updator"/>
    <Property Name="CreateActionId" Description="创建动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="CreateActId"/>
    <Property Name="UpdateActionId" Description="更新动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="UpdateActId"/>
    <Property Name="Reference1" Description="参考1" DataType="Alphanumeric" DataSubType="Default" EditSize="100" Mapped="Ref1"/>
    <Property Name="Reference2" Description="参考2" DataType="Alphanumeric" DataSubType="Default" EditSize="200" Mapped="Ref2"/>
    <Property Name="Referenced" Description="已引用" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Refed"/>
    <Property Name="Deleted" Description="删除的" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Deleted"/>
    <Property Name="BaseDocumentType" Description="基础单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="BaseType"/>
    <Property Name="BaseDocumentEntry" Description="基础单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BaseEntry"/>
    <Property Name="BaseDocumentLineId" Description="基础单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BaseLine"/>
    <Property Name="ProjectCode" Description="项目代码" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="Project"/>
    <Property Name="DistributionRule1" Description="分配规则1" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode1"/>
    <Property Name="DistributionRule2" Description="分配规则2" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode2"/>
    <Property Name="DistributionRule3" Description="分配规则3" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode3"/>
    <Property Name="DistributionRule4" Description="分配规则4" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode4"/>
    <Property Name="DistributionRule5" Description="分配规则5" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode5"/>
    <Property Name="OriginalDocumentType" Description="原始单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="BSType"/>
    <Property Name="OriginalDocumentEntry" Description="原始单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BSEntry"/>
    <Property Name="OriginalDocumentLineId" Description="原始单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BSLine"/>
    <Property Name="TargetDocumentType" Description="目标单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="TargetType"/>
    <Property Name="TargetDocumentEntry" Description="目标单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="TargetEntry"/>
    <Property Name="TargetDocumentLineId" Description="目标单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="TargetLine"/>
    <Property Name="ItemCode" Description="物料编码" DataType="Alphanumeric" DataSubType="Default" EditSize="50" Mapped="ItemCode"/>
    <Property Name="Quantity" Description="数量" DataType="Decimal" DataSubType="Quantity" EditSize="8" Mapped="Quantity"/>
    <Property Name="Price" Description="价格" DataType="Decimal" DataSubType="Price" EditSize="8" Mapped="Price"/>
  </Model>
  <Model Name="ChannelQuoteItemExpense" Description="渠道报价单-明细-费用" ModelType="DocumentLine" Mapped="AVA_SL_CQT11">
    <Property Name="DocEntry" Description="编码" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="DocEntry" PrimaryKey="Yes"/>
    <Property Name="LineId" Description="行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="LineId" PrimaryKey="Yes"/>
    <Property Name="ItemId" Description="父级行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="ItemId"/>
    <Property Name="VisOrder" Description="显示顺序" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="VisOrder"/>
    <Property Name="ObjectCode" Description="类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="Object"/>
    <Property Name="LogInst" Description="实例号（版本）" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="LogInst"/>
    <Property Name="DataSource" Description="数据源" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="DataSource"/>
    <Property Name="Canceled" Description="取消" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Canceled"/>
    <Property Name="Status" Description="状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emBOStatus" Mapped="Status"/>
    <Property Name="LineStatus" Description="单据状态" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emDocumentStatus" Mapped="LineStatus"/>
    <Property Name="CreateDate" Description="创建日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="CreateDate"/>
    <Property Name="CreateTime" Description="创建时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="CreateTime"/>
    <Property Name="UpdateDate" Description="修改日期" DataType="Date" DataSubType="Date" EditSize="8" Mapped="UpdateDate"/>
    <Property Name="UpdateTime" Description="修改时间" DataType="Date" DataSubType="Time" EditSize="8" Mapped="UpdateTime"/>
    <Property Name="CreateUserSign" Description="创建用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Creator"/>
    <Property Name="UpdateUserSign" Description="修改用户" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="Updator"/>
    <Property Name="CreateActionId" Description="创建动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="CreateActId"/>
    <Property Name="UpdateActionId" Description="更新动作标识" DataType="Alphanumeric" DataSubType="Default" EditSize="36" Mapped="UpdateActId"/>
    <Property Name="Reference1" Description="参考1" DataType="Alphanumeric" DataSubType="Default" EditSize="100" Mapped="Ref1"/>
    <Property Name="Reference2" Description="参考2" DataType="Alphanumeric" DataSubType="Default" EditSize="200" Mapped="Ref2"/>
    <Property Name="Referenced" Description="已引用" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Refed"/>
    <Property Name="Deleted" Description="删除的" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emYesNo" Mapped="Deleted"/>
    <Property Name="BaseDocumentType" Description="基础单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="BaseType"/>
    <Property Name="BaseDocumentEntry" Description="基础单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BaseEntry"/>
    <Property Name="BaseDocumentLineId" Description="基础单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BaseLine"/>
    <Property Name="ProjectCode" Description="项目代码" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="Project"/>
    <Property Name="DistributionRule1" Description="分配规则1" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode1"/>
    <Property Name="DistributionRule2" Description="分配规则2" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode2"/>
    <Property Name="DistributionRule3" Description="分配规则3" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode3"/>
    <Property Name="DistributionRule4" Description="分配规则4" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode4"/>
    <Property Name="DistributionRule5" Description="分配规则5" DataType="Alphanumeric" DataSubType="Default" EditSize="8" Mapped="OcrCode5"/>
    <Property Name="OriginalDocumentType" Description="原始单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="BSType"/>
    <Property Name="OriginalDocumentEntry" Description="原始单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BSEntry"/>
    <Property Name="OriginalDocumentLineId" Description="原始单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="BSLine"/>
    <Property Name="TargetDocumentType" Description="目标单据类型" DataType="Alphanumeric" DataSubType="Default" EditSize="30" Mapped="TargetType"/>
    <Property Name="TargetDocumentEntry" Description="目标单据编号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="TargetEntry"/>
    <Property Name="TargetDocumentLineId" Description="目标单据行号" DataType="Numeric" DataSubType="Default" EditSize="8" Mapped="TargetLine"/>
    <Property Name="ExpenseType" Description="费用类型" DataType="Alphanumeric" DataSubType="Default" EditSize="1" DeclaredType="emChannelQuoteExpenseType" Mapped="ExpenseType"/>
    <Property Name="Amount" Description="金额" DataType="Decimal" DataSubType="Sum" EditSize="8" Mapped="Amount"/>
  </Model>
  <BusinessObject MappedModel="ChannelQuote" ShortName="AVA_SL_CHANNELQUOTE">
    <RelatedBO Relation="OneToMany" MappedModel="ChannelQuoteItem">
      <RelatedBO Relation="OneToMany" MappedModel="ChannelQuoteItemExpense"/>
    </RelatedBO>
  </BusinessObject>
</Domain>
```

示例中的 `emChannelQuoteExpenseType` 表示允许先在 XML 中声明、后续代码生成阶段再补全的枚举。自检时应将它列入“待补全枚举”。
