# PURPOSE: Performance profiling utilities for PDF ingestion system.
# DEPENDENCIES: time, contextlib, tracemalloc, psutil (optional), json, csv.
# MODIFICATION NOTES: Provides timing, memory tracking, and I/O counting for performance analysis.

from __future__ import annotations

import contextlib
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, TextIO

try:
    import tracemalloc
    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceProfiler:
    """Context manager for tracking performance metrics."""
    
    def __init__(self, name: str, enable_memory: bool = True):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.enable_memory = enable_memory
        self.memory_start: Optional[float] = None
        self.memory_end: Optional[float] = None
        self.memory_peak: Optional[float] = None
        self.tracemalloc_snapshot_start = None
        self.tracemalloc_snapshot_end = None
        
    def __enter__(self) -> PerformanceProfiler:
        self.start_time = time.perf_counter()
        
        if self.enable_memory:
            if TRACEMALLOC_AVAILABLE:
                if not tracemalloc.is_tracing():
                    tracemalloc.start()
                self.tracemalloc_snapshot_start = tracemalloc.take_snapshot()
            
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                self.memory_start = process.memory_info().rss / 1024 / 1024  # MB
        
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        if self.enable_memory:
            if TRACEMALLOC_AVAILABLE:
                self.tracemalloc_snapshot_end = tracemalloc.take_snapshot()
                if self.tracemalloc_snapshot_start:
                    top_stats = self.tracemalloc_snapshot_end.compare_to(
                        self.tracemalloc_snapshot_start, 'lineno'
                    )
                    # Get peak memory from tracemalloc
                    current, peak = tracemalloc.get_traced_memory()
                    self.memory_peak = peak / 1024 / 1024  # MB
            
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                self.memory_end = process.memory_info().rss / 1024 / 1024  # MB
                if self.memory_start:
                    self.memory_peak = self.memory_end - self.memory_start
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profiler data to dictionary."""
        result = {
            "name": self.name,
            "duration_seconds": self.duration,
        }
        
        if self.memory_peak is not None:
            result["memory_peak_mb"] = self.memory_peak
        
        if self.memory_start is not None:
            result["memory_start_mb"] = self.memory_start
        
        if self.memory_end is not None:
            result["memory_end_mb"] = self.memory_end
        
        return result


class IOProfiler:
    """Track I/O operations."""
    
    def __init__(self):
        self.read_count = 0
        self.write_count = 0
        self.read_bytes = 0
        self.write_bytes = 0
        self.operations: list[Dict[str, Any]] = []
    
    def record_read(self, path: str, bytes_read: int) -> None:
        """Record a read operation."""
        self.read_count += 1
        self.read_bytes += bytes_read
        self.operations.append({
            "type": "read",
            "path": str(path),
            "bytes": bytes_read,
            "timestamp": time.perf_counter(),
        })
    
    def record_write(self, path: str, bytes_written: int) -> None:
        """Record a write operation."""
        self.write_count += 1
        self.write_bytes += bytes_written
        self.operations.append({
            "type": "write",
            "path": str(path),
            "bytes": bytes_written,
            "timestamp": time.perf_counter(),
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert I/O stats to dictionary."""
        return {
            "read_count": self.read_count,
            "write_count": self.write_count,
            "read_bytes": self.read_bytes,
            "write_bytes": self.write_bytes,
            "total_operations": len(self.operations),
        }
    
    def reset(self) -> None:
        """Reset all counters."""
        self.read_count = 0
        self.write_count = 0
        self.read_bytes = 0
        self.write_bytes = 0
        self.operations.clear()


class PerformanceCollector:
    """Collect performance metrics from multiple profilers."""
    
    def __init__(self):
        self.profilers: list[PerformanceProfiler] = []
        self.io_profiler = IOProfiler()
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
    
    def add_profiler(self, profiler: PerformanceProfiler) -> None:
        """Add a profiler to the collection."""
        self.profilers.append(profiler)
    
    def finish(self) -> None:
        """Mark collection as finished."""
        self.end_time = time.perf_counter()
    
    def get_total_duration(self) -> float:
        """Get total duration of all profiling."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all metrics to dictionary."""
        return {
            "total_duration_seconds": self.get_total_duration(),
            "operations": [p.to_dict() for p in self.profilers],
            "io_stats": self.io_profiler.to_dict(),
            "operation_count": len(self.profilers),
        }
    
    def export_json(self, path: Path) -> None:
        """Export metrics to JSON file."""
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def export_csv(self, path: Path) -> None:
        """Export operation metrics to CSV file."""
        with path.open("w", newline="", encoding="utf-8") as f:
            if not self.profilers:
                return
            
            writer = csv.DictWriter(f, fieldnames=["name", "duration_seconds", "memory_peak_mb"])
            writer.writeheader()
            
            for profiler in self.profilers:
                data = profiler.to_dict()
                writer.writerow({
                    "name": data["name"],
                    "duration_seconds": data.get("duration_seconds", ""),
                    "memory_peak_mb": data.get("memory_peak_mb", ""),
                })


# Global collector instance
_collector: Optional[PerformanceCollector] = None


def get_collector() -> PerformanceCollector:
    """Get or create global performance collector."""
    global _collector
    if _collector is None:
        _collector = PerformanceCollector()
    return _collector


def reset_collector() -> None:
    """Reset global performance collector."""
    global _collector
    _collector = PerformanceCollector()


@contextlib.contextmanager
def profile_operation(name: str, enable_memory: bool = True) -> Iterator[PerformanceProfiler]:
    """Context manager for profiling an operation."""
    profiler = PerformanceProfiler(name, enable_memory=enable_memory)
    collector = get_collector()
    
    with profiler:
        collector.add_profiler(profiler)
        yield profiler


def record_io_read(path: str, bytes_read: int) -> None:
    """Record an I/O read operation."""
    collector = get_collector()
    collector.io_profiler.record_read(path, bytes_read)


def record_io_write(path: str, bytes_written: int) -> None:
    """Record an I/O write operation."""
    collector = get_collector()
    collector.io_profiler.record_write(path, bytes_written)


def export_results(json_path: Optional[Path] = None, csv_path: Optional[Path] = None) -> None:
    """Export performance results to files."""
    collector = get_collector()
    collector.finish()
    
    if json_path:
        collector.export_json(json_path)
    
    if csv_path:
        collector.export_csv(csv_path)


def print_summary() -> None:
    """Print performance summary to stdout."""
    collector = get_collector()
    collector.finish()
    
    data = collector.to_dict()
    
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total Duration: {data['total_duration_seconds']:.2f} seconds")
    print(f"Operations Profiled: {data['operation_count']}")
    print()
    
    io_stats = data['io_stats']
    print("I/O Statistics:")
    print(f"  Reads: {io_stats['read_count']} ({io_stats['read_bytes'] / 1024 / 1024:.2f} MB)")
    print(f"  Writes: {io_stats['write_count']} ({io_stats['write_bytes'] / 1024 / 1024:.2f} MB)")
    print()
    
    if data['operations']:
        print("Top Operations by Duration:")
        sorted_ops = sorted(data['operations'], key=lambda x: x.get('duration_seconds', 0), reverse=True)
        for op in sorted_ops[:10]:
            duration = op.get('duration_seconds', 0)
            name = op.get('name', 'unknown')
            memory = op.get('memory_peak_mb')
            if memory:
                print(f"  {name}: {duration:.3f}s (peak: {memory:.2f} MB)")
            else:
                print(f"  {name}: {duration:.3f}s")
    
    print("=" * 60)
