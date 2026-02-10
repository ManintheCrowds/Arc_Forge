#!/usr/bin/env bash
# PURPOSE: Run tests for campaign_kb, workflow_ui, and ObsidianVault scripts from repo root.
# DEPENDENCIES: pytest; run from arc_forge root.
# MODIFICATION NOTES: Unified test runner; --suite and --tail added per chunk_tasks_to_avoid_timeout plan.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=0
SUITE=""
TAIL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --suite=*) SUITE="${1#--suite=}"; shift ;;
    --suite)   SUITE="$2"; shift 2 ;;
    --tail=*)  TAIL="${1#--tail=}"; shift ;;
    --tail)    TAIL="$2"; shift 2 ;;
    *)         shift ;;
  esac
done

run_suite() {
  local name="$1"
  local dir="$2"
  local extra="${3:-}"
  local tail_lines="${4:-0}"
  echo "===== $name ====="
  if [ "$tail_lines" -gt 0 ]; then
    local out ex=0
    out=$(cd "$dir" && python -m pytest $extra -v --tb=short 2>&1) || ex=1
    [ $ex -ne 0 ] && FAILED=1
    echo "$out" | tail -n "$tail_lines"
    echo "----- $name : $([ $ex -eq 0 ] && echo 'OK' || echo 'FAILED') -----"
  else
    if (cd "$dir" && python -m pytest $extra -v --tb=short 2>&1); then
      echo "----- $name: OK -----"
    else
      echo "----- $name: FAILED -----"
      FAILED=1
    fi
  fi
  echo ""
}

echo "Unified test run (root: $ROOT)"
echo ""

run_ck=1; run_wu=1; run_sc=1
if [ -n "$SUITE" ]; then
  run_ck=0; run_wu=0; run_sc=0
  [ "$SUITE" = "campaign_kb" ] && run_ck=1
  [ "$SUITE" = "workflow_ui" ] && run_wu=1
  [ "$SUITE" = "scripts" ] && run_sc=1
fi

if [ $run_ck -eq 1 ] && [ -d "$ROOT/campaign_kb/tests" ]; then
  run_suite "campaign_kb" "$ROOT/campaign_kb" "tests/" "$TAIL"
fi

if [ $run_wu -eq 1 ] && [ -d "$ROOT/ObsidianVault/workflow_ui/tests" ]; then
  run_suite "workflow_ui" "$ROOT/ObsidianVault" "workflow_ui/tests/" "$TAIL"
fi

if [ $run_sc -eq 1 ] && [ -d "$ROOT/ObsidianVault/scripts/tests" ]; then
  run_suite "ObsidianVault scripts" "$ROOT/ObsidianVault" "scripts/tests/" "$TAIL"
fi

[ $FAILED -eq 0 ] && echo "All suites passed." || echo "One or more suites failed."
exit $FAILED
