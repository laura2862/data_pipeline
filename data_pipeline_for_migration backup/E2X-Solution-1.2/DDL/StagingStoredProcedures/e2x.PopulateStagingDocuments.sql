CREATE OR ALTER PROCEDURE e2x.PopulateStagingDocuments
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingDocuments;

    WITH LEResolverCTE (LegalEntityId, DocumentId) AS
    (
        -- Legal Entity Context
        SELECT
            link.EntityId AS LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 30

        UNION

        -- Case Context
        SELECT
            assoc.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN dbo.LegalEntityAssociation AS assoc
            ON assoc.EntityId = link.EntityId
            AND assoc.BusinessEntityId = 1
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 1

        UNION

        -- Association - Senior Context
        SELECT
            assoc.EntityId AS LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN dbo.LegalEntityAssociation AS assoc
            ON assoc.Id = link.EntityId
            AND assoc.BusinessEntityId = 30
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 31
            AND assoc.IsDeleted = 0
            AND assoc.LookupAssociationStatusId = 1

        UNION

        -- Association - Junior Context
        SELECT
            assoc.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN dbo.LegalEntityAssociation AS assoc
            ON assoc.Id = link.EntityId
            AND assoc.BusinessEntityId <> 30
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 31
            AND assoc.IsDeleted = 0
            AND assoc.LookupAssociationStatusId = 1

        UNION

        -- Risk Context
        SELECT
            risk.EntityId AS LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN rr.CrrRiskAssessmentEntity AS risk
            ON risk.CrrRiskAssessmentId = link.EntityId
            AND risk.BusinessEntityId = 30
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 102

        UNION

        -- Classification Context
        SELECT
            class.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN classification.Classification AS class
            ON class.Id = link.EntityId
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 122

        UNION

        -- Product Context
        SELECT
            assoc.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN origination.Product AS product
            ON product.Id = link.EntityId
        INNER JOIN dbo.LegalEntityAssociation AS assoc
            ON assoc.EntityId = product.CaseId
            AND assoc.BusinessEntityId = 1
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 140

        UNION

        -- Screening Context
        SELECT
            assessment.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN legalEntity.Screening AS screening
            ON link.EntityId = screening.Id
        INNER JOIN LegalEntity.GenericAssessment AS assessment
            ON assessment.Id = screening.AssessmentId
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 5013

        UNION

        -- Generic Assessment Context
        SELECT
            assessment.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN LegalEntity.GenericAssessment AS assessment
            ON assessment.Id = link.EntityId
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 15003

        UNION

        -- Generic AML Context
        SELECT
            aml.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN LegalEntity.GenericAML AS aml
            ON aml.Id = link.EntityId
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 7000

        UNION

        -- Deferral Context
        SELECT
            assoc.LegalEntityId,
            link.DocumentId
        FROM dbo.LinkDocumentEntity AS link
        INNER JOIN wf.Deferral AS deferral
            ON deferral.Id = link.EntityId
        INNER JOIN wf.LinkDeferralTask AS deferralTask
            ON deferralTask.DeferralId = deferral.Id
        INNER JOIN wf.WFTask AS task
            ON deferralTask.WfTask = task.Id
        INNER JOIN dbo.LegalEntityAssociation AS assoc
            ON assoc.EntityId = task.ParentCaseId
            AND assoc.BusinessEntityId = 1
        WHERE link.IsActive = 1
            AND link.BusinessEntityId = 15004
    )
    INSERT INTO e2x.StagingDocuments
    (
        AlternateId,
        ParentAlternateId,
        DocumentId,
        LegalEntityId,
        SFTPPath,
        FenEName,
        FenELocation,
        FenEDocumentPurposeId,
        FenEDocumentPurpose,
        FenXDocumentPurpose,
        LoadTimestamp
    )
    SELECT
        'DOC' + CAST(leDoc.DocumentId AS VARCHAR(50)) + '_LE' + CAST(leDoc.LegalEntityId AS VARCHAR(50)) AS AlternateId,
        CAST(leDoc.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,
        leDoc.DocumentId,
        leDoc.LegalEntityId,
        NULL AS SFTPPath,
        doc.[Name] AS FenEName,
        doc.[Location] AS FenELocation,
        doc.DocumentPurposeId AS FenEDocumentPurposeId,
        lookupDocumentPurpose.EValue AS FenEDocumentPurpose,
        lookupDocumentPurpose.XValue AS FenXDocumentPurpose,
        CURRENT_TIMESTAMP AS LoadTimestamp
    FROM LEResolverCTE AS leDoc
    INNER JOIN dbo.Document AS doc
        ON leDoc.DocumentId = doc.Id
    LEFT JOIN e2x.Lookups AS lookupDocumentPurpose
        ON lookupDocumentPurpose.LookupName = 'DocumentPurpose'
        AND lookupDocumentPurpose.EId = doc.DocumentPurposeId
    WHERE doc.LookupDocumentStatusId NOT IN (11501, 11502);
END;
