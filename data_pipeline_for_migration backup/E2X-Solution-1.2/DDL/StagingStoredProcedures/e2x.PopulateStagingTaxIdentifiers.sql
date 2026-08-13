CREATE OR ALTER PROCEDURE e2x.PopulateStagingTaxIdentifiers
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingTaxIdentifiers;

    INSERT INTO e2x.StagingTaxIdentifiers
    (
        LegalEntityId,
        TaxIdentifierId,
        AlternateId,
        ParentAlternateId,
        FenECountryId,
        FenECountry,
        FenXCountry,
        FenETypeId,
        FenEType,
        FenXType,
        TaxIdentifierValue,
        FenEStatusId,
        FenEStatus,
        FenXStatus,
        IsTaxIdentifierProvided,
        FenEReasonNumberNotProvidedId,
        FenEReasonNumberNotProvided,
        FenXReasonNumberNotProvided,
        IsTaxResident,
        Comments,
        LoadTimestamp
    )
    SELECT
        ti.LegalEntityId AS LegalEntityId,
        ti.Id AS TaxIdentifierId,
        'TAX' + CAST(ti.Id AS VARCHAR(50)) + '-LE' + CAST(ti.LegalEntityId AS VARCHAR(50)) AS AlternateId,
        CAST(ti.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        ti.CountryId AS FenECountryId,
        lookupCountry.EValue AS FenECountry,
        lookupCountry.XValue AS FenXCountry,
        ti.TaxTypeId AS FenETypeId,
        lookupTaxIdType.EValue AS FenEType,
        lookupTaxIdType.XValue AS FenXType,
        ti.TaxIdentifierValue AS TaxIdentifierValue,
        ti.StatusId AS FenEStatusId,
        lookupTaxIdStatus.EValue AS FenEStatus,
        lookupTaxIdStatus.XValue AS FenXStatus,
        e2x.BitToYesNo(ti.IsTaxIdentifierProvided, NULL) AS IsTaxIdentifierProvided,
        ti.ReasonNumberNotProvided AS FenEReasonNumberNotProvidedId,
        lookupReasonNumberNotProvided.EValue AS FenEReasonNumberNotProvided,
        lookupReasonNumberNotProvided.XValue AS FenXReasonNumberNotProvided,
        e2x.BitToYesNo(ti.IsTaxResident, NULL) AS IsTaxResident,
        ti.Comments AS Comments,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.TaxIdentifier AS ti
    INNER JOIN dbo.LegalEntity AS le
        ON le.Id = ti.LegalEntityId
    LEFT JOIN e2x.Lookups AS lookupCountry
        ON lookupCountry.LookupName = 'Country'
        AND lookupCountry.EId = ti.CountryId
    LEFT JOIN e2x.Lookups AS lookupTaxIdType
        ON lookupTaxIdType.LookupName = 'TaxId'
        AND lookupTaxIdType.EId = ti.TaxTypeId
    LEFT JOIN e2x.Lookups AS lookupTaxIdStatus
        ON lookupTaxIdStatus.LookupName = 'LookupTaxIdentifierStatus'
        AND lookupTaxIdStatus.EId = ti.StatusId
    LEFT JOIN e2x.Lookups AS lookupReasonNumberNotProvided
        ON lookupReasonNumberNotProvided.LookupName = 'LookupTaxIdentifierReasonNumberNotProvided'
        AND lookupReasonNumberNotProvided.EId = ti.ReasonNumberNotProvided;
END;