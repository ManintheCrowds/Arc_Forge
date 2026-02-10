# PURPOSE: OCR processing for scanned PDFs (Long-Term Enhancement LTE1).
# DEPENDENCIES: pytesseract, Pillow, pdf2image, Tesseract OCR.
# MODIFICATION NOTES: Complete implementation with preprocessing, caching, and error handling.

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import OCR dependencies
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR dependencies not available. Install with: pip install pytesseract pdf2image Pillow")

def extract_text_with_ocr(
    pdf_path: Path,
    language: str = "eng",
    output_dir: Optional[Path] = None,
    deskew: bool = True,
    denoise: bool = True,
    contrast_enhancement: bool = True,
) -> Tuple[str, Optional[Path]]:
    """
    Extract text from scanned PDF using OCR.
    
    Args:
        pdf_path: Path to PDF file.
        language: OCR language code (default: "eng").
        output_dir: Directory to save OCR cache (optional).
        deskew: Whether to deskew images (default: True).
        denoise: Whether to denoise images (default: True).
        contrast_enhancement: Whether to enhance contrast (default: True).
        
    Returns:
        Tuple of (extracted_text, output_path). output_path is None if OCR fails.
    """
    if not OCR_AVAILABLE:
        logger.error("OCR dependencies not available")
        return "", None
    
    try:
        # Check cache first
        if output_dir:
            cache_path = _get_ocr_cache_path(pdf_path, output_dir)
            if cache_path and cache_path.exists():
                logger.info(f"Using cached OCR results for {pdf_path.name}")
                text = cache_path.read_text(encoding="utf-8", errors="replace")
                return text, cache_path
        
        logger.info(f"Starting OCR processing for {pdf_path.name}")
        
        # Convert PDF pages to images
        try:
            images = convert_from_path(str(pdf_path), dpi=300)
            logger.info(f"Converted {len(images)} pages to images")
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            return "", None
        
        # Process each page
        all_text = []
        for page_num, image in enumerate(images, start=1):
            try:
                # Preprocess image
                processed_image = preprocess_image(
                    image,
                    deskew=deskew,
                    denoise=denoise,
                    contrast_enhancement=contrast_enhancement,
                )
                
                # Run OCR
                page_text = pytesseract.image_to_string(processed_image, lang=language)
                if page_text.strip():
                    all_text.append(f"--- Page {page_num} ---\n{page_text}")
                    logger.debug(f"OCR extracted {len(page_text)} characters from page {page_num}")
                else:
                    logger.warning(f"No text extracted from page {page_num}")
            except Exception as e:
                logger.warning(f"OCR failed for page {page_num}: {e}")
                continue
        
        # Combine text from all pages
        extracted_text = "\n\n".join(all_text)
        
        if not extracted_text.strip():
            logger.warning(f"No text extracted from {pdf_path.name}")
            return "", None
        
        logger.info(f"OCR extracted {len(extracted_text)} characters from {pdf_path.name}")
        
        # Save to cache if output directory provided
        cache_path = None
        if output_dir and extracted_text:
            cache_path = _save_ocr_cache(pdf_path, extracted_text, output_dir)
        
        return extracted_text, cache_path
        
    except Exception as e:
        logger.error(f"OCR processing failed for {pdf_path.name}: {e}", exc_info=True)
        return "", None


def _get_ocr_cache_path(pdf_path: Path, output_dir: Path) -> Optional[Path]:
    """Get the cache path for OCR results."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Use PDF hash to create unique cache filename
        pdf_hash = hashlib.md5(pdf_path.read_bytes()).hexdigest()[:16]
        cache_filename = f"{pdf_path.stem}_{pdf_hash}_ocr.txt"
        return output_dir / cache_filename
    except Exception as e:
        logger.warning(f"Failed to create OCR cache path: {e}")
        return None


def _save_ocr_cache(pdf_path: Path, text: str, output_dir: Path) -> Optional[Path]:
    """Save OCR results to cache."""
    try:
        cache_path = _get_ocr_cache_path(pdf_path, output_dir)
        if cache_path:
            cache_path.write_text(text, encoding="utf-8")
            logger.info(f"Saved OCR cache to {cache_path}")
            return cache_path
    except Exception as e:
        logger.warning(f"Failed to save OCR cache: {e}")
    return None


def is_scanned_pdf(pdf_path: Path, threshold: float = 0.05) -> bool:
    """
    Detect if PDF is scanned/image-based (requires OCR).
    
    Checks if PDF has extractable text. If text extraction yields less than
    threshold percentage of expected content, considers it scanned.
    
    Args:
        pdf_path: Path to PDF file.
        threshold: Minimum ratio of text to page count (default: 0.05 = 5%).
        
    Returns:
        True if PDF appears to be scanned, False otherwise.
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        
        if page_count == 0:
            return True
        
        # Extract text from all pages
        total_text_length = 0
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
                total_text_length += len(page_text.strip())
            except Exception:
                continue
        
        # Calculate average text per page
        avg_text_per_page = total_text_length / page_count if page_count > 0 else 0
        
        # If average text per page is less than 50 characters, likely scanned
        # Also check if total text is less than threshold of expected content
        # (assuming ~2000 chars per page for text-based PDFs)
        expected_text_per_page = 2000
        text_ratio = avg_text_per_page / expected_text_per_page if expected_text_per_page > 0 else 0
        
        is_scanned = text_ratio < threshold or avg_text_per_page < 50
        
        if is_scanned:
            logger.info(f"PDF {pdf_path.name} appears to be scanned (text ratio: {text_ratio:.2%}, avg chars/page: {avg_text_per_page:.0f})")
        else:
            logger.debug(f"PDF {pdf_path.name} appears to be text-based (text ratio: {text_ratio:.2%}, avg chars/page: {avg_text_per_page:.0f})")
        
        return is_scanned
        
    except ImportError:
        logger.warning("pypdf not available for scanned PDF detection")
        return False
    except Exception as e:
        logger.warning(f"Failed to detect if PDF is scanned: {e}")
        # Default to False to avoid unnecessary OCR
        return False


def preprocess_image(
    image: Image.Image,
    deskew: bool = True,
    denoise: bool = True,
    contrast_enhancement: bool = True,
) -> Image.Image:
    """
    Preprocess image for better OCR results.
    
    Args:
        image: PIL Image to preprocess.
        deskew: Whether to deskew the image (default: True).
        denoise: Whether to denoise the image (default: True).
        contrast_enhancement: Whether to enhance contrast (default: True).
        
    Returns:
        Preprocessed PIL Image.
    """
    processed = image.copy()
    
    # Convert to grayscale if not already
    if processed.mode != "L":
        processed = processed.convert("L")
    
    # Contrast enhancement
    if contrast_enhancement:
        try:
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(1.5)  # Increase contrast by 50%
        except Exception as e:
            logger.debug(f"Contrast enhancement failed: {e}")
    
    # Denoising
    if denoise:
        try:
            # Apply a slight blur to reduce noise
            processed = processed.filter(ImageFilter.MedianFilter(size=3))
        except Exception as e:
            logger.debug(f"Denoising failed: {e}")
    
    # Deskewing (simplified - detect and correct rotation)
    if deskew:
        try:
            # Use pytesseract to detect orientation
            try:
                osd = pytesseract.image_to_osd(processed)
                # Parse orientation from OSD output
                # OSD format: "Page number: X\nOrientation in degrees: Y\n..."
                for line in osd.split("\n"):
                    if "Orientation in degrees" in line:
                        orientation = int(line.split(":")[1].strip())
                        if orientation != 0:
                            # Rotate image to correct orientation
                            processed = processed.rotate(-orientation, expand=True)
                            logger.debug(f"Deskewed image by {orientation} degrees")
                        break
            except Exception:
                # OSD detection failed, skip deskewing
                logger.debug("Could not detect image orientation, skipping deskew")
        except Exception as e:
            logger.debug(f"Deskewing failed: {e}")
    
    return processed
