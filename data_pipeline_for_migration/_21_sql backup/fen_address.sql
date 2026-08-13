WITH entityAddress AS (
    SELECT
        le.id AS LegalEntityId,
        lae.AddressId,
        addr.Active,
        c.CountryCode AS Country,
        addr.FullAddress,
        addr.CreatedDate,
        addr.LastUpdatedDate,
        adtp.Name AS AddressType,
        adgp.Name AS AddressGroup
    FROM LegalEntity le
    INNER JOIN LinkAddressEntity lae
        ON le.Id = lae.EntityId
    LEFT JOIN Address addr
        ON addr.Id = lae.AddressId
    LEFT JOIN LookupAddressType adtp
        ON adtp.Id = addr.AddressTypeId
    LEFT JOIN LookupAddressGroup adgp
        ON adtp.AddressGroupId = adgp.Id
    LEFT JOIN Country c
        ON addr.CountryId = c.Id
),
RankedAddresses AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY LegalEntityId, AddressType
            ORDER BY LastUpdatedDate DESC, AddressId DESC
        ) AS rn
    FROM entityAddress
)


SELECT DISTINCT *
FROM RankedAddresses
WHERE rn = 1;