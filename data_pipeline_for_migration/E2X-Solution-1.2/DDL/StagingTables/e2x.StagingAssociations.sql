CREATE TABLE e2x.StagingAssociations
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingAssociations PRIMARY KEY,

    AlternateId NVARCHAR(100) NOT NULL,

    SourceEntityType NVARCHAR(50) NULL,
    SourceAlternateId INT NOT NULL,

    TargetEntityType NVARCHAR(50) NULL,
    TargetAlternateId INT NOT NULL,

    Relationship NVARCHAR(250) NULL,

    Direction NVARCHAR(25) NULL,

    OwnershipPercentage NVARCHAR(MAX) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_StagingAssociations_AlternateId
    ON e2x.StagingAssociations (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAssociations_SourceAlternateId
    ON e2x.StagingAssociations (SourceAlternateId)
    INCLUDE (SourceEntityType, Relationship, OwnershipPercentage);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAssociations_TargetAlternateId
    ON e2x.StagingAssociations (TargetAlternateId)
    INCLUDE (Relationship, OwnershipPercentage);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAssociations_SourceEntityType
    ON e2x.StagingAssociations (SourceEntityType);
