# ============================================================================
#  Claude Workspace Auto-Sync  (Windows / PowerShell)
# ----------------------------------------------------------------------------
#  What this does, in plain English:
#    Every time it runs, it (1) saves any changes Co-Work made on your laptop,
#    (2) pulls in any changes Claude Code made in the cloud, and (3) pushes
#    everything back up to GitHub. Run it on a schedule and your laptop and
#    Claude Code stay in sync automatically — no clicking.
#
#  You do NOT need to edit this file: it figures out the repo location itself.
#  See README.md in this folder for the one-time setup (it's 3 steps).
# ============================================================================

# The shared branch both sides use. (After we merge into 'main', change this to "main".)
$Branch = "claude/pensive-cori-ywRyY"

# Work out the repo's root folder automatically:
#   this script lives in <repo>\projects\workspace-sync\, so go up two levels.
$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

# Where to write a simple activity log (ignored by git, so it never syncs).
$LogFile = Join-Path $RepoRoot "workspace\sync-log.txt"

function Log($msg) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$stamp  $msg"
}

Set-Location $RepoRoot

# Make sure we're on the shared branch.
git checkout $Branch *> $null

# 1) Save Co-Work's local changes first, so nothing can ever be lost.
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Auto-sync from laptop (Co-Work)" *> $null
    Log "Saved local changes from the laptop."
}

# 2) Pull Claude Code's latest changes from GitHub.
git fetch origin *> $null
git merge "origin/$Branch" *> $null
if ($LASTEXITCODE -ne 0) {
    # Both sides edited the same thing. Back out safely and ask for help —
    # nothing is lost; your committed work is intact.
    git merge --abort *> $null
    Log "CONFLICT: laptop and cloud edited the same file. Left safe — ask Claude to resolve."
    exit 1
}

# 3) Push everything back up to GitHub.
git push origin $Branch *> $null
if ($LASTEXITCODE -eq 0) {
    Log "Sync complete."
} else {
    Log "Push didn't go through this time — it'll retry on the next run."
}
