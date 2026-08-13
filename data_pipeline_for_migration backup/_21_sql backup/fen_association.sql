;WITH DedupLeas AS
(
    SELECT *
    FROM
    (
        SELECT
            leas.*,
            ROW_NUMBER() OVER
            (
                PARTITION BY
                    leas.LegalEntityId,
                    leas.EntityId,
                    leas.LookupLegalEntityAssociationId,
                    leas.LookupAssociationStatusId
                ORDER BY leas.Id DESC
            ) AS RowNum
        FROM dbo.LegalEntityAssociation leas
        WHERE leas.BusinessEntityId = 30
          AND leas.IsDeleted = 0
    ) x
    WHERE x.RowNum = 1
),
Assoc AS
(
    SELECT
        d.Id AS AssociatedRelationId,

        CASE WHEN COALESCE(d.Master,0) = 0 THEN d.LegalEntityId ELSE d.EntityId END AS SourceLegalEntityId,
        CASE WHEN COALESCE(d.Master,0) = 1 THEN d.LegalEntityId ELSE d.EntityId END AS TargetLegalEntityId,

        assoRole.Name AS Relationship,
		lass.Name AS AssociatedRelationStatus
    FROM DedupLeas d
    LEFT JOIN dbo.LuLeAs assoRole ON d.LookupLegalEntityAssociationId = assoRole.Id
	LEFT JOIN LookupAssociationStatus lass on lass.id= d.lookupAssociationStatusId -- 1- active, 2- inactive
),

ClientAssoc as(
SELECT
    SourceLegalEntityId AS LegalEntityId,
    TargetLegalEntityId AS AssociatedLegalEntityId,
    Relationship,
    AssociatedRelationId,
	AssociatedRelationStatus,
    'Is Of' AS RelationshipRole
FROM Assoc
UNION ALL
SELECT
    TargetLegalEntityId AS LegalEntityId,
    SourceLegalEntityId AS AssociatedLegalEntityId,
    Relationship,
    AssociatedRelationId,
	AssociatedRelationStatus,
    'Has Of' AS RelationshipRole
FROM Assoc)

select DISTINCT * from ClientAssoc 
where --LegalEntityId=1 and 
AssociatedRelationStatus ='Active'
order by LegalEntityId asc, AssociatedRelationStatus asc;