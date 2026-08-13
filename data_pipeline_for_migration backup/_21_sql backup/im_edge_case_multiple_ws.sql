WITH ws AS
(
    SELECT
        dm.docnum,
        dm.version,
        COUNT(DISTINCT w.prj_id) AS workspace_c1alias_count,
        'Multi_workspaces' AS Doc_Group
    FROM mhgroup.project_items pi WITH (NOLOCK)
    INNER JOIN mhgroup.projects p WITH (NOLOCK)
        ON pi.prj_id = p.prj_id
    INNER JOIN mhgroup.projects w WITH (NOLOCK)
        ON p.tree_id = w.prj_id
    INNER JOIN mhgroup.docmaster dm WITH (NOLOCK)
        ON dm.docnum = pi.item_id
        AND dm.[type] = 'D'
    WHERE w.prj_id = w.tree_id
      AND w.subtype = 'work'
      AND UPPER(w.prj_name) LIKE '%KYC ONBOARDING%'
    GROUP BY dm.docnum, dm.version
    HAVING COUNT(DISTINCT w.prj_id) > 1
),
c AS
(
    SELECT
        d.docnum,
        d.version,
        x.workspace_c1alias_count,
        'Multi_c1alias' AS Doc_Group
    FROM mhgroup.docmaster d WITH (NOLOCK)
    INNER JOIN
    (
        SELECT
            docnum,
            COUNT(DISTINCT ISNULL(c1alias,'<<NULL>>')) AS workspace_c1alias_count
        FROM mhgroup.docmaster WITH (NOLOCK)
        WHERE UPPER(c2alias) LIKE '%KYC_ONBOARDING%'or c2alias is null
          AND [type] = 'D'
        GROUP BY docnum
        HAVING COUNT(DISTINCT ISNULL(c1alias,'<<NULL>>')) > 1
    ) x
        ON d.docnum = x.docnum
    WHERE UPPER(d.c2alias) LIKE '%KYC_ONBOARDING%' or c2alias is null
      AND d.[type] = 'D'
)

SELECT *
FROM c

UNION ALL

SELECT *
FROM ws

ORDER BY docnum, version;

/*555355
2719749
2741925*/