# PURPOSE: PDF++ cache text extractor.
# DEPENDENCIES: PDF++ plugin cache directories.
# MODIFICATION NOTES: Phase 1 - Extracted from ingest_pdfs.py for modularity.

import logging
from pathlib import Path
from typing import Iterable, Optional, Tuple

from extractors.base_extractor import TextExtractor
from utils import sanitize_cache_dir, validate_vault_path

logger = logging.getLogger(__name__)


class PDFPlusExtractor(TextExtractor):
    """Extractor that uses PDF++ plugin cache for text extraction."""
    
    def __init__(self, config: dict):
        """
        Initialize PDF++ extractor.
        
        Args:
            config: Configuration dictionary with pdf_text_cache_dirs and pdf_text_cache_extensions
        """
        self.cache_dirs = config.get("pdf_text_cache_dirs", [])
        self.extensions = config.get("pdf_text_cache_extensions", [".txt", ".md"])
    
    def can_extract(self, pdf_path: Path) -> bool:
        """PDF++ can extract if cache is available."""
        return True  # Always try PDF++ first if cache exists
    
    def extract(self, pdf_path: Path, **kwargs) -> Tuple[str, Optional[Path], dict]:
        """
        Extract text from PDF++ cache.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Must include vault_root
            
        Returns:
            Tuple of (text, source_path, metadata)
        """
        vault_root = kwargs.get("vault_root")
        if not vault_root:
            return "", None, {"method": "pdfplus", "error": "vault_root not provided"}
        
        vault_root = Path(vault_root)
        pdfplus_text = self._find_pdfplus_text(pdf_path, vault_root)
        
        if pdfplus_text and pdfplus_text.exists():
            try:
                text = pdfplus_text.read_text(encoding="utf-8", errors="replace")
                metadata = {
                    "method": "pdfplus",
                    "source": str(pdfplus_text),
                    "cache_hit": True
                }
                return text, pdfplus_text, metadata
            except Exception as e:
                logger.warning(f"Failed to read PDF++ cache for {pdf_path.name}: {e}")
                return "", None, {"method": "pdfplus", "error": str(e)}
        
        # No cache found
        return "", None, {"method": "pdfplus", "cache_hit": False}
    
    def _find_pdfplus_text(
        self,
        pdf_path: Path,
        vault_root: Path,
    ) -> Optional[Path]:
        """
        Find extracted text file for a PDF in PDF++ cache directories.
        
        Args:
            pdf_path: Path to the PDF file.
            vault_root: Root directory of the vault.
            
        Returns:
            Path to extracted text file if found, None otherwise.
        """
        stem = pdf_path.stem
        for rel_dir in self.cache_dirs:
            try:
                # Sanitize directory name to prevent path traversal
                sanitized_dir = sanitize_cache_dir(rel_dir)
                cache_root = vault_root / sanitized_dir
                cache_root = validate_vault_path(vault_root, cache_root.resolve())
                
                if not cache_root.exists():
                    continue
                
                for ext in self.extensions:
                    # Validate extension doesn't contain path separators
                    if "/" in ext or "\\" in ext:
                        logger.warning(f"Invalid extension contains path separator: {ext}")
                        continue
                    
                    candidates = list(cache_root.rglob(f"{stem}{ext}"))
                    if candidates:
                        # Validate the found file is within vault
                        found_path = validate_vault_path(vault_root, candidates[0])
                        return found_path
            except ValueError as e:
                logger.warning(f"Invalid cache directory '{rel_dir}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Error searching cache directory '{rel_dir}': {e}")
                continue
        return None
