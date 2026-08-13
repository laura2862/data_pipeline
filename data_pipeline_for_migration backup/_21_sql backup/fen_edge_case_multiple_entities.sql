with DocToLE AS ( /* 1) Documents linked directly to Legal Entity: BusinessEntityId = 30 */ 
SELECT DISTINCT lde.DocumentId, lde.EntityId AS LegalEntityId 
FROM dbo.LinkDocumentEntity lde WITH (NOLOCK) 
WHERE lde.BusinessEntityId = 30 AND lde.DocumentId IS NOT NULL 

UNION  

/* 2) Documents linked to Case: BusinessEntityId = 1 Then map Case back to Legal Entity through LegalEntityAssociation */  

SELECT DISTINCT lde.DocumentId, lea.LegalEntityId 
FROM dbo.LinkDocumentEntity lde WITH (NOLOCK) 
INNER JOIN dbo.LegalEntityAssociation lea WITH (NOLOCK) ON lea.EntityId = lde.EntityId AND lea.BusinessEntityId = 1 
WHERE lde.BusinessEntityId = 1 AND lde.DocumentId IS NOT NULL AND lea.LegalEntityId IS NOT NULL ),  

DupDocs AS( 
select DocumentId from DocToLE GROUP BY DocumentId having count(distinct legalentityid)>1 
) 

select --count (distinct d.id)--
d.Id AS DocumentId, d.Name AS DocumentName, d.Location as DocLink, 
CASE WHEN d.Location IS NULL OR d.Location not like '%document%' THEN 'InvalidDocLink' ELSE CAST( TRY_CONVERT(INT, CASE WHEN d.Location LIKE '%!document:%' THEN SUBSTRING( d.Location, CHARINDEX('!document:', d.Location) + LEN('!document:'), CHARINDEX(',', d.Location) - (CHARINDEX('!document:', d.Location) + LEN('!document:')) ) ELSE NULL END ) AS VARCHAR(50) ) END AS iManage_Doc_Num,  
CASE WHEN d.Location IS NULL OR d.Location not like '%document%' THEN 'InvalidDocLink' ELSE CAST( TRY_CONVERT(int, CASE WHEN d.Location LIKE '%!document:%' AND CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) > 0 AND CHARINDEX(':', d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) > 0 THEN SUBSTRING( d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1, CHARINDEX(':', d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) - (CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) ) ELSE NULL END ) AS VARCHAR(50) )END AS iManage_Doc_Version,  
CASE WHEN d.Location IS NULL  THEN 0 ELSE 1 End as IsValidDocLink,
m.LegalEntityId, le.Name AS LegalEntityName, letp.Name AS LeType, le.ReferenceId, 
dstatus.Name AS DocumentStatus, dtype.Name AS DocType, ddir.Name AS DocDirection, dpurpose.Name AS DocPurpose, dcat.Name AS DocCategory,
d.LastUpdatedDate, d.LastUpdatedBy, d.CreatedDate, d.CreatedBy

from DupDocs dd 
inner join DocToLE m on dd.DocumentId =m.DocumentId 
LEFT JOIN Document d WITH (NOLOCK) ON d.Id = m.DocumentId 
LEFT JOIN LegalEntity le WITH (NOLOCK) ON le.Id = m.LegalEntityId 
LEFT JOIN LookupDocumentStatus dstatus WITH (NOLOCK) ON dstatus.Id = d.LookupDocumentStatusId 
LEFT JOIN DocumentType dtype WITH (NOLOCK) ON dtype.Id = d.DocumentTypeId 
LEFT JOIN LookupDocumentDirection ddir WITH (NOLOCK) ON ddir.Id = d.LookupDocumentDirectionId 
LEFT JOIN DocumentPurpose dpurpose WITH (NOLOCK) ON dpurpose.Id = d.DocumentPurposeId 
LEFT JOIN DocumentCategory dcat WITH (NOLOCK) ON dcat.Id = d.DocumentCategoryId 
LEFT JOIN LuLeSubTp letp WITH (NOLOCK) ON letp.Id = le.LegalEntitySubtypeId 
ORDER BY d.Id, le.Id;