/* Fenergo Document Details*/  

SELECT distinct d.Id AS DocumentId, 
d.Name AS DocumentName, 
d.Location as DocLink, /* Extract iManage document number from Location when present */ 
CASE WHEN d.Location IS NULL OR d.Location not like '%document%' THEN 'InvalidDocLink' ELSE CAST( TRY_CONVERT(INT, CASE WHEN d.Location LIKE '%!document:%' THEN SUBSTRING( d.Location, CHARINDEX('!document:', d.Location) + LEN('!document:'), CHARINDEX(',', d.Location) - (CHARINDEX('!document:', d.Location) + LEN('!document:')) ) ELSE NULL END ) AS VARCHAR(50) ) END AS iManage_Doc_Num, 
CASE WHEN d.Location IS NULL OR d.Location not like '%document%' THEN 'InvalidDocLink' ELSE CAST( TRY_CONVERT(int, CASE WHEN d.Location LIKE '%!document:%' AND CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) > 0 AND CHARINDEX(':', d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) > 0 THEN SUBSTRING( d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1, CHARINDEX(':', d.Location, CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) - (CHARINDEX(',', d.Location, CHARINDEX('!document:', d.Location)) + 1) ) ELSE NULL END ) AS VARCHAR(50) )END AS iManage_Doc_Version, 
dstatus.Name AS DocumentStatus, 
dtype.Name AS DocType, 
ddir.Name AS DocDirection, 
dpurpose.Name AS DocPurpose, 
dcat.Name AS DocCategory, 
d.LastUpdatedDate, 
d.LastUpdatedBy, 
d.CreatedDate, 
d.CreatedBy
FROM  Document d WITH (NOLOCK) 
LEFT JOIN LookupDocumentStatus dstatus WITH (NOLOCK) ON dstatus.Id = d.LookupDocumentStatusId 
LEFT JOIN DocumentType dtype WITH (NOLOCK) ON dtype.Id = d.DocumentTypeId 
LEFT JOIN LookupDocumentDirection ddir WITH (NOLOCK) ON ddir.Id = d.LookupDocumentDirectionId 
LEFT JOIN DocumentPurpose dpurpose WITH (NOLOCK) ON dpurpose.Id = d.DocumentPurposeId 
LEFT JOIN DocumentCategory dcat WITH (NOLOCK) ON dcat.Id = d.DocumentCategoryId
order by DocumentId asc;