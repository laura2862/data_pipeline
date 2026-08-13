CREATE OR ALTER VIEW e2x.vwMultiSelectAgg_LegalEntity
AS
WITH MS AS
(
    SELECT LegalEntityId AS PrimaryId,
           CAST('LinkParentEnListedOnEx' AS sysname) AS FieldName,
           CAST('LookupListenOn' AS sysname) AS LookupName,
           ExchangeId AS EId
    FROM dbo.LinkParentEnListedOnEx

    UNION ALL
    SELECT LegalEntityId,
           CAST('LECompanyRegulator' AS sysname),
           CAST('LookupRegulator' AS sysname),
           RegulatorId
    FROM dbo.LECompany

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkModelExclusions' AS sysname),
           CAST('GlobalModelExclusions' AS sysname),
           GlobalModelExclusionsId
    FROM scotia.LinkModelExclusions

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkSEDDEntityType' AS sysname),
           CAST('SpecializedEDDType' AS sysname),
           SpecializedEDDTypeID
    FROM scotia.LinkSEDDEntityType

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkLERegulatoryStatus' AS sysname),
           CAST('RegulatoryStatus' AS sysname),
           RegStatusId
    FROM scotia.LinkLERegulatoryStatus

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkLeFinCenExCt' AS sysname),
           CAST('FinCENExemptionCategory' AS sysname),
           FinCENExemptionCategoryId
    FROM dbo.LinkLeFinCenExCt

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkEnListedOnEx' AS sysname),
           CAST('LookupListenOn' AS sysname),
           ExchangeId
    FROM dbo.LinkEnListedOnEx

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkLEIdnIsiderStatus' AS sysname),
           CAST('LookUpInsiderStatusList' AS sysname),
           InsiderStatusId
    FROM scotia.LinkLEIdnIsiderStatus

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkSignificantCustomerCountries' AS sysname),
           CAST('Country' AS sysname),
           CountryId
    FROM scotia.LinkSignificantCustomerCountries

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkSignificantRevenueCountries' AS sysname),
           CAST('Country' AS sysname),
           CountryId
    FROM scotia.LinkSignificantRevenueCountries

    UNION ALL
    SELECT LegalEntityId,
           CAST('LinkSignificantSupplierCountries' AS sysname),
           CAST('Country' AS sysname),
           CountryId
    FROM scotia.LinkSignificantSupplierCountries
),
MSD AS
(
    SELECT DISTINCT PrimaryId, FieldName, LookupName, EId
    FROM MS
    WHERE EId IS NOT NULL
),
MSR AS
(
    SELECT
        d.PrimaryId,
        d.FieldName,
        d.EId,
        l.EValue,
        l.XValue
    FROM MSD AS d
    LEFT JOIN e2x.Lookups AS l
        ON l.LookupName = d.LookupName
       AND l.EId = d.EId
),
MSA AS
(
    SELECT
        PrimaryId,
        FieldName,
        STRING_AGG(CONVERT(varchar(max), EId), '|') AS FenEIds,
        STRING_AGG(CONVERT(nvarchar(max), EValue), '|') AS FenE,
        STRING_AGG(CONVERT(nvarchar(max), XValue), '|') AS FenX
    FROM MSR
    GROUP BY PrimaryId, FieldName
)
SELECT PrimaryId, FieldName, FenEIds, FenE, FenX
FROM MSA;
GO
