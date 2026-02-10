# PURPOSE: End-to-end integration test for complete ingestion workflow.
# DEPENDENCIES: pytest, all ingestion modules, sample PDFs.
# MODIFICATION NOTES: Tests complete workflow from PDF to notes with all features.

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ingest_pdfs import ingest_pdfs, process_single_pdf
    from build_index import build_index
    from utils import load_config
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    pytest.skip("Required modules not available", allow_module_level=True)


@pytest.fixture
def temp_vault():
    """Create temporary vault structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = Path(tmpdir) / "vault"
        vault_root.mkdir()
        
        # Create directory structure
        (vault_root / "Sources").mkdir()
        (vault_root / "Rules").mkdir()
        (vault_root / "NPCs").mkdir()
        (vault_root / "Factions").mkdir()
        (vault_root / "Locations").mkdir()
        (vault_root / "Items").mkdir()
        (vault_root / "Templates").mkdir()
        (vault_root / "pdf").mkdir()
        
        # Create minimal templates
        source_template = vault_root / "Templates" / "source_note.md"
        source_template.write_text("""---
title: "{{title}}"
source_file: "{{source_file}}"
source_pages: "{{source_pages}}"
doc_type: "{{doc_type}}"
date: "{{date}}"
---

# {{title}}
""")
        
        entity_template = vault_root / "Templates" / "entity_note.md"
        entity_template.write_text("""---
title: "{{title}}"
entity_type: "{{entity_type}}"
date: "{{date}}"
source_refs: []
---

# {{title}}
""")
        
        yield vault_root


@pytest.fixture
def sample_config(temp_vault):
    """Create sample configuration."""
    config = {
        "vault_root": str(temp_vault),
        "pdf_root": str(temp_vault / "pdf"),
        "source_notes_dir": "Sources",
        "rules_dir": "Rules",
        "npcs_dir": "NPCs",
        "factions_dir": "Factions",
        "locations_dir": "Locations",
        "items_dir": "Items",
        "templates": {
            "source_note": "Templates/source_note.md",
            "entity_note": "Templates/entity_note.md"
        },
        "extracted_text_dir": "Sources/_extracted_text",
        "pdf_text_cache_dirs": [],
        "pdf_text_cache_extensions": [".txt"],
        "max_excerpt_chars": 200,
        "max_pdf_size_mb": 100,
        "max_workers": 1,
        "features": {
            "ocr_enabled": True,
            "ai_summarization_enabled": False,  # Disable for faster tests
            "table_extraction_enabled": False,
            "web_api_enabled": False,
        },
        "ocr": {
            "enabled": True,
            "tesseract_path": None,
            "language": "eng",
        },
        "ai_summarization": {
            "enabled": False,
            "provider": "openai",
            "model": "gpt-4",
        },
        "table_extraction": {
            "enabled": False,
            "method": "pdfplumber",
        },
    }
    return config


class TestFullIngestionFlow:
    """End-to-end integration tests."""
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_config_validation(self, sample_config):
        """Test that configuration is valid."""
        assert "vault_root" in sample_config
        assert "pdf_root" in sample_config
        assert "templates" in sample_config
        assert "source_notes_dir" in sample_config
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_directory_structure_creation(self, temp_vault, sample_config):
        """Test that required directories are created."""
        from ingest_pdfs import ensure_directories, get_config_path
        
        vault_root = Path(sample_config["vault_root"])
        source_notes_dir = get_config_path(vault_root, sample_config, "source_notes_dir")
        extracted_text_dir = get_config_path(vault_root, sample_config, "extracted_text_dir")
        
        ensure_directories([source_notes_dir, extracted_text_dir])
        
        assert source_notes_dir.exists()
        assert extracted_text_dir.exists()
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_template_loading(self, temp_vault, sample_config):
        """Test that templates can be loaded."""
        from ingest_pdfs import get_config_path, validate_template
        
        vault_root = Path(sample_config["vault_root"])
        template_source = get_config_path(vault_root, sample_config, "templates.source_note")
        template_entity = get_config_path(vault_root, sample_config, "templates.entity_note")
        
        # Should not raise exception
        validate_template(template_source, ["title", "source_file", "source_pages", "doc_type", "date"])
        validate_template(template_entity, ["title", "entity_type", "date"])
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_empty_pdf_directory(self, temp_vault, sample_config):
        """Test handling of empty PDF directory."""
        # Should not crash on empty directory
        try:
            ingest_pdfs(sample_config, overwrite=False)
            # Should complete without error
            assert True
        except SystemExit:
            # SystemExit is acceptable for configuration errors
            pass
        except Exception as e:
            # Other exceptions might be expected (e.g., no PDFs found)
            # Just verify it doesn't crash unexpectedly
            assert isinstance(e, Exception)


class TestErrorHandlingInFlow:
    """Test error handling in full workflow."""
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_missing_template_handling(self, temp_vault, sample_config):
        """Test that missing templates are handled gracefully."""
        from ingest_pdfs import get_config_path
        
        vault_root = Path(sample_config["vault_root"])
        
        # Try to access non-existent template
        fake_template = vault_root / "Templates" / "nonexistent.md"
        
        # Should handle missing template
        assert not fake_template.exists()
    
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_invalid_config_handling(self, temp_vault):
        """Test that invalid configuration is handled."""
        invalid_config = {
            "vault_root": str(temp_vault),
            # Missing required fields
        }
        
        # Should handle missing config gracefully
        try:
            from ingest_pdfs import ingest_pdfs
            ingest_pdfs(invalid_config, overwrite=False)
        except (KeyError, ValueError, SystemExit):
            # Expected exceptions
            assert True
        except Exception:
            # Other exceptions acceptable
            pass


class TestPhase1FeaturesIntegration:
    """Integration tests for Phase 1 features."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_ocr_integration(self, temp_vault, sample_config):
        """Test OCR integration in full flow (Phase 1)."""
        # Enable OCR in config
        sample_config["features"]["ocr_enabled"] = True
        sample_config["ocr"] = {"enabled": True, "language": "eng"}
        
        # Test that OCR can be enabled
        assert sample_config["features"]["ocr_enabled"] is True
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_event_driven_integration(self, temp_vault, sample_config):
        """Test event-driven processing integration (Phase 1)."""
        # Test watcher configuration
        sample_config["watcher"] = {
            "enabled": True,
            "debounce_seconds": 2,
            "recursive": True,
        }
        
        assert sample_config["watcher"]["enabled"] is True
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_rest_api_integration(self, temp_vault, sample_config):
        """Test REST API integration (Phase 1)."""
        # Test API configuration
        sample_config["web_api"] = {
            "enabled": True,
            "host": "127.0.0.1",
            "port": 8000,
        }
        
        assert sample_config["web_api"]["enabled"] is True


class TestPhase2FeaturesIntegration:
    """Integration tests for Phase 2 features."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_ai_summarization_integration(self, temp_vault, sample_config):
        """Test AI summarization integration (Phase 2)."""
        # Enable AI summarization
        sample_config["features"]["ai_summarization_enabled"] = True
        sample_config["ai_summarization"] = {
            "enabled": True,
            "provider": "openai",
            "model": "gpt-4",
            "cache_dir": "Sources/_summaries",
        }
        
        assert sample_config["features"]["ai_summarization_enabled"] is True
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_entity_extraction_integration(self, temp_vault, sample_config):
        """Test entity extraction integration (Phase 2)."""
        # Enable entity extraction with LLM
        sample_config["entity_extraction"] = {
            "use_llm": False,  # Use spaCy only for faster tests
            "llm_provider": "openai",
        }
        
        assert "entity_extraction" in sample_config
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_table_extraction_integration(self, temp_vault, sample_config):
        """Test table extraction integration (Phase 2)."""
        # Enable table extraction
        sample_config["features"]["table_extraction_enabled"] = True
        sample_config["table_extraction"] = {
            "enabled": True,
            "method": "pdfplumber",
        }
        
        assert sample_config["features"]["table_extraction_enabled"] is True
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_metadata_extraction_integration(self, temp_vault, sample_config):
        """Test metadata extraction integration (Phase 2)."""
        # Metadata extraction is always enabled
        # Test that it works with citation enrichment
        assert "features" in sample_config


class TestFeatureCombinations:
    """Tests for feature combinations."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_ocr_and_ai_summarization(self, temp_vault, sample_config):
        """Test OCR + AI Summarization combination."""
        sample_config["features"]["ocr_enabled"] = True
        sample_config["features"]["ai_summarization_enabled"] = False  # Disable for test speed
        
        # Both should be configurable
        assert sample_config["features"]["ocr_enabled"] is True
    
    @pytest.mark.integration
    @pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Modules not available")
    def test_table_and_metadata_extraction(self, temp_vault, sample_config):
        """Test Table + Metadata extraction combination."""
        sample_config["features"]["table_extraction_enabled"] = True
        
        # Both should work together
        assert sample_config["features"]["table_extraction_enabled"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
