CREATE OR ALTER VIEW e2x.vwExtractDocuments
AS
SELECT
    stag.AlternateId,
    stag.ParentAlternateId,
    stag.DocumentId AS fenEId,
    stag.LegalEntityId,
    stag.SFTPPath AS documentPath,
    stag.FenEName AS friendlyName,
    stag.FenELocation AS FenELocation,
    stag.FenEDocumentPurposeId,
    stag.FenEDocumentPurpose AS FenEDocumentPurpose,
    stag.FenXDocumentPurpose AS documentType
FROM e2x.StagingDocuments AS stag;
