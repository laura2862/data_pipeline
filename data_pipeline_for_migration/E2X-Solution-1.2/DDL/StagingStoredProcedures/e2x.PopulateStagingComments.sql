CREATE OR ALTER PROCEDURE e2x.PopulateStagingComments
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingComments;

    With 
    CaseLegalEntity AS
    (
	    SELECT     
	    [CaseLE].Id, 
	    [LE].Id as 'LegalEntityId',
	    [CaseLE].EntityId as CaseId
	    FROM [LegalEntityAssociation] [CaseLE]
	    INNER JOIN [LegalEntity] [LE] on [LE].[Id] = [CaseLE].[LegalEntityId]
	    WHERE  ([CaseLE].[LookupLegalEntityAssociationId] = 9 OR [CaseLE].[LookupLegalEntityAssociationId] = 10 OR [CaseLE].[LookupLegalEntityAssociationId] is Null)
		    AND [CaseLE].[BusinessEntityId] = 1 AND [CaseLE].[IsDeleted] = 0
    ),
    DeduplicatedAssociations AS
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
            ) AS RowNumber
        FROM dbo.LegalEntityAssociation AS leas
        WHERE leas.BusinessEntityId = 30
            AND leas.IsDeleted = 0
            AND leas.LookupAssociationStatusId = 1
            AND leas.LookupLegalEntityAssociationId IS NOT NULL
    )
    INSERT INTO e2x.StagingComments
    (
        LegalEntityId,
		CommentId,
		AlternateId,
		ParentAlternateId,
		Details,
		CreatedBy,
		LastUpdatedDate,
		EntityId,
		EntityType,
		ConnectionPoint,
		LoadTimestamp
    )
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
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	WHERE link.BusinessEntityId = 30 -- Legal Entity

	UNION ALL

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
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	INNER JOIN CaseLegalEntity LECase ON LECase.CaseId = link.EntityId
	WHERE link.BusinessEntityId = 1 -- Case

	UNION ALL

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
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	INNER JOIN DeduplicatedAssociations DA ON DA.Id = link.EntityId 
	WHERE link.BusinessEntityId = 31 -- Associations
			AND DA.RowNumber = 1

	UNION ALL

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
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	INNER JOIN [classification].[Classification] class ON class.Id = link.EntityId
	WHERE link.BusinessEntityId = 122 -- Classifications

	UNION ALL

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
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	INNER JOIN CaseLegalEntity LECase ON LECase.CaseId = link.EntityId
	WHERE link.BusinessEntityId = 140 -- Product

	UNION ALL

	SELECT
		TI.LegalEntityId,
		c.Id AS CommentId,
		'COMM' + CAST(c.Id AS VARCHAR(50)) AS AlternateId,
		CAST(TI.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
		c.Details,
		c.CreatedBy,
		c.LastUpdatedDate,
		link.EntityId,
		BI.Name AS EntityType,
		BI.Name + ' [' + CONVERT(VARCHAR, link.EntityId) + ']' [ConnectionPoint],
		CURRENT_TIMESTAMP AS LoadTimestamp
	FROM [dbo].[Comment] c
	INNER JOIN [dbo].[LinkCommentEntity] link ON link.CommentId = c.Id
	INNER JOIN dbo.BusinessEntity BI ON link.BusinessEntityId = BI.Id
	INNER JOIN dbo.TaxIdentifier TI ON TI.Id = link.EntityId
	WHERE link.BusinessEntityId = 15000 -- Tax Id
END;