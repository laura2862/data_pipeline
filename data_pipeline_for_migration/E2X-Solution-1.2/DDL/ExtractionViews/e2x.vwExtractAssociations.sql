CREATE OR ALTER VIEW e2x.vwExtractAssociations
AS
SELECT
    stag.AlternateId,
    stag.SourceEntityType,
    stag.SourceAlternateId,
    stag.TargetEntityType,
    stag.TargetAlternateId,
    stag.Relationship,
    stag.Direction,
    stag.OwnershipPercentage
FROM e2x.StagingAssociations AS stag
WHERE
    EXISTS
    (
        SELECT 1
        FROM e2x.vwLegalEntitiesInScope AS src
        WHERE src.LegalEntityId = stag.SourceAlternateId
    )
    AND EXISTS
    (
        SELECT 1
        FROM e2x.vwLegalEntitiesInScope AS tgt
        WHERE tgt.LegalEntityId = stag.TargetAlternateId
    );
