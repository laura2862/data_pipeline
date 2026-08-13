CREATE OR ALTER VIEW [e2x].[vwUSTax]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_FATCA] AS usTax
    ON base.LatestClassificationId = usTax.ClassificationId
   AND base.ClassificationKind = 'USTax';
