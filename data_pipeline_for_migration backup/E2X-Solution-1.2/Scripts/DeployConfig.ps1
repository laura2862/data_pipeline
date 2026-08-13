# E2X migration deployment configuration
# Dot-source this file from Build-E2XDeploymentSql.ps1 and Deploy-E2XDeploymentSql.ps1.

$E2XDeployConfig = [ordered]@{
    # Target database used to prepend: USE [DatabaseName];
    DatabaseName = 'FenergoData'

    # Enables PRINT statements around every included script in the generated SQL.
    EnableSqlExecutionLogging = $true

    # Enables PowerShell transcript/log file output during build/deploy script execution.
    ProduceLogFile = $true

    # Default include file, relative to the repository root.
    RootIncludeFile = '_include.sql'

    # Output folder and generated SQL file name, relative to the repository root.
    OutputFolder = 'Output'
    OutputFileName = 'Deploy-ScotiaBank-E2XObjects.sql'

    # Log folder and file prefix, relative to the repository root.
    LogFolder = 'Output/Logs'
    LogFilePrefix = 'Deploy-ScotiaBank-E2XObjects'

    # Fail if an included script path cannot be found.
    StrictMissingFiles = $true

    # SQL Server connection settings used by Deploy-E2XDeploymentSql.ps1.
    # Leave ServerInstance as localhost or override it from the command line.
    ServerInstance = 'wvdbsu00612.uatbns.bns,5150'
    UseWindowsAuthentication = $true
    SqlUsername = 'fen_read_ist'
    SqlPassword = 'k1ng$treet2026'
}
