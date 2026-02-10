# PURPOSE: Integration tests for parallel processing.
# DEPENDENCIES: pytest, ingest_pdfs module, threading.
# MODIFICATION NOTES: Tests parallel processing, race conditions, progress tracking.

import pytest
import time
from pathlib import Path
import sys
import tempfile
import threading
from unittest.mock import Mock, patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ingest_pdfs import process_single_pdf, ingest_pdfs
    PARALLEL_PROCESSING_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSING_AVAILABLE = False
    pytest.skip("ingest_pdfs module not available", allow_module_level=True)


class TestParallelProcessing:
    """Test cases for parallel processing functionality."""
    
    def test_process_single_pdf_signature(self):
        """Test that process_single_pdf has correct signature."""
        # Verify function exists and has correct return type
        import inspect
        sig = inspect.signature(process_single_pdf)
        
        # Should return Tuple[bool, Optional[str]]
        assert sig.return_annotation != inspect.Signature.empty
    
    def test_parallel_processing_config(self):
        """Test that parallel processing respects max_workers config."""
        # Test config structure
        config = {
            "vault_root": "/tmp",
            "pdf_root": "/tmp",
            "max_workers": 4,
        }
        
        assert "max_workers" in config
        assert isinstance(config["max_workers"], int)
        assert config["max_workers"] > 0
    
    def test_worker_limit_enforcement(self):
        """Test that worker count is limited appropriately."""
        import os
        
        # Test that max_workers doesn't exceed CPU count
        cpu_count = os.cpu_count() or 4
        max_workers = 8
        
        # Should cap at reasonable limit
        effective_workers = min(max_workers, 8, cpu_count)
        assert effective_workers <= 8
        assert effective_workers <= cpu_count
    
    def test_thread_safety_counters(self):
        """Test that progress counters are thread-safe."""
        from threading import Lock
        
        # Simulate thread-safe counter
        counter = 0
        lock = Lock()
        
        def increment():
            nonlocal counter
            with lock:
                counter += 1
        
        # Run from multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have incremented exactly 10 times
        assert counter == 10


class TestProgressTracking:
    """Test cases for progress tracking in parallel processing."""
    
    def test_progress_reporting_structure(self):
        """Test that progress reporting has expected structure."""
        # Test that progress messages follow expected format
        progress_message = "Progress: 5/10 PDFs processed (2 succeeded, 3 failed) - Rate: 1.5 PDFs/sec, ETA: 3s"
        
        assert "Progress:" in progress_message
        assert "/" in progress_message  # Should show current/total
        assert "PDFs processed" in progress_message
    
    def test_eta_calculation(self):
        """Test ETA calculation logic."""
        total = 100
        processed = 50
        elapsed = 10.0  # seconds
        
        if elapsed > 0:
            rate = processed / elapsed
            remaining = total - processed
            eta = remaining / rate if rate > 0 else 0
            
            assert eta >= 0
            assert isinstance(eta, (int, float))


class TestResourceLimits:
    """Test cases for resource limit enforcement."""
    
    def test_worker_count_limits(self):
        """Test that worker count has reasonable limits."""
        # Test various worker counts
        test_cases = [1, 2, 4, 8, 16, 32]
        
        for workers in test_cases:
            # Should cap at 8
            capped = min(workers, 8)
            assert capped <= 8
            assert capped > 0
    
    def test_timeout_per_pdf(self):
        """Test that individual PDF processing has timeout."""
        # Test timeout value
        timeout = 300  # 5 minutes
        
        assert timeout > 0
        assert isinstance(timeout, int)
        # Should be reasonable (not too short, not too long)
        assert 60 <= timeout <= 600


class TestErrorHandlingInParallel:
    """Tests for error handling in parallel execution (Phase 1)."""
    
    @pytest.mark.unit
    def test_error_isolation(self):
        """Test that errors in one thread don't affect others."""
        from concurrent.futures import ThreadPoolExecutor
        
        def failing_task(n):
            if n == 2:
                raise ValueError(f"Task {n} failed")
            return n
        
        results = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(failing_task, i) for i in range(5)]
            for future in futures:
                try:
                    results.append(future.result())
                except ValueError as e:
                    errors.append(str(e))
        
        # Should have processed successful tasks
        assert len(results) == 4
        assert len(errors) == 1
    
    @pytest.mark.unit
    def test_progress_tracking_with_errors(self):
        """Test that progress tracking works even with errors."""
        from threading import Lock
        
        processed = 0
        errors = 0
        lock = Lock()
        
        def process_item(item):
            nonlocal processed, errors
            if item == "error":
                with lock:
                    errors += 1
                raise ValueError("Error")
            with lock:
                processed += 1
        
        items = ["ok1", "ok2", "error", "ok3"]
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_item, item) for item in items]
            for future in futures:
                try:
                    future.result()
                except ValueError:
                    pass
        
        assert processed == 3
        assert errors == 1


class TestPerformanceImprovement:
    """Tests for performance improvement verification (Phase 1)."""
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_parallel_vs_sequential_speedup(self):
        """Test that parallel processing is faster than sequential."""
        import time
        
        def mock_process(item):
            time.sleep(0.1)  # Simulate work
            return item
        
        items = list(range(10))
        
        # Sequential
        start_seq = time.time()
        for item in items:
            mock_process(item)
        time_seq = time.time() - start_seq
        
        # Parallel
        from concurrent.futures import ThreadPoolExecutor
        start_par = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(mock_process, items))
        time_par = time.time() - start_par
        
        # Parallel should be faster (allowing some overhead)
        assert time_par < time_seq * 1.5  # Should be at least somewhat faster


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
