/*doclist by workspace name 
max version
*/
with workspace_level as  
( 
select prj_id, prj_name, prj_owner, tree_id, editwhen--,subtype 
from mhgroup.projects 
where 
prj_id = tree_id 
AND subtype = 'work' 
AND upper(prj_name) LIKE '%KYC ONBOARDING%' 
) 

select  distinct * from (  
Select 
w.prj_name as 'Workspace',
dm.docnum, 
dm.version, 
dm.docname, 
dm.c1alias,c1.C_DESCRIPT, 
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
ROW_NUMBER() OVER (PARTITION BY dm.docnum ORDER BY dm.version DESC) AS rn 
from mhgroup.projects p WITH (NOLOCK) 
INNER join workspace_level W WITH (NOLOCK) on w.prj_id = p.tree_id 
INNER join mhgroup.project_items b WITH (NOLOCK) on b.PRJ_ID = p.PRJ_ID 
INNER join mhgroup.docmaster dm WITH (NOLOCK) on b.item_id = dm.docnum 
LEFT join MHGROUP.CUSTOM1 c1 WITH (NOLOCK) on dm.C1ALIAS = c1.CUSTOM_ALIAS 
WHERE dm.[type] IN( 'D' ) 
) x 

WHERE x.rn = 1  
Order by x.c1alias asc, x.docnum asc