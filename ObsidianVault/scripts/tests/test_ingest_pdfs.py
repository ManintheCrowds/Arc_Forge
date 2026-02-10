# PURPOSE: Integration tests for PDF ingestion pipeline.
# DEPENDENCIES: pytest, ingest_pdfs module, test fixtures.
# MODIFICATION NOTES: Tests full ingestion workflow with sample data.

import json
import tempfile
from pathlib import Path

import pytest

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest_pdfs import (
    build_entity_note,
    build_rule_note,
    build_source_note,
    extract_text,
    find_pdfplus_text,
    ingest_pdfs,
    list_pdfs,
    parse_entities,
    safe_note_name,
    to_file_url,
    write_extracted_text,
)


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample configuration for testing."""
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir()
    
    sources_dir = vault_root / "Sources"
    sources_dir.mkdir()
    
    templates_dir = vault_root / "Templates"
    templates_dir.mkdir()
    
    # Create template files
    source_template = templates_dir / "source_note.md"
    source_template.write_text(
        "---\n"
        "title: \"{{title}}\"\n"
        "source_file: \"{{source_file}}\"\n"
        "---\n\n"
        "## Summary\n\n- \n"
    )
    
    entity_template = templates_dir / "entity_note.md"
    entity_template.write_text(
        "---\n"
        "title: \"{{title}}\"\n"
        "entity_type: \"{{entity_type}}\"\n"
        "date: \"{{date}}\"\n"
        "source_refs: []\n"
        "---\n\n"
        "## Summary\n\n- \n"
    )
    
    config = {
        "vault_root": str(vault_root),
        "pdf_root": str(pdf_root),
        "source_notes_dir": "Sources",
        "rules_dir": "Rules",
        "npcs_dir": "NPCs",
        "factions_dir": "Factions",
        "locations_dir": "Locations",
        "items_dir": "Items",
        "extracted_text_dir": "Sources/_extracted_text",
        "templates": {
            "source_note": "Templates/source_note.md",
            "entity_note": "Templates/entity_note.md",
        },
        "pdf_text_cache_dirs": [".obsidian/plugins/pdf-plus"],
        "pdf_text_cache_extensions": [".txt", ".md"],
        "max_excerpt_chars": 200,
        "max_pdf_size_mb": 100,
    }
    
    return config


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF file for testing."""
    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir(exist_ok=True)
    
    # Create a dummy PDF file (just a text file with .pdf extension for testing)
    pdf_file = pdf_root / "test_document.pdf"
    pdf_file.write_text("This is a test PDF content.\nPage 2 content.")
    
    return pdf_file


class TestSafeNoteName:
    """Tests for safe_note_name function."""

    def test_removes_illegal_characters(self):
        """Test that illegal characters are removed."""
        result = safe_note_name("test/file:name*.pdf")
        assert "/" not in result
        assert ":" not in result
        assert "*" not in result

    def test_preserves_valid_characters(self):
        """Test that valid characters are preserved."""
        result = safe_note_name("Test Document 123")
        assert result == "Test Document 123"

    def test_normalizes_whitespace(self):
        """Test that multiple spaces are normalized."""
        result = safe_note_name("test    document")
        assert "  " not in result
        assert " " in result


class TestListPdfs:
    """Tests for list_pdfs function."""

    def test_finds_pdfs_in_directory(self, tmp_path):
        """Test finding PDFs in a directory."""
        pdf_root = tmp_path / "pdfs"
        pdf_root.mkdir()
        
        (pdf_root / "doc1.pdf").write_text("content")
        (pdf_root / "doc2.pdf").write_text("content")
        (pdf_root / "other.txt").write_text("content")
        
        pdfs = list_pdfs(pdf_root)
        assert len(pdfs) == 2
        assert all(p.suffix == ".pdf" for p in pdfs)

    def test_finds_pdfs_recursively(self, tmp_path):
        """Test finding PDFs recursively."""
        pdf_root = tmp_path / "pdfs"
        pdf_root.mkdir()
        subdir = pdf_root / "subdir"
        subdir.mkdir()
        
        (pdf_root / "doc1.pdf").write_text("content")
        (subdir / "doc2.pdf").write_text("content")
        
        pdfs = list_pdfs(pdf_root)
        assert len(pdfs) == 2

    def test_skips_large_files(self, tmp_path):
        """Test that files exceeding size limit are skipped."""
        pdf_root = tmp_path / "pdfs"
        pdf_root.mkdir()
        
        small_pdf = pdf_root / "small.pdf"
        small_pdf.write_text("content")
        
        large_pdf = pdf_root / "large.pdf"
        # Create a file larger than 1MB
        with large_pdf.open("wb") as f:
            f.write(b"x" * (2 * 1024 * 1024))
        
        pdfs = list_pdfs(pdf_root, max_size_mb=1)
        assert len(pdfs) == 1
        assert small_pdf in pdfs


class TestExtractText:
    """Tests for extract_text function."""

    def test_extract_from_pdfplus_cache(self, tmp_path, sample_pdf):
        """Test extracting text from PDF++ cache."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        cache_dir = vault_root / ".obsidian" / "plugins" / "pdf-plus"
        cache_dir.mkdir(parents=True)
        
        cache_file = cache_dir / "test_document.txt"
        cache_file.write_text("Cached extracted text")
        
        text, source_path, _ = extract_text(
            sample_pdf,
            vault_root,
            extractor_chain=None,
            cache_dirs=[".obsidian/plugins/pdf-plus"],
            extensions=[".txt"],
        )
        
        assert "Cached extracted text" in text
        assert source_path == cache_file

    def test_fallback_when_cache_missing(self, tmp_path, sample_pdf):
        """Test fallback when PDF++ cache is missing."""
        vault_root = tmp_path / "vault"
        vault_root.mkdir()
        
        # No cache directory
        text, source_path, _ = extract_text(
            sample_pdf,
            vault_root,
            extractor_chain=None,
            cache_dirs=[".obsidian/plugins/pdf-plus"],
            extensions=[".txt"],
        )
        
        # Should return empty or fallback text
        assert source_path is None


class TestParseEntities:
    """Tests for parse_entities function."""

    def test_parse_entities_from_source_note(self):
        """Test parsing entities from source note content."""
        content = """
        - NPCs: Alice, Bob, Charlie
        - Factions: Empire, Rebels
        - Locations: City, Forest
        - Items: Sword, Shield
        - Rules/Mechanics: Combat, Magic
        """
        
        entities = parse_entities(content)
        
        assert "Alice" in entities["NPCs"]
        assert "Empire" in entities["Factions"]
        assert "City" in entities["Locations"]
        assert "Sword" in entities["Items"]
        assert "Combat" in entities["Rules/Mechanics"]

    def test_parse_entities_with_semicolons(self):
        """Test parsing entities with semicolon separators."""
        content = "- NPCs: Alice; Bob; Charlie"
        
        entities = parse_entities(content)
        
        assert len(entities["NPCs"]) == 3
        assert "Alice" in entities["NPCs"]


class TestBuildSourceNote:
    """Tests for build_source_note function."""

    def test_builds_source_note_with_template(self, tmp_path, sample_config):
        """Test building a source note from template."""
        vault_root = Path(sample_config["vault_root"])
        template_path = vault_root / sample_config["templates"]["source_note"]
        
        content = build_source_note(
            template_path,
            "Test Document",
            "test.pdf",
            "file:///test.pdf",
            "Excerpt text",
            None,
            "2024-01-01",
        )
        
        assert "Test Document" in content
        assert "test.pdf" in content
        assert "Excerpt text" in content


class TestWriteExtractedText:
    """Tests for write_extracted_text function."""

    def test_writes_extracted_text(self, tmp_path):
        """Test writing extracted text to file."""
        out_dir = tmp_path / "extracted"
        text = "Extracted PDF text content"
        
        result = write_extracted_text(text, out_dir, "test_document")
        
        assert result is not None
        assert result.exists()
        assert result.read_text() == text

    def test_skips_empty_text(self, tmp_path):
        """Test that empty text is not written."""
        out_dir = tmp_path / "extracted"
        
        result = write_extracted_text("", out_dir, "test_document")
        
        assert result is None


class TestToFileUrl:
    """Tests for to_file_url function."""

    def test_converts_path_to_file_url(self, tmp_path):
        """Test converting a path to file:// URL."""
        test_file = tmp_path / "test file.pdf"
        test_file.write_text("content")
        
        url = to_file_url(test_file)
        
        assert url.startswith("file:///")
        assert "test%20file.pdf" in url  # URL-encoded space
