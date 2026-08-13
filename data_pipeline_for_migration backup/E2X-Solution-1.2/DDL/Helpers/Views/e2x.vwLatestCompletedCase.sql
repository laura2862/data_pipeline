CREATE OR ALTER VIEW [e2x].[vwLatestCompletedCase]
AS
WITH LatestClosedCompletedCase AS (
    SELECT 
        le.Id AS LegalEntityId,
        c.Id AS CaseId,
        c.CaseTypeId,
        c.LastUpdatedDate,
        ROW_NUMBER() OVER (
            PARTITION BY le.Id 
            ORDER BY c.LastUpdatedDate DESC
        ) AS rn
    FROM dbo.LegalEntity le
    LEFT JOIN dbo.LegalEntityAssociation leass 
        ON leass.LegalEntityId = le.Id
       AND leass.BusinessEntityId = 1
       AND (leass.LookupLegalEntityAssociationId = 9 OR leass.LookupLegalEntityAssociationId = 10 OR leass.LookupLegalEntityAssociationId IS NULL)
       AND leass.IsDeleted = 0
    LEFT JOIN dbo.[Case] c 
        ON leass.EntityId = c.Id
    WHERE c.MaintenanceStatusId = 239   -- Closed
      AND c.CaseStatusId = 5001         -- Complete
)
SELECT 
    le.Id AS LegalEntityId,
    lc.CaseId,
    ct.Name AS CaseType,
    lc.LastUpdatedDate
FROM dbo.LegalEntity le
LEFT JOIN LatestClosedCompletedCase lc
    ON le.Id = lc.LegalEntityId
   AND lc.rn = 1
LEFT JOIN dbo.CaseType ct
    ON lc.CaseTypeId = ct.Id
GO