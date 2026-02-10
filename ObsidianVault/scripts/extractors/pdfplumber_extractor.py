# PURPOSE: pdfplumber-based text extractor.
# DEPENDENCIES: pdfplumber library.
# MODIFICATION NOTES: Phase 1 - Extracted from ingest_pdfs.py for modularity.

import logging
from pathlib import Path
from typing import Optional, Tuple

from extractors.base_extractor import TextExtractor

logger = logging.getLogger(__name__)


class PDFPlumberExtractor(TextExtractor):
    """Extractor using pdfplumber library."""
    
    def __init__(self):
        """Initialize pdfplumber extractor."""
        self._available = self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if pdfplumber is available."""
        try:
            import pdfplumber  # type: ignore
            return True
        except ImportError:
            return False
    
    def can_extract(self, pdf_path: Path) -> bool:
        """pdfplumber can extract from any PDF if available."""
        return self._available
    
    def extract(self, pdf_path: Path, **kwargs) -> Tuple[str, Optional[Path], dict]:
        """
        Extract text using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Unused
            
        Returns:
            Tuple of (text, source_path, metadata)
        """
        if not self._available:
            return "", None, {"method": "pdfplumber", "error": "pdfplumber not available"}
        
        try:
            import pdfplumber  # type: ignore
            
            with pdfplumber.open(str(pdf_path)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            
            metadata = {
                "method": "pdfplumber",
                "pages": len(pdf.pages),
                "success": True
            }
            
            logger.info(f"Extracted text using pdfplumber for {pdf_path.name}")
            return text, None, metadata
            
        except ImportError:
            logger.debug("pdfplumber not available")
            return "", None, {"method": "pdfplumber", "error": "pdfplumber not installed"}
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {pdf_path.name}: {e}")
            return "", None, {"method": "pdfplumber", "error": str(e)}
