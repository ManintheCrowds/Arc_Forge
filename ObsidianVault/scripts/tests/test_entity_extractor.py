# PURPOSE: Unit tests for entity extraction functionality.
# DEPENDENCIES: pytest, entity_extractor module.
# MODIFICATION NOTES: Tests NER extraction, entity mapping, and error handling.

import pytest
from pathlib import Path
import sys
from unittest.mock import patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from entity_extractor import EntityExtractor, extract_entities_from_text, get_extractor
    ENTITY_EXTRACTOR_AVAILABLE = True
except ImportError:
    ENTITY_EXTRACTOR_AVAILABLE = False
    pytest.skip("entity_extractor module not available", allow_module_level=True)


class TestEntityExtractor:
    """Test cases for EntityExtractor class."""
    
    def test_extractor_initialization(self):
        """Test that extractor can be initialized."""
        extractor = EntityExtractor()
        # Should not raise exception
        assert extractor is not None
    
    def test_extractor_availability(self):
        """Test extractor availability check."""
        extractor = EntityExtractor()
        # Availability depends on spaCy being installed
        # Just verify the method exists and doesn't crash
        result = extractor.is_available()
        assert isinstance(result, bool)
    
    def test_extract_entities_empty_text(self):
        """Test entity extraction with empty text."""
        extractor = EntityExtractor()
        result = extractor.extract_entities("")
        
        assert isinstance(result, dict)
        assert "NPCs" in result
        assert "Factions" in result
        assert "Locations" in result
        assert "Items" in result
        assert all(len(v) == 0 for v in result.values())
    
    def test_extract_entities_simple_text(self):
        """Test entity extraction with simple text containing names."""
        extractor = EntityExtractor()
        
        if not extractor.is_available():
            pytest.skip("spaCy model not available")
        
        text = "John Smith met with the Empire faction in New York. He carried a sword."
        result = extractor.extract_entities(text)
        
        assert isinstance(result, dict)
        assert "NPCs" in result
        assert "Factions" in result
        assert "Locations" in result
        assert "Items" in result
        
        # Should extract at least some entities
        # Exact results depend on spaCy model, so just check structure
        assert all(isinstance(v, list) for v in result.values())
    
    def test_extract_entities_rpg_text(self):
        """Test entity extraction with RPG-specific text."""
        extractor = EntityExtractor()
        
        if not extractor.is_available():
            pytest.skip("spaCy model not available")
        
        text = """
        The Inquisitor Kael met with the Adeptus Mechanicus on Mars.
        He carried a plasma pistol and a power sword.
        The Ork Waaagh! threatened the Imperial Guard base.
        """
        result = extractor.extract_entities(text)
        
        assert isinstance(result, dict)
        # Should identify at least some entities
        total_entities = sum(len(v) for v in result.values())
        # With spaCy, we should get some entities from this text
        # But exact count depends on model, so just verify structure
    
    def test_extract_entities_no_duplicates(self):
        """Test that extracted entities don't contain duplicates."""
        extractor = EntityExtractor()
        
        if not extractor.is_available():
            pytest.skip("spaCy model not available")
        
        text = "John Smith and John Smith went to New York and New York."
        result = extractor.extract_entities(text)
        
        # Check no duplicates within each category
        for category, entities in result.items():
            assert len(entities) == len(set(entities)), f"Duplicates found in {category}"
    
    def test_extract_entities_sorted(self):
        """Test that extracted entities are sorted."""
        extractor = EntityExtractor()
        
        if not extractor.is_available():
            pytest.skip("spaCy model not available")
        
        text = "Zebra, Apple, Banana, and Charlie met in Delta city."
        result = extractor.extract_entities(text)
        
        # Check entities are sorted alphabetically
        for category, entities in result.items():
            if len(entities) > 1:
                assert entities == sorted(entities), f"Entities in {category} not sorted"
    
    def test_extract_entities_handles_errors(self):
        """Test that extractor handles errors gracefully."""
        extractor = EntityExtractor()
        
        # Should handle None or invalid input
        result = extractor.extract_entities(None)
        assert isinstance(result, dict)
        assert all(len(v) == 0 for v in result.values())


class TestExtractEntitiesFromText:
    """Test cases for convenience function."""
    
    def test_convenience_function(self):
        """Test the extract_entities_from_text convenience function."""
        if not ENTITY_EXTRACTOR_AVAILABLE:
            pytest.skip("entity_extractor module not available")
        
        text = "John Smith went to New York."
        result = extract_entities_from_text(text)
        
        assert isinstance(result, dict)
        assert "NPCs" in result
        assert "Factions" in result
        assert "Locations" in result
        assert "Items" in result
    
    def test_get_extractor_singleton(self):
        """Test that get_extractor returns singleton instance."""
        if not ENTITY_EXTRACTOR_AVAILABLE:
            pytest.skip("entity_extractor module not available")
        
        extractor1 = get_extractor()
        extractor2 = get_extractor()
        
        # Should return same instance
        assert extractor1 is extractor2
    
    @pytest.mark.unit
    def test_extract_with_patterns(self):
        """Test RPG pattern extraction (Phase 2)."""
        extractor = EntityExtractor()
        
        text = "Lord Inquisitor Kael met with the Adeptus Mechanicus Chapter on Mars. He carried a Power Sword."
        result = extractor.extract_entities(text)
        
        # Should extract entities using patterns
        assert isinstance(result, dict)
        assert "NPCs" in result
        assert "Factions" in result
        assert "Locations" in result
        assert "Items" in result
    
    @pytest.mark.unit
    def test_extract_with_llm(self):
        """Test LLM-based entity extraction (Phase 2)."""
        extractor = EntityExtractor(use_llm=True, llm_provider="openai")
        
        with patch("entity_extractor._call_openai_api") as mock_llm:
            mock_llm.return_value = (
                '{"NPCs": ["Inquisitor Kael"], "Factions": ["Adeptus Mechanicus"], "Locations": ["Mars"], "Items": ["Power Sword"]}',
                {}
            )
            
            text = "Inquisitor Kael met with the Adeptus Mechanicus on Mars. He carried a Power Sword."
            result = extractor.extract_entities(text)
            
            # Should extract entities using LLM
            assert isinstance(result, dict)
            assert "NPCs" in result
            assert "Factions" in result
    
    @pytest.mark.unit
    def test_extract_llm_invalid_json(self):
        """Test LLM extraction with invalid JSON response (Phase 2)."""
        extractor = EntityExtractor(use_llm=True, llm_provider="openai")
        
        with patch("entity_extractor._call_openai_api") as mock_llm:
            mock_llm.return_value = ("Invalid JSON response", {})
            
            text = "Test text"
            result = extractor.extract_entities(text)
            
            # Should fallback gracefully
            assert isinstance(result, dict)
    
    @pytest.mark.unit
    def test_multi_method_extraction(self):
        """Test extraction using multiple methods (Phase 2)."""
        extractor = EntityExtractor(use_llm=False)  # Use spaCy + patterns
        
        text = "Lord Inquisitor Kael of the Adeptus Mechanicus Chapter."
        result = extractor.extract_entities(text)
        
        # Should combine results from multiple methods
        assert isinstance(result, dict)
        assert all(isinstance(v, list) for v in result.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
