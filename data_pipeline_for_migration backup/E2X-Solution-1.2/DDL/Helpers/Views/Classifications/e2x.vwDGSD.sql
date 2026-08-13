CREATE OR ALTER VIEW [e2x].[vwDGSD]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName,
	dgsd.DGSDLegalEntityType,
	dgsd.UnderlyingCompany,
	dgsd.Budget,
	dgsd.NumberOfEmployees,
	dgsd.AnnualTurnOver,
	dgsd.AnnualBalanceSheet,
	dgsd.FinalDGSDLegalEntityType,
	dgsd.CounterPartyEligibility
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_DGSD] AS dgsd
    ON base.LatestClassificationId = dgsd.ClassificationId
   AND base.ClassificationKind = 'DGSD';
