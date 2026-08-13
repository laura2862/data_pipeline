<#
.SYNOPSIS
Executes the generated E2X deployment SQL and writes a deployment log.

.NOTES
Requires Invoke-Sqlcmd from the SqlServer PowerShell module.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'DeployConfig.ps1'),
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$SqlFilePath,
    [string]$ServerInstance,
    [switch]$NoLogFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { throw "Config file not found: $ConfigPath" }
. $ConfigPath
$config = @{} + $E2XDeployConfig

if ([string]::IsNullOrWhiteSpace($SqlFilePath)) {
    $SqlFilePath = Join-Path (Join-Path $RootPath ([string]$config.OutputFolder)) ([string]$config.OutputFileName)
}
if ([string]::IsNullOrWhiteSpace($ServerInstance)) { $ServerInstance = [string]$config.ServerInstance }
if (-not (Test-Path -LiteralPath $SqlFilePath -PathType Leaf)) { throw "SQL deployment file not found: $SqlFilePath" }

$produceLogFile = [bool]$config.ProduceLogFile
if ($NoLogFile) { $produceLogFile = $false }

$logPath = $null
if ($produceLogFile) {
    $logFolder = Join-Path $RootPath ([string]$config.LogFolder)
    if (-not (Test-Path -LiteralPath $logFolder -PathType Container)) { New-Item -ItemType Directory -Path $logFolder | Out-Null }
    $logPath = Join-Path $logFolder (([string]$config.LogFilePrefix) + '_Deploy_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')
    Start-Transcript -LiteralPath $logPath -Append | Out-Null
}

try {
    $params = @{
        ServerInstance = $ServerInstance
        InputFile = $SqlFilePath
        QueryTimeout = 0
        AbortOnError = $true
        Verbose = $true
    }

    if (-not [bool]$config.UseWindowsAuthentication) {
        $securePassword = ConvertTo-SecureString ([string]$config.SqlPassword) -AsPlainText -Force
        $params.Credential = New-Object System.Management.Automation.PSCredential(([string]$config.SqlUsername), $securePassword)
    }

    Write-Host "Deploying SQL file: $SqlFilePath"
    Write-Host "Server instance: $ServerInstance"
    Invoke-Sqlcmd @params 4>&1 | Tee-Object -FilePath $logPath -Append
    Write-Host "Deployment completed successfully."
    if ($logPath) { Write-Host "Deployment log: $logPath" }
}
finally {
    if ($produceLogFile) { Stop-Transcript | Out-Null }
}
