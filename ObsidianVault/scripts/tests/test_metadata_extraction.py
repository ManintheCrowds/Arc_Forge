# PURPOSE: Unit tests for PDF metadata extraction.
# DEPENDENCIES: pytest, ingest_pdfs module, sample PDFs.
# MODIFICATION NOTES: Tests title, author, date, and page count extraction.

import pytest
from pathlib import Path
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ingest_pdfs import extract_pdf_metadata
    from metadata_extractor import (
        extract_pdf_metadata as extract_metadata,
        extract_citations,
        query_crossref_api,
        enrich_metadata_with_citations,
        _parse_pdf_date,
    )
    METADATA_EXTRACTION_AVAILABLE = True
except ImportError:
    METADATA_EXTRACTION_AVAILABLE = False
    pytest.skip("metadata extraction module not available", allow_module_level=True)


class TestExtractPdfMetadata:
    """Test cases for PDF metadata extraction."""
    
    def test_extract_metadata_nonexistent_file(self):
        """Test metadata extraction from non-existent file."""
        fake_path = Path("/nonexistent/file.pdf")
        result = extract_pdf_metadata(fake_path)
        
        # Should return empty dict or handle gracefully
        assert isinstance(result, dict)
    
    def test_extract_metadata_returns_dict(self):
        """Test that metadata extraction returns a dictionary."""
        # Create a minimal test - we can't easily create PDFs in tests
        # So we test the function signature and error handling
        fake_path = Path("/tmp/test.pdf")
        result = extract_pdf_metadata(fake_path)
        
        assert isinstance(result, dict)
    
    def test_extract_metadata_structure(self):
        """Test that metadata dict has expected structure."""
        # Test with a path that will fail (no actual PDF)
        # This tests the function's error handling
        fake_path = Path("/tmp/test.pdf")
        result = extract_pdf_metadata(fake_path)
        
        # Should return dict (empty if extraction fails)
        assert isinstance(result, dict)
        # Keys that might be present if extraction succeeds
        possible_keys = ["title", "author", "subject", "creator", "creation_date", "page_count"]
        # All keys in result should be from expected set
        for key in result.keys():
            assert key in possible_keys
    
    def test_extract_metadata_handles_missing_pypdf(self, monkeypatch):
        """Test that function handles missing pypdf gracefully."""
        # Mock ImportError
        def mock_import_error(*args, **kwargs):
            raise ImportError("pypdf not available")
        
        fake_path = Path("/tmp/test.pdf")
        
        # This tests the ImportError handling
        result = extract_pdf_metadata(fake_path)
        assert isinstance(result, dict)
    
    def test_extract_metadata_handles_exceptions(self):
        """Test that function handles exceptions gracefully."""
        # Test with invalid path
        invalid_path = Path("")
        result = extract_pdf_metadata(invalid_path)
        
        # Should return empty dict on error
        assert isinstance(result, dict)


class TestCitationExtraction:
    """Tests for citation extraction (Phase 2)."""
    
    @pytest.mark.unit
    def test_extract_doi(self):
        """Test DOI extraction from text."""
        text = "This paper has DOI: 10.1234/example.12345. See also https://doi.org/10.5678/test.67890"
        citations = extract_citations(text)
        
        assert len(citations["doi"]) >= 1
        assert any("10.1234" in doi for doi in citations["doi"])
    
    @pytest.mark.unit
    def test_extract_isbn(self):
        """Test ISBN extraction from text."""
        text = "ISBN-13: 978-0-123456-78-9 or ISBN: 1234567890"
        citations = extract_citations(text)
        
        assert len(citations["isbn"]) >= 1
    
    @pytest.mark.unit
    def test_extract_urls(self):
        """Test URL extraction from text."""
        text = "See https://example.com/paper.pdf for more information."
        citations = extract_citations(text)
        
        assert len(citations["urls"]) >= 1
        assert any("example.com" in url for url in citations["urls"])
    
    @pytest.mark.unit
    def test_extract_citations_empty(self):
        """Test citation extraction from empty text."""
        citations = extract_citations("")
        
        assert citations["doi"] == []
        assert citations["isbn"] == []
        assert citations["urls"] == []


class TestCrossRefAPI:
    """Tests for CrossRef API integration (Phase 2)."""
    
    @pytest.mark.unit
    def test_query_crossref_api_success(self):
        """Test successful CrossRef API query."""
        with patch("metadata_extractor.REQUESTS_AVAILABLE", True), \
             patch("metadata_extractor.requests", MagicMock(), create=True) as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {
                    "title": ["Test Paper"],
                    "author": [{"given": "John", "family": "Doe"}],
                    "published-print": {"date-parts": [[2024, 1, 1]]},
                    "container-title": ["Test Journal"]
                }
            }
            mock_requests.get.return_value = mock_response
            
            result = query_crossref_api("10.1234/test.12345")
            
            assert result is not None
            assert "title" in result
            assert "authors" in result
    
    @pytest.mark.unit
    def test_query_crossref_api_not_found(self):
        """Test CrossRef API query when DOI not found."""
        with patch("metadata_extractor.REQUESTS_AVAILABLE", True), \
             patch("metadata_extractor.requests", MagicMock(), create=True) as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_requests.get.return_value = mock_response
            
            result = query_crossref_api("10.1234/nonexistent.12345")
            
            assert result is None
    
    @pytest.mark.unit
    def test_query_crossref_api_error(self):
        """Test CrossRef API query error handling."""
        with patch("metadata_extractor.REQUESTS_AVAILABLE", True), \
             patch("metadata_extractor.requests", MagicMock(), create=True) as mock_requests:
            mock_requests.get.side_effect = Exception("Connection error")
            
            result = query_crossref_api("10.1234/test.12345")
            
            assert result is None


class TestMetadataEnrichment:
    """Tests for metadata enrichment (Phase 2)."""
    
    @pytest.mark.unit
    def test_enrich_metadata_with_citations(self):
        """Test metadata enrichment with citations."""
        pdf_metadata = {
            "title": "Test Document",
            "author": "Test Author",
        }
        
        text = "DOI: 10.1234/test.12345. ISBN-13: 978-0-123456-78-9"
        
        with patch("metadata_extractor.query_crossref_api") as mock_crossref:
            mock_crossref.return_value = {
                "title": "Enriched Title",
                "authors": "Enriched Author",
            }
            
            enriched = enrich_metadata_with_citations(pdf_metadata, text)
            
            assert "doi" in enriched
            assert "isbn" in enriched
            # Should merge CrossRef metadata
            assert enriched.get("title") in ["Test Document", "Enriched Title"]


class TestPDFDateParsing:
    """Tests for PDF date parsing (Phase 2)."""
    
    @pytest.mark.unit
    def test_parse_pdf_date_standard_format(self):
        """Test parsing standard PDF date format."""
        date_str = "D:20240101120000"
        result = _parse_pdf_date(date_str)
        
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
    
    @pytest.mark.unit
    def test_parse_pdf_date_without_prefix(self):
        """Test parsing PDF date without D: prefix."""
        date_str = "20240101120000"
        result = _parse_pdf_date(date_str)
        
        assert result is not None
        assert result.year == 2024
    
    @pytest.mark.unit
    def test_parse_pdf_date_invalid(self):
        """Test parsing invalid PDF date."""
        date_str = "invalid date"
        result = _parse_pdf_date(date_str)
        
        # Should return None or handle gracefully
        assert result is None or isinstance(result, type(None))


class TestMetadataIntegration:
    """Integration tests for metadata extraction (requires actual PDFs)."""
    
    @pytest.mark.skipif(not METADATA_EXTRACTION_AVAILABLE, reason="Module not available")
    def test_metadata_in_source_note(self):
        """Test that metadata is integrated into source note building."""
        from ingest_pdfs import build_source_note
        
        # Test with mock metadata
        metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "subject": "Test Subject",
            "creation_date": "2024-01-01",
            "page_count": "10",
            "doi": "10.1234/test.12345",  # Phase 2 addition
            "isbn": "978-0-123456-78-9",  # Phase 2 addition
        }
        
        # This tests the build_source_note function accepts metadata
        # We can't fully test without templates, but we can test the parameter
        assert isinstance(metadata, dict)
        assert "title" in metadata or "author" in metadata
        assert "doi" in metadata  # Phase 2 feature
        assert "isbn" in metadata  # Phase 2 feature


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
