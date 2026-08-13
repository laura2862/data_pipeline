<#
.SYNOPSIS
Builds one deployable SQL file for E2X migration objects from _include.sql files.

.DESCRIPTION
Reads a root _include.sql file and recursively expands nested include files.
Include files should contain relative paths, one per line. Blank lines and lines
starting with --, #, or // are ignored.

This script is compatible with Windows PowerShell 5.1 and PowerShell 7+.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'DeployConfig.ps1'),
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$IncludeFile,
    [string]$OutputPath,
    [switch]$NoSqlExecutionLogging,
    [switch]$NoLogFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Quote-SqlIdentifier {
    param([Parameter(Mandatory = $true)][string]$Name)
    return '[' + ($Name -replace ']', ']]') + ']'
}

function Escape-SqlString {
    param([string]$Value)
    if ($null -eq $Value) { return '' }
    return $Value -replace "'", "''"
}

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-RelativePathCompat {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$TargetPath
    )

    # [System.IO.Path]::GetRelativePath is not available in Windows PowerShell 5.1.
    $baseFull = Resolve-FullPath $BasePath
    $targetFull = Resolve-FullPath $TargetPath

    if (-not $baseFull.EndsWith([string][System.IO.Path]::DirectorySeparatorChar) -and
        -not $baseFull.EndsWith([string][System.IO.Path]::AltDirectorySeparatorChar)) {
        $baseFull += [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = [System.Uri]::new($baseFull)
    $targetUri = [System.Uri]::new($targetFull)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    $relativePath = [System.Uri]::UnescapeDataString($relativeUri.ToString())
    return $relativePath -replace '/', [System.IO.Path]::DirectorySeparatorChar
}

function Resolve-IncludePath {
    param(
        [Parameter(Mandatory = $true)][string]$BaseDirectory,
        [Parameter(Mandatory = $true)][string]$RelativeOrAbsolutePath
    )

    $cleanPath = $RelativeOrAbsolutePath.Trim().Trim([char]0xFEFF).Trim().Trim('"').Trim("'")
    if ([System.IO.Path]::IsPathRooted($cleanPath)) {
        return Resolve-FullPath $cleanPath
    }

    return Resolve-FullPath (Join-Path $BaseDirectory $cleanPath)
}

function Read-IncludeFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [hashtable]$VisitedIncludes,
        [System.Collections.Generic.List[string]]$IncludeStack,
        [System.Collections.Generic.List[string]]$ResolvedSqlFiles,
        [hashtable]$ResolvedSqlFileSet,
        [bool]$StrictMissingFiles
    )

    if ($null -eq $VisitedIncludes) { $VisitedIncludes = @{} }
    if ($null -eq $IncludeStack) { $IncludeStack = [System.Collections.Generic.List[string]]::new() }
    if ($null -eq $ResolvedSqlFiles) { throw 'ResolvedSqlFiles cannot be null.' }
    if ($null -eq $ResolvedSqlFileSet) { throw 'ResolvedSqlFileSet cannot be null.' }

    $fullIncludePath = Resolve-FullPath $Path

    if ($IncludeStack.Contains($fullIncludePath)) {
        $cycleParts = @($IncludeStack.ToArray()) + @($fullIncludePath)
        $cycle = $cycleParts -join ' -> '
        throw "Circular include detected: $cycle"
    }

    if ($VisitedIncludes.ContainsKey($fullIncludePath)) { return }

    if (-not (Test-Path -LiteralPath $fullIncludePath -PathType Leaf)) {
        throw "Include file not found: $fullIncludePath"
    }

    [void]$IncludeStack.Add($fullIncludePath)
    $VisitedIncludes[$fullIncludePath] = $true
    $baseDirectory = Split-Path -Parent $fullIncludePath

    try {
        foreach ($rawLine in Get-Content -LiteralPath $fullIncludePath) {
            $line = $rawLine.Trim().Trim([char]0xFEFF).Trim()
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            if ($line.StartsWith('--') -or $line.StartsWith('#') -or $line.StartsWith('//')) { continue }

            $resolvedPath = Resolve-IncludePath -BaseDirectory $baseDirectory -RelativeOrAbsolutePath $line
            $extension = [System.IO.Path]::GetExtension($resolvedPath).ToLowerInvariant()

            if ($extension -ne '.sql') {
                if ($StrictMissingFiles) {
                    throw "Include entry has unsupported extension: $line in $fullIncludePath"
                }
                Write-Warning "Skipping non-SQL include entry: $line"
                continue
            }

            $isNestedInclude = [System.IO.Path]::GetFileName($resolvedPath).Equals('_include.sql', [System.StringComparison]::OrdinalIgnoreCase)

            if ($isNestedInclude) {
                Read-IncludeFile -Path $resolvedPath -VisitedIncludes $VisitedIncludes -IncludeStack $IncludeStack -ResolvedSqlFiles $ResolvedSqlFiles -ResolvedSqlFileSet $ResolvedSqlFileSet -StrictMissingFiles $StrictMissingFiles
                continue
            }

            if (-not (Test-Path -LiteralPath $resolvedPath -PathType Leaf)) {
                if ($StrictMissingFiles) {
                    throw "SQL file listed in include file but not found: $resolvedPath"
                }
                Write-Warning "Skipping missing SQL file: $resolvedPath"
                continue
            }

            $fullSqlPath = Resolve-FullPath $resolvedPath
            if ($ResolvedSqlFileSet.ContainsKey($fullSqlPath)) {
                throw "Duplicate SQL include detected: $fullSqlPath"
            }

            $ResolvedSqlFileSet[$fullSqlPath] = $true
            [void]$ResolvedSqlFiles.Add($fullSqlPath)
        }
    }
    finally {
        if ($IncludeStack.Count -gt 0) {
            [void]$IncludeStack.RemoveAt($IncludeStack.Count - 1)
        }
    }
}

function Add-PreDeploymentSqlFiles {
    param(
        [Parameter(Mandatory = $true)][System.Collections.Generic.List[string]]$SqlFiles,
        [Parameter(Mandatory = $true)][hashtable]$SqlFileSet,
        [Parameter(Mandatory = $true)][string]$ScriptsRoot,
        [Parameter(Mandatory = $true)][bool]$StrictMissingFiles
    )

    $preDeploymentFileNames = @(
        'Drop-E2XObjects.sql',
        'Deploy-E2XDataExtractsObjects.sql'
    )

    $orderedSqlFiles = [System.Collections.Generic.List[string]]::new()
    $orderedSqlFileSet = @{}

    foreach ($fileName in $preDeploymentFileNames) {
        $candidatePaths = @(
            (Join-Path (Join-Path $ScriptsRoot 'Sql') $fileName),
            (Join-Path $ScriptsRoot $fileName)
        )

        $preDeploymentPath = $null
        foreach ($candidatePath in $candidatePaths) {
            if (Test-Path -LiteralPath $candidatePath -PathType Leaf) {
                $preDeploymentPath = Resolve-FullPath $candidatePath
                break
            }
        }

        if ([string]::IsNullOrWhiteSpace($preDeploymentPath)) {
            if ($StrictMissingFiles) {
                throw "Required pre-deployment SQL file not found: $fileName. Checked: $($candidatePaths -join ', ')"
            }
            Write-Warning "Skipping missing pre-deployment SQL file: $fileName"
            continue
        }

        if (-not $orderedSqlFileSet.ContainsKey($preDeploymentPath)) {
            $orderedSqlFileSet[$preDeploymentPath] = $true
            [void]$orderedSqlFiles.Add($preDeploymentPath)
        }
    }

    foreach ($file in $SqlFiles) {
        $fullSqlPath = Resolve-FullPath $file
        if (-not $orderedSqlFileSet.ContainsKey($fullSqlPath)) {
            $orderedSqlFileSet[$fullSqlPath] = $true
            [void]$orderedSqlFiles.Add($fullSqlPath)
        }
    }

    $SqlFiles.Clear()
    foreach ($file in $orderedSqlFiles) {
        [void]$SqlFiles.Add($file)
    }

    $SqlFileSet.Clear()
    foreach ($file in $orderedSqlFiles) {
        $SqlFileSet[$file] = $true
    }
}

if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
    throw "Config file not found: $ConfigPath"
}

. $ConfigPath
$config = @{} + $E2XDeployConfig

if ([string]::IsNullOrWhiteSpace($IncludeFile)) { $IncludeFile = [string]$config.RootIncludeFile }
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $outputFolder = Join-Path $RootPath ([string]$config.OutputFolder)
    $OutputPath = Join-Path $outputFolder ([string]$config.OutputFileName)
}

$databaseName = [string]$config.DatabaseName
$enableSqlLogging = [bool]$config.EnableSqlExecutionLogging
if ($NoSqlExecutionLogging) { $enableSqlLogging = $false }
$produceLogFile = [bool]$config.ProduceLogFile
if ($NoLogFile) { $produceLogFile = $false }
$strictMissingFiles = [bool]$config.StrictMissingFiles

if ([string]::IsNullOrWhiteSpace($databaseName) -or $databaseName -eq 'YourDatabaseName') {
    throw 'Set DatabaseName in DeployConfig.ps1 before building the deployment SQL.'
}

$logPath = $null
if ($produceLogFile) {
    $logFolder = Join-Path $RootPath ([string]$config.LogFolder)
    if (-not (Test-Path -LiteralPath $logFolder -PathType Container)) { New-Item -ItemType Directory -Path $logFolder | Out-Null }
    $logPath = Join-Path $logFolder (([string]$config.LogFilePrefix) + '_Build_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')
    Start-Transcript -LiteralPath $logPath -Append | Out-Null
}

try {
    $rootIncludePath = Resolve-IncludePath -BaseDirectory $RootPath -RelativeOrAbsolutePath $IncludeFile
    $sqlFiles = [System.Collections.Generic.List[string]]::new()
    $visitedIncludes = @{}
    $includeStack = [System.Collections.Generic.List[string]]::new()
    $sqlFileSet = @{}

    Read-IncludeFile -Path $rootIncludePath -VisitedIncludes $visitedIncludes -IncludeStack $includeStack -ResolvedSqlFiles $sqlFiles -ResolvedSqlFileSet $sqlFileSet -StrictMissingFiles $strictMissingFiles
    Add-PreDeploymentSqlFiles -SqlFiles $sqlFiles -SqlFileSet $sqlFileSet -ScriptsRoot $PSScriptRoot -StrictMissingFiles $strictMissingFiles

    $outputDirectory = Split-Path -Parent (Resolve-FullPath $OutputPath)
    if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) { New-Item -ItemType Directory -Path $outputDirectory | Out-Null }

    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.AppendLine('/*')
    [void]$builder.AppendLine('Generated E2X deployment script')
    [void]$builder.AppendLine(('Generated at: {0:yyyy-MM-dd HH:mm:ss zzz}' -f (Get-Date)))
    [void]$builder.AppendLine(('Root include: {0}' -f $rootIncludePath))
    [void]$builder.AppendLine('*/')
    [void]$builder.AppendLine('SET NOCOUNT ON;')
    [void]$builder.AppendLine('SET XACT_ABORT ON;')
    [void]$builder.AppendLine(('USE {0};' -f (Quote-SqlIdentifier $databaseName)))
    [void]$builder.AppendLine('GO')
    [void]$builder.AppendLine('')

    foreach ($file in $sqlFiles) {
        $relativeFile = Get-RelativePathCompat -BasePath $RootPath -TargetPath $file
        if ($enableSqlLogging) {
            [void]$builder.AppendLine(('PRINT ''Deploying: {0}'';' -f (Escape-SqlString $relativeFile)))
            [void]$builder.AppendLine('GO')
        }
        [void]$builder.AppendLine(('/* BEGIN: {0} */' -f $relativeFile))
        [void]$builder.AppendLine((Get-Content -LiteralPath $file -Raw))
        [void]$builder.AppendLine('')
        [void]$builder.AppendLine(('/* END: {0} */' -f $relativeFile))
        [void]$builder.AppendLine('GO')
        [void]$builder.AppendLine('')
    }

    Set-Content -LiteralPath $OutputPath -Value $builder.ToString() -Encoding UTF8
    Write-Host "Generated deployment SQL: $OutputPath"
    Write-Host "Included SQL files: $($sqlFiles.Count)"
    if ($logPath) { Write-Host "Build log: $logPath" }
}
finally {
    if ($produceLogFile) { Stop-Transcript | Out-Null }
}
