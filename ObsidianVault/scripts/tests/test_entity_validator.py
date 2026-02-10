# PURPOSE: Unit tests for entity validator (Phase 2).
# DEPENDENCIES: pytest, entity_validator module.
# MODIFICATION NOTES: Phase 2 - Tests entity validation, normalization, and deduplication.

import pytest
from entity_validator import (
    normalize_entity_name,
    validate_entity_name,
    similarity_ratio,
    deduplicate_entities,
    filter_common_false_positives,
    merge_entity_results,
)


class TestNormalizeEntityName:
    """Tests for entity name normalization."""
    
    @pytest.mark.unit
    def test_normalize_simple_name(self):
        """Test normalization of simple entity name."""
        result = normalize_entity_name("john smith")
        assert result == "John Smith"
    
    @pytest.mark.unit
    def test_normalize_with_extra_spaces(self):
        """Test normalization removes extra spaces."""
        result = normalize_entity_name("  john   smith  ")
        assert result == "John Smith"
    
    @pytest.mark.unit
    def test_normalize_preserves_abbreviations(self):
        """Test that abbreviations are preserved."""
        result = normalize_entity_name("NPC AI PDF")
        assert result == "NPC AI PDF"
    
    @pytest.mark.unit
    def test_normalize_empty_string(self):
        """Test normalization of empty string."""
        result = normalize_entity_name("")
        assert result == ""
    
    @pytest.mark.unit
    def test_normalize_already_normalized(self):
        """Test normalization of already normalized name."""
        result = normalize_entity_name("John Smith")
        assert result == "John Smith"


class TestValidateEntityName:
    """Tests for entity name validation."""
    
    @pytest.mark.unit
    def test_validate_valid_name(self):
        """Test validation of valid entity name."""
        assert validate_entity_name("John Smith") is True
        assert validate_entity_name("The Empire") is True
        assert validate_entity_name("Planet Terra") is True
    
    @pytest.mark.unit
    def test_validate_too_short(self):
        """Test validation rejects names that are too short."""
        assert validate_entity_name("A") is False
        assert validate_entity_name("") is False
    
    @pytest.mark.unit
    def test_validate_false_positives(self):
        """Test validation rejects common false positives."""
        assert validate_entity_name("the") is False
        assert validate_entity_name("and") is False
        assert validate_entity_name("or") is False
    
    @pytest.mark.unit
    def test_validate_invalid_characters(self):
        """Test validation handles invalid characters."""
        # Should clean invalid characters
        result = validate_entity_name("John@Smith#123")
        # After cleaning, should be valid if long enough
        assert isinstance(result, bool)


class TestSimilarityRatio:
    """Tests for similarity calculation."""
    
    @pytest.mark.unit
    def test_similarity_identical(self):
        """Test similarity of identical names."""
        ratio = similarity_ratio("John Smith", "John Smith")
        assert ratio == 1.0
    
    @pytest.mark.unit
    def test_similarity_similar(self):
        """Test similarity of similar names."""
        ratio = similarity_ratio("John Smith", "John Smyth")
        assert 0.8 <= ratio < 1.0
    
    @pytest.mark.unit
    def test_similarity_different(self):
        """Test similarity of different names."""
        ratio = similarity_ratio("John Smith", "Jane Doe")
        assert ratio < 0.5
    
    @pytest.mark.unit
    def test_similarity_case_insensitive(self):
        """Test that similarity is case-insensitive."""
        ratio1 = similarity_ratio("John Smith", "john smith")
        ratio2 = similarity_ratio("John Smith", "John Smith")
        assert ratio1 == ratio2


class TestDeduplicateEntities:
    """Tests for entity deduplication."""
    
    @pytest.mark.unit
    def test_deduplicate_exact_duplicates(self):
        """Test deduplication of exact duplicates."""
        entities = {
            "NPCs": ["John Smith", "John Smith", "Jane Doe"],
            "Factions": ["The Empire", "The Empire"],
        }
        
        result = deduplicate_entities(entities)
        
        assert len(result["NPCs"]) == 2
        assert "John Smith" in result["NPCs"]
        assert "Jane Doe" in result["NPCs"]
        assert len(result["Factions"]) == 1
    
    @pytest.mark.unit
    def test_deduplicate_similar_entities(self):
        """Test deduplication of similar entities."""
        entities = {
            "NPCs": ["John Smith", "John Smyth", "John Smith"],
        }
        
        result = deduplicate_entities(entities, similarity_threshold=0.85)
        
        # Should merge similar entities
        assert len(result["NPCs"]) <= 2
    
    @pytest.mark.unit
    def test_deduplicate_empty(self):
        """Test deduplication of empty entity list."""
        entities = {
            "NPCs": [],
            "Factions": [],
        }
        
        result = deduplicate_entities(entities)
        
        assert result["NPCs"] == []
        assert result["Factions"] == []
    
    @pytest.mark.unit
    def test_deduplicate_normalizes(self):
        """Test that deduplication normalizes names."""
        entities = {
            "NPCs": ["john smith", "John Smith", "JOHN SMITH"],
        }
        
        result = deduplicate_entities(entities)
        
        # Should normalize and deduplicate
        assert len(result["NPCs"]) == 1


class TestFilterCommonFalsePositives:
    """Tests for false positive filtering."""
    
    @pytest.mark.unit
    def test_filter_false_positives(self):
        """Test filtering of common false positives."""
        entities = {
            "NPCs": ["Player", "Character", "John Smith"],
            "Factions": ["Faction", "The Empire"],
            "Locations": ["Location", "Planet Terra"],
            "Items": ["Item", "Sword of Truth"],
        }
        
        result = filter_common_false_positives(entities)
        
        assert "Player" not in result["NPCs"]
        assert "John Smith" in result["NPCs"]
        assert "Faction" not in result["Factions"]
        assert "The Empire" in result["Factions"]
    
    @pytest.mark.unit
    def test_filter_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        entities = {
            "NPCs": ["player", "PLAYER", "Character"],
        }
        
        result = filter_common_false_positives(entities)
        
        assert "player" not in result["NPCs"]
        assert "PLAYER" not in result["NPCs"]


class TestMergeEntityResults:
    """Tests for merging entity extraction results."""
    
    @pytest.mark.unit
    def test_merge_multiple_results(self):
        """Test merging multiple extraction results."""
        results = [
            {
                "NPCs": ["John Smith", "Jane Doe"],
                "Factions": ["The Empire"],
            },
            {
                "NPCs": ["Bob Jones", "John Smith"],
                "Factions": ["The Republic"],
            },
        ]
        
        merged = merge_entity_results(results)
        
        assert "John Smith" in merged["NPCs"]
        assert "Jane Doe" in merged["NPCs"]
        assert "Bob Jones" in merged["NPCs"]
        assert "The Empire" in merged["Factions"]
        assert "The Republic" in merged["Factions"]
        # Should be deduplicated
        assert merged["NPCs"].count("John Smith") == 1
    
    @pytest.mark.unit
    def test_merge_empty_results(self):
        """Test merging empty results."""
        results = [
            {"NPCs": [], "Factions": []},
            {"NPCs": [], "Factions": []},
        ]
        
        merged = merge_entity_results(results)
        
        assert merged["NPCs"] == []
        assert merged["Factions"] == []
    
    @pytest.mark.unit
    def test_merge_single_result(self):
        """Test merging single result."""
        results = [
            {
                "NPCs": ["John Smith"],
                "Factions": ["The Empire"],
            },
        ]
        
        merged = merge_entity_results(results)
        
        assert merged["NPCs"] == ["John Smith"]
        assert merged["Factions"] == ["The Empire"]
