# PURPOSE: Shared utility functions for PDF ingestion system.
# DEPENDENCIES: pathlib, json, typing.
# MODIFICATION NOTES: Centralized utilities to reduce code duplication.

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict
from urllib.parse import unquote


# PURPOSE: Reject strings containing null bytes (security vulnerability).
# DEPENDENCIES: None.
# MODIFICATION NOTES: Raises ValueError if null bytes found.
def _reject_null_bytes(path_str: str) -> None:
    """
    Reject strings containing null bytes.
    
    Null bytes can be used in path manipulation attacks and should be
    explicitly rejected in all path inputs.
    
    Args:
        path_str: String to check for null bytes.
        
    Raises:
        ValueError: If null bytes are found in the string.
    """
    if "\x00" in path_str:
        # Truncate for display if too long
        display_str = path_str[:50] + "..." if len(path_str) > 50 else path_str
        raise ValueError(
            f"Path contains null bytes, which is not allowed: {repr(display_str)}"
        )


# PURPOSE: Detect various path traversal patterns in a string.
# DEPENDENCIES: urllib.parse.unquote.
# MODIFICATION NOTES: Checks for URL-encoded and double-encoded patterns.
def _detect_path_traversal_patterns(path_str: str) -> bool:
    """
    Detect various path traversal patterns in a string.
    
    Checks for:
    - Direct ../ patterns
    - URL-encoded ../ patterns (%2E%2E%2F, %2e%2e%2f)
    - Double-encoded patterns (%252E%252E%252F)
    - Other encoding variants
    
    Args:
        path_str: String to check for path traversal patterns.
        
    Returns:
        True if any traversal pattern is detected, False otherwise.
    """
    # Check for direct path traversal
    if ".." in path_str:
        return True
    
    # Check for URL-encoded path traversal
    try:
        decoded = unquote(path_str)
        if ".." in decoded:
            return True
        
        # Check for double-encoded patterns
        if decoded != path_str:
            double_decoded = unquote(decoded)
            if ".." in double_decoded and double_decoded != decoded:
                return True
    except Exception:
        # If decoding fails, we can't check - but direct check already done
        pass
    
    # Check for hex-encoded patterns (e.g., \x2e\x2e\x2f)
    if "\\x2e\\x2e" in path_str or "\\x2E\\x2E" in path_str:
        return True
    
    return False
# DEPENDENCIES: ingest_config.json schema.
# MODIFICATION NOTES: Returns config dict. Raises on error.
def load_config(config_path: Path) -> Dict[str, object]:
    """
    Load and parse ingestion configuration from JSON file.
    
    Args:
        config_path: Path to the configuration JSON file.
        
    Returns:
        Dictionary containing configuration values.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If JSON is invalid.
        RuntimeError: If file read fails.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}") from e


# PURPOSE: Validate that a path is within the vault root (prevents path traversal).
# DEPENDENCIES: pathlib.Path.
# MODIFICATION NOTES: Raises ValueError if path escapes vault root.
def validate_vault_path(vault_root: Path, path: Path) -> Path:
    """
    Validate that a path is within the vault root directory.
    
    This prevents directory traversal attacks by ensuring all paths
    resolve to locations within the vault_root.
    
    Args:
        vault_root: The root directory of the vault.
        path: The path to validate (can be relative or absolute).
        
    Returns:
        Resolved Path object that is guaranteed to be within vault_root.
        
    Raises:
        ValueError: If path escapes vault_root or cannot be resolved.
    """
    # Check for null bytes in path string representation
    path_str = str(path)
    _reject_null_bytes(path_str)
    
    # Check for encoded path traversal patterns
    # For encoded patterns, catch early as they might resolve to valid paths
    # For direct patterns, let normal validation catch them for consistent error messages
    decoded_path_str = unquote(path_str) if "%" in path_str else path_str
    is_encoded = decoded_path_str != path_str
    has_traversal = ".." in decoded_path_str
    
    if has_traversal and is_encoded:
        # Encoded path traversal - catch early
        raise ValueError(
            f"Path contains encoded path traversal pattern: {repr(path_str[:50])}. "
            "This may indicate a path traversal attempt."
        )
    elif has_traversal and not is_encoded:
        # Direct path traversal - let normal validation catch it for consistent message
        pass
    
    vault_root = vault_root.resolve()
    
    # Resolve the path
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve path {path}: {e}") from e
    
    # Check if resolved path is within vault root
    try:
        # Use relative_to to check containment
        resolved_path.relative_to(vault_root)
    except ValueError:
        raise ValueError(
            f"Path {resolved_path} is outside vault root {vault_root}. "
            "This may indicate a path traversal attempt."
        )
    
    return resolved_path


# PURPOSE: Get a validated path from config relative to vault root.
# DEPENDENCIES: validate_vault_path.
# MODIFICATION NOTES: Convenience function for config path resolution.
def get_config_path(vault_root: Path, config: Dict[str, object], key: str) -> Path:
    """
    Get a validated path from config, ensuring it's within vault_root.
    
    Args:
        vault_root: Root directory of the vault.
        config: Configuration dictionary.
        key: Key to look up in config (supports nested keys with dots).
        
    Returns:
        Validated Path object within vault_root.
        
    Raises:
        KeyError: If key is missing from config.
        ValueError: If path escapes vault_root or contains security issues.
    """
    # Support nested keys like "templates.source_note"
    keys = key.split(".")
    value = config
    for k in keys:
        if not isinstance(value, dict) or k not in value:
            raise KeyError(f"Config key '{key}' not found")
        value = value[k]
    
    if not isinstance(value, str):
        raise ValueError(f"Config key '{key}' must be a string path")
    
    # Security checks: null bytes and path traversal patterns
    _reject_null_bytes(value)
    
    # Decode URL-encoded strings and check for path traversal
    # For encoded patterns, we need to catch them early as they might not be caught by normal validation
    # For direct patterns, let validate_vault_path catch them for consistent error messages
    decoded_value = unquote(value) if "%" in value else value
    is_encoded = decoded_value != value
    has_traversal = ".." in decoded_value
    
    if has_traversal and is_encoded:
        # Encoded path traversal - catch early with specific message
        raise ValueError(
            f"Config key '{key}' contains encoded path traversal pattern: {repr(value[:50])}"
        )
    elif has_traversal and not is_encoded:
        # Direct path traversal - let validate_vault_path catch it for consistent message
        pass
    
    path = Path(value)
    if not path.is_absolute():
        path = vault_root / path
    else:
        # Even absolute paths must be validated
        path = Path(value)
    
    return validate_vault_path(vault_root, path)


# PURPOSE: Truncate text to a maximum character length.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Adds ellipsis if truncated.
def truncate_text(text: str, max_chars: int) -> str:
    """
    Truncate text to maximum character length.
    
    Args:
        text: Text to truncate.
        max_chars: Maximum number of characters.
        
    Returns:
        Truncated text with "..." appended if truncated.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


# PURPOSE: Validate file size is within limits.
# DEPENDENCIES: pathlib.Path.
# MODIFICATION NOTES: Raises ValueError if file exceeds limit.
def validate_file_size(file_path: Path, max_size_mb: int = 100) -> None:
    """
    Validate that a file size is within acceptable limits.
    
    Args:
        file_path: Path to the file to check.
        max_size_mb: Maximum file size in megabytes (default: 100MB).
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file exceeds size limit.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = file_path.stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        raise ValueError(
            f"File {file_path.name} exceeds size limit: "
            f"{size_mb:.2f}MB > {max_size_mb}MB"
        )


# PURPOSE: Sanitize directory name from config to prevent path traversal.
# DEPENDENCIES: pathlib.Path.
# MODIFICATION NOTES: Removes dangerous path components.
def sanitize_cache_dir(rel_dir: str) -> str:
    """
    Sanitize a relative directory name from config.
    
    Removes path traversal sequences and normalizes the path.
    
    Args:
        rel_dir: Relative directory name from config.
        
    Returns:
        Sanitized directory name.
        
    Raises:
        ValueError: If directory name contains dangerous patterns.
    """
    # Security check: reject null bytes
    _reject_null_bytes(rel_dir)
    
    # Decode URL-encoded strings and check for path traversal patterns
    if _detect_path_traversal_patterns(rel_dir):
        raise ValueError(f"Directory name contains path traversal: {repr(rel_dir[:50])}")
    
    # Remove leading/trailing slashes
    rel_dir = rel_dir.strip("/\\")
    
    # Remove any absolute path indicators
    if Path(rel_dir).is_absolute():
        raise ValueError(f"Directory name must be relative: {rel_dir}")
    
    return rel_dir
