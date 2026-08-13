CREATE OR ALTER VIEW e2x.vwMultiSelectAgg_LegalEntity_Pivoted
AS
SELECT
    PrimaryId,

    MAX(CASE WHEN FieldName = 'LinkParentEnListedOnEx' THEN FenEIds END) AS FenENameOfExchangesTheParentEntityIsListedOnIds,
    MAX(CASE WHEN FieldName = 'LinkParentEnListedOnEx' THEN FenE END) AS FenENameOfExchangesTheParentEntityIsListedOn,
    MAX(CASE WHEN FieldName = 'LinkParentEnListedOnEx' THEN FenX END) AS FenXNameOfExchangesTheParentEntityIsListedOn,

    MAX(CASE WHEN FieldName = 'LECompanyRegulator' THEN FenEIds END) AS FenERegulatedByIds,
    MAX(CASE WHEN FieldName = 'LECompanyRegulator' THEN FenE END) AS FenERegulatedBy,
    MAX(CASE WHEN FieldName = 'LECompanyRegulator' THEN FenX END) AS FenXRegulatedBy,

    MAX(CASE WHEN FieldName = 'LinkModelExclusions' THEN FenEIds END) AS FenEGlobalModelExclusionsIds,
    MAX(CASE WHEN FieldName = 'LinkModelExclusions' THEN FenE END) AS FenEGlobalModelExclusions,
    MAX(CASE WHEN FieldName = 'LinkModelExclusions' THEN FenX END) AS FenXGlobalModelExclusions,

    MAX(CASE WHEN FieldName = 'LinkSEDDEntityType' THEN FenEIds END) AS FenESpecializedEddEntityTypeIds,
    MAX(CASE WHEN FieldName = 'LinkSEDDEntityType' THEN FenE END) AS FenESpecializedEddEntityType,
    MAX(CASE WHEN FieldName = 'LinkSEDDEntityType' THEN FenX END) AS FenXSpecializedEddEntityType,

    MAX(CASE WHEN FieldName = 'LinkLERegulatoryStatus' THEN FenEIds END) AS FenERegulatoryStatusIds,
    MAX(CASE WHEN FieldName = 'LinkLERegulatoryStatus' THEN FenE END) AS FenERegulatoryStatus,
    MAX(CASE WHEN FieldName = 'LinkLERegulatoryStatus' THEN FenX END) AS FenXRegulatoryStatus,

    MAX(CASE WHEN FieldName = 'LinkLeFinCenExCt' THEN FenEIds END) AS FenEApplicableExemptionCategoriesIds,
    MAX(CASE WHEN FieldName = 'LinkLeFinCenExCt' THEN FenE END) AS FenEApplicableExemptionCategories,
    MAX(CASE WHEN FieldName = 'LinkLeFinCenExCt' THEN FenX END) AS FenXApplicableExemptionCategories,

    MAX(CASE WHEN FieldName = 'LinkEnListedOnEx' THEN FenEIds END) AS FenENameOfExchangesTheEntityIsListedOnIds,
    MAX(CASE WHEN FieldName = 'LinkEnListedOnEx' THEN FenE END) AS FenENameOfExchangesTheEntityIsListedOn,
    MAX(CASE WHEN FieldName = 'LinkEnListedOnEx' THEN FenX END) AS FenXNameOfExchangesTheEntityIsListedOn,

    MAX(CASE WHEN FieldName = 'LinkLEIdnIsiderStatus' THEN FenEIds END) AS FenEInsiderStatusIds,
    MAX(CASE WHEN FieldName = 'LinkLEIdnIsiderStatus' THEN FenE END) AS FenEInsiderStatus,
    MAX(CASE WHEN FieldName = 'LinkLEIdnIsiderStatus' THEN FenX END) AS FenXInsiderStatus,

    MAX(CASE WHEN FieldName = 'LinkSignificantCustomerCountries' THEN FenEIds END) AS FenESignificantCustomerCountriesIds,
    MAX(CASE WHEN FieldName = 'LinkSignificantCustomerCountries' THEN FenE END) AS FenESignificantCustomerCountries,
    MAX(CASE WHEN FieldName = 'LinkSignificantCustomerCountries' THEN FenX END) AS FenXSignificantCustomerCountries,

    MAX(CASE WHEN FieldName = 'LinkSignificantRevenueCountries' THEN FenEIds END) AS FenESignificantRevenueCountriesIds,
    MAX(CASE WHEN FieldName = 'LinkSignificantRevenueCountries' THEN FenE END) AS FenESignificantRevenueCountries,
    MAX(CASE WHEN FieldName = 'LinkSignificantRevenueCountries' THEN FenX END) AS FenXSignificantRevenueCountries,

    MAX(CASE WHEN FieldName = 'LinkSignificantSupplierCountries' THEN FenEIds END) AS FenESignificantSupplierCountriesIds,
    MAX(CASE WHEN FieldName = 'LinkSignificantSupplierCountries' THEN FenE END) AS FenESignificantSupplierCountries,
    MAX(CASE WHEN FieldName = 'LinkSignificantSupplierCountries' THEN FenX END) AS FenXSignificantSupplierCountries
FROM e2x.vwMultiSelectAgg_LegalEntity
GROUP BY PrimaryId;
GO
