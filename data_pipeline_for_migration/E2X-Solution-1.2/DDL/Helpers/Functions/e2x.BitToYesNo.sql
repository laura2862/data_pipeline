CREATE OR ALTER FUNCTION e2x.BitToYesNo
(
    @BitValue BIT,
    @NullValue NVARCHAR(50) = NULL  -- optional parameter, defaults to NULL
)
RETURNS NVARCHAR(50)
AS
BEGIN
    RETURN (
        CASE 
            WHEN @BitValue = 1 THEN 'Yes'
            WHEN @BitValue = 0 THEN 'No'
            ELSE @NullValue
        END
    );
END;
GO