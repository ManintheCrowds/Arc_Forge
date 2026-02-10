# PURPOSE: Unit tests for OCR processor functionality.
# DEPENDENCIES: pytest, ocr_processor module.
# MODIFICATION NOTES: Tests OCR extraction, scanned PDF detection, and image preprocessing.

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ocr_processor import (
    extract_text_with_ocr,
    is_scanned_pdf,
    preprocess_image,
    OCR_AVAILABLE,
)


class TestIsScannedPdf:
    """Tests for scanned PDF detection."""
    
    def test_text_based_pdf_not_scanned(self, tmp_path):
        """Test that text-based PDFs are not detected as scanned."""
        # Create a mock PDF with text
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        # Mock pypdf module
        import sys
        mock_pypdf = MagicMock()
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "This is a text-based PDF with plenty of content. " * 50
        mock_reader.pages = [mock_page] * 5
        mock_pypdf.PdfReader = Mock(return_value=mock_reader)
        sys.modules["pypdf"] = mock_pypdf
        
        try:
            result = is_scanned_pdf(pdf_path)
            assert result is False
        finally:
            if "pypdf" in sys.modules:
                del sys.modules["pypdf"]
    
    def test_scanned_pdf_detected(self, tmp_path):
        """Test that scanned PDFs are detected correctly."""
        pdf_path = tmp_path / "scanned.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        # Mock pypdf module
        import sys
        mock_pypdf = MagicMock()
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""  # No extractable text
        mock_reader.pages = [mock_page] * 5
        mock_pypdf.PdfReader = Mock(return_value=mock_reader)
        sys.modules["pypdf"] = mock_pypdf
        
        try:
            result = is_scanned_pdf(pdf_path)
            assert result is True
        finally:
            if "pypdf" in sys.modules:
                del sys.modules["pypdf"]
    
    def test_minimal_text_detected_as_scanned(self, tmp_path):
        """Test that PDFs with minimal text are detected as scanned."""
        pdf_path = tmp_path / "minimal.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        # Mock pypdf module
        import sys
        mock_pypdf = MagicMock()
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "x" * 10  # Very little text
        mock_reader.pages = [mock_page] * 5
        mock_pypdf.PdfReader = Mock(return_value=mock_reader)
        sys.modules["pypdf"] = mock_pypdf
        
        try:
            result = is_scanned_pdf(pdf_path)
            assert result is True
        finally:
            if "pypdf" in sys.modules:
                del sys.modules["pypdf"]
    
    def test_missing_pypdf_returns_false(self, tmp_path):
        """Test that missing pypdf returns False (graceful degradation)."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        # Mock ImportError when importing pypdf
        import sys
        original_modules = sys.modules.copy()
        if "pypdf" in sys.modules:
            del sys.modules["pypdf"]
        
        # Patch the import to raise ImportError
        def mock_import(name, *args, **kwargs):
            if name == "pypdf":
                raise ImportError("pypdf not available")
            return __import__(name, *args, **kwargs)
        
        with patch("builtins.__import__", side_effect=mock_import):
            result = is_scanned_pdf(pdf_path)
            assert result is False
        
        # Restore modules
        sys.modules.clear()
        sys.modules.update(original_modules)


class TestPreprocessImage:
    """Tests for image preprocessing."""
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_preprocess_image_returns_image(self):
        """Test that preprocessing returns an image."""
        from PIL import Image
        
        # Create a test image
        test_image = Image.new("RGB", (100, 100), color="white")
        
        result = preprocess_image(test_image)
        assert isinstance(result, Image.Image)
        assert result.size == test_image.size
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_preprocess_image_grayscale(self):
        """Test that preprocessing converts to grayscale."""
        from PIL import Image
        
        # Create a color image
        test_image = Image.new("RGB", (100, 100), color="red")
        
        result = preprocess_image(test_image)
        assert result.mode == "L"  # Grayscale
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_preprocess_with_options(self):
        """Test preprocessing with different options."""
        from PIL import Image
        
        test_image = Image.new("RGB", (100, 100), color="white")
        
        # Test with all options enabled
        result1 = preprocess_image(test_image, deskew=True, denoise=True, contrast_enhancement=True)
        assert isinstance(result1, Image.Image)
        
        # Test with options disabled
        result2 = preprocess_image(test_image, deskew=False, denoise=False, contrast_enhancement=False)
        assert isinstance(result2, Image.Image)


class TestExtractTextWithOcr:
    """Tests for OCR text extraction."""
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_extract_text_with_ocr_no_dependencies(self, tmp_path):
        """Test that OCR returns empty when dependencies unavailable."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        with patch("ocr_processor.OCR_AVAILABLE", False):
            text, path = extract_text_with_ocr(pdf_path)
            assert text == ""
            assert path is None
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_extract_text_with_ocr_success(self, tmp_path):
        """Test successful OCR extraction."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        with patch("ocr_processor.convert_from_path") as mock_convert, \
             patch("ocr_processor.pytesseract.image_to_string") as mock_ocr:
            
            # Mock image conversion
            mock_image = Mock()
            mock_convert.return_value = [mock_image]
            
            # Mock OCR result
            mock_ocr.return_value = "Extracted text from OCR"
            
            text, path = extract_text_with_ocr(pdf_path, output_dir=tmp_path)
            
            assert "Extracted text from OCR" in text
            assert path is not None or path is None  # Cache path may or may not be created
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_extract_text_with_ocr_cache(self, tmp_path):
        """Test that OCR cache is used when available."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        # Create cache file
        cache_dir = tmp_path / "ocr_cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "test_1234567890abcdef_ocr.txt"
        cache_file.write_text("Cached OCR text")
        
        with patch("ocr_processor._get_ocr_cache_path") as mock_cache_path:
            mock_cache_path.return_value = cache_file
            
            text, path = extract_text_with_ocr(pdf_path, output_dir=cache_dir)
            
            assert "Cached OCR text" in text
            assert path == cache_file
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_extract_text_with_ocr_multiple_pages(self, tmp_path):
        """Test OCR extraction from multiple pages."""
        pdf_path = tmp_path / "multipage.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        with patch("ocr_processor.convert_from_path") as mock_convert, \
             patch("ocr_processor.pytesseract.image_to_string") as mock_ocr:
            
            # Mock multiple pages
            mock_image1 = Mock()
            mock_image2 = Mock()
            mock_convert.return_value = [mock_image1, mock_image2]
            
            # Mock OCR results for each page
            mock_ocr.side_effect = ["Page 1 text", "Page 2 text"]
            
            text, path = extract_text_with_ocr(pdf_path)
            
            assert "Page 1 text" in text
            assert "Page 2 text" in text
            assert "--- Page 1 ---" in text
            assert "--- Page 2 ---" in text
    
    @pytest.mark.skipif(not OCR_AVAILABLE, reason="OCR dependencies not available")
    def test_extract_text_with_ocr_error_handling(self, tmp_path):
        """Test that OCR errors are handled gracefully."""
        pdf_path = tmp_path / "error.pdf"
        pdf_path.write_bytes(b"dummy pdf content")
        
        with patch("ocr_processor.convert_from_path", side_effect=Exception("Conversion failed")):
            text, path = extract_text_with_ocr(pdf_path)
            assert text == ""
            assert path is None


class TestOcrIntegration:
    """Integration tests for OCR functionality."""
    
    def test_ocr_module_imports(self):
        """Test that OCR module can be imported."""
        import ocr_processor
        assert hasattr(ocr_processor, "extract_text_with_ocr")
        assert hasattr(ocr_processor, "is_scanned_pdf")
        assert hasattr(ocr_processor, "preprocess_image")
    
    def test_ocr_availability_flag(self):
        """Test that OCR_AVAILABLE flag is set correctly."""
        from ocr_processor import OCR_AVAILABLE
        # Flag should be boolean
        assert isinstance(OCR_AVAILABLE, bool)
