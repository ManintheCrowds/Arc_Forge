# PURPOSE: Unit tests for error handling utilities.
# DEPENDENCIES: pytest, error_handling module.
# MODIFICATION NOTES: Tests retry logic, error collection, and fallback decorators.

import json
import sys
import time
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from error_handling import (
        retry_with_backoff,
        with_fallback,
        ErrorCollector,
        log_structured_error,
    )
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False
    pytest.skip("error_handling module not available", allow_module_level=True)


class TestRetryWithBackoff:
    """Test cases for retry_with_backoff decorator."""
    
    def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        call_count = [0]
        
        @retry_with_backoff(max_attempts=3)
        def successful_func():
            call_count[0] += 1
            return "success"
        
        result = successful_func()
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_on_failure(self):
        """Test that function retries on failure."""
        call_count = [0]
        
        @retry_with_backoff(max_attempts=3, initial_delay=0.1)
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = failing_func()
        assert result == "success"
        assert call_count[0] == 3
    
    def test_max_attempts_exceeded(self):
        """Test that exception is raised after max attempts."""
        call_count = [0]
        
        @retry_with_backoff(max_attempts=2, initial_delay=0.1)
        def always_failing_func():
            call_count[0] += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_failing_func()
        
        assert call_count[0] == 2
    
    def test_backoff_delay(self):
        """Test that delay increases with backoff."""
        delays = []
        start_time = time.time()
        
        @retry_with_backoff(
            max_attempts=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            on_retry=lambda e, attempt: delays.append(time.time() - start_time)
        )
        def failing_func():
            if len(delays) < 2:
                raise ValueError("Fail")
            return "success"
        
        failing_func()
        
        # Should have 2 retries with increasing delays
        assert len(delays) == 2
        # Second delay should be longer than first
        assert delays[1] > delays[0]
    
    def test_specific_exception_types(self):
        """Test that only specified exceptions trigger retry."""
        call_count = [0]
        
        @retry_with_backoff(max_attempts=2, exceptions=(ValueError,))
        def raising_func():
            call_count[0] += 1
            raise KeyError("Wrong exception type")
        
        with pytest.raises(KeyError):
            raising_func()
        
        # Should not retry for KeyError
        assert call_count[0] == 1


class TestWithFallback:
    """Test cases for with_fallback decorator."""
    
    def test_successful_call_no_fallback(self):
        """Test that successful calls don't use fallback."""
        @with_fallback("fallback_value")
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_fallback_on_exception(self):
        """Test that fallback value is returned on exception."""
        @with_fallback("fallback_value")
        def failing_func():
            raise ValueError("Error")
        
        result = failing_func()
        assert result == "fallback_value"
    
    def test_fallback_none(self):
        """Test that None can be used as fallback."""
        @with_fallback(None)
        def failing_func():
            raise ValueError("Error")
        
        result = failing_func()
        assert result is None
    
    def test_specific_exception_types(self):
        """Test that only specified exceptions trigger fallback."""
        @with_fallback("fallback", exceptions=(ValueError,))
        def raising_func():
            raise KeyError("Wrong exception")
        
        with pytest.raises(KeyError):
            raising_func()


class TestErrorCollector:
    """Test cases for ErrorCollector class."""
    
    def test_initialization(self):
        """Test ErrorCollector initialization."""
        collector = ErrorCollector()
        assert collector.errors == []
        assert collector.warnings == []
    
    def test_add_error(self):
        """Test adding errors to collector."""
        collector = ErrorCollector()
        error = ValueError("Test error")
        
        collector.add_error("test_operation", error, {"context": "test"})
        
        assert len(collector.errors) == 1
        assert collector.errors[0]["operation"] == "test_operation"
        assert collector.errors[0]["error_type"] == "ValueError"
        assert collector.errors[0]["error_message"] == "Test error"
        assert collector.errors[0]["context"] == {"context": "test"}
    
    def test_add_warning(self):
        """Test adding warnings to collector."""
        collector = ErrorCollector()
        
        collector.add_warning("test_operation", "Test warning", {"context": "test"})
        
        assert len(collector.warnings) == 1
        assert collector.warnings[0]["operation"] == "test_operation"
        assert collector.warnings[0]["message"] == "Test warning"
        assert collector.warnings[0]["context"] == {"context": "test"}
    
    def test_get_summary(self):
        """Test getting error summary."""
        collector = ErrorCollector()
        collector.add_error("op1", ValueError("Error 1"))
        collector.add_warning("op2", "Warning 1")
        collector.add_error("op3", KeyError("Error 2"))
        
        summary = collector.get_summary()
        
        assert summary["total_errors"] == 2
        assert summary["total_warnings"] == 1
        assert len(summary["errors"]) == 2
        assert len(summary["warnings"]) == 1
    
    def test_clear(self):
        """Test clearing collected errors and warnings."""
        collector = ErrorCollector()
        collector.add_error("op1", ValueError("Error"))
        collector.add_warning("op2", "Warning")
        
        collector.clear()
        
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
    
    def test_print_summary_no_errors(self, capsys):
        """Test printing summary with no errors."""
        collector = ErrorCollector()
        collector.print_summary()
        
        captured = capsys.readouterr()
        assert "successfully" in captured.out.lower() or "no errors" in captured.out.lower()


class TestLogStructuredError:
    """T5.4 – test log_structured_error writes JSON with expected keys."""

    def test_log_structured_error_writes_file(self, tmp_path):
        """log_structured_error must write JSON line with error_type, message, traceback, timestamp, context, error_id, severity."""
        log_file = tmp_path / "errors.log"
        log_structured_error(
            "KeyError",
            "'source'",
            "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\nKeyError: 'source'",
            context={"entry": "run_pipeline"},
            log_path=str(log_file),
        )
        assert log_file.exists()
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["error_type"] == "KeyError"
        assert data["message"] == "'source'"
        assert "Traceback" in data["traceback"]
        assert "timestamp" in data
        assert data["context"] == {"entry": "run_pipeline"}
        assert "error_id" in data
        assert "severity" in data
        assert data["severity"] == "error"

    def test_log_structured_error_appends(self, tmp_path):
        """log_structured_error must append to existing file."""
        log_file = tmp_path / "errors.log"
        log_structured_error("E1", "m1", "tb1", log_path=str(log_file))
        log_structured_error("E2", "m2", "tb2", log_path=str(log_file))
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["error_type"] == "E1"
        assert json.loads(lines[1])["error_type"] == "E2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
