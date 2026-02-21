# PURPOSE: Credential vault for AI API keys; keyring with .env fallback.
# DEPENDENCIES: keyring (optional)
# MODIFICATION NOTES: AI security P0; no keys in code; keychain for prod, .env for dev.

"""
Credential vault: prefer OS keychain (keyring), fallback to environment.
Never hardcode API keys in code. Use .env for development; keychain for production.
"""

import os
from typing import Optional

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

SERVICE_NAME = "arc_forge"


def get_secret(key_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get API key from keyring (if available) or environment.
    Order: keyring -> os.environ -> default.
    """
    if KEYRING_AVAILABLE:
        try:
            val = keyring.get_password(SERVICE_NAME, key_name)
            if val:
                return val
        except Exception:
            pass
    return os.environ.get(key_name) or default


def set_secret(key_name: str, value: str) -> None:
    """Store API key in keyring (for setup). Does not write to .env."""
    if KEYRING_AVAILABLE:
        try:
            keyring.set_password(SERVICE_NAME, key_name, value)
        except Exception:
            raise RuntimeError(
                f"keyring unavailable; use .env: {key_name}=your-key"
            ) from None
    else:
        raise RuntimeError(
            "Install keyring: pip install keyring. Or set in .env for dev."
        )
