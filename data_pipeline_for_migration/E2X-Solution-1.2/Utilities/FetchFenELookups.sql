------------------------------------------------------------
-- 1. List Lookups to be Extracted
------------------------------------------------------------
DECLARE @tasks TABLE (
    LookupTableName sysname NOT NULL,
    UseIDEvenIfInternalValueProvided bit NULL      -- NULL = use default behaviour
);
-- Add lookups here
-- INSERT INTO @tasks (LookupTableName, UseIDEvenIfInternalValueProvided) VALUES
-- ('SomeLookup', NULL),
-- ('AnotherLookup', NULL);

INSERT INTO @tasks (LookupTableName, UseIDEvenIfInternalValueProvided) VALUES
('AppVHighRiskIndustry', NULL),
('Country', NULL),
('DocumentPurpose', NULL),
('EntityType', NULL),
('ExpectedActivityType', NULL),
('FinCENExemptionCategory', NULL),
('FreqTradingVol', NULL),
('Gender', NULL),
('IsicCodeDescription', NULL),
('KYCClientType', NULL),
('LECategory', NULL),
('LECompanyDesk', NULL),
('LookUpInsiderStatusList', NULL),
('LookupAddressType', NULL),
('LookupContactStatus', NULL),
('LookupContactSubType', NULL),
('LookupEmploymentStatus', NULL),
('LookupISCCode', NULL),
('LookupKYCLevel', NULL),
('LookupLegalStatus', NULL),
('LookupListenOn', NULL),
('LookupPrefix', NULL),
('LookupProductCategory', NULL),
('LookupProductType', NULL),
('LookupRegulator', NULL),
('LookupTaxIdentifierReasonNumberNotProvided', NULL),
('LookupTaxIdentifierStatus', NULL),
('LuCnBsTitle', NULL),
('LuLeAs', NULL),
('LuLeSubTpIndividual', NULL),
('LuLeSubTpWithUndefined', NULL),
('GlobalModelExclusions', NULL),
('NaceCodeDescription', NULL),
('NaicCodeDescription', NULL),
('ProductClosureReason', NULL),
('ProductStatus', NULL),
('RegulatoryStatus', NULL),
('RemediationStatus', NULL),
('RiskEntityType', NULL),
('SicCodeDescription', NULL),
('SourceFundsScotia', NULL),
('SpecializedEDDType', NULL),
('TaxId', NULL),
('TypeOfInvestor', NULL),
('YesNo', NULL),
('YesNoNotApplicable', NULL),
('productConfig.BookingEntity', NULL),
--dsdg
('DGSDLegalEntityType', NULL),
('UnderlyingCompanyList', NULL),
('BudgetList', NULL),
('NumberOfEmployeesList', NULL),
('AnnualTurnoverList', NULL),
('AnnualBalanceSheetList', NULL),
('FinalDGSDLegalEntityType', NULL),
('DGSDCounterpartyEligibility', NULL),
--finra
('SuitabilityCertificateProvider', NULL),
('FINRA_Institutional_client', NULL),
('Finra_Suitability_Factors', NULL);

-- TODO: add more

------------------------------------------------------------
-- 2. Temp table for final unified result
------------------------------------------------------------
IF OBJECT_ID('tempdb..#LookupValues') IS NOT NULL
    DROP TABLE #LookupValues;

CREATE TABLE #LookupValues (
    LookupName sysname       NOT NULL,
    EValue     nvarchar(max) NULL,
    EId        nvarchar(50)  NULL
);

------------------------------------------------------------
-- 2b. Temp table variable for external selects (UseExistingTable = 1)
-- Declared once and reused; contents cleared per iteration.
------------------------------------------------------------
DECLARE @TmpExternal TABLE (
    EId    nvarchar(50)  NULL,
    EValue nvarchar(max) NULL
);

------------------------------------------------------------
-- 3. Cursor over Lookups
------------------------------------------------------------
DECLARE @LookupName      sysname,
        @UseIDEvenIfInternalValueProvided bit,
        @UseExisting     bit,
        @SelectStatement nvarchar(max);

DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
    SELECT LookupTableName, UseIDEvenIfInternalValueProvided
    FROM @tasks;

OPEN cur;
FETCH NEXT FROM cur INTO @LookupName, @UseIDEvenIfInternalValueProvided;

WHILE @@FETCH_STATUS = 0
BEGIN
    --------------------------------------------------------
    -- Load LookupTable config for this lookup
    --------------------------------------------------------
    SET @UseExisting     = 0;
    SET @SelectStatement = NULL;

    SELECT 
        @UseExisting     = ISNULL(LT.UseExistingTable, 0),
        @SelectStatement = LT.SelectStatement
    FROM dbo.LookupTable AS LT
    WHERE LT.Name = @LookupName;

    IF @@ROWCOUNT = 0
    BEGIN
        RAISERROR('LookupTable "%s" not found.', 16, 1, @LookupName);
        FETCH NEXT FROM cur INTO @LookupName, @UseIDEvenIfInternalValueProvided;
        CONTINUE;
    END;

    --------------------------------------------------------
    -- Branch 1: UseExistingTable = 0
    -- Normal join LookupTable → LookupTableValue → LookupValue
    -- EId logic honours @UseIDEvenIfInternalValueProvided:
    --   - @UseIDEvenIfInternalValueProvided = 1	- always LV.Id
    --   - else				                    - InternalValue if NOT NULL, else LV.Id
    --------------------------------------------------------
    IF @UseExisting = 0
    BEGIN
        INSERT INTO #LookupValues (LookupName, EValue, EId)
        SELECT
            @LookupName                                                   AS LookupName,
            LV.Name                                                       AS EValue,
            CASE 
                WHEN @UseIDEvenIfInternalValueProvided = 1 OR LV.InternalValue IS NULL
                    THEN CAST(LV.Id AS nvarchar(50))
                ELSE LV.InternalValue
            END                                                           AS EId
        FROM dbo.LookupTable       AS LT
        INNER JOIN dbo.LookupTableValue AS LTV
            ON LT.Id = LTV.TableId
        INNER JOIN dbo.LookupValue AS LV
            ON LV.Id = LTV.ValueId
        WHERE LT.Name     = @LookupName
          AND LV.IsActive = 1;
    END
    --------------------------------------------------------
    -- Branch 2: UseExistingTable = 1
    -- Inline the dynamic SELECT logic from GenerateLookupInserts
    --------------------------------------------------------
    ELSE
    BEGIN
        ----------------------------------------------------
        -- Clear previous external rows to avoid mixing data
        -- between different lookups.
        ----------------------------------------------------
        DELETE FROM @TmpExternal;

        ----------------------------------------------------
        -- If SelectStatement is NULL, build default:
        --   SELECT Id, Name FROM <LookupTable.Name>
        -- If no schema in Name, assume dbo.
        ----------------------------------------------------
        IF @SelectStatement IS NULL
        BEGIN
            DECLARE @obj sysname = @LookupName;
            DECLARE @dot int     = CHARINDEX('.', @obj);

            IF @dot > 0
                SET @SelectStatement = N'SELECT Id, Name FROM ' + @obj;
            ELSE
                SET @SelectStatement = N'SELECT Id, Name FROM dbo.' + @obj;
        END;

        ----------------------------------------------------
        -- Strip ORDER BY (if present)
        ----------------------------------------------------
		DECLARE @stmtNormalized nvarchar(max) =
			REPLACE(
				REPLACE(
					REPLACE(@SelectStatement, CHAR(13), ' '),
					CHAR(10), ' '
				),
				CHAR(9), ' '
			);

		DECLARE @reversePos int =
			CHARINDEX(
				'yb redro',
				REVERSE(@stmtNormalized) COLLATE Latin1_General_100_CI_AS
			);

		DECLARE @posOrderBy int =
			CASE
				WHEN @reversePos > 0
					THEN LEN(@stmtNormalized) - @reversePos - LEN('order by') + 2
				ELSE 0
			END;

		DECLARE @SelectNoOrderBy nvarchar(max);

		IF @posOrderBy > 0
			SET @SelectNoOrderBy =
				RTRIM(LEFT(@SelectStatement, @posOrderBy - 1));
		ELSE
			SET @SelectNoOrderBy = @SelectStatement;

        ----------------------------------------------------
        -- Execute the external SELECT (Id, Name) and capture
        -- them as EId / EValue
        ----------------------------------------------------
        DECLARE @sql nvarchar(max) = N'
            SELECT
                CAST(src.Id   AS nvarchar(50))      AS EId,
                CAST(src.Name AS nvarchar(max))     AS EValue
            FROM (' + @SelectNoOrderBy + N') AS src;';

        INSERT INTO @TmpExternal (EId, EValue)
        EXEC sys.sp_executesql @sql;

        INSERT INTO #LookupValues (LookupName, EValue, EId)
        SELECT @LookupName, EValue, EId
        FROM @TmpExternal;
    END;

    FETCH NEXT FROM cur INTO @LookupName, @UseIDEvenIfInternalValueProvided;
END;

CLOSE cur;
DEALLOCATE cur;

------------------------------------------------------------
-- 4. Final unified TABLE result
------------------------------------------------------------
SELECT
    LookupName,
    EValue,
    EId,
    EValue,
    'INSERT INTO e2x.Lookups (LookupName, EValue, EId, XValue) VALUES ('''
    + REPLACE(LookupName, '''', '''''') + ''', '''
    + REPLACE(EValue, '''', '''''') + ''', '
    + CAST(EId AS varchar(20))
    + ', '''
    + REPLACE(EValue, '''', '''''') + ''');' AS InsertStatement -- Assume EValue is the same as XValue
FROM #LookupValues
ORDER BY LookupName, EId;