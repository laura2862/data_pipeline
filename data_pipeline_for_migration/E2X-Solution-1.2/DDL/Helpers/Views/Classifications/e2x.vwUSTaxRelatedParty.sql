CREATE OR ALTER VIEW [e2x].[vwUSTaxRelatedParty]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_FATCA] AS usTaxRelatedParty
    ON base.LatestClassificationId = usTaxRelatedParty.ClassificationId
   AND base.ClassificationKind = 'USTaxRelatedParty';
