select le.id as LegalEntityId, 
cs.Id as CaseId, 
css.name as CaseStage, 
lucs.name as CaseStatus, 
cstp.name as CaseType,
cs.LastUpdatedDate, 
cs.LastCaseStatusUpdateDate,
cs.CreatedDate
from Legalentity le 
inner JOIN LegalEntityassociation lea ON lea.LegalEntityId = le.Id and lea.businessEntityId=1 -- case
inner join [case] cs on lea.entityId=cs.id 
left join caseStatus css on cs.caseStatusId=css.id -- case stage -- 80=cancelled, 5001-complete
left join  dbo.LookupValue lucs on cs.maintenanceStatusId=lucs.id  -- case status -- 239=closed, 447=Workflow Exception
left join caseType cstp on cs.caseTypeId=cstp .id --case type
where lucs.id is not null /* filter out master case*/
order by LegalEntityId asc, cs.Id asc;