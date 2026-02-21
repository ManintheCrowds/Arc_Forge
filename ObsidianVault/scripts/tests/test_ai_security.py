# PURPOSE: Unit tests for AI security adoption (Phases 1-4).
# DEPENDENCIES: pytest
# MODIFICATION NOTES: Tests credential_vault, cloud_ai_consent, audit_ai, tool_registry.

import hashlib
import json
import sys
from pathlib import Path

import pytest

# Ensure scripts dir is on path when run from tests/
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


class TestCredentialVault:
    """Phase 1.1: Credential vault."""

    def test_get_secret_from_env(self, monkeypatch):
        """get_secret returns env value when keyring unavailable or empty."""
        monkeypatch.setenv("TEST_KEY", "env-secret")
        from credential_vault import get_secret
        assert get_secret("TEST_KEY") == "env-secret"

    def test_get_secret_default(self, monkeypatch):
        """get_secret returns default when not in env."""
        monkeypatch.delenv("MISSING_KEY", raising=False)
        from credential_vault import get_secret
        assert get_secret("MISSING_KEY", "default") == "default"
        assert get_secret("MISSING_KEY") is None


class TestCloudAIConsent:
    """Phase 1.3: Human-in-the-loop consent."""

    def test_has_consent_via_env(self, monkeypatch):
        """has_cloud_ai_consent returns True when CLOUD_AI_CONSENT=1."""
        monkeypatch.setenv("CLOUD_AI_CONSENT", "1")
        from cloud_ai_consent import has_cloud_ai_consent
        assert has_cloud_ai_consent() is True

    def test_has_consent_via_file(self, monkeypatch, tmp_path):
        """has_cloud_ai_consent returns True when consent file contains '1'."""
        consent_file = tmp_path / "cloud_ai_consent"
        consent_file.write_text("1")
        monkeypatch.delenv("CLOUD_AI_CONSENT", raising=False)
        monkeypatch.setattr("cloud_ai_consent.CONSENT_DIR", tmp_path)
        monkeypatch.setattr("cloud_ai_consent.CONSENT_FILE", consent_file)
        from cloud_ai_consent import has_cloud_ai_consent
        assert has_cloud_ai_consent() is True

    def test_no_consent(self, monkeypatch, tmp_path):
        """has_cloud_ai_consent returns False when neither env nor file."""
        monkeypatch.delenv("CLOUD_AI_CONSENT", raising=False)
        monkeypatch.setattr("cloud_ai_consent.CONSENT_FILE", tmp_path / "nonexistent")
        from cloud_ai_consent import has_cloud_ai_consent
        assert has_cloud_ai_consent() is False

    def test_set_cloud_ai_consent(self, monkeypatch, tmp_path):
        """set_cloud_ai_consent creates file with '1'."""
        consent_dir = tmp_path / "config"
        consent_file = consent_dir / "cloud_ai_consent"
        monkeypatch.setattr("cloud_ai_consent.CONSENT_DIR", consent_dir)
        monkeypatch.setattr("cloud_ai_consent.CONSENT_FILE", consent_file)
        from cloud_ai_consent import set_cloud_ai_consent, has_cloud_ai_consent
        set_cloud_ai_consent()
        assert consent_file.exists()
        assert consent_file.read_text().strip() == "1"
        assert has_cloud_ai_consent() is True

    def test_require_consent_raises(self, monkeypatch, tmp_path):
        """require_cloud_ai_consent raises when not consented."""
        monkeypatch.delenv("CLOUD_AI_CONSENT", raising=False)
        monkeypatch.setattr("cloud_ai_consent.CONSENT_FILE", tmp_path / "nonexistent")
        from cloud_ai_consent import require_cloud_ai_consent
        with pytest.raises(RuntimeError, match="consent required"):
            require_cloud_ai_consent()


class TestAuditAI:
    """Phase 2: Traceability."""

    def test_log_ai_action_creates_record(self, monkeypatch, tmp_path):
        """log_ai_action appends valid JSONL record."""
        audit_file = tmp_path / "ai_audit.jsonl"
        monkeypatch.setattr("audit_ai._AUDIT_DIR", tmp_path)
        monkeypatch.setattr("audit_ai.AUDIT_FILE", audit_file)
        from audit_ai import log_ai_action
        log_ai_action("test prompt", "ollama:llama2", "rag_query")
        assert audit_file.exists()
        lines = audit_file.read_text().strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["prompt_hash"] == hashlib.sha256(b"test prompt").hexdigest()
        assert record["model"] == "ollama:llama2"
        assert record["action_type"] == "rag_query"
        assert "timestamp" in record

    def test_log_ai_action_with_metadata(self, monkeypatch, tmp_path):
        """log_ai_action includes optional metadata."""
        audit_file = tmp_path / "ai_audit.jsonl"
        monkeypatch.setattr("audit_ai._AUDIT_DIR", tmp_path)
        monkeypatch.setattr("audit_ai.AUDIT_FILE", audit_file)
        from audit_ai import log_ai_action
        log_ai_action("p", "m", "a", metadata={"extra": "value"})
        record = json.loads(audit_file.read_text().strip())
        assert record["extra"] == "value"

    def test_log_ai_action_append_only(self, monkeypatch, tmp_path):
        """log_ai_action appends; does not overwrite."""
        audit_file = tmp_path / "ai_audit.jsonl"
        monkeypatch.setattr("audit_ai._AUDIT_DIR", tmp_path)
        monkeypatch.setattr("audit_ai.AUDIT_FILE", audit_file)
        from audit_ai import log_ai_action
        log_ai_action("first", "m", "a")
        log_ai_action("second", "m", "a")
        lines = audit_file.read_text().strip().split("\n")
        assert len(lines) == 2
        r1 = json.loads(lines[0])
        r2 = json.loads(lines[1])
        assert r1["prompt_hash"] != r2["prompt_hash"]


class TestToolRegistry:
    """Phase 4: Tool allowlist."""

    def test_is_tool_allowed_true(self):
        """is_tool_allowed returns True for allowed tools."""
        from tool_registry import is_tool_allowed
        assert is_tool_allowed("ai_summarizer.summarize_text") is True
        assert is_tool_allowed("entity_extractor.extract_entities_from_text") is True

    def test_is_tool_allowed_false(self):
        """is_tool_allowed returns False for disallowed tools."""
        from tool_registry import is_tool_allowed
        assert is_tool_allowed("evil_module.malicious_tool") is False
        assert is_tool_allowed("random.unknown") is False

    def test_ensure_tool_allowed_passes(self):
        """ensure_tool_allowed does not raise for allowed tools."""
        from tool_registry import ensure_tool_allowed
        ensure_tool_allowed("ai_summarizer.summarize_text")
        ensure_tool_allowed("entity_extractor.extract_entities_from_text")

    def test_ensure_tool_allowed_raises(self):
        """ensure_tool_allowed raises for disallowed tools."""
        from tool_registry import ensure_tool_allowed
        with pytest.raises(ValueError, match="not in registry"):
            ensure_tool_allowed("evil_module.malicious_tool")
