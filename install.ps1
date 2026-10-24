# ==============================================================================
# A.T.L.A.S — Windows installer entrypoint (PowerShell)
# ==============================================================================
# Usage (from PowerShell):
#   .\install.ps1                          # full bootstrap
#   .\install.ps1 -ForceSecrets           # rotate all secrets (destructive)
#   .\install.ps1 -NoPull                 # skip docker compose pull
#   .\install.ps1 -Profile observability
#   .\install.ps1 -SkipOpen               # do not open the app at the end
#
# Use install.bat to invoke this from cmd / Explorer.
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$ForceSecrets,
    [switch]$NoPull,
    [switch]$SkipOpen,
    [string[]]$Profile
)

$ErrorActionPreference = "Stop"

# Resolve repo root (this script lives at the repo root).
$AtlasRepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$AtlasLibDir   = Join-Path $AtlasRepoRoot "installer\lib"
if (-not $env:ATLAS_HOME) { $env:ATLAS_HOME = Join-Path $env:USERPROFILE ".atlas" }
$AtlasHome = $env:ATLAS_HOME

# Stash parsed args into script-scoped globals the bootstrap expects.
$AtlasForceSecrets = [bool]$ForceSecrets
$AtlasNoPull       = [bool]$NoPull
$AtlasSkipOpen     = [bool]$SkipOpen
$AtlasProfiles     = @($Profile)

. (Join-Path $AtlasLibDir "detect.ps1")
. (Join-Path $AtlasLibDir "docker_install.ps1")
. (Join-Path $AtlasLibDir "bootstrap.ps1")

$rc = Invoke-Bootstrap
exit $rc
