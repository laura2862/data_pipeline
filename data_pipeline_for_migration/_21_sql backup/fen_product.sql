select DISTINCT le.id as LegalEntityId, 
p.id as ProductId, 
pc.Name as ProductCategory, 
ptp.name as ProductType,
ps.name as ProductStatus,
pbe.name as ProductBookingEntity,
c.Name as ProductBookingEntityCountry, 
ptl.name as ProductTradingLocation,
CASE
        WHEN ptp.Name LIKE '%Legacy%' THEN 'Yes'
        ELSE 'No'
    END AS IsLegacy

--case
,cs.Id as CaseId, css.name as CaseStage, lucs.name as CaseStatus, cstp.name as CaseType
from Legalentity le 
inner JOIN LegalEntityassociation lea ON lea.LegalEntityId = le.Id and lea.businessEntityId=1 -- case
inner join [case] cs on lea.entityId=cs.id 
inner join origination.product p on p.caseId =cs.id -- product
left join productConfig.LookupProductCategory pc on pc.Id =p.LookupProductCategoryId -- product Category
left join productConfig.LookupProductType ptp on ptp.Id =p.LookupProductTypeId -- product Type
left join productConfig.LookupProductStatus ps on ps.Id =p.ProductStatusId -- product Status
left join productConfig.BookingEntity pbe on pbe.Id =p.BookingEntityId -- product bookingEntity
left join productConfig.BookingEntity ptl on ptl.Id =p.TradingLocationId -- product TradingLocation
left join productConfig.BookingEntityCountry pbec on pbec.BookingEntityId=p.BookingEntityId -- product bookingEntityCountry
left join country c on c.id =pbec.countryid
left join caseStatus css on cs.caseStatusId=css.id -- case stage -- 80=cancelled, 5001-complete
left join  dbo.LookupValue lucs on cs.maintenanceStatusId=lucs.id  -- case status -- 239=closed, 447=Workflow Exception
left join caseType cstp on cs.caseTypeId=cstp .id --case type*/
where ps.name in ('Pending Approval','Approved')  -- 1-'Pending Approval' 3&4 -'Approved'
order by LegalEntityId asc, ProductId asc;

