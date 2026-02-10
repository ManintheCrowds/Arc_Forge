#!/usr/bin/env bash
# PURPOSE: Start campaign_kb (FastAPI) and workflow_ui (Flask), then open the dashboard in the browser.
# DEPENDENCIES: Python, pip, campaign_kb and workflow_ui dependencies installed.
# MODIFICATION NOTES: Unified launcher per Wrath & Glory stack plan.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAMPAIGN_KB="${ROOT}/campaign_kb"
OBSIDIAN_VAULT="${ROOT}/ObsidianVault"

if [ ! -d "$CAMPAIGN_KB" ]; then echo "campaign_kb not found: $CAMPAIGN_KB"; exit 1; fi
if [ ! -d "$OBSIDIAN_VAULT/workflow_ui" ]; then echo "workflow_ui not found under ObsidianVault"; exit 1; fi

echo "Starting campaign_kb (FastAPI) on http://127.0.0.1:8000 ..."
(cd "$CAMPAIGN_KB" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
KB_PID=$!

sleep 2
echo "Starting workflow_ui (Flask) on http://127.0.0.1:5050 ..."
(cd "$OBSIDIAN_VAULT" && FLASK_APP=workflow_ui.app python -m flask run --host=127.0.0.1 --port=5050) &
UI_PID=$!

sleep 3
echo "Opening http://127.0.0.1:5050 in browser."
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://127.0.0.1:5050"
elif command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:5050"
else
  echo "Open http://127.0.0.1:5050 in your browser."
fi

echo "Stack running (campaign_kb PID=$KB_PID, workflow_ui PID=$UI_PID). Ctrl+C to stop."
trap "kill $KB_PID $UI_PID 2>/dev/null; exit 0" INT TERM
wait
