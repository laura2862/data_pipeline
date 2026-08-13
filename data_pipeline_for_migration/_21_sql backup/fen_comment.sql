WITH CaseLegalEntity AS
(
    SELECT     
        CaseLE.Id,
        LE.Id AS LegalEntityId,
        CaseLE.EntityId AS CaseId
    FROM dbo.LegalEntityAssociation AS CaseLE
    INNER JOIN dbo.LegalEntity AS LE
        ON LE.Id = CaseLE.LegalEntityId
    WHERE CaseLE.LookupLegalEntityAssociationId IS NOT NULL
        AND CaseLE.BusinessEntityId = 1
        AND CaseLE.IsDeleted = 0
),


DeduplicatedAssociations AS
(
    SELECT
        leas.*,
        ROW_NUMBER() OVER
        (
            PARTITION BY
                leas.LegalEntityId,--source entity has ..of
                leas.EntityId, -- target entity is .. of 
                leas.LookupLegalEntityAssociationId,
                leas.LookupAssociationStatusId
            ORDER BY
                leas.Id DESC
        ) AS RowNumber
    FROM dbo.LegalEntityAssociation AS leas
    WHERE leas.BusinessEntityId = 30
      AND leas.IsDeleted = 0
      AND leas.LookupAssociationStatusId = 1
      AND leas.LookupLegalEntityAssociationId IS NOT NULL
),
AllComments AS
(
    -- 1. Legal Entity Comments
    SELECT
        link.EntityId AS LegalEntityId,
        c.Id AS CommentId,
        'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
        CAST(link.EntityId AS VARCHAR(50)) AS ParentAlternateId,
        c.Details,
        c.CreatedBy,
        c.LastUpdatedDate,
        link.EntityId,
        BI.Name AS EntityType,
        BI.Name + ' [' + CONVERT(VARCHAR(50), link.EntityId) + ']' AS ConnectionPoint,
        'LegalEntity' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.Comment c
    INNER JOIN dbo.LinkCommentEntity link
        ON link.CommentId = c.Id
    INNER JOIN dbo.BusinessEntity BI
        ON link.BusinessEntityId = BI.Id
    WHERE link.BusinessEntityId = 30

    UNION ALL

    -- 2. Case Comments
    SELECT
        LECase.LegalEntityId,
        c.Id AS CommentId,
        'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
        CAST(LECase.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        c.Details,
        c.CreatedBy,
        c.LastUpdatedDate,
        link.EntityId,
        BI.Name AS EntityType,
        BI.Name + ' [' + CONVERT(VARCHAR(50), link.EntityId) + ']' AS ConnectionPoint,
        'Case' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.Comment c
    INNER JOIN dbo.LinkCommentEntity link
        ON link.CommentId = c.Id
    INNER JOIN dbo.BusinessEntity BI
        ON link.BusinessEntityId = BI.Id
    INNER JOIN CaseLegalEntity LECase
        ON LECase.CaseId = link.EntityId
    WHERE link.BusinessEntityId = 1

    UNION ALL

    -- 3. Association Comments
    SELECT
        DA.LegalEntityId,
        c.Id AS CommentId,
        'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
        CAST(DA.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        c.Details,
        c.CreatedBy,
        c.LastUpdatedDate,
        link.EntityId,
        BI.Name AS EntityType,
        BI.Name + ' [' + CONVERT(VARCHAR(50), link.EntityId) + ']' AS ConnectionPoint,
        'Association' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.Comment c
    INNER JOIN dbo.LinkCommentEntity link
        ON link.CommentId = c.Id
    INNER JOIN dbo.BusinessEntity BI
        ON link.BusinessEntityId = BI.Id
    INNER JOIN DeduplicatedAssociations DA
        ON DA.Id = link.EntityId
    WHERE link.BusinessEntityId = 31
      AND DA.RowNumber = 1

    UNION ALL

    -- 4. Classification Comments
    SELECT
        class.LegalEntityId,
        c.Id AS CommentId,
        'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
        CAST(class.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        c.Details,
        c.CreatedBy,
        c.LastUpdatedDate,
        link.EntityId,
        BI.Name AS EntityType,
        BI.Name + ' [' + CONVERT(VARCHAR(50), link.EntityId) + ']' AS ConnectionPoint,
        'Classification' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.Comment c
    INNER JOIN dbo.LinkCommentEntity link
        ON link.CommentId = c.Id
    INNER JOIN dbo.BusinessEntity BI
        ON link.BusinessEntityId = BI.Id
    INNER JOIN classification.Classification class
        ON class.Id = link.EntityId
    WHERE link.BusinessEntityId = 122

    UNION ALL

    -- 5. Product Comments
    SELECT
        LECase.LegalEntityId,
        c.Id AS CommentId,
        'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
        CAST(LECase.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        c.Details,
        c.CreatedBy,
        c.LastUpdatedDate,
        link.EntityId,
        BI.Name AS EntityType,
        BI.Name + ' [' + CONVERT(VARCHAR(50), link.EntityId) + ']' AS ConnectionPoint,
        'Product' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM dbo.Comment c
    INNER JOIN dbo.LinkCommentEntity link
        ON link.CommentId = c.Id
    INNER JOIN dbo.BusinessEntity BI
        ON link.BusinessEntityId = BI.Id
    INNER JOIN [origination].[product] p ON link.EntityId = p.Id
    INNER JOIN CaseLegalEntity LECase
        ON LECase.CaseId = p.CaseId
    WHERE link.BusinessEntityId = 140 

    UNION ALL

    ---- 6. Tax Identifier Comments - updated
    SELECT
        TI.LegalEntityId,
        TI.Id AS CommentId,
        'COMM' + CAST(TI.Id AS VARCHAR(50)) AS AlternateId,
        CAST(TI.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        TI.comments as Details,
        TI.CreatedBy,
        TI.LastUpdatedDate,
        TI.ID AS EntityId,
        'TaxIdentifier' AS EntityType,
        'TaxIdentifier' + ' [' + CONVERT(VARCHAR(50), TI.Id) + ']' AS ConnectionPoint,
        'TaxIdentifier' AS CommentLevel,
        CURRENT_TIMESTAMP AS LoadTimestamp



    FROM  dbo.TaxIdentifier TI

)

SELECT *
FROM AllComments
where LastUpdatedDate>'2022-06-10' and Details is not null
Order by LegalEntityId,CommentId;
--WHERE LegalEntityId = 290509;   -- optional filter

--select lc.CommentId,c.Details as Comment,lc.*
--from  comment c
--inner join dbo.LinkCommentEntity lc 
--on c.id=lc.CommentId and  lc.BusinessEntityId  in (140, 15000,31) 
--where c.Id in (261413,261414) -- Product, Association Comment

--select * from dbo.LegalEntityAssociation where BusinessEntityId  in (140, 15000,31) and 
--(   

--LegalEntityId in (139518,769424) 
--OR EntityId IN (139518,769424) 
--OR Id IN (139518,769424) 
--OR LookupLegalEntityAssociationId IN (139518,769424) 
--)


--select * from TaxIdentifier where legalentityid=290509 -- Tax Comment