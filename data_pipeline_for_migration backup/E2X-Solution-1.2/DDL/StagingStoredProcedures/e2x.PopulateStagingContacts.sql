CREATE OR ALTER PROCEDURE e2x.PopulateStagingContacts
AS
BEGIN
    SET NOCOUNT ON;

    TRUNCATE TABLE e2x.StagingContacts;

    INSERT INTO e2x.StagingContacts
    (
        LegalEntityId,
        ContactId,
        AlternateId,
        ParentAlternateId,
        FenEContactSubTypeId,
        FenEContactSubType,
        FenXContactSubType,
        FenEContactStatusId,
        FenEContactStatus,
        FenXContactStatus,
        FenETitleId,
        FenETitle,
        FenXTitle,
        FenEBusinessTitleId,
        FenEBusinessTitle,
        FenXBusinessTitle,
        FirstName,
        LastName,
        PrimaryPhoneNumber,
        HomePhone,
        WorkPhone,
        Mobile,
        Fax,
        Email,
        IsPrimary,
        Comments,
        LoadTimestamp
    )
    SELECT
        c2e.LegalEntityId,
        c.Id AS ContactId,

        'CNT'
            + CAST(c.Id AS VARCHAR(50))
            + '-LE'
            + CAST(c2e.LegalEntityId AS VARCHAR(50)) AS AlternateId,

        CAST(c2e.LegalEntityId AS VARCHAR(50)) AS ParentAlternateId,

        c.ContactSubTypeId AS FenEContactSubTypeId,
        lookupContactSubType.EValue AS FenEContactSubType,
        lookupContactSubType.XValue AS FenXContactSubType,

        c.LookupContactStatusId AS FenEContactStatusId,
        lookupContactStatus.EValue AS FenEContactStatus,
        lookupContactStatus.XValue AS FenXContactStatus,

        c.TitleId AS FenETitleId,
        lookupPrefix.EValue AS FenETitle,
        lookupPrefix.XValue AS FenXTitle,

        c.BusinessTitleId AS FenEBusinessTitleId,
        lookupBusinessTitle.EValue AS FenEBusinessTitle,
        lookupBusinessTitle.XValue AS FenXBusinessTitle,

        CASE
            WHEN c.ContactTypeId = 2
                THEN COALESCE(u.FirstName, c.FirstName)
            ELSE c.FirstName
        END AS FirstName,

        CASE
            WHEN c.ContactTypeId = 2
                THEN COALESCE(u.LastName, c.LastName)
            ELSE c.LastName
        END AS LastName,

        CASE
            WHEN c.ContactTypeId = 2
                THEN COALESCE(u.Phone, c.WorkPhone, c.Mobile, c.HomePhone)
            ELSE
                CASE c.PrimaryPhone
                    WHEN 1 THEN c.HomePhone
                    WHEN 2 THEN c.WorkPhone
                    WHEN 3 THEN c.Mobile
                END
        END AS PrimaryPhoneNumber,

        CASE
            WHEN c.ContactTypeId = 2 THEN NULL
            ELSE c.HomePhone
        END AS HomePhone,

        CASE
            WHEN c.ContactTypeId = 2
                THEN COALESCE(u.Phone, c.WorkPhone)
            ELSE c.WorkPhone
        END AS WorkPhone,

        CASE
            WHEN c.ContactTypeId = 2 THEN NULL
            ELSE c.Mobile
        END AS Mobile,

        CASE
            WHEN c.ContactTypeId = 2 THEN NULL
            ELSE c.Fax
        END AS Fax,

        CASE
            WHEN c.ContactTypeId = 2
                THEN COALESCE(u.EMail, c.Email)
            ELSE c.Email
        END AS Email,

        e2x.BitToYesNo(c.IsPrimary, 'No') AS IsPrimary,
        c.[Description] AS Comments,
        CURRENT_TIMESTAMP AS LoadTimestamp

    FROM dbo.Contact AS c

    INNER JOIN dbo.ContactLegalEntity AS c2e
        ON c2e.ContactId = c.Id

    INNER JOIN dbo.LegalEntity AS le
        ON le.Id = c2e.LegalEntityId

    LEFT JOIN authorisation.[User] AS u
        ON u.Id = c.UserId
        AND c.ContactTypeId = 2

    LEFT JOIN e2x.Lookups AS lookupContactSubType
        ON lookupContactSubType.LookupName = 'LookupContactSubType'
        AND lookupContactSubType.EId = c.ContactSubTypeId

    LEFT JOIN e2x.Lookups AS lookupContactStatus
        ON lookupContactStatus.LookupName = 'LookupContactStatus'
        AND lookupContactStatus.EId = c.LookupContactStatusId

    LEFT JOIN e2x.Lookups AS lookupPrefix
        ON lookupPrefix.LookupName = 'LookupPrefix'
        AND lookupPrefix.EId = c.TitleId

    LEFT JOIN e2x.Lookups AS lookupBusinessTitle
        ON lookupBusinessTitle.LookupName = 'LuCnBsTitle'
        AND lookupBusinessTitle.EId = c.BusinessTitleId

    WHERE c.Active = 1
      AND c.ContactTypeId IN (1, 2);

END;
GO