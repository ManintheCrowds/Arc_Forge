# PURPOSE: OCR-based text extraction using Tesseract.
# DEPENDENCIES: pytesseract, pdf2image, Tesseract OCR installed.
# MODIFICATION NOTES: Phase 1 - OCR integration for scanned PDFs.

import logging
from pathlib import Path
from typing import Optional, Tuple

from extractors.base_extractor import TextExtractor

logger = logging.getLogger(__name__)


class OCRExtractor(TextExtractor):
    """OCR-based text extractor using Tesseract."""
    
    def __init__(self, tesseract_path: Optional[str] = None, language: str = "eng", dpi: int = 300):
        """
        Initialize OCR extractor.
        
        Args:
            tesseract_path: Path to tesseract executable (None for auto-detect)
            language: OCR language code (default: "eng")
            dpi: DPI for PDF-to-image conversion (default: 300)
        """
        self.tesseract_path = tesseract_path
        self.language = language
        self.dpi = dpi
        self._available = self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Verify OCR dependencies are available."""
        try:
            import pytesseract
            import pdf2image
            if self.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            return True
        except ImportError:
            logger.warning("OCR dependencies not available. Install with: pip install pytesseract pdf2image Pillow")
            return False
        except Exception as e:
            logger.warning(f"OCR dependency check failed: {e}")
            return False
    
    def can_extract(self, pdf_path: Path) -> bool:
        """OCR can extract from any PDF (as fallback)."""
        return self._available
    
    def extract(self, pdf_path: Path, **kwargs) -> Tuple[str, Optional[Path], dict]:
        """
        Extract text using OCR.
        
        Returns metadata with confidence scores and processing info.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Unused
            
        Returns:
            Tuple of (text, source_path, metadata)
        """
        if not self._available:
            return "", None, {"method": "ocr", "error": "OCR dependencies not available"}
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(str(pdf_path), dpi=self.dpi)
            
            # Extract text from each page
            texts = []
            confidences = []
            for i, image in enumerate(images):
                try:
                    # Get text and confidence
                    data = pytesseract.image_to_data(
                        image, 
                        lang=self.language, 
                        output_type=pytesseract.Output.DICT
                    )
                    page_text = pytesseract.image_to_string(image, lang=self.language)
                    texts.append(page_text)
                    
                    # Calculate average confidence for page
                    confs = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_conf = sum(confs) / len(confs) if confs else 0
                    confidences.append(avg_conf)
                except Exception as e:
                    logger.warning(f"OCR failed for page {i+1} of {pdf_path.name}: {e}")
                    texts.append("")
                    confidences.append(0)
            
            full_text = "\n\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            metadata = {
                "method": "ocr",
                "confidence": avg_confidence,
                "pages": len(images),
                "language": self.language,
                "dpi": self.dpi,
                "success": True
            }
            
            logger.info(f"Extracted text using OCR for {pdf_path.name} (confidence: {avg_confidence:.1f}%)")
            return full_text, None, metadata
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {pdf_path.name}: {e}")
            return "", None, {"method": "ocr", "error": str(e)}
