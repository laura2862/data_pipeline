IF OBJECT_ID('e2x.ExtractConfig', 'U') IS NOT NULL
BEGIN
    DELETE FROM e2x.ExtractConfig;
END;

-- Entities (Companies and Individuals)

INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Lookups', 'Lookups', NULL, NULL, NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Addresses', 'vwExtractAddresses', NULL, 'parentAlternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Contacts', 'vwExtractContacts', NULL, 'parentAlternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Comments', 'vwExtractComments', NULL, 'parentAlternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('TaxIdentifiers', 'vwExtractTaxIdentifiers', NULL, 'parentAlternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Companies', 'vwExtractLegalEntityCompanies', NULL, 'alternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Individuals', 'vwExtractLegalEntityIndividuals', NULL, 'alternateId', NULL, 'LegalEntity', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Classifications', 'vwExtractClassifications', NULL, 'alternateId', NULL, 'LegalEntity', NULL, NULL);

-- Entity to Entity Associations 

INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Lookups', 'Lookups', NULL, NULL, NULL, 'LEAssociations', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Companies', 'vwExtractLegalEntityCompanies', NULL, 'alternateId', NULL, 'Associations', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Individuals', 'vwExtractLegalEntityIndividuals', NULL, 'alternateId', NULL, 'Associations', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Associations', 'vwExtractAssociations', NULL, 'targetAlternateId', NULL, 'Associations', NULL, NULL);

-- Products

INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Lookups', 'Lookups', NULL, NULL, NULL, 'Products', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Companies', 'vwExtractLegalEntityCompanies', NULL, 'alternateId',NULL, 'Products', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Individuals', 'vwExtractLegalEntityIndividuals', NULL, 'alternateId', NULL, 'Products', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Products', 'vwExtractProducts', NULL, 'parentAlternateId', NULL, 'Products', NULL, NULL);

-- Documents

INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Lookups', 'Lookups', NULL, NULL, NULL, 'Documents', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Companies', 'vwExtractLegalEntityCompanies', NULL, 'alternateId',NULL, 'Documents', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Individuals', 'vwExtractLegalEntityIndividuals', NULL, 'alternateId', NULL, 'Documents', NULL, NULL);
INSERT INTO e2x.ExtractConfig(XTableName, DBViewName, EBusinessEntityId, LEIdColumn, ReturnOneRow, MigrationTypeName, CustomExecutionStrategy, AssociationSourceLEIdColumn) 
VALUES('Documents', 'vwExtractDocuments', NULL, 'parentAlternateId', NULL, 'Documents', NULL, NULL);