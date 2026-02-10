# PURPOSE: Automatic entity extraction using spaCy NER and LLM (Phase 2).
# DEPENDENCIES: spaCy library, language model, optional LLM APIs.
# MODIFICATION NOTES: Phase 2 - Enhanced with LLM extraction, RPG patterns, and validation.

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import LLM dependencies for enhanced extraction
try:
    from ai_summarizer import _call_openai_api, _call_anthropic_api, _call_ollama_api
    LLM_EXTRACTION_AVAILABLE = True
except ImportError:
    LLM_EXTRACTION_AVAILABLE = False
    logger.debug("LLM extraction not available (ai_summarizer not found)")

# Try to import entity validator
try:
    from entity_validator import deduplicate_entities, filter_common_false_positives, merge_entity_results
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    logger.debug("Entity validation not available")

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")


# PURPOSE: Extract entities from text using spaCy NER.
# DEPENDENCIES: spaCy model loaded.
# MODIFICATION NOTES: Maps NER entity types to RPG entity categories.
class EntityExtractor:
    def __init__(
        self, 
        model_name: str = "en_core_web_sm",
        use_llm: bool = False,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        llm_api_key: Optional[str] = None,
    ):
        """
        Initialize entity extractor with spaCy model and optional LLM.
        
        Args:
            model_name: Name of spaCy model to load (default: en_core_web_sm).
            use_llm: Whether to use LLM for enhanced extraction (default: False).
            llm_provider: LLM provider if use_llm is True (default: "openai").
            llm_model: LLM model name (default: "gpt-4").
            llm_api_key: Optional API key for LLM.
        """
        self.model_name = model_name
        self.nlp: Optional[object] = None
        self.use_llm = use_llm and LLM_EXTRACTION_AVAILABLE
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_key = llm_api_key
        self._load_model()
        
        # RPG-specific patterns
        self.rpg_patterns = self._init_rpg_patterns()
    
    def _load_model(self) -> None:
        """Load spaCy model."""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available, entity extraction disabled")
            return
        
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.error(
                f"spaCy model '{self.model_name}' not found. "
                f"Install with: python -m spacy download {self.model_name}"
            )
            self.nlp = None
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
    
    def _init_rpg_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize RPG-specific regex patterns for entity detection."""
        patterns = {
            "NPCs": [
                re.compile(r'\b(?:Lord|Lady|Captain|Commander|Inquisitor|Magos|Tech-Priest|Adept)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.IGNORECASE),
                re.compile(r'\b([A-Z][a-z]+\s+(?:the\s+)?(?:Elder|Ancient|Wise|Great))\b', re.IGNORECASE),
            ],
            "Factions": [
                re.compile(r'\b(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Chapter|Legion|Order|Brotherhood|Cult|Covenant))\b', re.IGNORECASE),
                re.compile(r'\b(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Empire|Imperium|Alliance|Confederation))\b', re.IGNORECASE),
            ],
            "Locations": [
                re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Planet|World|System|Sector|Station|Base|Fortress|Citadel))\b', re.IGNORECASE),
                re.compile(r'\b(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Realm|Domain|Territory))\b', re.IGNORECASE),
            ],
            "Items": [
                re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Blade|Sword|Axe|Hammer|Staff|Rod|Relic|Artifact))\b', re.IGNORECASE),
                re.compile(r'\b(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Armor|Armour|Shield|Helm|Gauntlet))\b', re.IGNORECASE),
            ],
        }
        return patterns
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using spaCy and optionally LLM.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            Dictionary mapping entity types to lists of entity names.
        """
        if not text:
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
        
        results = []
        
        # Extract using spaCy
        spacy_entities = self._extract_with_spacy(text)
        if spacy_entities:
            results.append(spacy_entities)
        
        # Extract using RPG patterns
        pattern_entities = self._extract_with_patterns(text)
        if pattern_entities:
            results.append(pattern_entities)
        
        # Extract using LLM if enabled
        if self.use_llm:
            llm_entities = self._extract_with_llm(text)
            if llm_entities:
                results.append(llm_entities)
        
        # Merge all results
        if results:
            merged = merge_entity_results(results) if VALIDATION_AVAILABLE else self._merge_results(results)
        else:
            merged = {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
        
        # Validate and deduplicate if validator available
        if VALIDATION_AVAILABLE:
            merged = deduplicate_entities(merged)
            merged = filter_common_false_positives(merged)
        
        logger.debug(
            f"Extracted entities: {sum(len(v) for v in merged.values())} total "
            f"({len(merged['NPCs'])} NPCs, {len(merged['Factions'])} Factions, "
            f"{len(merged['Locations'])} Locations, {len(merged['Items'])} Items)"
        )
        
        return merged
    
    def _extract_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy NER."""
        if not self.nlp:
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
        
        try:
            doc = self.nlp(text)
            
            entities = {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
            
            seen_entities = set()
            
            for ent in doc.ents:
                entity_text = ent.text.strip()
                
                if not entity_text or entity_text in seen_entities or len(entity_text) < 2:
                    continue
                
                seen_entities.add(entity_text)
                
                # Map entity types with improved heuristics
                if ent.label_ == "PERSON":
                    entities["NPCs"].append(entity_text)
                elif ent.label_ == "ORG":
                    # Organizations are usually factions
                    entities["Factions"].append(entity_text)
                elif ent.label_ == "GPE":
                    # Geopolitical entities are usually locations
                    entities["Locations"].append(entity_text)
                elif ent.label_ in ["PRODUCT", "EVENT"]:
                    entities["Items"].append(entity_text)
            
            # Remove duplicates and sort
            for key in entities:
                entities[key] = sorted(list(set(entities[key])))
            
            return entities
            
        except Exception as e:
            logger.warning(f"Error in spaCy extraction: {e}")
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
    
    def _extract_with_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using RPG-specific patterns."""
        entities = {
            "NPCs": [],
            "Factions": [],
            "Locations": [],
            "Items": [],
        }
        
        seen = set()
        
        for category, patterns in self.rpg_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                for match in matches:
                    entity = match if isinstance(match, str) else " ".join(match) if isinstance(match, tuple) else str(match)
                    entity = entity.strip()
                    if entity and entity not in seen and len(entity) >= 2:
                        entities[category].append(entity)
                        seen.add(entity)
        
        # Remove duplicates
        for key in entities:
            entities[key] = sorted(list(set(entities[key])))
        
        return entities
    
    def _extract_with_llm(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using LLM."""
        if not LLM_EXTRACTION_AVAILABLE:
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
        
        # Create prompt for entity extraction
        prompt = f"""Extract RPG entities from the following text. Return a JSON object with four arrays: NPCs, Factions, Locations, Items.

Text:
{text[:4000]}  # Limit text length for LLM

Return only valid JSON in this format:
{{
  "NPCs": ["name1", "name2"],
  "Factions": ["faction1"],
  "Locations": ["location1"],
  "Items": ["item1"]
}}"""
        
        try:
            if self.llm_provider == "openai":
                response, _ = _call_openai_api(prompt, self.llm_model, self.llm_api_key, 1000, 0.3)
            elif self.llm_provider == "anthropic":
                response, _ = _call_anthropic_api(prompt, self.llm_model, self.llm_api_key, 1000, 0.3)
            elif self.llm_provider == "ollama":
                # Ollama doesn't need api_key, pass None for endpoint (uses default)
                response, _ = _call_ollama_api(prompt, self.llm_model, 1000, 0.3, endpoint=None)
            else:
                logger.warning(f"Unknown LLM provider: {self.llm_provider}")
                return {
                    "NPCs": [],
                    "Factions": [],
                    "Locations": [],
                    "Items": [],
                }
            
            if not response:
                return {
                    "NPCs": [],
                    "Factions": [],
                    "Locations": [],
                    "Items": [],
                }
            
            # Parse JSON response
            # Try to extract JSON from response (might have markdown code blocks)
            json_match = re.search(r'\{[^{}]*"NPCs"[^{}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
            
            entities = json.loads(json_str)
            
            # Ensure all categories exist
            result = {
                "NPCs": entities.get("NPCs", []),
                "Factions": entities.get("Factions", []),
                "Locations": entities.get("Locations", []),
                "Items": entities.get("Items", []),
            }
            
            logger.debug(f"LLM extracted {sum(len(v) for v in result.values())} entities")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM entity extraction response: {e}")
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
        except Exception as e:
            logger.warning(f"Error in LLM extraction: {e}")
            return {
                "NPCs": [],
                "Factions": [],
                "Locations": [],
                "Items": [],
            }
    
    def _merge_results(self, results: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
        """Merge entity results (fallback if validator not available)."""
        merged = {
            "NPCs": [],
            "Factions": [],
            "Locations": [],
            "Items": [],
        }
        
        for result in results:
            for category in merged:
                merged[category].extend(result.get(category, []))
        
        # Remove duplicates
        for category in merged:
            merged[category] = sorted(list(set(merged[category])))
        
        return merged
    
    def is_available(self) -> bool:
        """Check if entity extraction is available."""
        return self.nlp is not None


# Global extractor instance (lazy-loaded)
_extractor_instance: Optional[EntityExtractor] = None


def get_extractor(
    model_name: str = "en_core_web_sm",
    use_llm: bool = False,
    llm_provider: str = "openai",
    llm_model: str = "gpt-4",
    llm_api_key: Optional[str] = None,
) -> EntityExtractor:
    """
    Get or create global entity extractor instance.
    
    Args:
        model_name: Name of spaCy model to use.
        use_llm: Whether to use LLM for enhanced extraction.
        llm_provider: LLM provider if use_llm is True.
        llm_model: LLM model name.
        llm_api_key: Optional API key for LLM.
        
    Returns:
        EntityExtractor instance.
    """
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = EntityExtractor(
            model_name=model_name,
            use_llm=use_llm,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
        )
    return _extractor_instance


def extract_entities_from_text(
    text: str,
    model_name: str = "en_core_web_sm",
    use_llm: bool = False,
    llm_provider: str = "openai",
    llm_model: str = "gpt-4",
    llm_api_key: Optional[str] = None,
) -> Dict[str, List[str]]:
    """
    Convenience function to extract entities from text.
    
    Args:
        text: Text to extract entities from.
        model_name: Name of spaCy model to use.
        use_llm: Whether to use LLM for enhanced extraction.
        llm_provider: LLM provider if use_llm is True.
        llm_model: LLM model name.
        llm_api_key: Optional API key for LLM.
        
    Returns:
        Dictionary of extracted entities by category.
    """
    extractor = get_extractor(
        model_name=model_name,
        use_llm=use_llm,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
    )
    return extractor.extract_entities(text)
