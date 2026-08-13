CREATE TABLE e2x.StagingComments
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingComments PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    CommentId INT NOT NULL,
    AlternateId VARCHAR(50) NOT NULL,
    ParentAlternateId VARCHAR(50) NOT NULL,
    Details VARCHAR(4000) NULL,
	CreatedBy  VARCHAR(500) NULL,
	LastUpdatedDate DATETIME,
    EntityId INT NOT NULL,
    EntityType VARCHAR(50) NOT NULL,
    ConnectionPoint VARCHAR(100) NOT NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_StagingComments_AlternateId
    ON e2x.StagingComments (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingComments_LegalEntityId
    ON e2x.StagingComments (LegalEntityId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingComments_CommentId
    ON e2x.StagingComments (CommentId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingComments_ParentAlternateId
    ON e2x.StagingComments (ParentAlternateId);
