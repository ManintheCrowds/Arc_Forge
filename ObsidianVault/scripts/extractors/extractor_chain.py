# PURPOSE: Manages extraction chain with fallback logic.
# DEPENDENCIES: All extractor implementations.
# MODIFICATION NOTES: Phase 1 - Centralized extraction orchestration.

import logging
from pathlib import Path
from typing import List, Tuple, Optional

from extractors.base_extractor import TextExtractor
from extractors.pdfplus_extractor import PDFPlusExtractor
from extractors.pypdf_extractor import PyPDFExtractor
from extractors.pdfplumber_extractor import PDFPlumberExtractor
from extractors.ocr_extractor import OCRExtractor

logger = logging.getLogger(__name__)


class ExtractorChain:
    """Manages the extraction chain with fallback logic."""
    
    def __init__(self, config: dict):
        """
        Initialize extractor chain.
        
        Args:
            config: Configuration dictionary
        """
        self.extractors: List[TextExtractor] = []
        
        # Initialize extractors in priority order
        self.extractors.append(PDFPlusExtractor(config))
        self.extractors.append(PyPDFExtractor())
        self.extractors.append(PDFPlumberExtractor())
        
        # Add OCR if enabled
        ocr_config = config.get("ocr", {})
        if ocr_config.get("enabled", False):
            self.extractors.append(OCRExtractor(
                tesseract_path=ocr_config.get("tesseract_path"),
                language=ocr_config.get("language", "eng"),
                dpi=ocr_config.get("dpi", 300)
            ))
            logger.info("OCR extractor enabled in chain")
    
    def extract(self, pdf_path: Path, vault_root: Path) -> Tuple[str, Optional[Path], dict]:
        """
        Try extractors in order until one succeeds.
        
        Args:
            pdf_path: Path to PDF file
            vault_root: Root directory of the vault
            
        Returns:
            Tuple of (text, source_path, metadata)
        """
        for extractor in self.extractors:
            if extractor.can_extract(pdf_path):
                try:
                    text, source_path, metadata = extractor.extract(pdf_path, vault_root=vault_root)
                    if text.strip():  # Success if we got text
                        logger.debug(f"Extraction succeeded with {metadata.get('method', 'unknown')} for {pdf_path.name}")
                        return text, source_path, metadata
                except Exception as e:
                    logger.debug(f"Extractor {extractor.__class__.__name__} failed for {pdf_path.name}: {e}")
                    continue  # Try next extractor
        
        logger.warning(f"All extractors failed for {pdf_path.name}")
        return "", None, {"method": "none", "error": "All extractors failed"}
