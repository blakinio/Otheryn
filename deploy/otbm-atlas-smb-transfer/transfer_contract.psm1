Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AtlasManifestSha256 {
    param([Parameter(Mandatory = $true)][string]$AtlasPath)

    $manifest = Join-Path $AtlasPath "manifest.json"
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
        throw "Missing Atlas manifest: $manifest"
    }
    return (Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-AtlasCurrentStateStable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CurrentPath,
        [Parameter(Mandatory = $true)]
        [bool]$ExistedInitially,
        [AllowNull()]
        [string]$ManifestInitially
    )

    $existsNow = Test-Path -LiteralPath $CurrentPath -PathType Container
    if ($existsNow -ne $ExistedInitially) {
        throw "Atlas current state changed during transfer. Refusing promotion."
    }

    if ($existsNow) {
        if ([string]::IsNullOrWhiteSpace($ManifestInitially)) {
            throw "Missing initial Atlas current manifest fingerprint. Refusing promotion."
        }
        $manifestNow = Get-AtlasManifestSha256 -AtlasPath $CurrentPath
        if ($manifestNow -ne $ManifestInitially) {
            throw "Atlas current manifest changed during transfer. Refusing promotion."
        }
    }

    return $existsNow
}

Export-ModuleMember -Function Get-AtlasManifestSha256, Assert-AtlasCurrentStateStable
