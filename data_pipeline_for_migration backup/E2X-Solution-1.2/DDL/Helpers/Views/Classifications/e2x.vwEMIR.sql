CREATE OR ALTER VIEW [e2x].[vwEMIR]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_EMIR] AS emir
    ON base.LatestClassificationId = emir.ClassificationId
   AND base.ClassificationKind = 'EMIR';
