# Install the tracking hooks into your GAME repo (Windows / PowerShell).
#   ./hooks/install.ps1 -GameRepo C:\path\to\your\game\repo
# Run this from the student-game-producer-agent folder.
# (Git for Windows runs hook scripts through its bundled sh, so the shell
#  hooks work fine — this script just copies and rewrites the path.)

param(
  [Parameter(Mandatory = $true)][string]$GameRepo
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$producerDir = (Resolve-Path "$here\..").Path -replace '\\', '/'
$hooks = Join-Path $GameRepo ".git\hooks"

if (-not (Test-Path $hooks)) {
  Write-Error "$GameRepo has no .git\hooks - is it a git repo?"
}

foreach ($h in @("post-commit", "post-merge")) {
  $target = Join-Path $hooks $h
  if ((Test-Path $target) -and -not (Select-String -Path $target -Pattern "producer-agent" -Quiet)) {
    Copy-Item $target "$target.pre-producer.bak"
    Write-Host "backed up existing hook -> $target.pre-producer.bak"
  }
  (Get-Content "$here\$h" -Raw).Replace("__PRODUCER_DIR__", $producerDir) |
    Set-Content -Path $target -Encoding ascii -NoNewline
  Write-Host "installed $target"
}

Write-Host ""
Write-Host "done. Test it:  cd `"$GameRepo`" ; git commit --allow-empty -m 'test hook'"
Write-Host "then check:     ls `"$producerDir/state/`""
