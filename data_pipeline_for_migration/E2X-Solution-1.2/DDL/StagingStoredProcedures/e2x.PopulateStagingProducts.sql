CREATE OR ALTER PROCEDURE e2x.PopulateStagingProducts
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingProducts;

    WITH CaseLegalEntity (LegalEntityId, CaseId) AS
    (
        SELECT assoc.LegalEntityId, assoc.EntityId AS CaseId
        FROM dbo.LegalEntityAssociation AS assoc
        WHERE assoc.BusinessEntityId = 1
          AND assoc.LookupLegalEntityAssociationId = 9
          AND assoc.IsDeleted = 0
    )
    INSERT INTO e2x.StagingProducts
    (
        [AlternateId],
        [ProductId],
        [LegalEntityId],
        [CaseId],
        [FenEProductCategoryId],
        [FenEProductCategory],
        [FenXProductCategory],
        [FenELookupProductTypeId],
        [FenELookupProductType],
        [FenXLookupProductType],
        [FenEProductStatusId],
        [FenEProductStatus],
        [FenXProductStatus],
        [ParentAlternateId],
        [FenEBookingEntityId],
        [FenEBookingEntity],
        [FenXBookingEntity],
        [FenEArrangingEntityId],
        [FenEArrangingEntity],
        [FenXArrangingEntity],
        [FenEInternalDeskId],
        [FenEInternalDesk],
        [FenXInternalDesk],
        [IntendedUseOfAccount],
        [CreatedDate],
        [ActivatedDate],
        [LastUpdated],
        [KycApprovalDate],
        [NamesOfSalesPersons],
        [FenEReasonForProductClosureId],
        [FenEReasonForProductClosure],
        [FenXReasonForProductClosure],
        [FenEExpectedActivityTypeId],
        [FenEExpectedActivityType],
        [FenXExpectedActivityType],
        [FenEFrequencyOfTradingVolumeId],
        [FenEFrequencyOfTradingVolume],
        [FenXFrequencyOfTradingVolume],
        [FenESourceOfFundsId],
        [FenESourceOfFunds],
        [FenXSourceOfFunds],
        [SourceOfFundsDetails],
        [LoadTimestamp]
    )
    SELECT
        'PRD' + CAST(product.Id AS VARCHAR(50)) AS AlternateId,
        product.Id AS ProductId,
        caseLe.LegalEntityId,
        product.CaseId,
        product.LookupProductCategoryId AS FenEProductCategoryId,
        lookupProductCategory.EValue AS FenEProductCategory,
        lookupProductCategory.XValue AS FenXProductCategory,
        product.LookupProductTypeId AS FenELookupProductTypeId,
        lookupProductType.EValue AS FenELookupProductType,
        lookupProductType.XValue AS FenXLookupProductType,
        product.ProductStatusId AS FenEProductStatusId,
        lookupProductStatus.EValue AS FenEProductStatus,
        lookupProductStatus.XValue AS FenXProductStatus,
        CAST(caseLe.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        product.[BookingEntityId] AS [FenEBookingEntityId],
        lookupBookingEntity1.EValue AS [FenEBookingEntity],
        lookupBookingEntity1.XValue AS [FenXBookingEntity],
        product.[TradingLocationId] AS [FenEArrangingEntityId],
        lookupArrangingEntity2.EValue AS [FenEArrangingEntity],
        lookupArrangingEntity2.XValue AS [FenXArrangingEntity],
        pex.[InternalDesk] AS [FenEInternalDeskId],
        lookupInternalDesk3.EValue AS [FenEInternalDesk],
        lookupInternalDesk3.XValue AS [FenXInternalDesk],
        product.[PurposeOfAccount] AS [IntendedUseOfAccount],
        product.[CreatedDate] AS [CreatedDate],
        product.[ActivatedDate] AS [ActivatedDate],
        product.[LastUpdatedDate] AS [LastUpdated],
        pex.[KYCApprovalDate] AS [KycApprovalDate],
        pex.[NamesSalesPersons] AS [NamesOfSalesPersons],
        pex.[ReasonProductClosure] AS [FenEReasonForProductClosureId],
        lookupReasonForProductClosure10.EValue AS [FenEReasonForProductClosure],
        lookupReasonForProductClosure10.XValue AS [FenXReasonForProductClosure],
        pex.[ExpectedActivityType] AS [FenEExpectedActivityTypeId],
        lookupExpectedActivityType11.EValue AS [FenEExpectedActivityType],
        lookupExpectedActivityType11.XValue AS [FenXExpectedActivityType],
        pex.[FreqTradingVolume] AS [FenEFrequencyOfTradingVolumeId],
        lookupFrequencyOfTradingVolume12.EValue AS [FenEFrequencyOfTradingVolume],
        lookupFrequencyOfTradingVolume12.XValue AS [FenXFrequencyOfTradingVolume],
        pex.[SourceFunds] AS [FenESourceOfFundsId],
        lookupSourceOfFunds13.EValue AS [FenESourceOfFunds],
        lookupSourceOfFunds13.XValue AS [FenXSourceOfFunds],
        pex.[SourceFundsDetails] AS [SourceOfFundsDetails],
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM origination.Product AS product
    INNER JOIN CaseLegalEntity AS caseLe ON caseLe.CaseId = product.CaseId
    LEFT JOIN e2x.Lookups AS lookupProductCategory ON lookupProductCategory.LookupName = 'LookupProductCategory' AND lookupProductCategory.EId = product.LookupProductCategoryId
    LEFT JOIN e2x.Lookups AS lookupProductType ON lookupProductType.LookupName = 'LookupProductType' AND lookupProductType.EId = product.LookupProductTypeId
    LEFT JOIN e2x.Lookups AS lookupProductStatus ON lookupProductStatus.LookupName = 'ProductStatus' AND lookupProductStatus.EId = product.ProductStatusId
    LEFT JOIN scotia.ProductExtension AS pex ON pex.ProductId = product.Id
    LEFT JOIN e2x.Lookups AS lookupBookingEntity1 ON lookupBookingEntity1.LookupName = 'productConfig.BookingEntity' AND lookupBookingEntity1.EId = product.[BookingEntityId]
    LEFT JOIN e2x.Lookups AS lookupArrangingEntity2 ON lookupArrangingEntity2.LookupName = 'productConfig.BookingEntity' AND lookupArrangingEntity2.EId = product.[TradingLocationId]
    LEFT JOIN e2x.Lookups AS lookupInternalDesk3 ON lookupInternalDesk3.LookupName = 'LECompanyDesk' AND lookupInternalDesk3.EId = pex.[InternalDesk]
    LEFT JOIN e2x.Lookups AS lookupReasonForProductClosure10 ON lookupReasonForProductClosure10.LookupName = 'ProductClosureReason' AND lookupReasonForProductClosure10.EId = pex.[ReasonProductClosure]
    LEFT JOIN e2x.Lookups AS lookupExpectedActivityType11 ON lookupExpectedActivityType11.LookupName = 'ExpectedActivityType' AND lookupExpectedActivityType11.EId = pex.[ExpectedActivityType]
    LEFT JOIN e2x.Lookups AS lookupFrequencyOfTradingVolume12 ON lookupFrequencyOfTradingVolume12.LookupName = 'FreqTradingVol' AND lookupFrequencyOfTradingVolume12.EId = pex.[FreqTradingVolume]
    LEFT JOIN e2x.Lookups AS lookupSourceOfFunds13 ON lookupSourceOfFunds13.LookupName = 'SourceFundsScotia' AND lookupSourceOfFunds13.EId = pex.[SourceFunds]
    WHERE product.IsDeleted = 0
      AND product.ProductStatusId IN (1,3,4);
END;
GO
