/* Fenergo Client Details Including
Role Status
Role Type


Add Indicators:
isClientEntity: when a Legal Entity has a role type as 'Client/Counterparty' 
Onboarding status
Offboarded status

*/  

WITH ClientEntity AS( 
SELECT DISTINCT lea.LegalEntityId FROM dbo.LEAssociate lea WITH (NOLOCK) where lea.LEAssociateTypeID =101-- Client/Counterparty
),

OffboardedEntity AS( 
SELECT DISTINCT lea.LegalEntityId
FROM dbo.LEAssociate lea WITH (NOLOCK) where LegalEntityRoleStatusId =8 --Offboarded
),

Jurisdiction as ( 
SELECT distinct [EntityId] ,[jurisdictionId],lv.[Name] 
FROM [FenergoData].[dbo].[Entityjurisdiction] ej 
inner join dbo.LegalEntity le on le.id= ej.EntityId 
left join dbo.jurisdiction lv on lv.Id= ej.[jurisdictionId] 
where ej.EntityTypeId=30 /*added to filter the legal entity type */
group by [EntityId],jurisdictionId,lv.Name ), 

Jurisdictions as ( 
select distinct [EntityId] as LegalEntityId, 
STRING_AGG( Name, '|') as 'Jurisdictions' 
From Jurisdiction 
group by [EntityId] ), 

GlobalRisk AS ( 
SELECT LegalEntityID, 
RiskStatus as GlobalRisk 
FROM [FenergoData].[dbo].[vwLECompRiskProfile] WITH (NOLOCK) ), 

Alias AS (
SELECT LegalEntityID,Alias1,Alias2,Alias3,Alias4
FROM scotia.legalentityExtension  WITH (NOLOCK)
),

ClientDetail as (
SELECT le.Id AS LegalEntityId, 

REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            ISNULL(le.Name,'')
            , '"', ' ')
            , ',', ' ')
            , CHAR(13), ' ')
            , CHAR(10), ' ')
            , CHAR(9), ' ') AS LegalEntityName, 
letp.Name AS LeType, le.ReferenceId, 
Alias.Alias1,Alias.Alias2,Alias.Alias3,Alias.Alias4,
leat.name as RoleType, lers.name as RoleStatus,
case when llt.LegalEntityTypeId=3 then 'Company' else 'Individual' end as EntityType, 
case when le.IsMigrated=1  then 1 else 0 end as isFromV7, 
case when ce.legalentityid is not null then 1 else 0 end as isClientEntity, 
case when offe.legalentityid is not null then 1 else 0 end as IsOffboarded, 
gr.GlobalRisk, 
j.Jurisdictions 

FROM  LegalEntity le WITH (NOLOCK) 
LEFT JOIN LuLeSubTp letp WITH (NOLOCK) ON letp.Id = le.LegalEntitySubtypeId 
LEFT JOIN dbo.LEAssociate lea ON lea.LegalEntityId = le.Id --role
LEFT JOIN dbo.LookupLEAssociateType leat ON leat.Id = lea.LEAssociateTypeID -- role type, 101- counter party/client
LEFT JOIN dbo.LinkLuLeTpLuLeSt llt WITH (NOLOCK) ON llt.LegalEntitySubTypeId = letp.Id and llt.LegalEntityTypeId in (3,4) -- Company / Individual
LEFT JOIN dbo.LuLeRoleStatus lers ON lers.Id = lea.LegalEntityRoleStatusId -- role status 3-active, 8-offboard, 6- inactive
LEFT JOIN ClientEntity ce WITH (NOLOCK) ON ce.Legalentityid=le.id 
LEFT JOIN OffboardedEntity offe WITH (NOLOCK) ON offe.Legalentityid=le.id 
LEFT JOIN Alias  WITH (NOLOCK) ON Alias.Legalentityid=le.id 
LEFT JOIN GlobalRisk gr WITH (NOLOCK) ON gr.Legalentityid=le.id 
LEFT JOIN Jurisdictions j WITH (NOLOCK) ON j.LegalEntityId=le.id 

where le.active=0 -- filter archived client
--and lea.LEAssociateTypeID=101 
)

/* Final query */ 
SELECT  distinct * from ClientDetail
--where IsOffboarded=1 
--and  isClientEntity=1 
--and isFromV7=1
WHERE RoleStatus in ('Active','Offboarded')
ORDER BY LegalEntityId ASC;



