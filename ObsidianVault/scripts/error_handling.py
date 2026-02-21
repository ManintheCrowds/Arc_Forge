# PURPOSE: Enhanced error handling utilities with retry logic and graceful degradation.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Provides retry decorators, error reporting, and structured error logging.

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

# Default path for structured error log (relative to cwd when not absolute)
DEFAULT_ERROR_LOG_PATH = "Campaigns/_rag_cache/errors.log"


def _severity_for_error_type(error_type: str) -> str:
    """Map exception type to severity. Returns 'critical', 'error', or 'warning'."""
    critical = {"OSError", "ConnectionError", "TimeoutError", "MemoryError"}
    warning = {"UserWarning", "DeprecationWarning"}
    if error_type in critical:
        return "critical"
    if error_type in warning:
        return "warning"
    return "error"  # KeyError, ValueError, TypeError, etc.


def _post_error_to_watchtower(
    project: str,
    error_type: str,
    message: str,
    traceback_str: str,
    context: Optional[Dict[str, Any]] = None,
    error_id: Optional[str] = None,
    severity: Optional[str] = None,
) -> bool:
    """POST error to WatchTower /api/errors. Returns True if successful."""
    url = (
        os.environ.get("WATCHTOWER_ERRORS_URL", "").strip()
        or os.environ.get("WATCHTOWER_METRICS_URL", "").strip()
    ).rstrip("/")
    if not url:
        return False
    try:
        import urllib.request
        endpoint = f"{url}/api/errors"
        payload = {
            "project": project,
            "error_type": error_type,
            "message": message,
            "traceback": traceback_str,
            "context": context or {},
        }
        if error_id is not None:
            payload["error_id"] = error_id
        if severity is not None:
            payload["severity"] = severity
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status in (200, 204)
    except Exception as exc:
        logger.debug(f"WatchTower POST failed: {exc}")
        return False


def log_structured_error(
    error_type: str,
    message: str,
    traceback_str: str,
    context: Optional[Dict[str, Any]] = None,
    log_path: Optional[Union[str, Path]] = None,
    project: Optional[str] = None,
) -> None:
    """
    Write structured error JSON to file for centralized exception capture.
    If WATCHTOWER_METRICS_URL or WATCHTOWER_ERRORS_URL is set, also POST to /api/errors.

    Args:
        error_type: Exception type name (e.g. KeyError, ValueError).
        message: Exception message.
        traceback_str: Full traceback string.
        context: Optional dict with entry point, query, etc.
        log_path: Path to errors log file. Defaults to RAG_ERROR_LOG_PATH env or
            Campaigns/_rag_cache/errors.log relative to cwd.
        project: Project label for WatchTower (default from context or "unknown").

    Env vars: RAG_ERROR_LOG_PATH (client log path), WATCHTOWER_ERRORS_URL or
    WATCHTOWER_METRICS_URL (WatchTower base URL). See ERROR_MONITORING_AND_KNOWN_ISSUES.md.
    """
    ctx = context or {}
    proj = project or ctx.get("project", "unknown")
    error_id = str(uuid.uuid4())
    severity = _severity_for_error_type(error_type)
    log_file = Path(log_path) if log_path else Path(os.environ.get("RAG_ERROR_LOG_PATH", DEFAULT_ERROR_LOG_PATH))
    if not log_file.is_absolute():
        log_file = Path.cwd() / log_file
    log_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "error_id": error_id,
        "error_type": error_type,
        "message": message,
        "traceback": traceback_str,
        "severity": severity,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "context": ctx,
    }
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning(f"Failed to write structured error log: {exc}")
    _post_error_to_watchtower(proj, error_type, message, traceback_str, ctx, error_id=error_id, severity=severity)

T = TypeVar("T")


# PURPOSE: Retry a function with exponential backoff.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Retries transient failures with configurable attempts and delays.
def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3).
        initial_delay: Initial delay in seconds (default: 1.0).
        max_delay: Maximum delay in seconds (default: 60.0).
        backoff_factor: Multiplier for delay on each retry (default: 2.0).
        exceptions: Tuple of exception types to catch and retry (default: all exceptions).
        on_retry: Optional callback function called on each retry (exception, attempt_number).
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(e, attempt)
                        else:
                            logger.warning(
                                f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                        
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            # All attempts failed, raise last exception
            raise last_exception
        
        return wrapper
    return decorator


# PURPOSE: Handle errors gracefully with fallback value.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Returns fallback value on exception instead of raising.
def with_fallback(
    fallback: T,
    exceptions: tuple = (Exception,),
    log_error: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to return fallback value on exception.
    
    Args:
        fallback: Value to return on exception.
        exceptions: Tuple of exception types to catch (default: all exceptions).
        log_error: Whether to log errors (default: True).
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    logger.warning(f"{func.__name__} failed, using fallback: {e}")
                return fallback
        
        return wrapper
    return decorator


# PURPOSE: Collect and report error summary.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Tracks errors during processing and generates summary.
class ErrorCollector:
    def __init__(self):
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
    
    def add_error(self, operation: str, error: Exception, context: Optional[dict] = None):
        """Add an error to the collection."""
        error_info = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }
        self.errors.append(error_info)
        logger.error(f"{operation} failed: {error}", exc_info=True)
    
    def add_warning(self, operation: str, message: str, context: Optional[dict] = None):
        """Add a warning to the collection."""
        warning_info = {
            "operation": operation,
            "message": message,
            "context": context or {},
        }
        self.warnings.append(warning_info)
        logger.warning(f"{operation}: {message}")
    
    def get_summary(self) -> dict[str, Any]:
        """Get error summary report."""
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }
    
    def print_summary(self):
        """Print error summary to logger and stdout."""
        import sys
        summary = self.get_summary()
        
        if summary["total_errors"] > 0:
            msg = f"Processing completed with {summary['total_errors']} error(s):"
            logger.error(msg)
            print(msg, file=sys.stdout)
            for error in summary["errors"]:
                error_msg = f"  - {error['operation']}: {error['error_type']} - {error['error_message']}"
                logger.error(error_msg)
                print(error_msg, file=sys.stdout)
        
        if summary["total_warnings"] > 0:
            msg = f"Processing completed with {summary['total_warnings']} warning(s):"
            logger.warning(msg)
            print(msg, file=sys.stdout)
            for warning in summary["warnings"]:
                warning_msg = f"  - {warning['operation']}: {warning['message']}"
                logger.warning(warning_msg)
                print(warning_msg, file=sys.stdout)
        
        if summary["total_errors"] == 0 and summary["total_warnings"] == 0:
            msg = "Processing completed successfully with no errors or warnings."
            logger.info(msg)
            print(msg, file=sys.stdout)
    
    def clear(self):
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
