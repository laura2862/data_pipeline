/* 
   KYC documents based on client name / C2Alias
   Only keep documents that are NOT already in KYC workspace list
*/

;WITH C2Alias_Base AS
(
    SELECT
        dm.docnum,
        dm.version,
        dm.docname,
        dm.c1alias,
        dm.c2alias,
        dm.author,
        dm.t_alias,
        dm.subclass_alias,
        dm.[type],
        dm.docsize,
        dm.entrywhen,
        dm.editwhen,
        dm.editprofilewhen,
        dm.fileentrywhen,
        dm.fileeditwhen,
        dm.docloc,
        dm.Operator,
        ROW_NUMBER() OVER
        (
            PARTITION BY dm.docnum
            ORDER BY dm.version DESC
        ) AS rn
    FROM mhgroup.docmaster dm WITH (NOLOCK)
    WHERE UPPER(dm.c2alias) LIKE '%KYC_ONBOARDING%'
      AND dm.[type] = 'D'
),

C2Alias_KYC AS
(
    SELECT
        b.docnum,
        b.version,
        b.docname,
        b.c1alias,
        c1.C_DESCRIPT,
        b.c2alias,
        b.author,
        b.t_alias,
        b.subclass_alias,
        b.[type],
        b.docsize,
        b.entrywhen,
        b.editwhen,
        b.editprofilewhen,
        b.fileentrywhen,
        b.fileeditwhen,
        b.docloc,
        b.Operator
    FROM C2Alias_Base b
    LEFT JOIN mhgroup.CUSTOM1 c1 WITH (NOLOCK)
        ON b.c1alias = c1.CUSTOM_ALIAS
    WHERE b.rn = 1
),

Workspace_KYC_Docs AS
(
    SELECT DISTINCT
        pi.item_id AS docnum
    FROM mhgroup.projects w WITH (NOLOCK)
    INNER JOIN mhgroup.projects p WITH (NOLOCK)
        ON p.tree_id = w.prj_id
    INNER JOIN mhgroup.project_items pi WITH (NOLOCK)
        ON pi.prj_id = p.prj_id
    INNER JOIN mhgroup.docmaster dm WITH (NOLOCK)
        ON dm.docnum = pi.item_id
       AND dm.[type] = 'D'
    WHERE w.prj_id = w.tree_id
      AND w.subtype = 'work'
      AND UPPER(w.prj_name) LIKE '%KYC ONBOARDING%'
      AND pi.item_id IS NOT NULL
),

Workspace_Name AS
(
    SELECT
        pi.item_id AS docnum,
        w.prj_name AS workspace_name,
        ROW_NUMBER() OVER
        (
            PARTITION BY pi.item_id
            ORDER BY p.editwhen DESC
        ) AS rn
    FROM mhgroup.project_items pi WITH (NOLOCK)
    INNER JOIN mhgroup.projects p WITH (NOLOCK)
        ON pi.prj_id = p.prj_id
    INNER JOIN mhgroup.projects w WITH (NOLOCK)
        ON p.tree_id = w.prj_id
       AND w.subtype = 'work'
       AND w.prj_id = w.tree_id
)

SELECT
    wn.workspace_name,
    c.docnum,
    c.version,
    c.docname,
    c.c1alias,
    c.C_DESCRIPT,
    c.c2alias,
    c.author,
    c.t_alias,
    c.subclass_alias,
    c.[type],
    c.docsize,
    c.entrywhen,
    c.editwhen,
    c.editprofilewhen,
    c.fileentrywhen,
    c.fileeditwhen,
    c.docloc,
    c.Operator
FROM C2Alias_KYC c
LEFT JOIN Workspace_Name wn
    ON c.docnum = wn.docnum
   AND wn.rn = 1
WHERE NOT EXISTS
(
    SELECT 1
    FROM Workspace_KYC_Docs w
    WHERE w.docnum = c.docnum
)
ORDER BY
    c.c1alias,
    c.docnum;