CREATE TABLE e2x.ExcludedLegalEntities
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_ExcludedLegalEntities PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    ExclusionReason NVARCHAR(500) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_ExcludedLegalEntities_LegalEntityId
    ON e2x.ExcludedLegalEntities (LegalEntityId);