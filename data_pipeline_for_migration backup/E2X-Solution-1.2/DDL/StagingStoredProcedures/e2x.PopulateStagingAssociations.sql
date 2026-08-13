CREATE OR ALTER PROCEDURE e2x.PopulateStagingAssociations
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingAssociations;

    ;WITH DeduplicatedAssociations AS
    (
        SELECT
            leas.*,
            ROW_NUMBER() OVER
            (
                PARTITION BY
                    leas.LegalEntityId,
                    leas.EntityId,
                    leas.LookupLegalEntityAssociationId,
                    leas.LookupAssociationStatusId
                ORDER BY leas.Id DESC
            ) AS RowNumber
        FROM dbo.LegalEntityAssociation AS leas
        WHERE leas.BusinessEntityId = 30
            AND leas.IsDeleted = 0
            AND leas.LookupAssociationStatusId = 1
            AND leas.LookupLegalEntityAssociationId IS NOT NULL
    )

    INSERT INTO e2x.StagingAssociations
    (
        AlternateId,
        SourceEntityType,
        SourceAlternateId,
        TargetEntityType,
        TargetAlternateId,
        Relationship,
        Direction,
        OwnershipPercentage,
        LoadTimestamp
    )
    SELECT
        CONCAT('LEASSOC', leas.Id) AS AlternateId,

        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LinkLuLeTpLuLeSt link
                WHERE link.LegalEntitySubtypeId = sourceEntity.LegalEntitySubtypeId
                  AND link.LegalEntityTypeId = 3
            ) THEN 'Company'

            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LinkLuLeTpLuLeSt link
                WHERE link.LegalEntitySubtypeId = sourceEntity.LegalEntitySubtypeId
                  AND link.LegalEntityTypeId = 4
            ) THEN 'Individual'
        END AS SourceEntityType,

        leas.LegalEntityId AS SourceAlternateId,

        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LinkLuLeTpLuLeSt link
                WHERE link.LegalEntitySubtypeId = targetEntity.LegalEntitySubtypeId
                  AND link.LegalEntityTypeId = 3
            ) THEN 'Company'

            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LinkLuLeTpLuLeSt link
                WHERE link.LegalEntitySubtypeId = targetEntity.LegalEntitySubtypeId
                  AND link.LegalEntityTypeId = 4
            ) THEN 'Individual'
        END AS TargetEntityType,

        leas.EntityId AS TargetAlternateId,

        lookupAssociation.XValue AS Relationship,

        CASE
            WHEN COALESCE(leas.Master, 0) = 0 THEN 'Is A'
            ELSE 'Has A'
        END AS Direction,

        shareholder.Percentage AS OwnershipPercentage,

        CURRENT_TIMESTAMP AS LoadTimestamp

    FROM DeduplicatedAssociations AS leas

    INNER JOIN dbo.LegalEntity AS sourceEntity
        ON sourceEntity.Id = leas.LegalEntityId

    INNER JOIN dbo.LegalEntity AS targetEntity
        ON targetEntity.Id = leas.EntityId

    LEFT JOIN dbo.LeAsShareholder AS shareholder
        ON shareholder.LegalEntityAssociationId = leas.Id

    LEFT JOIN e2x.Lookups AS lookupAssociation
        ON lookupAssociation.LookupName = 'LuLeAs'
       AND lookupAssociation.EId = leas.LookupLegalEntityAssociationId

    WHERE leas.RowNumber = 1

      AND EXISTS
      (
          SELECT 1
          FROM dbo.LinkLuLeTpLuLeSt link
          WHERE link.LegalEntitySubtypeId = sourceEntity.LegalEntitySubtypeId
            AND link.LegalEntityTypeId IN (3, 4)
      )

      AND EXISTS
      (
          SELECT 1
          FROM dbo.LinkLuLeTpLuLeSt link
          WHERE link.LegalEntitySubtypeId = targetEntity.LegalEntitySubtypeId
            AND link.LegalEntityTypeId IN (3, 4)
      );
END;