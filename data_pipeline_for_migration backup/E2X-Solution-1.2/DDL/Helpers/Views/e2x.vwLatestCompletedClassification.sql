CREATE OR ALTER VIEW [e2x].[vwLatestCompletedClassification]
AS
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
            WHEN cls.TypeId IN (5, 105)                 THEN 'CFIU'              /* Canadian Derivatives Classification */
            WHEN cls.TypeId IN (19, 119)                THEN 'CRS'               /* CRS Classification */
            WHEN cls.TypeId IN (2, 4)                   THEN 'DFA'               /* Dodd-Frank Classification */
            WHEN cls.TypeId IN (280000, 280100)         THEN 'DGSD'              /* DGSD Classification */
            WHEN cls.TypeId IN (10004, 10014)           THEN 'UKEMIR'            /* UK EMIR Classification */
            WHEN cls.TypeId IN (7, 107)                 THEN 'EMIR'              /* EEA EMIR Classification */
            WHEN cls.TypeId IN (20, 120)                THEN 'FINRA'             /* FINRA Rule 2111 Classification */
            WHEN cls.TypeId IN (15, 115)                THEN 'MAS'               /* MAS Classification */
            WHEN cls.TypeId IN (11, 111)                THEN 'MiFIDII'           /* MiFID II Classification */
            WHEN cls.TypeId IN (2001, 2002, 2101, 2102) THEN 'USTax'             /* US Tax Classification */
            WHEN cls.TypeId IN (2003, 2004, 2103, 2104) THEN 'USTaxRelatedParty' /* US Tax Related Party Classification */
        END AS ClassificationKind,

        CASE
            WHEN cls.TypeId IN
            (
                105,      /* Standalone Canadian Derivatives */
                119,      /* Standalone CRS */
                4,        /* Standalone Dodd-Frank */
                280100,   /* Standalone DGSD */
                10014,    /* Standalone UK EMIR */
                107,      /* Standalone EEA EMIR */
                120,      /* Standalone FINRA Rule 2111 */
                115,      /* Standalone MAS */
                111,      /* Standalone MiFID II */
                2101,     /* Standalone US Tax */
                2102,     /* Standalone US Tax */
                2103,     /* Standalone US Tax Related Party */
                2104      /* Standalone US Tax Related Party */
            )
            THEN 1
            ELSE 0
        END AS IsStandalone,

        CASE
            WHEN cls.TypeId IN
            (
                105,      /* Standalone Canadian Derivatives */
                119,      /* Standalone CRS */
                4,        /* Standalone Dodd-Frank */
                280100,   /* Standalone DGSD */
                10014,    /* Standalone UK EMIR */
                107,      /* Standalone EEA EMIR */
                120,      /* Standalone FINRA Rule 2111 */
                115,      /* Standalone MAS */
                111,      /* Standalone MiFID II */
                2101,     /* Standalone US Tax */
                2102,     /* Standalone US Tax */
                2103,     /* Standalone US Tax Related Party */
                2104      /* Standalone US Tax Related Party */
            )
            THEN 1

            WHEN wft.StatusId = 2 /* Completed */
            THEN 1

            ELSE 0
        END AS IsEligible

    FROM [classification].[Classification] cls

    INNER JOIN [classification].[LuCfTp] lu
        ON lu.Id = cls.TypeId

    LEFT JOIN [wf].[WFTask] wft
        ON wft.Id = cls.TaskId

    LEFT JOIN [dbo].[Case] c
        ON c.Id = wft.ParentCaseId

    WHERE cls.StatusId = 1
      AND cls.TypeId IN
      (
          5, 105,                    /* Canadian Derivatives */
          19, 119,                   /* CRS */
          2, 4,                      /* Dodd-Frank */
          280000, 280100,            /* DGSD */
          10004, 10014,              /* UK EMIR */
          7, 107,                    /* EEA EMIR */
          20, 120,                   /* FINRA Rule 2111 */
          15, 115,                   /* MAS */
          11, 111,                   /* MiFID II */
          2001, 2002, 2101, 2102,    /* US Tax */
          2003, 2004, 2103, 2104     /* US Tax Related Party */
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
    FROM Base b
    WHERE b.IsEligible = 1
)
SELECT
    LegalEntityId,
    ClassificationKind,
    TypeId,
    ClassificationId AS LatestClassificationId,
    ClassificationName,
    ClassificationFriendlyName
FROM Ranked
WHERE rn = 1;
GO