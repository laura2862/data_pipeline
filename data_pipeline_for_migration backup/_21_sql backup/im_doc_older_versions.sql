/* All iManage KYC docs - Non-latest versions only */

WITH Workspace_Docs AS
(
    SELECT DISTINCT
        dm.docnum,
        dm.version
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

Client_Docs AS
(
    SELECT DISTINCT
        dm.docnum,
        dm.version
    FROM mhgroup.docmaster dm WITH (NOLOCK)
    WHERE UPPER(dm.c2alias) LIKE '%KYC_ONBOARDING%'
      AND dm.[type] = 'D'
      AND NOT EXISTS
      (
          SELECT 1
          FROM Workspace_Docs wd
          WHERE wd.docnum = dm.docnum
      )
),

Doc_List AS
(
    SELECT
        docnum,
        version,
        'Workspace' AS byKYC
    FROM Workspace_Docs

    UNION ALL

    SELECT
        docnum,
        version,
        'Client' AS byKYC
    FROM Client_Docs
),

Version_Ranking AS
(
    SELECT
        docnum,
        version,
        byKYC,
        ROW_NUMBER() OVER
        (
            PARTITION BY docnum
            ORDER BY version DESC
        ) AS rn,
        COUNT(*) OVER
        (
            PARTITION BY docnum
        ) AS version_count
    FROM Doc_List
)

SELECT
    docnum,
    version,
    byKYC
FROM Version_Ranking
WHERE version_count > 1   -- only docs with multiple versions
  AND rn > 1             -- exclude latest version
ORDER BY
    docnum,
    version;