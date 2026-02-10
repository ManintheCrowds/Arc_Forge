# PURPOSE: Entity validation and deduplication (Phase 2).
# DEPENDENCIES: None (pure Python).
# MODIFICATION NOTES: Phase 2 - Entity validation, normalization, and deduplication.

from __future__ import annotations

import logging
import re
from typing import Dict, List, Set
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def normalize_entity_name(name: str) -> str:
    """
    Normalize entity name (capitalization, spacing, etc.).
    
    Args:
        name: Entity name to normalize.
        
    Returns:
        Normalized entity name.
    """
    if not name:
        return ""
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    
    # Capitalize first letter of each word (title case)
    # But preserve common RPG abbreviations
    words = name.split()
    normalized_words = []
    for word in words:
        # Preserve all-caps abbreviations (e.g., "PDF", "NPC", "AI")
        if word.isupper() and len(word) <= 5:
            normalized_words.append(word)
        else:
            normalized_words.append(word.capitalize())
    
    return " ".join(normalized_words)


def validate_entity_name(name: str) -> bool:
    """
    Validate entity name (remove invalid characters, check length).
    
    Args:
        name: Entity name to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if not name or len(name.strip()) < 2:
        return False
    
    # Remove invalid characters (keep alphanumeric, spaces, hyphens, apostrophes)
    cleaned = re.sub(r'[^a-zA-Z0-9\s\-\']', '', name)
    
    # Check if name is too short after cleaning
    if len(cleaned.strip()) < 2:
        return False
    
    # Check for common false positives
    false_positives = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "can", "this",
        "that", "these", "those", "it", "its", "they", "them", "their",
    }
    
    if name.lower().strip() in false_positives:
        return False
    
    return True


def similarity_ratio(name1: str, name2: str) -> float:
    """
    Calculate similarity ratio between two entity names.
    
    Args:
        name1: First entity name.
        name2: Second entity name.
        
    Returns:
        Similarity ratio (0.0 to 1.0).
    """
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def deduplicate_entities(entities: Dict[str, List[str]], similarity_threshold: float = 0.85) -> Dict[str, List[str]]:
    """
    Deduplicate entities by removing similar/duplicate names.
    
    Args:
        entities: Dictionary of entities by category.
        similarity_threshold: Minimum similarity to consider duplicates (default: 0.85).
        
    Returns:
        Deduplicated entities dictionary.
    """
    deduplicated = {}
    
    for category, entity_list in entities.items():
        if not entity_list:
            deduplicated[category] = []
            continue
        
        # Normalize and validate entities
        normalized_entities = []
        for entity in entity_list:
            if validate_entity_name(entity):
                normalized = normalize_entity_name(entity)
                if normalized:
                    normalized_entities.append(normalized)
        
        # Remove exact duplicates
        unique_entities = list(dict.fromkeys(normalized_entities))  # Preserves order
        
        # For very large entity lists, skip expensive fuzzy matching
        # Fuzzy matching is O(n²) and becomes prohibitively slow with thousands of entities
        MAX_ENTITIES_FOR_FUZZY = 500
        if len(unique_entities) > MAX_ENTITIES_FOR_FUZZY:
            logger.warning(
                f"Skipping fuzzy deduplication for {category} ({len(unique_entities)} entities). "
                f"Using exact deduplication only. Consider filtering entities before extraction."
            )
            deduplicated[category] = sorted(unique_entities)
            continue
        
        # Remove similar entities (fuzzy matching) - only for smaller lists
        final_entities = []
        seen = set()
        
        for entity in unique_entities:
            entity_lower = entity.lower()
            
            # Check if similar to any already seen entity
            is_duplicate = False
            for seen_entity in seen:
                if similarity_ratio(entity_lower, seen_entity) >= similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Merging similar entities: '{entity}' -> '{seen_entity}'")
                    break
            
            if not is_duplicate:
                final_entities.append(entity)
                seen.add(entity_lower)
        
        deduplicated[category] = sorted(final_entities)
    
    return deduplicated


def filter_common_false_positives(entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Filter out common false positive entities.
    
    Args:
        entities: Dictionary of entities by category.
        
    Returns:
        Filtered entities dictionary.
    """
    # Common false positives for RPG documents
    false_positives = {
        "NPCs": {"Player", "Character", "PC", "NPC", "GM", "DM"},
        "Factions": {"Faction", "Group", "Organization", "Alliance"},
        "Locations": {"Location", "Place", "Area", "Region", "Zone"},
        "Items": {"Item", "Object", "Thing", "Equipment", "Gear"},
    }
    
    filtered = {}
    for category, entity_list in entities.items():
        fp_set = false_positives.get(category, set())
        filtered[category] = [
            entity for entity in entity_list
            if entity not in fp_set and entity.lower() not in {fp.lower() for fp in fp_set}
        ]
    
    return filtered


def merge_entity_results(results: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """
    Merge multiple entity extraction results.
    
    Args:
        results: List of entity dictionaries to merge.
        
    Returns:
        Merged entities dictionary.
    """
    merged = {
        "NPCs": [],
        "Factions": [],
        "Locations": [],
        "Items": [],
    }
    
    for result in results:
        for category in merged:
            merged[category].extend(result.get(category, []))
    
    # Deduplicate merged results
    merged = deduplicate_entities(merged)
    merged = filter_common_false_positives(merged)
    
    return merged
