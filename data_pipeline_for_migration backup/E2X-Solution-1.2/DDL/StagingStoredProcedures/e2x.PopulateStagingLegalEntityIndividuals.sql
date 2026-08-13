CREATE OR ALTER PROCEDURE e2x.PopulateStagingLegalEntityIndividuals
AS
BEGIN
    SET NOCOUNT ON;

    SELECT *
    INTO #MultiSelectLE
    FROM e2x.vwMultiSelectAgg_LegalEntity_Pivoted;

    CREATE UNIQUE CLUSTERED INDEX IX_tmp_MultiSelectLE
        ON #MultiSelectLE (PrimaryId);

    TRUNCATE TABLE e2x.StagingLegalEntityIndividuals;

    INSERT INTO e2x.StagingLegalEntityIndividuals
    (
        [LegalEntityId],
        [AlternateId],
        [IsCustomer],
        [FirstName],
        [LastName],
        [DOB],
        [FenENationalCountryId],
        [FenENationalCountry],
        [FenXNationalCountry],
        [FenECitizenshipId],
        [FenECitizenship],
        [FenXCitizenship],
        [FenENaicsId],
        [FenENaics],
        [FenXNaics],
        [FenEPlaceOfBirthId],
        [FenEPlaceOfBirth],
        [FenXPlaceOfBirth],
        [FenELegalEntityTypeId],
        [FenELegalEntityType],
        [FenXLegalEntityType],
        [FenETypeOfInvestorId],
        [FenETypeOfInvestor],
        [FenXTypeOfInvestor],
        [FenESpecializedEddRequiredId],
        [FenESpecializedEddRequired],
        [FenXSpecializedEddRequired],
        [FenESpecializedEddEntityTypeIds],
        [FenESpecializedEddEntityType],
        [FenXSpecializedEddEntityType],
        [FenEKycLevelId],
        [FenEKycLevel],
        [FenXKycLevel],
        [KycLevelOverrideComment],
        [RegistrationNumber],
        [AnticipatedActivityOfAccount],
        [FenERemediationStatusId],
        [FenERemediationStatus],
        [FenXRemediationStatus],
        [FenETitleId],
        [FenETitle],
        [FenXTitle],
        [FenEInsiderStatusIds],
        [FenEInsiderStatus],
        [FenXInsiderStatus],
        [CompanyNameInsiderOrShareholderOf],
        [Occupation],
        [FenEGenderId],
        [FenEGender],
        [FenXGender],
        [NumberOfIdentificationDocument],
        [FenEEmploymentStatusId],
        [FenEEmploymentStatus],
        [FenXEmploymentStatus],
        [NameOfEmployer],
        [NatureOfSelfEmployment],
        [NationalIdentificationNumber],
        [NetWorthOfTheIndividual],
        [LengthOfRelationshipWithScotiabank],
        [FenENegativeNewsScreeningConductedId],
        [FenENegativeNewsScreeningConducted],
        [FenXNegativeNewsScreeningConducted],
        [SummaryOfBusinessActivitiesWithScotia],
        [PrimaryRevenueGeneratingProductsAndServices],
        [NationalInsuranceNumber],
        [DirectorsIdentificationNumber],
        [FenEPepSanctionsId],
        [FenEPepSanctions],
        [FenXPepSanctions],
        [MarketingInfo],
        [LastUpdatedBy],
        [LoadTimestamp]
    )
    SELECT
        le.Id AS LegalEntityId,
        CAST(le.Id AS VARCHAR(50)) AS AlternateId,
        CASE WHEN EXISTS (SELECT 1 FROM dbo.LEAssociate AS ler WHERE ler.LegalEntityId = le.Id AND ler.Active = 1 AND ler.LEAssociateTypeID = 101 AND ler.LegalEntityRoleStatusId IN (1,3)) THEN 1 ELSE 0 END AS IsCustomer,
        individual.FirstName,
        individual.LastName,
        individual.DOB,
        le.NationalCountryId AS FenENationalCountryId,
        lookupNationalCountry.EValue AS FenENationalCountry,
        lookupNationalCountry.XValue AS FenXNationalCountry,
        individual.CitizenshipId AS FenECitizenshipId,
        lookupCitizenship.EValue AS FenECitizenship,
        lookupCitizenship.XValue AS FenXCitizenship,
        lec.[NaicCode] AS [FenENaicsId],
        lookupNaics1.EValue AS [FenENaics],
        lookupNaics1.XValue AS [FenXNaics],
        individual.[PlaceOfBirth] AS [FenEPlaceOfBirthId],
        lookupPlaceOfBirth2.EValue AS [FenEPlaceOfBirth],
        lookupPlaceOfBirth2.XValue AS [FenXPlaceOfBirth],
        le.[LegalEntitySubtypeId] AS [FenELegalEntityTypeId],
        lookupLegalEntityType3.EValue AS [FenELegalEntityType],
        lookupLegalEntityType3.XValue AS [FenXLegalEntityType],
        lex.[TypeOfInvestorId] AS [FenETypeOfInvestorId],
        lookupTypeOfInvestor4.EValue AS [FenETypeOfInvestor],
        lookupTypeOfInvestor4.XValue AS [FenXTypeOfInvestor],
        lex.[SpecEDDRequiredId] AS [FenESpecializedEddRequiredId],
        lookupSpecializedEddRequired5.EValue AS [FenESpecializedEddRequired],
        lookupSpecializedEddRequired5.XValue AS [FenXSpecializedEddRequired],
        msaLE.FenESpecializedEddEntityTypeIds AS [FenESpecializedEddEntityTypeIds],
        msaLE.FenESpecializedEddEntityType AS [FenESpecializedEddEntityType],
        msaLE.FenXSpecializedEddEntityType AS [FenXSpecializedEddEntityType],
        le.[KYCLevelId] AS [FenEKycLevelId],
        lookupKycLevel6.EValue AS [FenEKycLevel],
        lookupKycLevel6.XValue AS [FenXKycLevel],
        le.[KYCOverrideComment] AS [KycLevelOverrideComment],
        individual.[RegistrationNumber] AS [RegistrationNumber],
        lek.[AnticipatedActivityAccount] AS [AnticipatedActivityOfAccount],
        lex.[RemediationStatusId] AS [FenERemediationStatusId],
        lookupRemediationStatus7.EValue AS [FenERemediationStatus],
        lookupRemediationStatus7.XValue AS [FenXRemediationStatus],
        individual.[Title] AS [FenETitleId],
        lookupTitle8.EValue AS [FenETitle],
        lookupTitle8.XValue AS [FenXTitle],
        msaLE.FenEInsiderStatusIds AS [FenEInsiderStatusIds],
        msaLE.FenEInsiderStatus AS [FenEInsiderStatus],
        msaLE.FenXInsiderStatus AS [FenXInsiderStatus],
        leiex.[CompanyName] AS [CompanyNameInsiderOrShareholderOf],
        individual.[Occupation] AS [Occupation],
        individual.[GenderId] AS [FenEGenderId],
        lookupGender9.EValue AS [FenEGender],
        lookupGender9.XValue AS [FenXGender],
        individual.[NumberOfIdentificationDocument] AS [NumberOfIdentificationDocument],
        individual.[EmploymentStatusId] AS [FenEEmploymentStatusId],
        lookupEmploymentStatus10.EValue AS [FenEEmploymentStatus],
        lookupEmploymentStatus10.XValue AS [FenXEmploymentStatus],
        individual.[NameOfEmployer] AS [NameOfEmployer],
        individual.[NatureOfSelfEmployment] AS [NatureOfSelfEmployment],
        individual.[NationalIdentificationNumber] AS [NationalIdentificationNumber],
        individual.[ActOrEstNetWorth] AS [NetWorthOfTheIndividual],
        lex.[LengthRelationship] AS [LengthOfRelationshipWithScotiabank],
        lex.[NegNewsScreenConducted] AS [FenENegativeNewsScreeningConductedId],
        lookupNegativeNewsScreeningConducted11.EValue AS [FenENegativeNewsScreeningConducted],
        lookupNegativeNewsScreeningConducted11.XValue AS [FenXNegativeNewsScreeningConducted],
        lex.[SumBusActWithScotia] AS [SummaryOfBusinessActivitiesWithScotia],
        lex.[PrimaryRevGenProdServ] AS [PrimaryRevenueGeneratingProductsAndServices],
        individual.[NationalInsuranceNumber] AS [NationalInsuranceNumber],
        individual.[DirectorsIdentificationNumber] AS [DirectorsIdentificationNumber],
        individual.[PEPSanctions] AS [FenEPepSanctionsId],
        lookupPepSanctions12.EValue AS [FenEPepSanctions],
        lookupPepSanctions12.XValue AS [FenXPepSanctions],
        individual.[MarketingInfo] AS [MarketingInfo],
        le.[LastUpdatedBy] AS [LastUpdatedBy],
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.LegalEntity AS le
    LEFT JOIN dbo.LEIndividual AS individual ON individual.LegalEntityId = le.Id
    LEFT JOIN e2x.Lookups AS lookupNationalCountry ON lookupNationalCountry.LookupName = 'Country' AND lookupNationalCountry.EId = le.NationalCountryId
    LEFT JOIN e2x.Lookups AS lookupCitizenship ON lookupCitizenship.LookupName = 'Country' AND lookupCitizenship.EId = individual.CitizenshipId
    LEFT JOIN dbo.LECompany AS lec ON lec.LegalEntityId = le.Id
    LEFT JOIN dbo.LegalEntityKYC AS lek ON lek.LegalEntityId = le.Id
    LEFT JOIN scotia.LegalEntityExtension AS lex ON lex.LegalEntityId = le.Id
    LEFT JOIN scotia.LEIndividualExtension AS leiex ON leiex.LegalEntityId = le.Id
    LEFT JOIN e2x.Lookups AS lookupNaics1 ON lookupNaics1.LookupName = 'NaicCodeDescription' AND lookupNaics1.EId = lec.[NaicCode]
    LEFT JOIN e2x.Lookups AS lookupPlaceOfBirth2 ON lookupPlaceOfBirth2.LookupName = 'Country' AND lookupPlaceOfBirth2.EId = individual.[PlaceOfBirth]
    LEFT JOIN e2x.Lookups AS lookupLegalEntityType3 ON lookupLegalEntityType3.LookupName = 'LuLeSubTpIndividual' AND lookupLegalEntityType3.EId = le.[LegalEntitySubtypeId]
    LEFT JOIN e2x.Lookups AS lookupTypeOfInvestor4 ON lookupTypeOfInvestor4.LookupName = 'TypeOfInvestor' AND lookupTypeOfInvestor4.EId = lex.[TypeOfInvestorId]
    LEFT JOIN e2x.Lookups AS lookupSpecializedEddRequired5 ON lookupSpecializedEddRequired5.LookupName = 'YesNo' AND lookupSpecializedEddRequired5.EId = lex.[SpecEDDRequiredId]
    LEFT JOIN e2x.Lookups AS lookupKycLevel6 ON lookupKycLevel6.LookupName = 'LookupKYCLevel' AND lookupKycLevel6.EId = le.[KYCLevelId]
    LEFT JOIN e2x.Lookups AS lookupRemediationStatus7 ON lookupRemediationStatus7.LookupName = 'RemediationStatus' AND lookupRemediationStatus7.EId = lex.[RemediationStatusId]
    LEFT JOIN e2x.Lookups AS lookupTitle8 ON lookupTitle8.LookupName = 'LookupPrefix' AND lookupTitle8.EId = individual.[Title]
    LEFT JOIN e2x.Lookups AS lookupGender9 ON lookupGender9.LookupName = 'Gender' AND lookupGender9.EId = individual.[GenderId]
    LEFT JOIN e2x.Lookups AS lookupEmploymentStatus10 ON lookupEmploymentStatus10.LookupName = 'LookupEmploymentStatus' AND lookupEmploymentStatus10.EId = individual.[EmploymentStatusId]
    LEFT JOIN e2x.Lookups AS lookupNegativeNewsScreeningConducted11 ON lookupNegativeNewsScreeningConducted11.LookupName = 'YesNo' AND lookupNegativeNewsScreeningConducted11.EId = lex.[NegNewsScreenConducted]
    LEFT JOIN e2x.Lookups AS lookupPepSanctions12 ON lookupPepSanctions12.LookupName = 'YesNo' AND lookupPepSanctions12.EId = individual.[PEPSanctions]
    LEFT JOIN #MultiSelectLE AS msaLE ON msaLE.PrimaryId = le.Id
    WHERE le.LegalEntitySubtypeId = 17
        AND ISNULL(le.IsDeleted, 0) <> 1;
END;
GO
