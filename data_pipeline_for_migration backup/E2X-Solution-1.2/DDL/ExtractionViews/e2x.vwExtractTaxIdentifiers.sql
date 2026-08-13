CREATE OR ALTER VIEW e2x.vwExtractTaxIdentifiers
AS
SELECT DISTINCT
    stag.LegalEntityId,
    stag.TaxIdentifierId AS fenEId,
    stag.AlternateId,
    stag.ParentAlternateId,
    stag.FenECountryId,
    stag.FenECountry AS FenECountry,
    stag.FenXCountry AS country,
    stag.FenETypeId,
    stag.FenEType AS FenEType,
    stag.FenXType AS taxIdentifierType,
    stag.TaxIdentifierValue AS taxValue,
    stag.FenEStatusId,
    stag.FenEStatus AS FenEStatus,
    stag.FenXStatus AS [status],
    stag.IsTaxIdentifierProvided AS taxIdentifierProvided,
    stag.FenEReasonNumberNotProvidedId,
    stag.FenEReasonNumberNotProvided AS FenEReasonNumberNotProvided,
    stag.FenXReasonNumberNotProvided AS reasonNumberNotProvided,
    stag.IsTaxResident AS taxResident,
    stag.Comments AS comments
FROM e2x.StagingTaxIdentifiers AS stag;
