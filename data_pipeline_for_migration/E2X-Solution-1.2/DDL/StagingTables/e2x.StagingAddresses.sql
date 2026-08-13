CREATE TABLE e2x.StagingAddresses
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingAddresses PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    AddressId INT NOT NULL,
    AlternateId VARCHAR(50) NOT NULL,
    ParentAlternateId VARCHAR(50) NOT NULL,
    FenEAddressTypeId INT NULL,
    FenEAddressType VARCHAR(100) NULL,
    FenXAddressType VARCHAR(100) NULL,
    FenECountryId INT NULL,
    FenECountry VARCHAR(250) NULL,
    FenXCountry VARCHAR(250) NULL,
    Town NVARCHAR(250) NULL,
    ZipCode NVARCHAR(20) NULL,
    Line1 NVARCHAR(500) NULL,
    Line2 NVARCHAR(500) NULL,
    Line3 NVARCHAR(500) NULL,
    Line4 NVARCHAR(500) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE UNIQUE NONCLUSTERED INDEX IX_E2X_StagingAddresses_AlternateId
    ON e2x.StagingAddresses (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAddresses_LegalEntityId
    ON e2x.StagingAddresses (LegalEntityId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAddresses_AddressId
    ON e2x.StagingAddresses (AddressId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingAddresses_ParentAlternateId
    ON e2x.StagingAddresses (ParentAlternateId);
