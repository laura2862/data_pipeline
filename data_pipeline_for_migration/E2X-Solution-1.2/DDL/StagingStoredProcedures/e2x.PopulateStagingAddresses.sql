CREATE OR ALTER PROCEDURE e2x.PopulateStagingAddresses
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingAddresses;

    ;WITH RankedAddresses AS
    (
        SELECT
            addr2e.EntityId AS LegalEntityId,
            addr.Id AS AddressId,
            addr.AddressTypeId,
            addr.CountryId,
            addr.Town,
            addr.ZipCode,
            addr.Line1,
            addr.Line2,
            addr.Line3,
            addr.Line4,
            addr.LastUpdatedDate,
            ROW_NUMBER() OVER
            (
                PARTITION BY addr2e.EntityId, addr.AddressTypeId
                ORDER BY addr.LastUpdatedDate DESC, addr.Id DESC
            ) AS rn
        FROM dbo.[Address] AS addr
        INNER JOIN dbo.LinkAddressEntity AS addr2e
            ON addr2e.AddressId = addr.Id
            AND addr2e.BusinessEntityId = 30
        -- Keep only the most recently updated address of each type per Legal Entity.
        WHERE addr.Active = 1
    )

    INSERT INTO e2x.StagingAddresses
    (
        LegalEntityId,
        AddressId,
        AlternateId,
        ParentAlternateId,
        FenEAddressTypeId,
        FenEAddressType,
        FenXAddressType,
        FenECountryId,
        FenECountry,
        FenXCountry,
        Town,
        ZipCode,
        Line1,
        Line2,
        Line3,
        Line4,
        LoadTimestamp
    )
    SELECT
        ra.LegalEntityId,
        ra.AddressId,
        'ADD' + CAST(ra.AddressId AS VARCHAR(50)) AS AlternateId,
        CAST(ra.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        ra.AddressTypeId AS FenEAddressTypeId,
        lookupAddressType.EValue AS FenEAddressType,
        lookupAddressType.XValue AS FenXAddressType,
        ra.CountryId AS FenECountryId,
        lookupCountry.EValue AS FenECountry,
        lookupCountry.XValue AS FenXCountry,
        ra.Town,
        ra.ZipCode,
        ra.Line1,
        ra.Line2,
        ra.Line3,
        ra.Line4,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM RankedAddresses AS ra
    LEFT JOIN e2x.Lookups AS lookupAddressType
        ON lookupAddressType.LookupName = 'LookupAddressType'
        AND lookupAddressType.EId = ra.AddressTypeId
    LEFT JOIN e2x.Lookups AS lookupCountry
        ON lookupCountry.LookupName = 'Country'
        AND lookupCountry.EId = ra.CountryId
    WHERE ra.rn = 1;
END;