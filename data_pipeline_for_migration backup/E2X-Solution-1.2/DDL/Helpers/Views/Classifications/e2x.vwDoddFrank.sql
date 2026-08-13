CREATE OR ALTER VIEW [e2x].[vwDoddFrank]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_DFA] AS doddFrank
    ON base.LatestClassificationId = doddFrank.ClassificationId
   AND base.ClassificationKind = 'DFA';
