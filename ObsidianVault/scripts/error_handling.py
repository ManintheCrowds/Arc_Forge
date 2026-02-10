# PURPOSE: Enhanced error handling utilities with retry logic and graceful degradation.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Provides retry decorators and error reporting utilities.

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

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
