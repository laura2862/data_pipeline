select DISTINCT le.id as legalentityid,
c.id as ContactID,
c.Active,
c.Email,
c.IsPrimary,
c.workPhone as PrimaryPhone,
ctp.name as ContactType
--,cstp.name as ContactSubType,cs.name as ContactStatus
from Legalentity le 
inner join contactLegalEntity cle on cle.LegalEntityId=le.id
inner join contact c on cle.ContactId=c.id
left join contactType ctp on c.ContactTypeId=ctp.id
--left join lookupvalue cstp on cstp.id=c.ContactSubTypeId
--left join lookupvalue cs on cs.id=c.LookupContactStatusId
where c.active=1