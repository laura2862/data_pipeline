IF
NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'e2x')
BEGIN
EXEC('CREATE SCHEMA e2x')
END
GO
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[E2X].[Recon]') AND type in (N'U'))
ALTER TABLE [E2X].[Recon] DROP CONSTRAINT IF EXISTS [FK_Recon_Extract]
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[E2X].[Extract]') AND type in (N'U'))
ALTER TABLE [E2X].[Extract] DROP CONSTRAINT IF EXISTS [FK_Extract_Batch]
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[E2X].[Error]') AND type in (N'U'))
ALTER TABLE [E2X].[Error] DROP CONSTRAINT IF EXISTS [FK_Error_Extract]
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[E2X].[EntitiesInScope]') AND type in (N'U'))
ALTER TABLE [E2X].[EntitiesInScope] DROP CONSTRAINT IF EXISTS [FK_BatchId_EntityInScope]
GO
DROP TABLE IF EXISTS [E2X].[Recon]
GO
DROP TABLE IF EXISTS [E2X].[Extract]
GO
DROP TABLE IF EXISTS [E2X].[Error]
GO
DROP TABLE IF EXISTS [E2X].[Batch]
GO
DROP TABLE IF EXISTS [E2X].[EntitiesInScope]
GO
DROP TABLE IF EXISTS [E2X].[DOCEXPORTFILE]
GO
DROP TABLE IF EXISTS [E2X].[DOCPROCESSINGRESULT]
GO
DROP TABLE IF EXISTS [E2X].[DOCFORPRODUCTIMPORT]
GO
DROP TABLE IF EXISTS [E2X].[EXTRACTCONFIG]
GO
DROP TABLE IF EXISTS [E2X].[IDLIST]
GO  
DROP TABLE IF EXISTS [E2X].[LEDocDownloading]
GO
DROP TABLE IF EXISTS [E2X].[Lookups]
GO

CREATE TABLE [e2x].[Lookups](
    [Id][int] IDENTITY(1,1) NOT NULL,
    [LookupName] [nvarchar] (300) NOT NULL,
    [EValue] [nvarchar] (2000) NOT NULL,
    [EId] [int] NOT NULL,
    [XValue] [nvarchar] (2000) NULL,
    CONSTRAINT[PK_Lookups] PRIMARY KEY CLUSTERED ([Id] ASC)
    WITH(PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON[PRIMARY]
) ON[PRIMARY]
GO

CREATE TABLE e2x.ExtractConfig
(
    Id INT IDENTITY(1,1) PRIMARY KEY,
    XTableName VARCHAR(100) NULL,
    DBViewName VARCHAR(250) NULL,
    EBusinessEntityId INT NULL,
    LEIdColumn VARCHAR(150) NULL,
    ReturnOneRow BIT NULL,
    PostDataExtractStrategy NVARCHAR(250) NULL,
    MigrationTypeName NVARCHAR(100) NULL,
    CustomExecutionStrategy NVARCHAR(100) NULL,
    AssociationSourceLEIdColumn NVARCHAR(150) NULL
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[LEDocDownloading] 
(
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [FenELegalEntityId] INT,    
    CONSTRAINT [PK_DocDownloading_1] PRIMARY KEY CLUSTERED ([Id] ASC) WITH 
	(
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[DOCEXPORTFILE] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [CreatedDate] DATETIME, 
    [EntityId] NVARCHAR (1000),
    [FileName] NVARCHAR (1000),
    [JourneyId] NVARCHAR (1000),
    [DocumentType] NVARCHAR (1000),
    [FriendlyName] NVARCHAR (1000),
    [Properties] NVARCHAR (MAX),
    [FenXDocID] NVARCHAR (1000),
    [MigrationStatus] NVARCHAR (1000),
    [MigrationErrorDetails] NVARCHAR (1000),
    [FenEDocumentId] INT,
    FenEEntityId INT,
    FenEEntityTypeName NVARCHAR (1000),
    CONSTRAINT [PK_DOCEXPORTFILE_1] PRIMARY KEY CLUSTERED ([Id] ASC) WITH (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[DOCPROCESSINGRESULT] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [FenELegalEntityId] INT,
    [FenEDocumentId] INT,
    [Processed] BIT,
    [DocumentDownloaded] BIT, 
    CONSTRAINT [PK_DOCPROCESSINGRESULT_1] PRIMARY KEY CLUSTERED ([Id] ASC) WITH (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[Batch]
(
    [Id] [int]  IDENTITY(1,1) NOT NULL,
    [Description] [nvarchar](500) NULL,
    [CreatedDate] [datetime] NULL,
    [Name] [nvarchar](50) NULL,
    CONSTRAINT [PK_Batch_1] PRIMARY KEY CLUSTERED
    ([Id] ASC) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
    ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[EntitiesInScope] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [BatchId] [int] NOT NULL,
    [LEId] [int] NULL,
    [XEntityId] [int] NULL,
    CONSTRAINT [PK_E2X_EntitiesInScope] PRIMARY KEY CLUSTERED ([Id] ASC) WITH 
    (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[Error] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [ExtractId] [int] NOT NULL,
    [Domain] [nvarchar] (350) NULL,
    [AlternativeId] [nvarchar] (50) NULL,
    [ParentAlternativeId] [nvarchar] (50) NULL,
    [FenXId] [nvarchar] (50) NULL,
    [ErrorMessage] [nvarchar] (3000) NULL,
    [LastUpdateDate] [datetime] NULL,
    CONSTRAINT [PK_Error] PRIMARY KEY CLUSTERED ([Id] ASC) WITH (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[Extract] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [CreatedDate] [datetime] NULL,
    [LastUpdateDate] [datetime] NULL,
    [BatchId] [int] NULL,
    [XMigrationId] [int] NULL,
    CONSTRAINT [PK_Extract] PRIMARY KEY CLUSTERED ([Id] ASC) WITH (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE [E2X].[Recon] (
    [Id] [int] IDENTITY (1, 1) NOT NULL,
    [ExtractId] [int] NOT NULL,
    [Domain] [nvarchar] (350) NULL,
    [EBusinessentityId] [int] NULL,
    [EId] [int] NULL,
    [FenXId] [nvarchar] (50) NULL,
    [Status] [nvarchar] (50) NULL,
    [LastUpdateDate] [datetime] NULL,
    [AlternateId] nvarchar (1000) NULL,
    CONSTRAINT [PK_Recon] PRIMARY KEY CLUSTERED ([Id] ASC) WITH (
        PAD_INDEX = OFF,
        STATISTICS_NORECOMPUTE = OFF,
        IGNORE_DUP_KEY = OFF,
        ALLOW_ROW_LOCKS = ON,
        ALLOW_PAGE_LOCKS = ON
    ) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE TABLE E2X.IDLIST  
(
     Id INT,
    BatchId INT,
    CONSTRAINT PK_IDLIST PRIMARY KEY (Id)
);

ALTER TABLE
    [E2X].[EntitiesInScope] WITH CHECK
ADD
    CONSTRAINT [FK_BatchId_EntityInScope] FOREIGN KEY ([BatchId]) REFERENCES [E2X].[Batch] ([Id])
GO
ALTER TABLE
    [E2X].[EntitiesInScope] CHECK CONSTRAINT [FK_BatchId_EntityInScope]
GO
ALTER TABLE
    [E2X].[Error] WITH CHECK
ADD
    CONSTRAINT [FK_Error_Extract] FOREIGN KEY ([ExtractId]) REFERENCES [E2X].[Extract] ([Id])
GO
ALTER TABLE
    [E2X].[Error] CHECK CONSTRAINT [FK_Error_Extract]
GO
ALTER TABLE
    [E2X].[Extract] WITH CHECK
ADD
    CONSTRAINT [FK_Extract_Batch] FOREIGN KEY ([BatchId]) REFERENCES [E2X].[Batch] ([Id])
GO
ALTER TABLE
    [E2X].[Extract] CHECK CONSTRAINT [FK_Extract_Batch]
GO
ALTER TABLE
    [E2X].[Recon] WITH CHECK
ADD
    CONSTRAINT [FK_Recon_Extract] FOREIGN KEY ([ExtractId]) REFERENCES [E2X].[Extract] ([Id])
GO
ALTER TABLE
    [E2X].[Recon] CHECK CONSTRAINT [FK_Recon_Extract]
GO

--SPECIFIC FOR PROJECT NEED TO BE UPDATED FOR OTHER PROJECT
CREATE OR ALTER VIEW E2X.VWDOCUMENTEXTENSION AS
SELECT
    DISTINCT DCU.ID,
    DCU.NAME AS "fileName",
    CASE
        WHEN "CURRENT" = 0 THEN 'No'
        ELSE 'Yes'
    END AS "current",
    DCU.DOCUMENTEXPIRATIONDATE AS "expirationDate",
    DCU.DOCUMENTIDENTIFICATIONNUMBER AS "documentIdentificationNumber",
    DCU.ISSUANCEDATE AS "dateOfIssuance",
    DCU.ISSUANCEPLACE AS "placeOfIssuance",
    DCU.ISSUER AS "issuerOfTheDocument",
    CASE
        WHEN LANGNOTENGLISH = 0 THEN 'No'
        ELSE 'Yes'
    END AS "annotatedIfInALanguageOtherThanEnglish",
    DCU.LASTUPDATEDDATE AS "legacyLastUpdatedDate",
    CASE
        WHEN LEGIBLE = 0 THEN 'No'
        ELSE 'Yes'
    END AS "legible",
    CASE
        WHEN SIGNEDANDINFULL = 0 THEN 'No'
        ELSE 'Yes'
    END AS "signedAndInFullIfApplicable",
    P.NAME AS "documentType"
FROM
    "DBO"."DOCUMENT" DCU
    LEFT JOIN DBO.DOCUMENTPURPOSE P ON DCU.DOCUMENTPURPOSEID = P.ID;

GO
DROP TABLE IF EXISTS [E2X].DOCFORPRODUCTIMPORT
GO
CREATE TABLE E2X.DOCFORPRODUCTIMPORT (
    Id INT IDENTITY(1, 1) PRIMARY KEY,
    INPUTFILENAME NVARCHAR (100),
    CREATEDDATE DATETIME,
    FENEENTITYID INT,
    FENXENTITYID NVARCHAR(100),
    FENEPRODUCTID INT,
    FENXPRODUCTID NVARCHAR(100),
    FENXJOURNEYID NVARCHAR(100),
    FENECASEID INT
)
GO

GO
DROP TABLE IF EXISTS [E2X].PRODUCTIMPORTTEMP
GO
CREATE TABLE E2X.PRODUCTIMPORTTEMP
(
  Id INT IDENTITY(1, 1) PRIMARY KEY,
  FENEPRODUCTID INT,
);
GO

CREATE OR ALTER VIEW E2X.vwActiveDocumentLinks AS
SELECT
    Id,
    DocumentId,
    EntityId AS ContextId,
    IsActive,
    IsMain,
    BusinessEntityId,
    ParentBusinessEntityId,
    ParentEntityId
FROM dbo.LinkDocumentEntity
WHERE IsActive = 1;
GO

CREATE OR ALTER VIEW E2X.VWDOCUMENTS_ALL AS
WITH DocumentData_CTE AS
( 
  SELECT DISTINCT
    doc.Id AS ID,
    vwEDG.EntityId AS "LEID",
    doc.Name AS "FILENAME", 
    doc.Location,
    documentCategory.Name AS DOCUMENTCATEGORY,
    documentPurpose.Name AS DOCUMENTPURPOSE,
    documentPurpose.Name AS DOCUMENTTYPE, -- Doc Type in FenX = Document Purpose
    doc.LastUpdatedDate,
    CASE
        WHEN doc.LookupDocumentStatusId = 7 THEN '0'
        ELSE '1'
    END AS ISACTIVE,
    'Inbound' AS DOCUMENTDIRECTION,
    documentStatus.Name AS DOCUMENTSTATUS    
  FROM E2X.vwActiveDocumentLinks adl
  INNER JOIN dbo.Document doc ON adl.DocumentId = doc.Id
  INNER JOIN vwEntityDocumentGrid vwEDG ON vwEDG.Id = doc.Id
  INNER JOIN dbo.DocumentCategory documentCategory ON doc.DocumentCategoryId = documentCategory.Id
  INNER JOIN dbo.DocumentPurpose documentPurpose ON doc.DocumentPurposeId = documentPurpose.Id
  INNER JOIN dbo.DocumentType documentType ON doc.DocumentTypeId = documentType.Id
  INNER JOIN dbo.LookupDocumentStatus documentStatus ON doc.LookupDocumentStatusId = documentStatus.Id
  LEFT JOIN dbo.LegalEntityAssociation lea ON adl.BusinessEntityId = 31 AND adl.ContextId = lea.Id
  WHERE doc.DOCUMENTTYPEID = 3
  AND LEN(ISNULL(doc.Location,'')) > 0
)
, ReconData_CTE (FenXId,EId) AS
(
  SELECT DISTINCT
     FenXId
    ,EId
  FROM 
    e2x.Recon WHERE EBUSINESSENTITYID = 30
)
SELECT
    documentData."ID"
    ,documentData."LEID"
    ,documentData."FILENAME"
    ,documentData."LOCATION"
    ,documentData."DOCUMENTCATEGORY"
    ,documentData."DOCUMENTPURPOSE"
    ,documentData."DOCUMENTTYPE"
    ,documentData."LASTUPDATEDDATE"
    ,documentData."ISACTIVE"
    ,documentData."DOCUMENTDIRECTION"
    ,documentData."DOCUMENTSTATUS"
    ,r.FenXId
FROM DocumentData_CTE documentData
INNER JOIN ReconData_CTE r ON documentData.LEID = r.EId
WHERE documentData."LEID" IS NOT NULL;
GO

CREATE OR ALTER VIEW E2X.VWDOCUMENTS AS 
SELECT DISTINCT
    documentData."ID"
    ,documentData."LEID"
    ,documentData."FILENAME"
    ,doc."LOCATION"
    ,documentData."DOCUMENTCATEGORY"
    ,documentData."DOCUMENTPURPOSE"
    ,documentData."DOCUMENTTYPE"
    ,documentData."LASTUPDATEDDATE"
    ,documentData."ISACTIVE"
    ,documentData."DOCUMENTDIRECTION"
    ,documentData."DOCUMENTSTATUS"
    ,documentData.FenXId
FROM E2X.VWDOCUMENTS_ALL documentData
INNER JOIN dbo.Document doc ON documentData.Id = doc.Id
INNER JOIN dbo.LookupDocumentStatus documentStatus ON doc.LookupDocumentStatusId = documentStatus.Id
LEFT JOIN E2X.DOCEXPORTFILE DEF ON DEF.FENEDOCUMENTID = doc.Id 
WHERE documentstatus.Id NOT IN (3,11502) AND DEF.ID IS NULL;

GO
CREATE OR ALTER VIEW E2X.VWDOCUMENTSTOPROCESS AS
SELECT documents.* FROM E2X.LEDOCDOWNLOADING LEC
INNER JOIN E2X.VwDocuments documents ON documents.LEID = LEC.FENELEGALENTITYID
GO
CREATE OR ALTER VIEW E2X.VwDocumentsToRemigrate AS
SELECT documents.* FROM E2X.DocExportFile DEF
INNER JOIN E2X.VwDocuments documents ON documents.Id = DEF.FeneDocumentId
WHERE DEF.MigrationStatus = 'NotProcessed';
GO

CREATE OR ALTER VIEW E2X.VWPRODUCTRECON AS 
SELECT 
    ExtractId as "EXTRACTID"
    ,EID as "FENEPRODUCTID"
    ,FenXId as "FENXPRODUCTID"
FROM E2X.Recon WHERE EBusinessEntityId = 140 AND Status = 'Accepted';
GO

CREATE INDEX IDX_LEDocDownloading_FenELegalEntityId ON E2X.LEDocDownloading (FenELegalEntityId);
GO
CREATE INDEX IDX_EID_RECON ON E2X.RECON (EID)
GO
CREATE INDEX IDX_FENEDOCID_RECON ON E2X.Docexportfile (FENEDOCUMENTID)
GO
CREATE INDEX IDX_ENTID_RECON ON E2X.Docexportfile (FENEENTITYID)
GO
CREATE INDEX IDX_IDLIST_BatchId ON E2X.IDLIST (BatchId)

GO
CREATE OR ALTER VIEW E2X.DOCUMENTSFORPRODUCTLINK AS
SELECT DISTINCT
    VWG.ID AS DocumentId
    ,VWG.mainentityid AS ProductId
FROM DBO.VWENTITYDOCUMENTGRID VWG
INNER JOIN E2X.PRODUCTIMPORTTEMP PT ON 
     PT.feneproductid = VWG.mainentityid   
WHERE businesscontextid = 140 AND ISMAIN = 1;

GO
CREATE OR ALTER VIEW E2X.VWDOCUMENTSFORPRODUCTS AS
SELECT  DISTINCT
     vwedl.EntityId AS "PRODUCTID"
    ,VWEDL.Id AS "DOCUMENTID"
	,VWEDL."NAME" AS "FILENAME"
	,vwedl.location AS "LOCATION"
	,VWEDL.DOCUMENTCATEGORYNAME AS "DOCUMENTCATEGORY"
	,vwedl.documentpurposename AS "DOCUMENTPURPOSE"
	,vwedl.documentpurposename AS "DOCUMENTTYPE"
FROM 
	dbo.vwEntityDocumentGrid  VWEDL  
INNER JOIN E2X.DOCUMENTSFORPRODUCTLINK DFPL
    ON VWEDL.Id = DFPL.DocumentId
LEFT JOIN E2X.DOCEXPORTFILE DEF ON DEF.FENEDOCUMENTID = VWEDL.Id AND DEF.FENEENTITYTYPENAME = 'Product'
WHERE businesscontextid = 140 
AND vwedl.DocumentCategoryId  IN (7512)   -- Uploaded Document
AND ISMAIN = 1 AND vwedl.location IS NOT NULL
AND DEF.ID IS NULL;

GO
DROP TABLE IF EXISTS [E2X].MIGRATIONSTATUS
GO
CREATE TABLE E2X.MIGRATIONSTATUS (
    Id INT IDENTITY(1, 1),
    MigrationId VARCHAR(36),
    MigrationDate datetime NULL,
    MigrationStatus NVARCHAR(50) NULL,
    MigratedEntityCount INT NULL,
    MigratedProductCount INT NULL,
    MigratedAssociationCount INT NULL,
    ExtractPath NVARCHAR(1000) NULL,
    JurisdictionEvaluationId VARCHAR(36) NULL,
    JurisdictionEvaluationStatus NVARCHAR(50) NULL,
    AccessLayerId VARCHAR(36) NULL,
    AccessLayerStatus NVARCHAR(50) NULL,
    CONSTRAINT PK_MigrationStatus_Id PRIMARY KEY (Id)
)
GO

CREATE OR ALTER VIEW E2X.VWMIGRATIONSTATUS AS
SELECT
    ID,
    MIGRATIONID,
    MIGRATIONDATE,
    MIGRATIONSTATUS,
    MIGRATEDENTITYCOUNT,
    MIGRATEDPRODUCTCOUNT,
    MIGRATEDASSOCIATIONCOUNT,
    EXTRACTPATH,
    JURISDICTIONEVALUATIONID,
    JURISDICTIONEVALUATIONSTATUS,
    ACCESSLAYERID,
    ACCESSLAYERSTATUS
FROM
    E2X.MIGRATIONSTATUS;

GO
