[CmdletBinding()]
param(
    [string]$Source = "build/full-map-atlas",
    [string]$AtlasRoot = "\\Synology\docker\otheryn\atlas",
    [string]$Python = "python",
    [ValidateRange(1, 128)]
    [int]$Threads = 16,
    [switch]$AllowReplaceCurrent,
    [switch]$PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-PublicationGate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AtlasPath,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    & $Python $script:PublicationGate $AtlasPath --mode private-local --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Atlas publication gate failed for '$AtlasPath'. Evidence: $OutputPath"
    }
}

function Get-ManifestSha256 {
    param([Parameter(Mandatory = $true)][string]$AtlasPath)

    $manifest = Join-Path $AtlasPath "manifest.json"
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
        throw "Missing manifest after promotion: $manifest"
    }
    return (Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant()
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$script:PublicationGate = Join-Path $repoRoot "deploy\otbm-atlas-controlled-beta\publication_gate.py"
if (-not (Test-Path -LiteralPath $script:PublicationGate -PathType Leaf)) {
    throw "Publication gate not found: $script:PublicationGate"
}

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
    throw "Atlas source directory does not exist: $sourcePath"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$suffix = [Guid]::NewGuid().ToString("N").Substring(0, 8)
$incomingLeaf = "incoming-$stamp-$suffix"
$currentLeaf = "current"
$previousLeaf = "previous-$stamp-$suffix"
$incomingPath = Join-Path $AtlasRoot $incomingLeaf
$currentPath = Join-Path $AtlasRoot $currentLeaf
$previousPath = Join-Path $AtlasRoot $previousLeaf
$evidenceDir = Join-Path $repoRoot "build\atlas-deployment-evidence\$stamp-$suffix"
$sourceGateReport = Join-Path $evidenceDir "source-publication-gate.json"
$remoteGateReport = Join-Path $evidenceDir "smb-publication-gate.json"
$robocopyLog = Join-Path $evidenceDir "robocopy.log"
$receiptPath = Join-Path $evidenceDir "promotion-receipt.json"

$plan = [ordered]@{
    source = $sourcePath
    atlasRoot = $AtlasRoot
    incoming = $incomingPath
    current = $currentPath
    previous = $previousPath
    evidence = $evidenceDir
    replaceCurrentAllowed = [bool]$AllowReplaceCurrent
    threads = $Threads
    mode = "private-local"
}

if ($PlanOnly) {
    $plan | ConvertTo-Json -Depth 5
    exit 0
}

New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

Write-Host "[1/5] Verifying the existing desktop Atlas before transfer..."
Invoke-PublicationGate -AtlasPath $sourcePath -OutputPath $sourceGateReport

if (-not (Test-Path -LiteralPath $AtlasRoot -PathType Container)) {
    Write-Host "Creating Atlas root on the existing SMB share: $AtlasRoot"
    New-Item -ItemType Directory -Path $AtlasRoot -Force | Out-Null
}

if (Test-Path -LiteralPath $currentPath) {
    if (-not $AllowReplaceCurrent) {
        throw "'$currentPath' already exists. Refusing to replace a live/current Atlas without -AllowReplaceCurrent. Stop the preview first and rerun explicitly if replacement is intended."
    }
}

if (Test-Path -LiteralPath $incomingPath) {
    throw "Unexpected staging path already exists: $incomingPath"
}

Write-Host "[2/5] Copying the verified corpus to isolated SMB staging..."
New-Item -ItemType Directory -Path $incomingPath -Force | Out-Null
$robocopyArgs = @(
    $sourcePath,
    $incomingPath,
    "/MIR",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/R:2",
    "/W:2",
    "/MT:$Threads",
    "/XJ",
    "/NP",
    "/LOG:$robocopyLog"
)
& robocopy.exe @robocopyArgs
$robocopyExitCode = $LASTEXITCODE
if ($robocopyExitCode -ge 8) {
    throw "robocopy failed with exit code $robocopyExitCode. Staging was not promoted. Log: $robocopyLog"
}

Write-Host "[3/5] Re-verifying the copied corpus over SMB..."
Invoke-PublicationGate -AtlasPath $incomingPath -OutputPath $remoteGateReport

Write-Host "[4/5] Promoting verified staging to current..."
$previousCreated = $false
if (Test-Path -LiteralPath $currentPath) {
    if (Test-Path -LiteralPath $previousPath) {
        throw "Rollback path already exists: $previousPath"
    }
    Rename-Item -LiteralPath $currentPath -NewName $previousLeaf
    $previousCreated = $true
}

try {
    Rename-Item -LiteralPath $incomingPath -NewName $currentLeaf
}
catch {
    if ($previousCreated -and (Test-Path -LiteralPath $previousPath) -and -not (Test-Path -LiteralPath $currentPath)) {
        Rename-Item -LiteralPath $previousPath -NewName $currentLeaf
    }
    throw
}

$manifestSha256 = Get-ManifestSha256 -AtlasPath $currentPath
$receipt = [ordered]@{
    schemaVersion = 1
    promotedAt = (Get-Date).ToString("o")
    source = $sourcePath
    current = $currentPath
    previous = if ($previousCreated) { $previousPath } else { $null }
    manifestSha256 = $manifestSha256
    robocopyExitCode = $robocopyExitCode
    sourceGateReport = $sourceGateReport
    remoteGateReport = $remoteGateReport
    publicationMode = "private-local"
    internetExposureActivated = $false
}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

Write-Host "[5/5] Promotion complete."
Write-Host "Current Atlas: $currentPath"
Write-Host "Manifest SHA-256: $manifestSha256"
Write-Host "Evidence: $evidenceDir"
Write-Host "No DSM project, reverse proxy, Cloudflare route, or Internet exposure was changed by this script."
