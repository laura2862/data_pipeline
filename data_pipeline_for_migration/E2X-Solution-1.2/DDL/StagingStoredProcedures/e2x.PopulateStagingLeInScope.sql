CREATE OR ALTER PROCEDURE e2x.PopulateStagingLeInScope
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingLeInScope;

    INSERT INTO e2x.StagingLeInScope
    (
        LegalEntityId,
        IsCustomer,
        IsOffboarded,
        LoadTimestamp
    )
    SELECT
        le.Id AS LegalEntityId,

        -- Active Client/Counterparty role.
        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LEAssociateTypeID = 101
                    AND ler.LegalEntityRoleStatusId = 3
            )
            THEN 1
            ELSE 0
        END AS IsCustomer,

        -- Offboarded Client/Counterparty role.
        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LEAssociateTypeID = 101
                    AND ler.LegalEntityRoleStatusId = 8
            )
            THEN 1
            ELSE 0
        END AS IsOffboarded,

        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.LegalEntity AS le
    WHERE ISNULL(le.IsDeleted, 0) <> 1

        -- Explicit Legal Entity exclusion.
        AND NOT EXISTS
        (
            SELECT 1
            FROM e2x.ExcludedLegalEntities AS ele
            WHERE ele.LegalEntityId = le.Id
        )

        AND
        (
            -- Include entities with at least one active role.
            EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LegalEntityRoleStatusId = 3
            )

            OR

            -- Or with an offboarded Client/Counterparty role.
            EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LEAssociateTypeID = 101
                    AND ler.LegalEntityRoleStatusId = 8
            )
        );
END;
GO