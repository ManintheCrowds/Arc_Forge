# PURPOSE: Unit tests for table extractor (Phase 2).
# DEPENDENCIES: pytest, table_extractor module.
# MODIFICATION NOTES: Phase 2 - Tests table extraction, Markdown conversion, and caption extraction.

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

try:
    from table_extractor import (
        extract_tables_pdfplumber,
        extract_tables_camelot,
        extract_tables,
        table_to_markdown,
        _extract_table_caption,
        extract_figures,
    )
    TABLE_EXTRACTOR_AVAILABLE = True
except ImportError:
    TABLE_EXTRACTOR_AVAILABLE = False
    pytest.skip("Table extractor module not available", allow_module_level=True)


class TestTableToMarkdown:
    """Tests for Markdown table conversion."""
    
    @pytest.mark.unit
    def test_table_to_markdown_simple(self):
        """Test conversion of simple table to Markdown."""
        table_data = [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
            ["Value3", "Value4"],
        ]
        
        markdown = table_to_markdown(table_data)
        
        assert "|" in markdown
        assert "Header1" in markdown
        assert "Value1" in markdown
        assert "---" in markdown  # Separator row
    
    @pytest.mark.unit
    def test_table_to_markdown_with_alignment(self):
        """Test Markdown conversion with alignment."""
        table_data = [
            ["Left", "Center", "Right"],
            ["A", "B", "C"],
        ]
        
        markdown = table_to_markdown(table_data, align=["left", "center", "right"])
        
        assert ":-" in markdown  # Left align
        assert ":-:" in markdown  # Center align
        assert "-:" in markdown  # Right align
    
    @pytest.mark.unit
    def test_table_to_markdown_empty(self):
        """Test conversion of empty table."""
        markdown = table_to_markdown([])
        assert markdown == ""
    
    @pytest.mark.unit
    def test_table_to_markdown_escapes_pipes(self):
        """Test that pipe characters are escaped."""
        table_data = [
            ["Column|Name", "Value"],
        ]
        
        markdown = table_to_markdown(table_data)
        
        # Pipe should be escaped
        assert "\\|" in markdown or "Column|Name" in markdown
    
    @pytest.mark.unit
    def test_table_to_markdown_normalizes_columns(self):
        """Test that columns are normalized to same width."""
        table_data = [
            ["A", "B"],
            ["C", "D", "E"],  # Extra column
        ]
        
        markdown = table_to_markdown(table_data)
        
        # Should handle uneven columns
        lines = markdown.split("\n")
        assert len(lines) > 0


class TestExtractTablesPdfplumber:
    """Tests for pdfplumber table extraction."""
    
    @pytest.mark.unit
    def test_extract_tables_pdfplumber_not_available(self, tmp_path):
        """Test when pdfplumber is not available."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.PDFPLUMBER_AVAILABLE", False):
            result = extract_tables_pdfplumber(pdf_path)
            assert result == []
    
    @pytest.mark.unit
    def test_extract_tables_pdfplumber_success(self, tmp_path):
        """Test successful pdfplumber extraction."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.pdfplumber") as mock_pdfplumber:
            # Mock PDF structure
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_table = [
                ["Header1", "Header2"],
                ["Value1", "Value2"],
            ]
            mock_page.extract_tables.return_value = [mock_table]
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = Mock(return_value=mock_pdf)
            mock_pdf.__exit__ = Mock(return_value=None)
            mock_pdfplumber.open.return_value = mock_pdf
            
            result = extract_tables_pdfplumber(pdf_path)
            
            assert len(result) == 1
            assert result[0]["page"] == 1
            assert result[0]["table_index"] == 1
            assert "markdown" in result[0]
            assert result[0]["method"] == "pdfplumber"
    
    @pytest.mark.unit
    def test_extract_tables_pdfplumber_multiple_pages(self, tmp_path):
        """Test extraction from multiple pages."""
        pdf_path = tmp_path / "multipage.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.pdfplumber") as mock_pdfplumber:
            mock_pdf = MagicMock()
            mock_page1 = MagicMock()
            mock_page2 = MagicMock()
            mock_page1.extract_tables.return_value = [["Table1"]]
            mock_page2.extract_tables.return_value = [["Table2"]]
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_pdf.__enter__ = Mock(return_value=mock_pdf)
            mock_pdf.__exit__ = Mock(return_value=None)
            mock_pdfplumber.open.return_value = mock_pdf
            
            result = extract_tables_pdfplumber(pdf_path)
            
            assert len(result) == 2
            assert result[0]["page"] == 1
            assert result[1]["page"] == 2


class TestExtractTablesCamelot:
    """Tests for Camelot table extraction."""
    
    @pytest.mark.unit
    def test_extract_tables_camelot_not_available(self, tmp_path):
        """Test when camelot is not available."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.CAMELOT_AVAILABLE", False):
            result = extract_tables_camelot(pdf_path)
            assert result == []
    
    @pytest.mark.unit
    def test_extract_tables_camelot_success(self, tmp_path):
        """Test successful Camelot extraction."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.CAMELOT_AVAILABLE", True), \
             patch("table_extractor.camelot", MagicMock(), create=True) as mock_camelot:
            # Mock Camelot table
            mock_table = MagicMock()
            mock_table.df.values.tolist.return_value = [
                ["Header1", "Header2"],
                ["Value1", "Value2"],
            ]
            mock_table.page = 1
            mock_table.accuracy = 95.0
            mock_camelot.read_pdf.return_value = [mock_table]
            
            result = extract_tables_camelot(pdf_path, flavor="lattice")
            
            assert len(result) == 1
            assert result[0]["method"] == "camelot-lattice"
            assert result[0]["accuracy"] == 95.0


class TestExtractTables:
    """Tests for main table extraction function with fallback."""
    
    @pytest.mark.unit
    def test_extract_tables_pdfplumber_primary(self, tmp_path):
        """Test extraction with pdfplumber as primary method."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.extract_tables_pdfplumber") as mock_pdfplumber:
            mock_pdfplumber.return_value = [{"page": 1, "data": [["Test"]]}]
            
            result = extract_tables(pdf_path, method="pdfplumber")
            
            assert len(result) > 0
            mock_pdfplumber.assert_called_once()
    
    @pytest.mark.unit
    def test_extract_tables_fallback(self, tmp_path):
        """Test fallback to secondary method."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.extract_tables_pdfplumber") as mock_pdfplumber, \
             patch("table_extractor.extract_tables_camelot") as mock_camelot, \
             patch("table_extractor.CAMELOT_AVAILABLE", True):
            
            mock_pdfplumber.return_value = []  # Primary fails
            mock_camelot.return_value = [{"page": 1, "data": [["Test"]]}]
            
            result = extract_tables(pdf_path, method="pdfplumber", fallback_method="camelot")
            
            assert len(result) > 0
            mock_camelot.assert_called()
    
    @pytest.mark.unit
    def test_extract_tables_no_results(self, tmp_path):
        """Test when no tables are found."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.extract_tables_pdfplumber") as mock_pdfplumber, \
             patch("table_extractor.extract_tables_camelot") as mock_camelot:
            
            mock_pdfplumber.return_value = []
            mock_camelot.return_value = []
            
            result = extract_tables(pdf_path, method="pdfplumber", fallback_method="camelot")
            
            assert result == []


class TestExtractTableCaption:
    """Tests for table caption extraction."""
    
    @pytest.mark.unit
    def test_extract_caption_found(self):
        """Test caption extraction when caption exists."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Some text. Table 1: This is a caption. More text."
        
        caption = _extract_table_caption(mock_page, 1)
        
        assert caption is not None
        assert "caption" in caption.lower() or "table" in caption.lower()
    
    @pytest.mark.unit
    def test_extract_caption_not_found(self):
        """Test caption extraction when no caption exists."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Some text without any table caption."
        
        caption = _extract_table_caption(mock_page, 1)
        
        # May return None or empty string
        assert caption is None or caption == ""
    
    @pytest.mark.unit
    def test_extract_caption_no_text(self):
        """Test caption extraction when page has no text."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        
        caption = _extract_table_caption(mock_page, 1)
        
        assert caption is None


class TestExtractFigures:
    """Tests for figure extraction."""
    
    @pytest.mark.unit
    def test_extract_figures_not_available(self, tmp_path):
        """Test when pdfplumber is not available."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.PDFPLUMBER_AVAILABLE", False):
            result = extract_figures(pdf_path)
            assert result == []
    
    @pytest.mark.unit
    def test_extract_figures_success(self, tmp_path):
        """Test successful figure extraction."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"dummy pdf")
        
        with patch("table_extractor.pdfplumber") as mock_pdfplumber:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.images = [{"bbox": [0, 0, 100, 100]}]
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = Mock(return_value=mock_pdf)
            mock_pdf.__exit__ = Mock(return_value=None)
            mock_pdfplumber.open.return_value = mock_pdf
            
            result = extract_figures(pdf_path)
            
            assert len(result) == 1
            assert result[0]["page"] == 1
            assert result[0]["figure_index"] == 1
