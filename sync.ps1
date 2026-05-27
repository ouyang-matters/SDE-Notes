<#
.SYNOPSIS
  One-click Overleaf <-> local <-> GitHub sync for the SDE-Notes project.

.DESCRIPTION
  Thin wrapper around the overleaf-git-sync CLI. Forwards all arguments to
  `ovsync sync`.

  Install (one-time):
    pip install git+https://github.com/ouyang-matters/overleaf-git-sync.git

  Daily use:
    .\sync.ps1                  # pull from Overleaf, commit & push to GitHub
    .\sync.ps1 --push-first     # also push local edits up to Overleaf first
    .\sync.ps1 --dry-run        # show plan without touching anything
#>
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
ovsync --path $here sync @args
