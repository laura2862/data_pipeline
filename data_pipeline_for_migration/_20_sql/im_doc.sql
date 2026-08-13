/* All iManage KYC docs - All versions */
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
)


select * from Doc_List;
--where byKYC = 'Client'
--where byKYC =   'Workspace'
