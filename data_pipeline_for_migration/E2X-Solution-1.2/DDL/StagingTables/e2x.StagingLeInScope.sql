CREATE TABLE e2x.StagingLeInScope
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingLeInScope PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    IsCustomer BIT NULL,
    IsOffboarded BIT NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE NONCLUSTERED INDEX IX_E2X_StagingLeInScope_LegalEntityId
    ON e2x.StagingLeInScope (LegalEntityId);
