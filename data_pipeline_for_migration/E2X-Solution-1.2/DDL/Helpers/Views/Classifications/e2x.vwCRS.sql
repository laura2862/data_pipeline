CREATE OR ALTER VIEW [e2x].[vwCRS]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_CRS] AS crs
    ON base.LatestClassificationId = crs.ClassificationId
   AND base.ClassificationKind = 'CRS';
