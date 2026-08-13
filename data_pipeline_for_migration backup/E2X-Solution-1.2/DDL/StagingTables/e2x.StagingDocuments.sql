CREATE TABLE e2x.StagingDocuments
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingDocuments PRIMARY KEY,
    AlternateId VARCHAR(100) NOT NULL,
    ParentAlternateId VARCHAR(100) NOT NULL,
    DocumentId INT NOT NULL,
    LegalEntityId INT NOT NULL,
    SFTPPath NVARCHAR(MAX) NULL,
    FenEName NVARCHAR(500) NULL,
    FenELocation NVARCHAR(MAX) NULL,
    FenEDocumentPurposeId INT NULL,
    FenEDocumentPurpose VARCHAR(500) NULL,
    FenXDocumentPurpose VARCHAR(500) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_StagingDocuments_AlternateId
    ON e2x.StagingDocuments (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingDocuments_LegalEntityId
    ON e2x.StagingDocuments (LegalEntityId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingDocuments_DocumentId
    ON e2x.StagingDocuments (DocumentId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingDocuments_ParentAlternateId
    ON e2x.StagingDocuments (ParentAlternateId);
