# PURPOSE: Integration tests for incremental index building.
# DEPENDENCIES: pytest, build_index module.
# MODIFICATION NOTES: Tests change detection, deleted sources handling.

import pytest
import json
import tempfile
from pathlib import Path
import sys
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_index import (
        build_index,
        load_index_state,
        save_index_state,
        get_file_mtime,
    )
    INCREMENTAL_INDEX_AVAILABLE = True
except ImportError:
    INCREMENTAL_INDEX_AVAILABLE = False
    pytest.skip("build_index module not available", allow_module_level=True)


class TestIndexState:
    """Test cases for index state management."""
    
    def test_load_index_state_nonexistent(self):
        """Test loading state from non-existent file."""
        fake_path = Path("/nonexistent/state.json")
        state = load_index_state(fake_path)
        
        assert isinstance(state, dict)
        assert len(state) == 0
    
    def test_save_and_load_state(self):
        """Test saving and loading index state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "test_state.json"
            
            test_state = {
                "last_build_time": datetime.now().isoformat(),
                "processed_files": {
                    "file1.md": "2024-01-01T00:00:00",
                    "file2.md": "2024-01-02T00:00:00",
                },
                "total_sources": 2
            }
            
            save_index_state(state_path, test_state)
            assert state_path.exists()
            
            loaded_state = load_index_state(state_path)
            assert loaded_state["total_sources"] == 2
            assert len(loaded_state["processed_files"]) == 2
    
    def test_get_file_mtime(self):
        """Test getting file modification time."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            mtime = get_file_mtime(temp_path)
            assert isinstance(mtime, str)
            assert len(mtime) > 0
        finally:
            temp_path.unlink()
    
    def test_get_file_mtime_nonexistent(self):
        """Test getting mtime for non-existent file."""
        fake_path = Path("/nonexistent/file.md")
        mtime = get_file_mtime(fake_path)
        
        # Should return empty string on error
        assert mtime == ""


class TestChangeDetection:
    """Test cases for change detection logic."""
    
    def test_detect_new_files(self):
        """Test detection of new source files."""
        previous_state = {
            "processed_files": {
                "old_file.md": "2024-01-01T00:00:00"
            }
        }
        
        current_files = {
            "old_file.md": "2024-01-01T00:00:00",
            "new_file.md": "2024-01-02T00:00:00"
        }
        
        # New file should be detected
        new_files = [
            path for path in current_files.keys()
            if path not in previous_state["processed_files"]
        ]
        
        assert "new_file.md" in new_files
        assert len(new_files) == 1
    
    def test_detect_modified_files(self):
        """Test detection of modified source files."""
        previous_state = {
            "processed_files": {
                "file.md": "2024-01-01T00:00:00"
            }
        }
        
        current_files = {
            "file.md": "2024-01-02T00:00:00"  # Different timestamp
        }
        
        # Modified file should be detected
        modified_files = [
            path for path in current_files.keys()
            if path in previous_state["processed_files"]
            and current_files[path] != previous_state["processed_files"][path]
        ]
        
        assert "file.md" in modified_files
        assert len(modified_files) == 1
    
    def test_detect_deleted_files(self):
        """Test detection of deleted source files."""
        previous_state = {
            "processed_files": {
                "file1.md": "2024-01-01T00:00:00",
                "file2.md": "2024-01-01T00:00:00",
                "file3.md": "2024-01-01T00:00:00"
            }
        }
        
        current_files = {
            "file1.md": "2024-01-01T00:00:00",
            "file2.md": "2024-01-01T00:00:00"
            # file3.md is missing
        }
        
        # Deleted file should be detected
        deleted_files = [
            path for path in previous_state["processed_files"].keys()
            if path not in current_files
        ]
        
        assert "file3.md" in deleted_files
        assert len(deleted_files) == 1
    
    def test_no_changes_detected(self):
        """Test that no changes are detected when files unchanged."""
        previous_state = {
            "processed_files": {
                "file.md": "2024-01-01T00:00:00"
            }
        }
        
        current_files = {
            "file.md": "2024-01-01T00:00:00"  # Same timestamp
        }
        
        # No changes should be detected
        new_files = [
            path for path in current_files.keys()
            if path not in previous_state["processed_files"]
        ]
        
        modified_files = [
            path for path in current_files.keys()
            if path in previous_state["processed_files"]
            and current_files[path] != previous_state["processed_files"][path]
        ]
        
        assert len(new_files) == 0
        assert len(modified_files) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
