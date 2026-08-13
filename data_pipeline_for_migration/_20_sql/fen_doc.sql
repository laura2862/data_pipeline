;WITH AllContexts AS
(
    -- Legal Entity Context
    SELECT
        lk.EntityId AS LegalEntityId,
        lk.DocumentId,
        'Legal Entity' AS Context
    FROM dbo.LinkDocumentEntity lk
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 30

    UNION ALL

    -- Case Context
    SELECT
        leas.LegalEntityId,
        lk.DocumentId,
        'Case' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN dbo.LegalEntityAssociation leas
        ON leas.EntityId = lk.EntityId
       AND leas.BusinessEntityId = 1
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 1

    UNION ALL

    -- Association - Senior Context
    SELECT
        leas.EntityId AS LegalEntityId,
        lk.DocumentId,
        'Association - Senior' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN dbo.LegalEntityAssociation leas
        ON leas.Id = lk.EntityId
       AND leas.BusinessEntityId = 30
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 31
      AND leas.IsDeleted = 0
      AND leas.LookupAssociationStatusId = 1

    UNION ALL

    -- Association - Junior Context
    SELECT
        leas.LegalEntityId,
        lk.DocumentId,
        'Association - Junior' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN dbo.LegalEntityAssociation leas
        ON leas.Id = lk.EntityId
       AND leas.BusinessEntityId <> 30
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 31
      AND leas.IsDeleted = 0
      AND leas.LookupAssociationStatusId = 1

    UNION ALL

    -- Risk Context
    SELECT
        rk.EntityId AS LegalEntityId,
        lk.DocumentId,
        'Risk' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN rr.CrrRiskAssessmentEntity rk
        ON rk.CrrRiskAssessmentId = lk.EntityId
       AND rk.BusinessEntityId = 30
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 102

    UNION ALL

    -- Classification Context
    SELECT
        cs.LegalEntityId,
        lk.DocumentId,
        'Classification' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN classification.Classification cs
        ON cs.Id = lk.EntityId
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 122

    UNION ALL

    -- Product Context
    SELECT
        leas.LegalEntityId,
        lk.DocumentId,
        'Product' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN origination.Product pr
        ON pr.Id = lk.EntityId
    INNER JOIN dbo.LegalEntityAssociation leas
        ON leas.EntityId = pr.CaseId
       AND leas.BusinessEntityId = 1
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 140

    UNION ALL

    -- Screening Context
    SELECT
        ga.LegalEntityId,
        lk.DocumentId,
        'Screening' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN legalEntity.Screening scr
        ON scr.Id = lk.EntityId
    INNER JOIN LegalEntity.GenericAssessment ga
        ON ga.Id = scr.AssessmentId
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 5013

    UNION ALL

    -- Generic Assessment Context
    SELECT
        ga.LegalEntityId,
        lk.DocumentId,
        'Generic Assessment' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN LegalEntity.GenericAssessment ga
        ON ga.Id = lk.EntityId
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 15003

    UNION ALL

    -- Generic AML Context
    SELECT
        gm.LegalEntityId,
        lk.DocumentId,
        'Generic AML' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN LegalEntity.GenericAML gm
        ON gm.Id = lk.EntityId
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 7000

    UNION ALL

    -- Deferral Context
    SELECT
        leas.LegalEntityId,
        lk.DocumentId,
        'Deferral' AS Context
    FROM dbo.LinkDocumentEntity lk
    INNER JOIN wf.Deferral wfd
        ON wfd.Id = lk.EntityId
    INNER JOIN wf.LinkDeferralTask lwfd
        ON lwfd.DeferralId = wfd.Id
    INNER JOIN wf.WFTask wft
        ON lwfd.WfTask = wft.Id
    INNER JOIN dbo.LegalEntityAssociation leas
        ON leas.EntityId = wft.ParentCaseId
       AND leas.BusinessEntityId = 1
    WHERE lk.IsActive = 1
      AND lk.BusinessEntityId = 15004
)

SELECT DISTINCT
    ac.Context,
    ac.LegalEntityId,
    ac.DocumentId

FROM AllContexts ac

ORDER BY
    ac.LegalEntityId,
    ac.DocumentId,
    ac.Context;
