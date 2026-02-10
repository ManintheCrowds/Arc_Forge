# PURPOSE: pypdf-based text extractor.
# DEPENDENCIES: pypdf library.
# MODIFICATION NOTES: Phase 1 - Extracted from ingest_pdfs.py for modularity.

import logging
from pathlib import Path
from typing import Optional, Tuple

from extractors.base_extractor import TextExtractor

logger = logging.getLogger(__name__)


class PyPDFExtractor(TextExtractor):
    """Extractor using pypdf library."""
    
    def __init__(self):
        """Initialize pypdf extractor."""
        self._available = self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if pypdf is available."""
        try:
            import pypdf  # type: ignore
            return True
        except ImportError:
            return False
    
    def can_extract(self, pdf_path: Path) -> bool:
        """pypdf can extract from any PDF if available."""
        return self._available
    
    def extract(self, pdf_path: Path, **kwargs) -> Tuple[str, Optional[Path], dict]:
        """
        Extract text using pypdf.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Unused
            
        Returns:
            Tuple of (text, source_path, metadata)
        """
        if not self._available:
            return "", None, {"method": "pypdf", "error": "pypdf not available"}
        
        try:
            from pypdf import PdfReader  # type: ignore
            
            reader = PdfReader(str(pdf_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            
            metadata = {
                "method": "pypdf",
                "pages": len(reader.pages),
                "success": True
            }
            
            logger.info(f"Extracted text using pypdf for {pdf_path.name}")
            return text, None, metadata
            
        except ImportError:
            logger.debug("pypdf not available")
            return "", None, {"method": "pypdf", "error": "pypdf not installed"}
        except Exception as e:
            logger.warning(f"pypdf extraction failed for {pdf_path.name}: {e}")
            return "", None, {"method": "pypdf", "error": str(e)}
