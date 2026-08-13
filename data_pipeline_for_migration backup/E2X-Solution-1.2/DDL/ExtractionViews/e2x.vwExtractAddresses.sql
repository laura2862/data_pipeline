CREATE OR ALTER VIEW e2x.vwExtractAddresses
AS
SELECT DISTINCT
    stag.LegalEntityId,
    stag.AddressId AS fenEId,
    stag.AlternateId,
    stag.ParentAlternateId,
    stag.FenEAddressTypeId,
    stag.FenEAddressType,
    stag.FenXAddressType AS addressType,
    stag.FenECountryId,
    stag.FenECountry,
    stag.FenXCountry AS country,
    stag.Town AS city,
    stag.ZipCode AS postalCode,
    stag.Line1 AS addressLine1,
    stag.Line2 AS addressLine2,
    stag.Line3 AS addressLine3,
    stag.Line4 AS addressLine4
FROM e2x.StagingAddresses AS stag;
