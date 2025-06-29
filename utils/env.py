"""Environment helper functions.

Provides typed access to environment variables loaded via python-dotenv (already called in various modules).
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get(key: str, default: Optional[str] = None, *, required: bool = False) -> Optional[str]:
    """Return env var or default.

    Args:
        key: Environment variable name.
        default: Fallback value.
        required: If True and var missing, raise RuntimeError.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise RuntimeError(f"Environment variable '{key}' is required but not set.")
    return value


def require(keys: list[str]):
    """Ensure a list of keys are present, raising if any missing."""
    for k in keys:
        get(k, required=True) 