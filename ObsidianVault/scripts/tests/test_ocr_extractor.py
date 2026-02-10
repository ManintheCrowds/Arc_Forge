# PURPOSE: Unit tests for OCR extractor (Phase 1).
# DEPENDENCIES: pytest, extractors.ocr_extractor module.
# MODIFICATION NOTES: Phase 1 - Tests OCR extraction, confidence scoring, and error handling.

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

try:
    from extractors.ocr_extractor import OCRExtractor
    OCR_EXTRACTOR_AVAILABLE = True
except ImportError:
    OCR_EXTRACTOR_AVAILABLE = False
    pytest.skip("OCR extractor module not available", allow_module_level=True)


class TestOCRExtractor:
    """Tests for OCRExtractor class."""
    
    def test_initialization(self):
        """Test that OCRExtractor can be initialized."""
        extractor = OCRExtractor()
        assert extractor is not None
        assert extractor.language == "eng"
        assert extractor.dpi == 300
    
    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        extractor = OCRExtractor(tesseract_path="/usr/bin/tesseract", language="fra", dpi=400)
        assert extractor.tesseract_path == "/usr/bin/tesseract"
        assert extractor.language == "fra"
        assert extractor.dpi == 400
    
    def test_can_extract(self):
        """Test can_extract() method."""
        extractor = OCRExtractor()
        pdf_path = Path("/tmp/test.pdf")
        
        # Can extract if dependencies available
        result = extractor.can_extract(pdf_path)
        assert isinstance(result, bool)
    
    def test_can_extract_without_dependencies(self):
        """Test can_extract() when dependencies unavailable."""
        with patch("extractors.ocr_extractor.OCRExtractor._check_dependencies", return_value=False):
            extractor = OCRExtractor()
            extractor._available = False
            pdf_path = Path("/tmp/test.pdf")
            
            result = extractor.can_extract(pdf_path)
            assert result is False
    
    @pytest.mark.unit
    def test_extract_without_dependencies(self, tmp_path):
        """Test extract() when dependencies unavailable."""
        extractor = OCRExtractor()
        extractor._available = False
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        text, source_path, metadata = extractor.extract(pdf_path)
        
        assert text == ""
        assert source_path is None
        assert "error" in metadata
        assert metadata["method"] == "ocr"
    
    @pytest.mark.unit
    def test_extract_with_mocked_dependencies(self, tmp_path):
        """Test extract() with mocked OCR dependencies."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            mock_to_string.return_value = "Extracted OCR text"
            mock_to_data.return_value = {"conf": ["90", "85", "92", "-1", "88"]}
            
            extractor = OCRExtractor()
            extractor._available = True
            
            text, source_path, metadata = extractor.extract(pdf_path)
            
            assert "Extracted OCR text" in text
            assert source_path is None
            assert metadata["method"] == "ocr"
            assert metadata["success"] is True
            assert "confidence" in metadata
            assert "pages" in metadata
    
    @pytest.mark.unit
    def test_extract_multiple_pages(self, tmp_path):
        """Test extract() with multiple pages."""
        pdf_path = tmp_path / "multipage.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image1 = MagicMock()
            mock_image2 = MagicMock()
            mock_convert.return_value = [mock_image1, mock_image2]
            mock_to_string.side_effect = ["Page 1 text", "Page 2 text"]
            mock_to_data.return_value = {"conf": ["90", "85"]}
            
            extractor = OCRExtractor()
            extractor._available = True
            
            text, source_path, metadata = extractor.extract(pdf_path)
            
            assert "Page 1 text" in text
            assert "Page 2 text" in text
            assert metadata["pages"] == 2
    
    @pytest.mark.unit
    def test_extract_confidence_scoring(self, tmp_path):
        """Test confidence scoring in metadata."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            mock_to_string.return_value = "Test text"
            mock_to_data.return_value = {"conf": ["90", "85", "92", "88", "-1"]}
            extractor = OCRExtractor()
            extractor._available = True
            text, source_path, metadata = extractor.extract(pdf_path)
            assert metadata["confidence"] == pytest.approx(88.75, rel=0.1)
    
    @pytest.mark.unit
    def test_extract_error_handling(self, tmp_path):
        """Test error handling during extraction."""
        pdf_path = tmp_path / "error.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path", side_effect=Exception("Conversion failed")):
            extractor = OCRExtractor()
            extractor._available = True
            
            text, source_path, metadata = extractor.extract(pdf_path)
            
            assert text == ""
            assert source_path is None
            assert "error" in metadata
    
    @pytest.mark.unit
    def test_extract_page_error_handling(self, tmp_path):
        """Test error handling for individual page failures."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image1 = MagicMock()
            mock_image2 = MagicMock()
            mock_convert.return_value = [mock_image1, mock_image2]
            mock_to_string.side_effect = ["Page 1 text", Exception("OCR failed")]
            mock_to_data.return_value = {"conf": ["90"]}
            extractor = OCRExtractor()
            extractor._available = True
            text, source_path, metadata = extractor.extract(pdf_path)
            assert "Page 1 text" in text
            assert metadata["pages"] == 2
    
    @pytest.mark.unit
    def test_extract_language_support(self, tmp_path):
        """Test OCR with different languages."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            mock_to_string.return_value = "Texte français"
            mock_to_data.return_value = {"conf": ["90"]}
            extractor = OCRExtractor(language="fra")
            extractor._available = True
            text, source_path, metadata = extractor.extract(pdf_path)
            assert metadata["language"] == "fra"
            mock_to_string.assert_called()
            call_args = mock_to_string.call_args
            assert call_args[1]["lang"] == "fra"
    
    @pytest.mark.unit
    def test_extract_dpi_configuration(self, tmp_path):
        """Test OCR with different DPI settings."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            mock_to_string.return_value = "Test text"
            mock_to_data.return_value = {"conf": ["90"]}
            extractor = OCRExtractor(dpi=400)
            extractor._available = True
            text, source_path, metadata = extractor.extract(pdf_path)
            assert metadata["dpi"] == 400
            mock_convert.assert_called_once()
            call_args = mock_convert.call_args
            assert call_args[1]["dpi"] == 400


class TestOCRExtractorIntegration:
    """Integration tests for OCR extractor."""
    
    @pytest.mark.integration
    def test_ocr_in_extractor_chain(self, tmp_path):
        """Test OCR as fallback in extractor chain."""
        from extractors.extractor_chain import ExtractorChain
        
        pdf_path = tmp_path / "scanned.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        config = {
            "vault_root": str(tmp_path),
            "pdf_text_cache_dirs": [],
            "pdf_text_cache_extensions": [],
            "ocr": {
                "enabled": True,
                "tesseract_path": None,
                "language": "eng",
            }
        }
        
        chain = ExtractorChain(config)
        
        # Mock OCR dependencies
        with patch("pdf2image.convert_from_path") as mock_convert, \
             patch("pytesseract.image_to_string") as mock_to_string, \
             patch("pytesseract.image_to_data") as mock_to_data:
            mock_image = MagicMock()
            mock_convert.return_value = [mock_image]
            mock_to_string.return_value = "OCR text"
            mock_to_data.return_value = {"conf": ["90"]}
            text, source_path, metadata = chain.extract(pdf_path, vault_root=tmp_path)
            
            # Should eventually use OCR as fallback
            # (after PDF++, pypdf, pdfplumber fail)
            assert isinstance(text, str)
            assert isinstance(metadata, dict)
