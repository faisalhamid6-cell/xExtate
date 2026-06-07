# ============================================================================
#  Generic Repo Auto-Sync  (Windows / PowerShell)  —  DROP-IN VERSION
# ----------------------------------------------------------------------------
#  Use this in your PRIVATE repo (gladiuxtech-cowork-os) where Co-Work writes.
#
#  Unlike sync.ps1 (which lives inside xExtate's projects folder), THIS script
#  is meant to sit at the TOP/ROOT of whatever repo you drop it into, and it
#  syncs that whole repo. Co-Work writes -> this pushes it to GitHub, and pulls
#  down anything new, automatically.
#
#  SETUP: copy this file into the root of your cloned private repo, then
#  schedule it (see README.md, "Two repos" section). No editing needed unless
#  your branch isn't 'main'.
# ============================================================================

# The branch to sync. Your private Co-Work repo can simply use "main".
$Branch = "main"

# This script sits at the repo root, so the repo root is its own folder.
$RepoRoot = $PSScriptRoot
$LogFile  = Join-Path $RepoRoot "sync-log.txt"

function Log($msg) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$stamp  $msg"
}

Set-Location $RepoRoot
git checkout $Branch *> $null

# 1) Save Co-Work's local changes first, so nothing is ever lost.
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Auto-sync from laptop (Co-Work)" *> $null
    Log "Saved local changes from the laptop."
}

# 2) Pull anything new from GitHub.
git fetch origin *> $null
git merge "origin/$Branch" *> $null
if ($LASTEXITCODE -ne 0) {
    git merge --abort *> $null
    Log "CONFLICT detected. Left safe — ask Claude to help resolve."
    exit 1
}

# 3) Push back up.
git push origin $Branch *> $null
if ($LASTEXITCODE -eq 0) { Log "Sync complete." }
else { Log "Push didn't go through; it'll retry next run." }
