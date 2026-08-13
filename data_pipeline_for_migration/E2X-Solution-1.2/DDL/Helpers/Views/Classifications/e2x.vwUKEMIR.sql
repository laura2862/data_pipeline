CREATE OR ALTER VIEW [e2x].[vwUKEMIR]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_EMIR] AS ukEmir
    ON base.LatestClassificationId = ukEmir.ClassificationId
   AND base.ClassificationKind = 'UKEMIR';
