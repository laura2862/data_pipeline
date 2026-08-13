CREATE OR ALTER VIEW [e2x].[vwFINRA]
AS
SELECT
    base.LegalEntityId,
    base.TypeId,
    base.LatestClassificationId,
    base.ClassificationName,
    base.ClassificationFriendlyName,

    finra.SuitabilityCertificateProvided,
	finra.SuitabilityCertificateSource,
	finra.SuitabilityCertificateComment,
	finra.EntityClassification,
	finra.TotalAssetsGt50,
	finra.InvRisksIndependent,
	finra.IndependentJudgement,
	finra.DilligencePerformed,
	finra.IrrelevantInvFactorsComments,
	finra.RecommendationsMade,
	finra.RecommendationsNotExcessive
FROM [e2x].[vwLatestCompletedClassification] AS base
INNER JOIN [classification].[Classification_FINRA] AS finra
    ON base.LatestClassificationId = finra.ClassificationId
   AND base.ClassificationKind = 'FINRA';
