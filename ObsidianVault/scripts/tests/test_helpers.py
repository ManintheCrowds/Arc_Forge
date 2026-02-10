# PURPOSE: Test helper utilities for creating test data and mocking (Phase 1 & 2).
# DEPENDENCIES: pytest, pathlib, unittest.mock.
# MODIFICATION NOTES: Phase 1 & 2 - Helper functions for test data creation and API mocking.

import json
from pathlib import Path
from unittest.mock import Mock, MagicMock


def create_sample_pdf(output_path: Path, title: str = "Test Document", author: str = "Test Author") -> Path:
    """
    Create a minimal sample PDF file for testing.
    
    Args:
        output_path: Path where PDF should be created.
        title: PDF title metadata.
        author: PDF author metadata.
        
    Returns:
        Path to created PDF file.
    """
    # Create minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Title (%s)
/Author (%s)
>>
endobj
xref
0 1
trailer
<<
/Root 1 0 R
>>
%%EOF""" % (title.encode(), author.encode())
    
    output_path.write_bytes(pdf_content)
    return output_path


def create_scanned_pdf(output_path: Path) -> Path:
    """
    Create a mock scanned PDF (no extractable text).
    
    Args:
        output_path: Path where PDF should be created.
        
    Returns:
        Path to created PDF file.
    """
    # Create PDF with minimal text (simulating scanned PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
>>
endobj
xref
0 1
trailer
<<
/Root 1 0 R
>>
%%EOF"""
    
    output_path.write_bytes(pdf_content)
    return output_path


def create_pdf_with_tables(output_path: Path) -> Path:
    """
    Create a mock PDF with tables (structure only).
    
    Args:
        output_path: Path where PDF should be created.
        
    Returns:
        Path to created PDF file.
    """
    # Create minimal PDF (actual table extraction requires real PDF structure)
    return create_sample_pdf(output_path, title="Document with Tables")


def create_pdf_with_metadata(output_path: Path, metadata: dict = None) -> Path:
    """
    Create a PDF with metadata.
    
    Args:
        output_path: Path where PDF should be created.
        metadata: Dictionary with metadata keys (title, author, subject, etc.).
        
    Returns:
        Path to created PDF file.
    """
    if metadata is None:
        metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "subject": "Test Subject",
        }
    
    return create_sample_pdf(
        output_path,
        title=metadata.get("title", "Test Document"),
        author=metadata.get("author", "Test Author")
    )


def mock_llm_response(provider: str = "openai", summary: str = "Mocked summary", tokens: int = 100):
    """
    Create a mock LLM API response.
    
    Args:
        provider: LLM provider ("openai", "anthropic", "ollama").
        summary: Summary text to return.
        tokens: Number of tokens used.
        
    Returns:
        Mock response object.
    """
    if provider == "openai":
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = summary
        mock_response.usage.total_tokens = tokens
        return mock_response
    elif provider == "anthropic":
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = summary
        mock_response.usage.input_tokens = tokens // 2
        mock_response.usage.output_tokens = tokens // 2
        return mock_response
    elif provider == "ollama":
        return {
            "message": {"content": summary},
            "prompt_eval_count": tokens // 2,
            "eval_count": tokens // 2,
        }
    return None


def mock_crossref_response(doi: str = "10.1234/test.12345"):
    """
    Create a mock CrossRef API response.
    
    Args:
        doi: DOI identifier.
        
    Returns:
        Mock response dictionary.
    """
    return {
        "message": {
            "title": ["Test Paper Title"],
            "author": [
                {"given": "John", "family": "Doe"},
                {"given": "Jane", "family": "Smith"}
            ],
            "published-print": {"date-parts": [[2024, 1, 1]]},
            "container-title": ["Test Journal"]
        }
    }


def create_rpg_text_sample() -> str:
    """Create a sample RPG text for testing."""
    return """
    Inquisitor Lord Kryptman of the Ordo Xenos has discovered a Tyranid Hive Fleet
    approaching the Segmentum Ultima. The Adeptus Astartes Chapter known as the
    Ultramarines must prepare for war. The planet Macragge stands as the first
    line of defense against the alien menace.
    
    Captain Titus of the Ultramarines carries a Power Sword and Plasma Pistol.
    The Imperium of Man faces threats from multiple factions: Chaos Space Marines,
    Orks, Eldar, and now the Tyranids.
    """


def create_academic_text_sample() -> str:
    """Create a sample academic text with citations for testing."""
    return """
    This paper discusses the impact of technology on society (DOI: 10.1234/example.12345).
    For more information, see ISBN-13: 978-0-123456-78-9.
    Additional resources available at https://example.com/research.pdf.
    """
