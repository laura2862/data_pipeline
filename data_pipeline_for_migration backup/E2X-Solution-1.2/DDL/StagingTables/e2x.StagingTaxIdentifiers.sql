CREATE TABLE e2x.StagingTaxIdentifiers
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingTaxIdentifiers PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    TaxIdentifierId INT NOT NULL,
    AlternateId VARCHAR(50) NOT NULL,
    ParentAlternateId VARCHAR(50) NOT NULL,
    FenECountryId INT NULL,
    FenECountry VARCHAR(250) NULL,
    FenXCountry VARCHAR(250) NULL,
    FenETypeId INT NULL,
    FenEType VARCHAR(250) NULL,
    FenXType VARCHAR(250) NULL,
    TaxIdentifierValue NVARCHAR(50) NULL,
    FenEStatusId INT NULL,
    FenEStatus VARCHAR(100) NULL,
    FenXStatus VARCHAR(100) NULL,
    IsTaxIdentifierProvided NVARCHAR(50) NULL,
    FenEReasonNumberNotProvidedId INT NULL,
    FenEReasonNumberNotProvided VARCHAR(250) NULL,
    FenXReasonNumberNotProvided VARCHAR(250) NULL,
    IsTaxResident NVARCHAR(50) NULL,
    Comments NVARCHAR(MAX) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_StagingTaxIdentifiers_AlternateId
    ON e2x.StagingTaxIdentifiers (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingTaxIdentifiers_LegalEntityId
    ON e2x.StagingTaxIdentifiers (LegalEntityId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingTaxIdentifiers_TaxIdentifierId
    ON e2x.StagingTaxIdentifiers (TaxIdentifierId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingTaxIdentifiers_ParentAlternateId
    ON e2x.StagingTaxIdentifiers (ParentAlternateId);
