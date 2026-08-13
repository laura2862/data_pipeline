CREATE OR ALTER VIEW [e2x].[vwMiFIDII]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_MiFIDII] AS mifidII
    ON base.LatestClassificationId = mifidII.ClassificationId
   AND base.ClassificationKind = 'MiFIDII';
