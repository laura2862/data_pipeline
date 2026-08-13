CREATE OR ALTER VIEW e2x.vwExtractComments
AS
SELECT DISTINCT
    stag.LegalEntityId,
    stag.CommentId AS fenEId,
    stag.AlternateId,
    stag.ParentAlternateId,
    stag.Details AS comments,
	stag.CreatedBy AS commentBy,
	stag.LastUpdatedDate AS commentDate,
    stag.EntityId,
    stag.EntityType,
    stag.ConnectionPoint
FROM e2x.StagingComments AS stag;
