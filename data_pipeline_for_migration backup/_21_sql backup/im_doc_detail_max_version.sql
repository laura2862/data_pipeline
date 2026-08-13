--select *
--from mhgroup.doctypes
--order by appextension


--select t_alias,is_hipaa,*
--from mhgroup.docmaster

/* DOC details
max document version
lastest workspace if a doc linked with more than one workspaces

*/
WITH Workspace_Name AS
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
      AND w.prj_id = w.tree_id
      AND w.subtype = 'work'
),

Latest_Doc AS
(
    SELECT
        dm.docnum,

        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            ISNULL(wn.workspace_name,'')
            , '"', ' ')
            , ',', ' ')
            , CHAR(13), ' ')
            , CHAR(10), ' ')
            , CHAR(9), ' ') AS workspace_name,

        dm.version,

        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            ISNULL(dm.docname,'')
            , '"', ' ')
            , ',', ' ')
            , CHAR(13), ' ')
            , CHAR(10), ' ')
            , CHAR(9), ' ') AS docname,

		-- adjusted docname with extention
		REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
			ISNULL(CAST(dm.docnum AS varchar(50)), '') 
			, '"', ' ')
			, ',', ' ')
			, CHAR(13), ' ')
			, CHAR(10), ' ')
			, CHAR(9), ' ') 
			+ '.'
			+ CAST(dm.version as varchar(3))
			+ ISNULL(
				CASE
					WHEN LTRIM(RTRIM(dt.appextension)) <> ''
					THEN '.' + lower(LTRIM(RTRIM(dt.appextension)))
				END,
				''
			)

			
			
			AS FriendlyDocName,


        dm.c1alias,

        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            ISNULL(c1.C_DESCRIPT,'')
            , '"', ' ')
            , ',', ' ')
            , CHAR(13), ' ')
            , CHAR(10), ' ')
            , CHAR(9), ' ') AS C_DESCRIPT,

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
		dt.appextension,
		dm.Is_HIPAA,

        ROW_NUMBER() OVER
        (
            PARTITION BY dm.docnum
            ORDER BY dm.version DESC
        ) AS rn

    FROM mhgroup.docmaster dm WITH (NOLOCK)
    LEFT JOIN Workspace_Name wn
        ON dm.docnum = wn.docnum
       AND wn.rn = 1
    LEFT JOIN mhgroup.CUSTOM1 c1 WITH (NOLOCK)
        ON dm.c1alias = c1.CUSTOM_ALIAS
	 LEFT JOIN mhgroup.doctypes dt  -- appExtension as file extension
        ON dm.t_alias = dt.t_alias
    WHERE dm.[type] = 'D'
)

SELECT 
    docnum,
	FriendlyDocName,
	workspace_name,
	docname,
    version,
    c1alias,
	appextension,
	C_DESCRIPT,
    c2alias,
    author,
    t_alias,
    subclass_alias,
    [type],
    docsize,
    entrywhen,
    editwhen,
    editprofilewhen,
    fileentrywhen,
    fileeditwhen,
    docloc,
    Operator,
	Is_HIPAA
FROM Latest_Doc
WHERE rn = 1
order by docnum asc, c1alias asc;

