# PURPOSE: Run tests for campaign_kb, workflow_ui, and ObsidianVault scripts from repo root.
# DEPENDENCIES: pytest; run from arc_forge root.
# MODIFICATION NOTES: Unified test runner; -Suite and -Tail added per chunk_tasks_to_avoid_timeout plan.

param(
  [ValidateSet("", "campaign_kb", "workflow_ui", "scripts")]
  [string]$Suite = "",
  [int]$Tail = 0
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Failed = 0

function Run-Suite {
  param([string]$Name, [string]$Dir, [string]$Extra = "", [int]$TailLines = 0)
  Write-Host "===== $Name ====="
  Push-Location $Dir
  try {
    if ($TailLines -gt 0) {
      $out = if ($Extra) { python -m pytest $Extra -v --tb=short 2>&1 | Out-String } else { python -m pytest -v --tb=short 2>&1 | Out-String }
      if ($LASTEXITCODE -ne 0) { $script:Failed = 1 }
      $lines = ($out -split "`n")
      $lines | Select-Object -Last $TailLines | ForEach-Object { Write-Host $_ }
    } else {
      if ($Extra) { python -m pytest $Extra -v --tb=short } else { python -m pytest -v --tb=short }
      if ($LASTEXITCODE -ne 0) { $script:Failed = 1 }
    }
    Write-Host "----- $Name : $(if ($LASTEXITCODE -eq 0) { 'OK' } else { 'FAILED' }) -----"
  } finally {
    Pop-Location
  }
  Write-Host ""
}

Write-Host "Unified test run (root: $Root)`n"

$ck = Join-Path $Root "campaign_kb"
$ov = Join-Path $Root "ObsidianVault"

$runCk = (-not $Suite) -or ($Suite -eq "campaign_kb")
$runWu = (-not $Suite) -or ($Suite -eq "workflow_ui")
$runSc = (-not $Suite) -or ($Suite -eq "scripts")

if ($runCk -and (Test-Path (Join-Path $ck "tests"))) {
  Run-Suite "campaign_kb" $ck "tests/" $Tail
}
if ($runWu -and (Test-Path (Join-Path $ov "workflow_ui\tests"))) {
  Run-Suite "workflow_ui" $ov "workflow_ui/tests/" $Tail
}
if ($runSc -and (Test-Path (Join-Path $ov "scripts\tests"))) {
  Run-Suite "ObsidianVault scripts" $ov "scripts/tests/" $Tail
}

if ($Failed -eq 0) { Write-Host "All suites passed." } else { Write-Host "One or more suites failed." }
exit $Failed
