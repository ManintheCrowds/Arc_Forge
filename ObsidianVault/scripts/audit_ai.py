# PURPOSE: Append-only audit log for AI prompts (traceability).
# DEPENDENCIES: hashlib, json, pathlib
# MODIFICATION NOTES: AI security P1; prompt hash, timestamp, model, action.

"""
Append-only audit log for AI operations.
Fields: prompt_hash (SHA256), timestamp, model, action_type.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

_AUDIT_DIR = Path(os.environ.get("AI_AUDIT_LOG_DIR", "")) or (Path(__file__).parent / "logs")
AUDIT_FILE = _AUDIT_DIR / "ai_audit.jsonl"


def _ensure_log_dir() -> None:
    _AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def log_ai_action(prompt: str, model: str, action_type: str, metadata: dict | None = None) -> None:
    """
    Append one record to the AI audit log.
    prompt_hash is SHA256 of prompt (no PII stored).
    """
    _ensure_log_dir()
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    record = {
        "prompt_hash": prompt_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "action_type": action_type,
        **(metadata or {}),
    }
    try:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass
