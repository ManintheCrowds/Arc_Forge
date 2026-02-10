# PURPOSE: Cache index system for PDF++ text files to replace rglob() lookups.
# DEPENDENCIES: pathlib, json.
# MODIFICATION NOTES: Builds O(1) stem-to-path mapping stored in JSON.

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class CacheIndex:
    """Manages cache index for PDF++ extracted text files."""
    
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index: Dict[str, str] = {}  # stem -> path mapping
        self._loaded = False
    
    def load(self) -> None:
        """Load index from disk."""
        if self._loaded:
            return
        
        if self.index_path.exists():
            try:
                with self.index_path.open("r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception:
                self.index = {}
        else:
            self.index = {}
        
        self._loaded = True
    
    def save(self) -> None:
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)
    
    def build(self, cache_dirs: list[Path], extensions: list[str]) -> None:
        """Build index by scanning cache directories."""
        self.index = {}
        
        for cache_dir in cache_dirs:
            if not cache_dir.exists():
                continue
            
            for ext in extensions:
                # Search for files with matching extensions
                for cache_file in cache_dir.rglob(f"*{ext}"):
                    stem = cache_file.stem
                    # Store absolute path as string
                    if stem not in self.index:
                        self.index[stem] = str(cache_file.resolve())
    
    def find(self, stem: str) -> Optional[Path]:
        """Find cache file by stem (O(1) lookup)."""
        if not self._loaded:
            self.load()
        
        path_str = self.index.get(stem)
        if path_str:
            return Path(path_str)
        return None
    
    def update_incremental(self, cache_dirs: list[Path], extensions: list[str]) -> None:
        """Update index incrementally (only scan new/changed files)."""
        if not self._loaded:
            self.load()
        
        # For now, do full rebuild. In future, could track mtimes.
        self.build(cache_dirs, extensions)
