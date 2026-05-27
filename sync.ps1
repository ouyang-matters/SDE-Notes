<#
.SYNOPSIS
  Daily Overleaf <-> local <-> GitHub sync for SDE notes.

.DESCRIPTION
  Run this after a session of editing on Overleaf web. It:
    1. Pulls latest Overleaf state into the local working tree (additive,
       never deletes local-only files).
    2. If anything changed, stages and commits with a timestamped message.
    3. Pushes to GitHub.

.PARAMETER Push
  Also push local-only or locally-changed files up to Overleaf BEFORE pulling.
  Use after Claude or another tool writes new files locally that you want
  reflected on Overleaf.

.PARAMETER DryRun
  Show what would change but don't apply.

.EXAMPLE
  .\sync.ps1                 # pull from Overleaf, commit & push to GitHub
  .\sync.ps1 -Push           # push local up first, then pull, then git commit/push
  .\sync.ps1 -DryRun         # show plan only
#>
param(
  [switch]$Push,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONIOENCODING = 'utf-8'

if ($Push) {
  Write-Host "=== Push local -> Overleaf ===" -ForegroundColor Cyan
  if ($DryRun) {
    py scripts/sync_push.py
  } else {
    py scripts/sync_push.py --apply
  }
}

Write-Host "`n=== Pull Overleaf -> local ===" -ForegroundColor Cyan
if ($DryRun) {
  py scripts/sync_pull.py
} else {
  py scripts/sync_pull.py --apply
}

if ($DryRun) {
  Write-Host "`n(DryRun: not touching git)" -ForegroundColor Yellow
  return
}

Write-Host "`n=== Git status ===" -ForegroundColor Cyan
$gitStatus = git status --short
if (-not $gitStatus) {
  Write-Host "  Working tree clean — nothing to commit."
  return
}
$gitStatus | ForEach-Object { Write-Host "  $_" }

Write-Host "`n=== Commit & push ===" -ForegroundColor Cyan
git add -A
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
git commit -m "Sync from Overleaf $stamp"
git push
Write-Host "  Pushed."
