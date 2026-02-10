# PURPOSE: Start campaign_kb (FastAPI) and workflow_ui (Flask), then open the dashboard in the browser.
# DEPENDENCIES: Python, pip, campaign_kb and workflow_ui dependencies installed.
# MODIFICATION NOTES: Unified launcher per Wrath & Glory stack plan.

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot + "\.."
$CampaignKb = Join-Path $Root "campaign_kb"
$ObsidianVault = Join-Path $Root "ObsidianVault"
$WorkflowUi = Join-Path $ObsidianVault "workflow_ui"

if (-not (Test-Path $CampaignKb)) { Write-Error "campaign_kb not found: $CampaignKb" }
if (-not (Test-Path $WorkflowUi)) { Write-Error "workflow_ui not found: $WorkflowUi" }

Write-Host "Starting campaign_kb (FastAPI) on http://127.0.0.1:8000 ..."
$kbJob = Start-Job -ScriptBlock { param($dir); Set-Location $dir; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 } -ArgumentList $CampaignKb

Start-Sleep -Seconds 2
Write-Host "Starting workflow_ui (Flask) on http://127.0.0.1:5050 ..."
$uiJob = Start-Job -ScriptBlock { param($dir); Set-Location $dir; $env:FLASK_APP = "workflow_ui.app"; python -m flask run --host=127.0.0.1 --port=5050 } -ArgumentList $ObsidianVault

Start-Sleep -Seconds 3
Write-Host "Opening http://127.0.0.1:5050 in browser."
Start-Process "http://127.0.0.1:5050"

Write-Host "Stack is running. Press Enter to stop both servers (jobs will be removed)."
Read-Host
Stop-Job $kbJob, $uiJob -ErrorAction SilentlyContinue
Remove-Job $kbJob, $uiJob -Force -ErrorAction SilentlyContinue
