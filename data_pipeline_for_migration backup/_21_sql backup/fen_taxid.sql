select DISTINCT le.id as Legalentity,
ti.id as TaxId, ti.TaxIdentifierValue,ti.isActive,
ts.name as TaxIdentifierStatus, -- status
ttp.name as TaxType, --Type
c.name as TaxCountry-- country
from Legalentity le 
inner join taxidentifier ti on le.id=ti.LegalEntityid --TaxId
left join lookupvalue ttp on ttp.id=ti.TaxTypeId --TaxType
left join lookupvalue ts on ts.id=ti.StatusId --TaxID Status
left join country c on ti.CountryId=c.Id --Tax country
where  ti.IsActive =1
    AND ti.TaxIdentifierValue IS NOT NULL
    AND UPPER(LTRIM(RTRIM(ti.TaxIdentifierValue))) NOT IN (
			'',
            'N/A',
            'NA',
            'N.A',
            'N/A.',
            'NOT APPLICABLE',
            'NOT AVAILABLE',
            'NOT PROVIDED',
            'NOT FOUND',
            'IDENTIFIER UNAVAILABLE',
            'JURISIDICTION DOES NOT ISSUE TAX IDENTIFIER',
            'JURISDICTION DOES NOT ISSUE TAX IDENTIFIER',
            '000000000',
            '9999999',
            '999999999',
            '9999999999',
            '999999999999999',
            '9999999999999999',
            'T99999999',
            'NA000'
    )

	AND NOT( UPPER(ti.TaxIdentifierValue) LIKE 'N/A%'
			OR UPPER(ti.TaxIdentifierValue) LIKE 'NA%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT APPLICABLE%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT AVAILABLE%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT PROVIDED%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT FOUND%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%IDENTIFIER UNAVAILABLE%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NO US CONNECTION%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%SIN/TIN NOT REQUIRED%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%TIN NOT REQUIRED%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT REQUIRED%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%CTA%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%GOV ENTITY%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%GOVERNMENT ENTITY%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%BVI%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%BERMUDA%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%CAYMAN%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%DOES NOT ISSUE TAX IDENTIFIER%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%NOT YET RECEIVED TIN%'
			OR UPPER(ti.TaxIdentifierValue) LIKE '%TAX OPS CONFIRMED NOT REQUIRED%'
	)

ORDER BY
    LE.Id,
    tI.TaxIdentifierValue;



