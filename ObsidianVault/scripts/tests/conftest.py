# PURPOSE: Pytest configuration and shared fixtures (Phase 1 & 2).
# DEPENDENCIES: pytest, pathlib.
# MODIFICATION NOTES: Phase 1 & 2 - Enhanced with fixtures for OCR, API, LLM, tables, metadata.

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

import pytest


@pytest.fixture
def tmp_path():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
    return pdf_path


@pytest.fixture
def scanned_pdf_path(tmp_path):
    """Create a scanned PDF file for testing (mock)."""
    pdf_path = tmp_path / "scanned.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
    return pdf_path


@pytest.fixture
def pdf_with_tables(tmp_path):
    """Create a PDF with tables for testing (mock)."""
    pdf_path = tmp_path / "with_tables.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
    return pdf_path


@pytest.fixture
def pdf_with_metadata(tmp_path):
    """Create a PDF with metadata for testing (mock)."""
    pdf_path = tmp_path / "with_metadata.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Title (Test Document)\n/Author (Test Author)\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
    return pdf_path


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a sample text document for testing purposes. It contains multiple sentences and paragraphs."


@pytest.fixture
def rpg_text():
    """RPG-specific text sample for testing."""
    return """
    Inquisitor Lord Kryptman of the Ordo Xenos has discovered a Tyranid Hive Fleet
    approaching the Segmentum Ultima. The Adeptus Astartes Chapter known as the
    Ultramarines must prepare for war. The planet Macragge stands as the first
    line of defense against the alien menace.
    
    The Imperium of Man faces threats from multiple factions: Chaos Space Marines,
    Orks, Eldar, and now the Tyranids. Each faction poses unique challenges to
    the Emperor's forces.
    """


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked OpenAI summary"
    mock_response.usage.total_tokens = 100
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Mocked Anthropic summary"
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 50
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    def mock_chat(*args, **kwargs):
        return {
            "message": {"content": "Mocked Ollama summary"},
            "prompt_eval_count": 25,
            "eval_count": 25
        }
    return mock_chat


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Temporary cache directory for testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def test_config(tmp_path):
    """Test configuration dictionary."""
    return {
        "vault_root": str(tmp_path),
        "pdf_root": str(tmp_path / "pdfs"),
        "source_notes_dir": "Sources",
        "features": {
            "ocr_enabled": True,
            "ai_summarization_enabled": True,
            "table_extraction_enabled": True,
            "web_api_enabled": True,
        },
        "ocr": {
            "enabled": True,
            "tesseract_path": None,
            "language": "eng",
            "dpi": 300,
        },
        "ai_summarization": {
            "enabled": True,
            "provider": "openai",
            "model": "gpt-4",
            "api_key": None,
            "max_tokens": 500,
            "temperature": 0.7,
            "cache_dir": "Sources/_summaries",
        },
        "table_extraction": {
            "enabled": True,
            "method": "pdfplumber",
            "fallback_method": "camelot",
        },
        "web_api": {
            "enabled": True,
            "host": "127.0.0.1",
            "port": 8000,
            "auth_enabled": False,
        },
        "entity_extraction": {
            "use_llm": False,
            "llm_provider": "openai",
            "llm_model": "gpt-4",
        },
    }


@pytest.fixture
def test_config_file(tmp_path, test_config):
    """Test configuration file."""
    config_file = tmp_path / "test_config.json"
    config_file.write_text(json.dumps(test_config, indent=2), encoding="utf-8")
    return config_file
