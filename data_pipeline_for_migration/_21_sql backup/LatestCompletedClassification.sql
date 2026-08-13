WITH Base AS
(
    SELECT
        cls.LegalEntityId,
        cls.TypeId,
        cls.Id AS ClassificationId,
        cls.CreatedDate,
        lu.Name AS ClassificationName,
        lu.FriendlyName AS ClassificationFriendlyName,

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

        CASE
            WHEN cls.TypeId IN (5, 105)                 THEN 'CFIU'
            WHEN cls.TypeId IN (19, 119)                THEN 'CRS'
            WHEN cls.TypeId IN (2, 4)                   THEN 'DFA'
            WHEN cls.TypeId IN (280000, 280100)         THEN 'DGSD'
            WHEN cls.TypeId IN (10004, 10014)           THEN 'UKEMIR'
            WHEN cls.TypeId IN (7, 107)                 THEN 'EMIR'
            WHEN cls.TypeId IN (20, 120)                THEN 'FINRA'
            WHEN cls.TypeId IN (15, 115)                THEN 'MAS'
            WHEN cls.TypeId IN (11, 111)                THEN 'MiFIDII'
            WHEN cls.TypeId IN (2001, 2002, 2101, 2102) THEN 'USTax'
            WHEN cls.TypeId IN (2003, 2004, 2103, 2104) THEN 'USTaxRelatedParty'
        END AS ClassificationKind,

        CASE
            WHEN cls.TypeId IN
            (
                105,
                119,
                4,
                280100,
                10014,
                107,
                120,
                115,
                111,
                2101,
                2102,
                2103,
                2104
            )
            THEN 1
            ELSE 0
        END AS IsStandalone,

        CASE
            WHEN cls.TypeId IN
            (
                105,
                119,
                4,
                280100,
                10014,
                107,
                120,
                115,
                111,
                2101,
                2102,
                2103,
                2104
            )
            THEN 1

            WHEN wft.StatusId = 2
            THEN 1

            ELSE 0
        END AS IsEligible

    FROM classification.Classification AS cls

    INNER JOIN classification.LuCfTp AS lu
        ON lu.Id = cls.TypeId

    INNER JOIN dbo.LegalEntity AS le
        ON le.Id = cls.LegalEntityId

    LEFT JOIN wf.WFTask AS wft
        ON wft.Id = cls.TaskId

    LEFT JOIN dbo.[Case] AS c
        ON c.Id = wft.ParentCaseId

    WHERE cls.StatusId = 1
        AND cls.TypeId IN
        (
            5, 105,
            19, 119,
            2, 4,
            280000, 280100,
            10004, 10014,
            7, 107,
            20, 120,
            15, 115,
            11, 111,
            2001, 2002, 2101, 2102,
            2003, 2004, 2103, 2104
        )

        AND ISNULL(le.IsDeleted, 0) <> 1

        AND
        (
            EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LegalEntityRoleStatusId = 3
            )

            OR

            EXISTS
            (
                SELECT 1
                FROM dbo.LEAssociate AS ler
                WHERE ler.LegalEntityId = le.Id
                    AND ler.Active = 1
                    AND ler.LEAssociateTypeID = 101
                    AND ler.LegalEntityRoleStatusId = 8
            )
        )
),
Ranked AS
(
    SELECT
        b.*,
        ROW_NUMBER() OVER
        (
            PARTITION BY
                b.LegalEntityId,
                b.ClassificationKind
            ORDER BY
                b.ClassificationId DESC
        ) AS rn
    FROM Base AS b
    WHERE b.IsEligible = 1
)
SELECT
    LegalEntityId,
    IsOffboarded,
    ClassificationKind,
    TypeId,
    ClassificationId AS LatestClassificationId,
    ClassificationName,
    ClassificationFriendlyName
FROM Ranked
WHERE rn = 1
ORDER BY
    LegalEntityId,
    ClassificationKind;