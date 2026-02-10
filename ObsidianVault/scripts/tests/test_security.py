# PURPOSE: Security tests for PDF ingestion system.
# DEPENDENCIES: pytest, utils module.
# MODIFICATION NOTES: Tests path traversal, malicious config, and security vulnerabilities.

import json
import tempfile
from pathlib import Path

import pytest

from utils import get_config_path, sanitize_cache_dir, validate_vault_path


class TestPathTraversalProtection:
    """Tests for path traversal attack prevention."""

    def test_path_traversal_in_pdf_root(self, tmp_path):
        """Test that path traversal in pdf_root config is rejected."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        config = {"pdf_root": "../../../etc"}

        with pytest.raises(ValueError, match="outside vault root"):
            get_config_path(vault_root, config, "pdf_root")

    def test_path_traversal_in_cache_dir(self):
        """Test that path traversal in cache directory name is rejected."""
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_cache_dir("../../../etc/passwd")

    def test_multiple_path_traversals(self, tmp_path):
        """Test that multiple ../ sequences are caught."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        malicious_path = vault_root / ".." / ".." / ".." / ".." / "etc" / "passwd"

        with pytest.raises(ValueError):
            validate_vault_path(vault_root, malicious_path)

    def test_encoded_path_traversal(self, tmp_path):
        """Test that encoded path traversal attempts are caught."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        # URL-encoded ../
        config = {"malicious": "%2E%2E%2F%2E%2E%2Fetc"}

        # Should still be caught when resolved
        path = Path(config["malicious"])
        with pytest.raises(ValueError):
            validate_vault_path(vault_root, vault_root / path)


class TestMaliciousConfig:
    """Tests for handling malicious configuration files."""

    def test_config_with_absolute_path_outside_vault(self, tmp_path):
        """Test config with absolute path outside vault."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        
        config = {"source_notes_dir": str(outside_dir)}

        with pytest.raises(ValueError, match="outside vault root"):
            get_config_path(vault_root, config, "source_notes_dir")

    def test_config_with_symlink_attempt(self, tmp_path):
        """Test that symlink attempts are handled (if symlinks exist)."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        target = tmp_path / "target"
        target.mkdir()
        
        # Create symlink (if supported)
        try:
            symlink = vault_root / "symlink"
            symlink.symlink_to(target)
            
            # Should validate the resolved path, not the symlink
            validated = validate_vault_path(vault_root, symlink)
            # The resolved path should still be validated
            assert validated.exists()
        except (OSError, NotImplementedError):
            # Symlinks not supported on this platform
            pytest.skip("Symlinks not supported on this platform")

    def test_config_with_null_bytes(self, tmp_path):
        """Test that null bytes in config paths are handled."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        config = {"malicious": "path\x00with\x00nulls"}

        # Path should be sanitized or rejected
        path_str = config["malicious"]
        # Null bytes should cause issues
        with pytest.raises((ValueError, OSError)):
            get_config_path(vault_root, config, "malicious")


class TestLargeFileHandling:
    """Tests for handling large files."""

    def test_very_large_pdf_rejected(self, tmp_path):
        """Test that very large PDFs are rejected."""
        from utils import validate_file_size

        # Create a file that's too large (simulated)
        large_file = tmp_path / "large.pdf"
        # Write 150MB of data
        with large_file.open("wb") as f:
            f.write(b"x" * (150 * 1024 * 1024))

        with pytest.raises(ValueError, match="exceeds size limit"):
            validate_file_size(large_file, max_size_mb=100)

    def test_extremely_large_file_handling(self, tmp_path):
        """Test handling of extremely large files (DoS prevention)."""
        from utils import validate_file_size

        # Test with very small limit to catch large files quickly
        test_file = tmp_path / "test.pdf"
        with test_file.open("wb") as f:
            f.write(b"x" * (10 * 1024 * 1024))  # 10MB

        # Should be rejected with 5MB limit
        with pytest.raises(ValueError):
            validate_file_size(test_file, max_size_mb=5)


class TestSymlinkHandling:
    """Tests for symlink handling."""

    def test_symlink_within_vault_allowed(self, tmp_path):
        """Test that symlinks within vault are allowed."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        target = vault_root / "target"
        target.mkdir()
        
        try:
            symlink = vault_root / "link"
            symlink.symlink_to(target)
            
            # Should validate successfully
            validated = validate_vault_path(vault_root, symlink)
            assert validated.exists()
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported")

    def test_symlink_outside_vault_rejected(self, tmp_path):
        """Test that symlinks pointing outside vault are rejected."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        outside_target = tmp_path / "outside"
        outside_target.mkdir()
        
        try:
            symlink = vault_root / "link"
            symlink.symlink_to(outside_target)
            
            # Should be rejected
            with pytest.raises(ValueError, match="outside vault root"):
                validate_vault_path(vault_root, symlink)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported")


class TestInputSanitization:
    """Tests for input sanitization."""

    def test_cache_dir_with_special_chars(self):
        """Test cache directory names with special characters."""
        # Should handle or reject special characters appropriately
        result = sanitize_cache_dir(".obsidian/plugins/my-plugin")
        assert ".." not in result

    def test_cache_dir_with_unicode(self):
        """Test cache directory names with Unicode characters."""
        # Unicode should be preserved but validated
        result = sanitize_cache_dir("plugins/测试")
        assert result == "plugins/测试"

    def test_empty_cache_dir_name(self):
        """Test that empty cache directory names are handled."""
        result = sanitize_cache_dir("")
        assert result == ""
