CREATE TABLE e2x.StagingContacts
(
    Id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_E2X_StagingContacts PRIMARY KEY,
    LegalEntityId INT NOT NULL,
    ContactId INT NOT NULL,
    AlternateId VARCHAR(50) NOT NULL,
    ParentAlternateId VARCHAR(50) NOT NULL,
    FenEContactSubTypeId INT NULL,
    FenEContactSubType VARCHAR(100) NULL,
    FenXContactSubType VARCHAR(100) NULL,
    FenEContactStatusId INT NULL,
    FenEContactStatus VARCHAR(100) NULL,
    FenXContactStatus VARCHAR(100) NULL,
    FenETitleId INT NULL,
    FenETitle VARCHAR(100) NULL,
    FenXTitle VARCHAR(100) NULL,
    FenEBusinessTitleId INT NULL,
    FenEBusinessTitle VARCHAR(100) NULL,
    FenXBusinessTitle VARCHAR(100) NULL,
    FirstName NVARCHAR(250) NULL,
    LastName NVARCHAR(250) NULL,
    PrimaryPhoneNumber NVARCHAR(50) NULL,
    HomePhone NVARCHAR(50) NULL,
    WorkPhone NVARCHAR(50) NULL,
    Mobile NVARCHAR(50) NULL,
    Fax NVARCHAR(50) NULL,
    Email NVARCHAR(250) NULL,
    IsPrimary VARCHAR(10) NULL,
    Comments NVARCHAR(4000) NULL,
    LoadTimestamp DATETIME NOT NULL
);

CREATE NONCLUSTERED INDEX IX_E2X_StagingContacts_AlternateId
    ON e2x.StagingContacts (AlternateId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingContacts_LegalEntityId
    ON e2x.StagingContacts (LegalEntityId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingContacts_ContactId
    ON e2x.StagingContacts (ContactId);

CREATE NONCLUSTERED INDEX IX_E2X_StagingContacts_ParentAlternateId
    ON e2x.StagingContacts (ParentAlternateId);
