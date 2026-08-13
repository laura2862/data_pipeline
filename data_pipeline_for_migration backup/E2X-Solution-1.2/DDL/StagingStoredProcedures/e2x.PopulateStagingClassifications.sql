CREATE OR ALTER PROCEDURE e2x.PopulateStagingClassifications
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingClassifications;

    -------------------------------------------------------------------------
    -- Materialize classification views
    -------------------------------------------------------------------------

    SELECT * INTO #CFIU              FROM e2x.vwCFIU;
    SELECT * INTO #CRS               FROM e2x.vwCRS;
    SELECT * INTO #DoddFrank         FROM e2x.vwDoddFrank;
    SELECT * INTO #DGSD              FROM e2x.vwDGSD;
    SELECT * INTO #UKEMIR            FROM e2x.vwUKEMIR;
    SELECT * INTO #EMIR              FROM e2x.vwEMIR;
    SELECT * INTO #FINRA             FROM e2x.vwFINRA;
    SELECT * INTO #MAS               FROM e2x.vwMAS;
    SELECT * INTO #MiFIDII           FROM e2x.vwMiFIDII;
    SELECT * INTO #USTax             FROM e2x.vwUSTax;
    SELECT * INTO #USTaxRelatedParty FROM e2x.vwUSTaxRelatedParty;

    -------------------------------------------------------------------------
    -- Indexes
    -------------------------------------------------------------------------

    CREATE NONCLUSTERED INDEX IX_tmp_CFIU              ON #CFIU              (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_CRS               ON #CRS               (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_DoddFrank         ON #DoddFrank         (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_DGSD              ON #DGSD              (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_UKEMIR            ON #UKEMIR            (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_EMIR              ON #EMIR              (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_FINRA             ON #FINRA             (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_MAS               ON #MAS               (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_MiFIDII           ON #MiFIDII           (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_USTax             ON #USTax             (LegalEntityId);
    CREATE NONCLUSTERED INDEX IX_tmp_USTaxRelatedParty ON #USTaxRelatedParty (LegalEntityId);

    -------------------------------------------------------------------------
    -- Populate staging
    -------------------------------------------------------------------------

    INSERT INTO e2x.StagingClassifications
    (
        LegalEntityId,
        AlternateId,
        LoadTimestamp,
        FenELegalEntityCategoryId,
        FenELegalEntityCategory,
        FenXLegalEntityCategory,
        --DGSD
        FenEDGSDLegalEntityTypeId,
        FenEDGSDLegalEntityType,
        FenXDGSDLegalEntityType,
        FenEUnderlyingCompanyId,
        FenEUnderlyingCompany,
        FenXUnderlyingCompany,
        FenEBudgetId,
        FenEBudget,
        FenXBudget,
        FenENumberOfEmployeesId,
        FenENumberOfEmployees,
        FenXNumberOfEmployees,
        FenEAnnualTurnOverId,
        FenEAnnualTurnOver,
        FenXAnnualTurnOver,
        FenEAnnualBalanceSheetId, 
        FenEAnnualBalanceSheet,
        FenXAnnualBalanceSheet,
        FenEFinalDGSDLegalEntityTypeId,
        FenEFinalDGSDLegalEntityType,
        FenXFinalDGSDLegalEntityType,
        FenECounterPartyEligibilityId,
        FenECounterPartyEligibility,
        FenXCounterPartyEligibility,
        --Finra
        FenESuitabilityCertificateProvidedId,
        FenESuitabilityCertificateProvided,
        FenXSuitabilityCertificateProvided,
        FenESuitabilityCertificateSourceId,
		FenESuitabilityCertificateSource,
		FenXSuitabilityCertificateSource,
        SuitabilityCertificateComment,
        FenEEntityClassificationId,
        FenEEntityClassification,
        FenXEntityClassification,
        FenETotalAssetsGt50Id,
        FenETotalAssetsGt50,
        FenXTotalAssetsGt50,
        FenEInvRisksIndependentId,
        FenEInvRisksIndependent,
        FenXInvRisksIndependent,
        FenEIndependentJudgementId,
        FenEIndependentJudgement,
        FenXIndependentJudgement,
        FenEDilligencePerformedId,
        FenEDilligencePerformed,
        FenXDilligencePerformed,
        IrrelevantInvFactorsComments,
        FenERecommendationsMadeId,
        FenERecommendationsMade,
        FenXRecommendationsMade,
        FenERecommendationsNotExcessiveId,
        FenERecommendationsNotExcessive,
        FenXRecommendationsNotExcessive
    )
    SELECT
        le.Id AS LegalEntityId,
        CAST(le.Id AS VARCHAR(50)) AS AlternateId,
        CURRENT_TIMESTAMP AS LoadTimestamp,
        le.Category AS FenELegalEntityCategoryId,
        lookupLegalEntityCategory1.EValue AS FenELegalEntityCategory,
        lookupLegalEntityCategory1.XValue AS FenXLegalEntityCategory,
        --dgsd
        dgsd.DGSDLegalEntityType AS FenEDGSDLegalEntityTypeId,
        lookupDGSDLegalEntityType2.EValue AS FenEDGSDLegalEntityType,
        lookupDGSDLegalEntityType2.XValue AS FenXDGSDLegalEntityType,
		dgsd.UnderlyingCompany AS FenEUnderlyingCompanyId,
        lookupUnderlyingCompany3.EValue AS FenEUnderlyingCompany,
		lookupUnderlyingCompany3.XValue AS FenXUnderlyingCompany,
        dgsd.Budget AS FenEBudgetId,
        lookupBudget4.EValue AS FenEBudget,
        lookupBudget4.XValue AS FenXBudget,
        dgsd.NumberOfEmployees AS FenENumberOfEmployeesId,
        lookupNumberOfEmployees5.EValue AS FenENumberOfEmployees,
        lookupNumberOfEmployees5.XValue AS FenXNumberOfEmployees,
        dgsd.AnnualTurnOver AS FenEAnnualTurnOverId,
        lookupAnnualTurnover6.EValue AS FenEAnnualTurnOver,
        lookupAnnualTurnover6.XValue AS FenXAnnualTurnOver,
		dgsd.AnnualBalanceSheet AS FenEAnnualBalanceSheetId, 
        lookupAnnualBalanceSheet7.EValue AS FenEAnnualBalanceSheet,
        lookupAnnualBalanceSheet7.XValue AS FenXAnnualBalanceSheet,
		dgsd.FinalDGSDLegalEntityType AS FenEFinalDGSDLegalEntityTypeId,
		lookupFinalDGSDLegalEntityType8.EValue AS FenEFinalDGSDLegalEntityType,
        lookupFinalDGSDLegalEntityType8.XValue AS FenXFinalDGSDLegalEntityType,
		dgsd.CounterPartyEligibility AS FenECounterPartyEligibility,
		lookupDGSDCounterpartyEligibility9.EValue AS FenECounterPartyEligibility,
		lookupDGSDCounterpartyEligibility9.XValue AS FenXCounterPartyEligibility,
        --finra
		finra.SuitabilityCertificateProvided AS FenESuitabilityCertificateProvidedId,
		lookupSuitabilityCertificateProvided10.EValue AS FenESuitabilityCertificateProvided,
		lookupSuitabilityCertificateProvided10.XValue AS FenXSuitabilityCertificateProvided,
		finra.SuitabilityCertificateSource AS FenESuitabilityCertificateSourceId,
		lookupSuitabilityCertificateProvider11.EValue AS FenESuitabilityCertificateSource,
		lookupSuitabilityCertificateProvider11.XValue AS FenXSuitabilityCertificateSource,
        finra.SuitabilityCertificateComment AS SuitabilityCertificateComment,
        finra.EntityClassification AS FenEEntityClassificationId,
        lookupFINRA_Institutional_client12.EValue AS FenEEntityClassification,
        lookupFINRA_Institutional_client12.XValue AS FenXEntityClassification,
        finra.TotalAssetsGt50 AS FenETotalAssetsGt50Id,
        lookupTotalAssetsGt5013.EValue AS FenETotalAssetsGt50,
        lookupTotalAssetsGt5013.XValue AS FenXTotalAssetsGt50,
        finra.InvRisksIndependent AS FenEInvRisksIndependentId,
        lookupInvRisksIndependent14.EValue AS FenEInvRisksIndependent,
        lookupInvRisksIndependent14.XValue AS FenXInvRisksIndependent,
        finra.IndependentJudgement AS FenEIndependentJudgementId,
        lookupIndependentJudgement15.EValue AS FenEIndependentJudgement,
		lookupIndependentJudgement15.EValue AS FenXIndependentJudgement,
        finra.DilligencePerformed AS FenEDilligencePerformedId,
        lookupDilligencePerformed16.EValue AS FenEDilligencePerformed,
        lookupDilligencePerformed16.XValue AS FenXDilligencePerformed,
        finra.IrrelevantInvFactorsComments AS IrrelevantInvFactorsComments,
        finra.RecommendationsMade AS FenERecommendationsMadeId,
        lookupRecommendationsMade17.EValue AS FenERecommendationsMade,
        lookupRecommendationsMade17.XValue AS FenXRecommendationsMade,
        finra.RecommendationsNotExcessive AS FenERecommendationsNotExcessiveId,
        lookupRecommendationsNotExcessive18.EValue AS FenERecommendationsNotExcessive,
        lookupRecommendationsNotExcessive18.XValue AS FenXRecommendationsNotExcessive

    FROM dbo.LegalEntity AS le

    LEFT JOIN dbo.LECompany AS lec
        ON lec.LegalEntityId = le.Id

    LEFT JOIN e2x.Lookups AS lookupSubType
        ON lookupSubType.LookupName = 'LuLeSubTpWithUndefined'
       AND lookupSubType.EId = le.LegalEntitySubtypeId

    LEFT JOIN #CFIU AS cfiu
        ON cfiu.LegalEntityId = le.Id

    LEFT JOIN #CRS AS crs
        ON crs.LegalEntityId = le.Id

    LEFT JOIN #DoddFrank AS doddFrank
        ON doddFrank.LegalEntityId = le.Id

    LEFT JOIN #DGSD AS dgsd
        ON dgsd.LegalEntityId = le.Id

    LEFT JOIN #UKEMIR AS ukEmir
        ON ukEmir.LegalEntityId = le.Id

    LEFT JOIN #EMIR AS emir
        ON emir.LegalEntityId = le.Id

    LEFT JOIN #FINRA AS finra
        ON finra.LegalEntityId = le.Id

    LEFT JOIN #MAS AS mas
        ON mas.LegalEntityId = le.Id

    LEFT JOIN #MiFIDII AS mifidii
        ON mifidii.LegalEntityId = le.Id

    LEFT JOIN #USTax AS usTax
        ON usTax.LegalEntityId = le.Id

    LEFT JOIN #USTaxRelatedParty AS usTaxRelatedParty
        ON usTaxRelatedParty.LegalEntityId = le.Id

    LEFT JOIN e2x.Lookups AS lookupLegalEntityCategory1 ON lookupLegalEntityCategory1.LookupName = 'LECategory' AND lookupLegalEntityCategory1.EId = le.[Category]
    LEFT JOIN e2x.Lookups AS lookupDGSDLegalEntityType2 ON lookupDGSDLegalEntityType2.LookupName = 'DGSDLegalEntityType' AND lookupDGSDLegalEntityType2.EId = dgsd.[DGSDLegalEntityType]
    LEFT JOIN e2x.Lookups AS lookupUnderlyingCompany3 ON lookupUnderlyingCompany3.LookupName = 'UnderlyingCompanyList' AND lookupUnderlyingCompany3.EId = dgsd.[UnderlyingCompany]
    LEFT JOIN e2x.Lookups AS lookupBudget4 ON lookupBudget4.LookupName = 'BudgetList' AND lookupBudget4.EId = dgsd.[Budget]
    LEFT JOIN e2x.Lookups AS lookupNumberOfEmployees5 ON lookupNumberOfEmployees5.LookupName = 'NumberOfEmployeesList' AND lookupNumberOfEmployees5.EId = dgsd.[NumberOfEmployees]
    LEFT JOIN e2x.Lookups AS lookupAnnualTurnover6 ON lookupAnnualTurnover6.LookupName = 'AnnualTurnoverList' AND lookupAnnualTurnover6.EId = dgsd.[AnnualTurnover]
    LEFT JOIN e2x.Lookups AS lookupAnnualBalanceSheet7 ON lookupAnnualBalanceSheet7.LookupName = 'AnnualBalanceSheetList' AND lookupAnnualBalanceSheet7.EId = dgsd.[AnnualBalanceSheet]
    LEFT JOIN e2x.Lookups AS lookupFinalDGSDLegalEntityType8 ON lookupFinalDGSDLegalEntityType8.LookupName = 'FinalDGSDLegalEntityType' AND lookupFinalDGSDLegalEntityType8.EId = dgsd.[FinalDGSDLegalEntityType]
    LEFT JOIN e2x.Lookups AS lookupDGSDCounterpartyEligibility9 ON lookupDGSDCounterpartyEligibility9.LookupName = 'DGSDCounterpartyEligibility' AND lookupDGSDCounterpartyEligibility9.EId = dgsd.[CounterPartyEligibility]
    LEFT JOIN e2x.Lookups AS lookupSuitabilityCertificateProvided10 ON lookupSuitabilityCertificateProvided10.LookupName = 'YesNo' AND lookupSuitabilityCertificateProvided10.EId = finra.[SuitabilityCertificateProvided]
    LEFT JOIN e2x.Lookups AS lookupSuitabilityCertificateProvider11 ON lookupSuitabilityCertificateProvider11.LookupName = 'SuitabilityCertificateProvider' AND lookupSuitabilityCertificateProvider11.EId = finra.[SuitabilityCertificateSource]
    LEFT JOIN e2x.Lookups AS lookupFINRA_Institutional_client12 ON lookupFINRA_Institutional_client12.LookupName = 'FINRA_Institutional_client' AND lookupFINRA_Institutional_client12.EId = finra.[EntityClassification]
    LEFT JOIN e2x.Lookups AS lookupTotalAssetsGt5013 ON lookupTotalAssetsGt5013.LookupName = 'YesNo' AND lookupTotalAssetsGt5013.EId = finra.[TotalAssetsGt50]
    LEFT JOIN e2x.Lookups AS lookupInvRisksIndependent14 ON lookupInvRisksIndependent14.LookupName = 'YesNo' AND lookupInvRisksIndependent14.EId = finra.[InvRisksIndependent]
    LEFT JOIN e2x.Lookups AS lookupIndependentJudgement15 ON lookupIndependentJudgement15.LookupName = 'YesNo' AND lookupIndependentJudgement15.EId = finra.[IndependentJudgement]
    LEFT JOIN e2x.Lookups AS lookupDilligencePerformed16 ON lookupDilligencePerformed16.LookupName = 'YesNo' AND lookupDilligencePerformed16.EId = finra.[DilligencePerformed]
    LEFT JOIN e2x.Lookups AS lookupRecommendationsMade17 ON lookupRecommendationsMade17.LookupName = 'YesNo' AND lookupRecommendationsMade17.EId = finra.[RecommendationsMade]
    LEFT JOIN e2x.Lookups AS lookupRecommendationsNotExcessive18 ON lookupRecommendationsNotExcessive18.LookupName = 'YesNo' AND lookupRecommendationsNotExcessive18.EId = finra.[RecommendationsNotExcessive]
END;
GO