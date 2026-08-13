CREATE OR ALTER VIEW [e2x].[vwMAS]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_MAS] AS mas
    ON base.LatestClassificationId = mas.ClassificationId
   AND base.ClassificationKind = 'MAS';
