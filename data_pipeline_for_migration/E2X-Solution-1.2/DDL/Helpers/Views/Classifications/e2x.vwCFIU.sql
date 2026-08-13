CREATE OR ALTER VIEW [e2x].[vwCFIU]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_CFIU] AS cfiu
    ON base.LatestClassificationId = cfiu.ClassificationId
   AND base.ClassificationKind = 'CFIU';
