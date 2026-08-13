SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @sql nvarchar(max) = N'';

-- Drop foreign keys where either the parent or referenced table is in e2x.
SELECT @sql += N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(fk.parent_object_id)) + N'.' + QUOTENAME(OBJECT_NAME(fk.parent_object_id)) +
               N' DROP CONSTRAINT ' + QUOTENAME(fk.name) + N';' + CHAR(13) + CHAR(10)
FROM sys.foreign_keys fk
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) = N'e2x'
   OR OBJECT_SCHEMA_NAME(fk.referenced_object_id) = N'e2x';

-- Drop views.
SELECT @sql += N'DROP VIEW ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.views
WHERE SCHEMA_NAME(schema_id) = N'e2x';

-- Drop stored procedures.
SELECT @sql += N'DROP PROCEDURE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.procedures
WHERE SCHEMA_NAME(schema_id) = N'e2x';

-- Drop functions.
SELECT @sql += N'DROP FUNCTION ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.objects
WHERE SCHEMA_NAME(schema_id) = N'e2x'
  AND type IN (N'FN', N'IF', N'TF', N'FS', N'FT');

-- Drop synonyms.
SELECT @sql += N'DROP SYNONYM ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.synonyms
WHERE SCHEMA_NAME(schema_id) = N'e2x';

-- Drop sequences.
SELECT @sql += N'DROP SEQUENCE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.sequences
WHERE SCHEMA_NAME(schema_id) = N'e2x';

-- Drop tables after dependent objects.
SELECT @sql += N'DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13) + CHAR(10)
FROM sys.tables
WHERE SCHEMA_NAME(schema_id) = N'e2x';

IF LEN(@sql) > 0
BEGIN
    PRINT @sql;
    EXEC sys.sp_executesql @sql;
END
ELSE
BEGIN
    PRINT 'No objects found in schema [e2x].';
END;
GO
