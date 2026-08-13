CREATE OR ALTER VIEW e2x.vwLegalEntitiesInScope
AS
SELECT DISTINCT
    stag.LegalEntityId
FROM e2x.StagingLeInScope AS stag;
