# PURPOSE: Unit tests for shared utility functions.
# DEPENDENCIES: pytest, utils module.
# MODIFICATION NOTES: Tests path validation, config loading, and utility functions.

import json
import tempfile
from pathlib import Path

import pytest

from utils import (
    get_config_path,
    load_config,
    sanitize_cache_dir,
    truncate_text,
    validate_file_size,
    validate_vault_path,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        config_file = tmp_path / "config.json"
        config_data = {"vault_root": str(tmp_path), "pdf_root": str(tmp_path / "pdfs")}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = load_config(config_file)
        assert config["vault_root"] == str(tmp_path)
        assert config["pdf_root"] == str(tmp_path / "pdfs")

    def test_load_missing_config(self, tmp_path):
        """Test loading a non-existent configuration file."""
        config_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_config(config_file)

    def test_load_invalid_json(self, tmp_path):
        """Test loading an invalid JSON file."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_config(config_file)

    def test_load_empty_config(self, tmp_path):
        """Test loading an empty configuration file."""
        config_file = tmp_path / "empty.json"
        config_file.write_text("", encoding="utf-8")

        with pytest.raises(ValueError):
            load_config(config_file)


class TestValidateVaultPath:
    """Tests for validate_vault_path function."""

    def test_valid_path_within_vault(self, tmp_path):
        """Test validating a path within vault root."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        test_path = vault_root / "subdir" / "file.txt"
        test_path.parent.mkdir(parents=True)

        validated = validate_vault_path(vault_root, test_path)
        assert validated == test_path.resolve()

    def test_path_traversal_attempt(self, tmp_path):
        """Test that path traversal attempts are rejected."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        malicious_path = vault_root / ".." / ".." / "etc" / "passwd"

        with pytest.raises(ValueError, match="outside vault root"):
            validate_vault_path(vault_root, malicious_path)

    def test_absolute_path_outside_vault(self, tmp_path):
        """Test that absolute paths outside vault are rejected."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        outside_path = tmp_path / "outside" / "file.txt"

        with pytest.raises(ValueError, match="outside vault root"):
            validate_vault_path(vault_root, outside_path)

    def test_relative_path_resolution(self, tmp_path):
        """Test that relative paths are resolved correctly."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        subdir = vault_root / "subdir"
        subdir.mkdir()
        
        # Change to subdir and use relative path
        relative_path = Path("file.txt")
        validated = validate_vault_path(vault_root, subdir / relative_path)
        assert validated.is_absolute()
        assert vault_root in validated.parents


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_get_simple_config_path(self, tmp_path):
        """Test getting a simple config path."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        config = {"source_notes_dir": "Sources"}
        (vault_root / "Sources").mkdir()

        path = get_config_path(vault_root, config, "source_notes_dir")
        assert path == (vault_root / "Sources").resolve()

    def test_get_nested_config_path(self, tmp_path):
        """Test getting a nested config path."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        config = {"templates": {"source_note": "Templates/source.md"}}
        (vault_root / "Templates").mkdir()

        path = get_config_path(vault_root, config, "templates.source_note")
        assert "Templates" in str(path)

    def test_missing_config_key(self, tmp_path):
        """Test error when config key is missing."""
        vault_root = tmp_path / "vault"
        config = {}

        with pytest.raises(KeyError):
            get_config_path(vault_root, config, "missing_key")

    def test_path_traversal_in_config(self, tmp_path):
        """Test that path traversal in config is rejected."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        config = {"malicious_path": "../../etc/passwd"}

        with pytest.raises(ValueError, match="outside vault root"):
            get_config_path(vault_root, config, "malicious_path")


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_long_text(self):
        """Test truncating text that exceeds limit."""
        text = "a" * 100
        result = truncate_text(text, 50)
        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")

    def test_truncate_short_text(self):
        """Test that short text is not truncated."""
        text = "short text"
        result = truncate_text(text, 100)
        assert result == text
        assert not result.endswith("...")

    def test_truncate_exact_length(self):
        """Test truncating text at exact length."""
        text = "a" * 50
        result = truncate_text(text, 50)
        assert result == text
        assert not result.endswith("...")


class TestValidateFileSize:
    """Tests for validate_file_size function."""

    def test_valid_file_size(self, tmp_path):
        """Test validating a file within size limit."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("small content")

        # Should not raise
        validate_file_size(test_file, max_size_mb=1)

    def test_file_exceeds_size_limit(self, tmp_path):
        """Test that files exceeding size limit raise error."""
        test_file = tmp_path / "large.txt"
        # Create a file larger than 1MB
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        test_file.write_text(large_content)

        with pytest.raises(ValueError, match="exceeds size limit"):
            validate_file_size(test_file, max_size_mb=1)

    def test_missing_file(self, tmp_path):
        """Test error when file doesn't exist."""
        missing_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            validate_file_size(missing_file)


class TestSanitizeCacheDir:
    """Tests for sanitize_cache_dir function."""

    def test_valid_cache_dir(self):
        """Test sanitizing a valid cache directory name."""
        result = sanitize_cache_dir(".obsidian/plugins/pdf-plus")
        assert result == ".obsidian/plugins/pdf-plus"

    def test_path_traversal_in_dir_name(self):
        """Test that path traversal in directory name is rejected."""
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_cache_dir("../../../etc")

    def test_absolute_path_rejected(self):
        """Test that absolute paths are rejected."""
        with pytest.raises(ValueError, match="must be relative"):
            sanitize_cache_dir("C:/Windows/System32")

    def test_strips_leading_slashes(self):
        """Test that leading slashes are stripped."""
        result = sanitize_cache_dir("/plugins/pdf-plus")
        assert not result.startswith("/")

    def test_strips_trailing_slashes(self):
        """Test that trailing slashes are stripped."""
        result = sanitize_cache_dir("plugins/pdf-plus/")
        assert not result.endswith("/")
