# PURPOSE: Orchestrate RAG workflows for the Wrath and Glory knowledge stack.
# DEPENDENCIES: ai_summarizer, entity_extractor, campaign_kb search, utils.
# MODIFICATION NOTES: Initial pipeline for pattern analysis and content generation.

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils import load_config, validate_vault_path

# #region agent log
DEBUG_LOG_PATH = Path("d:\\CodeRepositories\\.cursor\\debug.log")
def _debug_log(location: str, message: str, data: dict, hypothesis_id: str = "A"):
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except: pass
# #endregion

logger = logging.getLogger(__name__)

try:
    from entity_extractor import extract_entities_from_text
    ENTITY_EXTRACTION_AVAILABLE = True
except ImportError:
    ENTITY_EXTRACTION_AVAILABLE = False
    logger.warning("Entity extraction not available. Install dependencies to enable patterns.")

try:
    from ai_summarizer import summarize_text, _call_openai_api, _call_anthropic_api, _call_ollama_api, chunk_text
    SUMMARIZATION_AVAILABLE = True
    CHUNKING_AVAILABLE = True
except ImportError:
    SUMMARIZATION_AVAILABLE = False
    CHUNKING_AVAILABLE = False
    logger.warning("AI summarizer not available. Install dependencies to enable summaries.")

import hashlib
import os
from collections import defaultdict

# Schema keys for chunk tags (B2); empty string = unrestricted for filtering.
CHUNK_TAG_KEYS = (
    "system",
    "faction",
    "location",
    "time_period",
    "mechanical_vs_narrative",
    "tone",
)


# PURPOSE: Extract chunk-level tags from doc key and text for B2 ingestion.
# DEPENDENCIES: 05_rag_integration chunk metadata schema.
# MODIFICATION NOTES: Heuristic-based; config overrides win when non-empty.
def extract_chunk_tags(
    doc_key: str,
    text: str,
    doc_type: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Compute tags for a chunk per schema in 05_rag_integration.md.
    Returns dict with keys: system, faction, location, time_period, mechanical_vs_narrative, tone.
    """
    config = config or {}
    defaults = config.get("defaults", {})
    overrides = config.get("overrides", {})

    key_lower = doc_key.lower()
    text_lower = text[:15000].lower()  # First 15K chars for heuristic

    # System: PDFs with wrath/warhammer/W&G; campaign -> W&G
    system = ""
    if doc_type == "campaign":
        system = "W&G"
    elif "wrath" in key_lower or "warhammer" in key_lower or "w&g" in key_lower:
        system = "W&G"
    elif "d&d" in key_lower or "dragon" in key_lower:
        system = "D&D"
    if not system and defaults.get("system"):
        system = str(defaults["system"])

    # Faction: keyword match
    faction = ""
    faction_keywords = [
        ("ork", "Orks"),
        ("inquisition", "Inquisition"),
        ("mechanicus", "Mechanicus"),
        ("astartes", "Adeptus Astartes"),
        ("ecclesiarchy", "Ecclesiarchy"),
        ("militarum", "Astra Militarum"),
    ]
    for kw, label in faction_keywords:
        if kw in text_lower or kw in key_lower:
            faction = label
            break
    if not faction and defaults.get("faction"):
        faction = str(defaults["faction"])

    # Location: keyword match
    location = ""
    location_keywords = ["gilead", "footfall", "ostia", "void"]
    for kw in location_keywords:
        if kw in text_lower:
            location = kw.capitalize()
            break
    if not location and defaults.get("location"):
        location = str(defaults["location"])

    # Time_period: default empty
    time_period = str(defaults.get("time_period", ""))

    # Mechanical_vs_narrative: rules/mechanics vs narrative
    mechanical_vs_narrative = ""
    mech_keywords = ["dice", "damage", "dn ", "test", "roll", "wounds", "shock", "tier"]
    narr_keywords = ["adventure", "scene", "narrative", "story", "hook"]
    mech_count = sum(1 for kw in mech_keywords if kw in text_lower)
    narr_count = sum(1 for kw in narr_keywords if kw in text_lower)
    if mech_count > narr_count:
        mechanical_vs_narrative = "mechanical"
    elif narr_count > mech_count:
        mechanical_vs_narrative = "narrative"
    if not mechanical_vs_narrative and defaults.get("mechanical_vs_narrative"):
        mechanical_vs_narrative = str(defaults["mechanical_vs_narrative"])

    # Tone: explicit terms
    tone = ""
    tone_keywords = [
        ("grimdark", "grimdark"),
        ("heroic", "heroic"),
        ("absurd", "absurd"),
        ("neutral", "neutral"),
    ]
    for kw, label in tone_keywords:
        if kw in text_lower:
            tone = label
            break
    if not tone and defaults.get("tone"):
        tone = str(defaults["tone"])

    tags = {
        "system": system,
        "faction": faction,
        "location": location,
        "time_period": time_period,
        "mechanical_vs_narrative": mechanical_vs_narrative,
        "tone": tone,
    }

    # Apply per-doc overrides (exact key or pattern)
    for override_key, override_values in overrides.items():
        if override_key == doc_key:
            for k, v in (override_values or {}).items():
                if k in tags and v:
                    tags[k] = str(v)
            break
        # Support fnmatch-style pattern (simple substring)
        if override_key in doc_key:
            for k, v in (override_values or {}).items():
                if k in tags and v:
                    tags[k] = str(v)
            break

    return tags


# PURPOSE: Lightweight document index for fast retrieval without loading full text.
# DEPENDENCIES: filesystem access, json.
# MODIFICATION NOTES: Caches per-document metadata, keywords, and themes for fast query matching.
class DocumentIndex:
    """Lightweight index for fast document retrieval without loading full text."""
    
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
    
    def _load_index(self):
        """Load index from cache file if it exists."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
                logger.info(f"Loaded document index with {len(self.index)} entries")
            except Exception as exc:
                logger.warning(f"Failed to load document index: {exc}")
                self.index = {}
    
    def _save_index(self):
        """Save index to cache file."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.warning(f"Failed to save document index: {exc}")
    
    def _get_file_mtime(self, file_path: str) -> Optional[float]:
        """Get file modification time, handling both file paths and document keys."""
        try:
            # Try as direct file path first
            if Path(file_path).exists():
                return Path(file_path).stat().st_mtime
            # For PDF chunks or other keys, try to extract base path
            if file_path.startswith("[PDF]"):
                # Extract filename from key like "[PDF] filename.txt [chunk 1/5]"
                parts = file_path.replace("[PDF]", "").strip().split(" [chunk")
                if parts:
                    # Would need pdf_dir to resolve, but for now return None
                    return None
            return None
        except Exception:
            return None
    
    def build(
        self,
        text_map: Dict[str, str],
        theme_keywords: List[str],
        invalidate_on_mtime: bool = True,
        chunk_tags_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Build index from text_map, extracting metadata and keywords per document.
        
        Args:
            text_map: Dictionary mapping document keys to text content.
            theme_keywords: List of theme keywords to extract.
            invalidate_on_mtime: If True, check mtime and skip if unchanged.
            chunk_tags_config: Optional dict with "defaults" and "overrides" for B2 tags.
        """
        logger.info(f"Building document index for {len(text_map)} documents...")
        updated_count = 0
        new_count = 0
        chunk_tags_config = chunk_tags_config or {}

        for doc_key, text in text_map.items():
            # Check if entry exists and is still valid
            was_already_indexed = doc_key in self.index
            existing_tags = (self.index.get(doc_key) or {}).get("tags")
            needs_tags = not existing_tags or not all(k in (existing_tags or {}) for k in CHUNK_TAG_KEYS)
            if invalidate_on_mtime and was_already_indexed and not needs_tags:
                cached_mtime = self.index[doc_key].get("mtime")
                current_mtime = self._get_file_mtime(doc_key)
                if cached_mtime and current_mtime and cached_mtime == current_mtime:
                    # Skip if unchanged and already has full tags
                    continue
            
            # Extract metadata
            text_length = len(text)
            doc_type = "pdf" if doc_key.startswith("[PDF]") else "campaign"
            
            # Extract keywords from first 10K chars (fast)
            preview_text = text[:10000].lower()
            words = preview_text.split()
            # Simple keyword extraction: words that appear multiple times
            word_counts = defaultdict(int)
            for word in words:
                if len(word) > 3:  # Skip very short words
                    word_counts[word] += 1
            keywords = [word for word, count in word_counts.items() if count >= 2][:20]  # Top 20
            
            # Extract themes (fast regex-based)
            themes = build_theme_counts(text[:50000], theme_keywords)  # First 50K for speed
            
            # Chunk-level tags (B2): extract_chunk_tags with schema keys
            tags = extract_chunk_tags(doc_key, text, doc_type, chunk_tags_config)
            # Ensure all schema keys present
            for k in CHUNK_TAG_KEYS:
                if k not in tags:
                    tags[k] = ""
            # Preserve existing tags on re-index: config/heuristic wins over existing for non-empty
            existing = (self.index.get(doc_key) or {}).get("tags") or {}
            for k in CHUNK_TAG_KEYS:
                if k in existing and existing[k] and not tags.get(k):
                    tags[k] = existing[k]
            tags = {k: tags.get(k, "") or "" for k in CHUNK_TAG_KEYS}
            
            # Store metadata
            self.index[doc_key] = {
                "path": doc_key,
                "size": text_length,
                "mtime": self._get_file_mtime(doc_key),
                "type": doc_type,
                "keywords": keywords,
                "themes": themes,
                "preview": text[:500],  # First 500 chars for preview
                "tags": tags or {},
            }
            
            if was_already_indexed:
                updated_count += 1
            else:
                new_count += 1
        
        self._save_index()
        logger.info(f"Index built: {new_count} new, {updated_count} updated, {len(self.index)} total")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 8,
        retrieval_mode: str = "Strict Canon",
        tag_filters: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        Fast keyword-based retrieval with optional tag filtering/ranking (B3).
        
        Args:
            query: Query string.
            top_k: Number of top documents to return.
            retrieval_mode: "Strict Canon" | "Loose Canon" | "Inspired By". Strict = only
                entries whose tags match tag_filters; Loose = include all, boost for tag
                match; Inspired = no tag filter, rank by text similarity only.
            tag_filters: Optional dict of tag key -> value. Used when retrieval_mode is
                Strict or Loose. Omitted keys are unrestricted.
            
        Returns:
            List of document keys ordered by relevance.
        """
        query_lower = query.lower()
        query_terms = [term.lower() for term in query.split() if len(term) > 2]
        query_phrases = []
        words = query.split()
        for i in range(len(words) - 1):
            phrase = " ".join(words[i:i+2]).lower()
            if len(phrase) > 3:
                query_phrases.append(phrase)
        
        tag_filters = tag_filters or {}
        scored: List[Tuple[str, float]] = []
        
        for doc_key, metadata in self.index.items():
            tags = metadata.get("tags") or {}
            # Strict Canon: exclude entries that don't satisfy all tag_filters
            if retrieval_mode == "Strict Canon" and tag_filters:
                if not all(tags.get(k) == v for k, v in tag_filters.items()):
                    continue
            # Inspired By: no tag-based filtering; fall through to scoring only
            
            score = 0.0
            keywords = metadata.get("keywords", [])
            preview = metadata.get("preview", "").lower()
            
            # Score by keyword matches
            for term in query_terms:
                if term in keywords:
                    score += 2.0  # Keyword match is strong signal
                score += preview.count(term) * 0.5  # Preview text matches
            
            # Boost for phrase matches
            for phrase in query_phrases:
                if phrase in preview:
                    score += 3.0  # Phrase matches are very strong
            
            # Boost for theme matches
            themes = metadata.get("themes", {})
            for term in query_terms:
                if term in themes:
                    score += themes[term] * 0.3
            
            # Loose Canon: boost for tag match (exact or partial)
            if retrieval_mode == "Loose Canon" and tag_filters:
                match_count = sum(1 for k, v in tag_filters.items() if tags.get(k) == v)
                if match_count == len(tag_filters):
                    score += 5.0  # Full tag match
                elif match_count > 0:
                    score += 2.0  # Partial tag match
            
            if score > 0:
                scored.append((doc_key, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc_key for doc_key, _ in scored[:top_k]]


# PURPOSE: Cache entity extraction results per document to avoid recomputation.
# DEPENDENCIES: filesystem access, hashlib, json.
# MODIFICATION NOTES: Uses file path + text hash + mtime for cache invalidation.
class EntityCache:
    """Cache entity extraction results per document."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "entities"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, doc_key: str, text: str) -> str:
        """Generate cache key from document key and text hash."""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
        # Sanitize doc_key for filename
        safe_key = doc_key.replace("[PDF]", "PDF_").replace("/", "_").replace("\\", "_").replace(" ", "_")
        safe_key = "".join(c for c in safe_key if c.isalnum() or c in "._-")[:100]  # Limit length
        return f"{safe_key}_{text_hash}.json"
    
    def get(self, doc_key: str, text: str) -> Optional[Dict[str, Any]]:
        """
        Get cached entities for document if available and valid.
        
        Args:
            doc_key: Document identifier.
            text: Document text content.
            
        Returns:
            Cached entities dict or None if not cached/invalid.
        """
        cache_file = self.cache_dir / self._get_cache_key(doc_key, text)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Verify text hash matches (content hasn't changed)
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
            if cached.get("text_hash") != text_hash:
                return None  # Content changed, cache invalid
            
            return cached.get("entities")
        except Exception as exc:
            logger.debug(f"Failed to load entity cache for {doc_key}: {exc}")
            return None
    
    def set(self, doc_key: str, text: str, entities: Dict[str, Any]):
        """
        Cache entity extraction results for document.
        
        Args:
            doc_key: Document identifier.
            text: Document text content.
            entities: Extracted entities dictionary.
        """
        cache_file = self.cache_dir / self._get_cache_key(doc_key, text)
        try:
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
            cached_data = {
                "doc_key": doc_key,
                "text_hash": text_hash,
                "entities": entities,
                "timestamp": time.time(),
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.warning(f"Failed to cache entities for {doc_key}: {exc}")


# PURPOSE: Merge nested configuration dictionaries with defaults.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Shallow merge with nested dict support.
def merge_config(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


# PURPOSE: Load and normalize RAG pipeline config.
# DEPENDENCIES: utils.load_config.
# MODIFICATION NOTES: Applies defaults and validates vault output paths.
def load_pipeline_config(config_path: Path) -> Dict[str, Any]:
    base_config = load_config(config_path)
    rag_defaults = {
        "enabled": True,
        "campaign_kb_root": "D:\\Arc_Forge\\campaign_kb",
        "campaign_docs": [
            "campaign/00_overview.md",
            "campaign/01_factions.md",
            "campaign/02_locations.md",
            "campaign/03_npcs.md",
            "campaign/04_missions.md",
            "campaign/05_rag_integration.md",
        ],
        "output_dir": "Campaigns/_rag_outputs",
        "pattern_analysis_enabled": True,
        "content_generation_enabled": True,
        "use_kb_search": True,
        "search": {
            "limit": 8,
            "source_name": None,
            "doc_type": None,
        },
        "summarization": {
            "provider": "ollama",
            "model": "llama2",
            "api_key": None,
            "max_tokens": 500,
            "temperature": 0.7,
            "cache_dir": "Sources/_summaries",
            "ollama_endpoint": None,
        },
        "generation": {
            "provider": "ollama",
            "model": "llama2",
            "api_key": None,
            "max_tokens": 800,
            "temperature": 0.8,
            "ollama_endpoint": None,
        },
        "theme_keywords": [
            "faith",
            "entropy",
            "cold",
            "heat",
            "decay",
            "survival",
            "heresy",
            "machine spirit",
            "warp",
            "void",
            "promethium",
        ],
        "pdf_extraction_dir": "Sources/_extracted_text",
        "include_pdfs": True,
        "pdf_file_pattern": "*.txt",
        "cache": {
            "enabled": True,
            "cache_dir": "Campaigns/_rag_cache",
            "index_cache": "document_index.json",
            "entity_cache_dir": "entities",
            "invalidate_on_mtime_change": True,
        },
        "query_mode": {
            "skip_full_analysis": True,
            "max_retrieved_docs": 8,
            "lazy_entity_extraction": True,
        },
    }

    rag_config = merge_config(rag_defaults, base_config.get("rag_pipeline", {}))

    vault_root = Path(base_config.get("vault_root", "D:\\Arc_Forge\\ObsidianVault"))
    output_dir = Path(rag_config["output_dir"])
    if not output_dir.is_absolute():
        output_dir = vault_root / output_dir
    rag_config["output_dir"] = validate_vault_path(vault_root, output_dir)
    rag_config["vault_root"] = vault_root
    rag_config["entity_extraction"] = base_config.get("entity_extraction", {})
    
    # Resolve PDF extraction directory path relative to vault_root
    pdf_dir = Path(rag_config.get("pdf_extraction_dir", "Sources/_extracted_text"))
    if not pdf_dir.is_absolute():
        pdf_dir = vault_root / pdf_dir
    rag_config["pdf_extraction_dir"] = str(pdf_dir)

    return {"base": base_config, "rag": rag_config}


# PURPOSE: Resolve campaign document paths from config.
# DEPENDENCIES: pathlib.Path.
# MODIFICATION NOTES: Validates existence and logs missing docs.
def resolve_campaign_docs(campaign_kb_root: Path, doc_rel_paths: List[str]) -> List[Path]:
    resolved = []
    for rel_path in doc_rel_paths:
        doc_path = campaign_kb_root / rel_path
        if doc_path.exists():
            resolved.append(doc_path)
        else:
            logger.warning(f"Campaign doc missing: {doc_path}")
    return resolved


# PURPOSE: Read campaign docs into a path->text mapping.
# DEPENDENCIES: filesystem access.
# MODIFICATION NOTES: Skips unreadable files with warnings.
def read_campaign_docs(doc_paths: List[Path]) -> Dict[str, str]:
    text_map: Dict[str, str] = {}
    for path in doc_paths:
        try:
            text_map[str(path)] = path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning(f"Failed to read {path}: {exc}")
    return text_map


# PURPOSE: Read extracted PDF text files incrementally with chunking to avoid memory/performance issues.
# DEPENDENCIES: filesystem access, pathlib.Path, ai_summarizer.chunk_text.
# MODIFICATION NOTES: Implements lightweight RAG incremental ingestion - chunks large PDFs before adding to text_map.
def read_pdf_texts(
    pdf_extraction_dir: Path,
    file_pattern: str = "*.txt",
    max_chunk_size: int = 50000,
    max_chunks_per_pdf: int = 10,
    max_total_text_chars: int = 2000000,
) -> Dict[str, str]:
    """
    Incrementally ingest PDF texts with chunking to prevent memory/performance issues.
    
    Args:
        pdf_extraction_dir: Directory containing extracted PDF text files.
        file_pattern: File pattern to match (default: "*.txt").
        max_chunk_size: Maximum characters per chunk (default: 50000).
        max_chunks_per_pdf: Maximum chunks per PDF file (default: 10).
        max_total_text_chars: Maximum total characters across all PDFs (default: 2M).
        
    Returns:
        Dictionary mapping PDF source keys to text chunks.
    """
    text_map: Dict[str, str] = {}
    if not pdf_extraction_dir.exists():
        logger.warning(f"PDF extraction directory not found: {pdf_extraction_dir}")
        return text_map
    
    pdf_files = sorted(pdf_extraction_dir.glob(file_pattern))  # Sort for deterministic processing
    logger.info(f"Found {len(pdf_files)} PDF text files in {pdf_extraction_dir}")
    
    total_chars = 0
    processed_pdfs = 0
    skipped_pdfs = 0
    
    for pdf_path in pdf_files:
        # Check total size limit before processing
        if total_chars >= max_total_text_chars:
            logger.warning(
                f"Reached total text size limit ({max_total_text_chars} chars). "
                f"Skipping remaining {len(pdf_files) - processed_pdfs} PDFs."
            )
            skipped_pdfs = len(pdf_files) - processed_pdfs
            break
        
        try:
            # #region agent log
            _debug_log("rag_pipeline.py:195", "Reading PDF file", {
                "filename": pdf_path.name,
                "size_bytes": pdf_path.stat().st_size,
                "total_chars_so_far": total_chars
            }, "A")
            # #endregion
            
            text = pdf_path.read_text(encoding="utf-8")
            text_length = len(text)
            
            # #region agent log
            _debug_log("rag_pipeline.py:203", "PDF file read complete", {
                "filename": pdf_path.name,
                "text_length": text_length
            }, "A")
            # #endregion
            
            # Chunk large PDFs incrementally
            if CHUNKING_AVAILABLE and text_length > max_chunk_size:
                chunks = chunk_text(text, max_chunk_size=max_chunk_size, overlap=200)
                # Limit chunks per PDF
                chunks = chunks[:max_chunks_per_pdf]
                logger.info(
                    f"Chunked {pdf_path.name} into {len(chunks)} chunks "
                    f"(original: {text_length} chars, limited to {max_chunks_per_pdf} chunks)"
                )
                
                # Add chunks incrementally with size tracking
                for i, chunk in enumerate(chunks):
                    if total_chars + len(chunk) > max_total_text_chars:
                        logger.warning(
                            f"Reached total size limit while processing {pdf_path.name} chunk {i+1}. "
                            f"Stopping PDF ingestion."
                        )
                        break
                    
                    chunk_key = f"[PDF] {pdf_path.name} [chunk {i+1}/{len(chunks)}]"
                    text_map[chunk_key] = chunk
                    total_chars += len(chunk)
                    
                    # #region agent log
                    _debug_log("rag_pipeline.py:228", "PDF chunk added", {
                        "chunk_key": chunk_key,
                        "chunk_size": len(chunk),
                        "total_chars": total_chars
                    }, "A")
                    # #endregion
            else:
                # Small PDF or chunking unavailable - add as-is
                if total_chars + text_length > max_total_text_chars:
                    logger.warning(
                        f"Skipping {pdf_path.name} - would exceed total size limit "
                        f"({total_chars + text_length} > {max_total_text_chars})"
                    )
                    skipped_pdfs += 1
                    continue
                
                text_map[f"[PDF] {pdf_path.name}"] = text
                total_chars += text_length
                
                # #region agent log
                _debug_log("rag_pipeline.py:245", "PDF added (no chunking)", {
                    "filename": pdf_path.name,
                    "text_length": text_length,
                    "total_chars": total_chars
                }, "A")
                # #endregion
            
            processed_pdfs += 1
            
        except Exception as exc:
            logger.warning(f"Failed to read PDF text {pdf_path}: {exc}")
            skipped_pdfs += 1
            # #region agent log
            _debug_log("rag_pipeline.py:258", "PDF read failed", {"filename": pdf_path.name, "error": str(exc)}, "A")
            # #endregion
    
    # #region agent log
    _debug_log("rag_pipeline.py:262", "PDF reading complete", {
        "total_pdfs": len(pdf_files),
        "processed": processed_pdfs,
        "skipped": skipped_pdfs,
        "successful_sources": len(text_map),
        "total_chars": total_chars
    }, "A")
    # #endregion
    
    logger.info(
        f"PDF ingestion complete: {processed_pdfs} processed, {skipped_pdfs} skipped, "
        f"{len(text_map)} sources, {total_chars:,} total characters"
    )
    
    return text_map


# PURPOSE: Build a theme frequency map from text.
# DEPENDENCIES: theme keyword list.
# MODIFICATION NOTES: Case-insensitive substring count.
def build_theme_counts(text: str, keywords: List[str]) -> Dict[str, int]:
    lowered = text.lower()
    return {keyword: lowered.count(keyword.lower()) for keyword in keywords}


# PURPOSE: Extract entities from a subset of documents (lazy evaluation).
# DEPENDENCIES: entity_extractor, EntityCache.
# MODIFICATION NOTES: Only processes provided document subset, uses cache to avoid re-extraction.
def extract_entities_from_docs(
    doc_keys: List[str],
    text_map: Dict[str, str],
    rag_config: Dict[str, Any],
    entity_cache: Optional[EntityCache] = None,
) -> Dict[str, List[str]]:
    """
    Extract entities only from specified documents (lazy evaluation for queries).
    
    Args:
        doc_keys: List of document keys to process.
        text_map: Full text map (will only use specified keys).
        rag_config: RAG configuration.
        entity_cache: Optional entity cache instance.
        
    Returns:
        Dictionary of entities by category.
    """
    entities: Dict[str, List[str]] = {"NPCs": [], "Factions": [], "Locations": [], "Items": []}
    
    if not doc_keys or not ENTITY_EXTRACTION_AVAILABLE:
        return entities
    
    # Collect text from specified documents only
    relevant_texts = []
    for doc_key in doc_keys:
        if doc_key in text_map:
            text = text_map[doc_key]
            # Check cache first
            if entity_cache:
                cached = entity_cache.get(doc_key, text)
                if cached:
                    # Merge cached entities
                    for category in entities:
                        entities[category].extend(cached.get(category, []))
                    continue
            relevant_texts.append((doc_key, text))
    
    if not relevant_texts:
        return entities
    
    # Combine text from relevant docs
    combined_text = "\n\n".join([text for _, text in relevant_texts])
    
    # Limit size for entity extraction
    MAX_TEXT_FOR_ENTITY_EXTRACTION = 500000  # 500K chars for query mode (smaller than full analysis)
    if len(combined_text) > MAX_TEXT_FOR_ENTITY_EXTRACTION:
        logger.info(f"Truncating combined text for entity extraction: {len(combined_text):,} -> {MAX_TEXT_FOR_ENTITY_EXTRACTION:,} chars")
        combined_text = combined_text[:MAX_TEXT_FOR_ENTITY_EXTRACTION]
    
    # Extract entities
    extracted = extract_entities_from_text(
        combined_text,
        use_llm=rag_config.get("entity_extraction", {}).get("use_llm", False),
        llm_provider=rag_config.get("entity_extraction", {}).get("llm_provider", "ollama"),
        llm_model=rag_config.get("entity_extraction", {}).get("llm_model", "llama2"),
        llm_api_key=rag_config.get("entity_extraction", {}).get("llm_api_key"),
    )
    
    if extracted:
        # Cache results per document
        if entity_cache:
            for doc_key, text in relevant_texts:
                # Cache entities for this document (approximate - using combined extraction)
                entity_cache.set(doc_key, text, extracted)
        
        entities = extracted
    
    return entities


# PURPOSE: Summarize context from a subset of documents (lazy evaluation).
# DEPENDENCIES: ai_summarizer.
# MODIFICATION NOTES: Only summarizes retrieved documents, not entire corpus.
def summarize_context_from_docs(
    doc_keys: List[str],
    text_map: Dict[str, str],
    rag_config: Dict[str, Any],
) -> Optional[str]:
    """
    Summarize context only from specified documents (lazy evaluation for queries).
    
    Args:
        doc_keys: List of document keys to summarize.
        text_map: Full text map (will only use specified keys).
        rag_config: RAG configuration.
        
    Returns:
        Summary string or None if summarization unavailable.
    """
    if not doc_keys or not SUMMARIZATION_AVAILABLE:
        return None
    
    # Collect text from specified documents only
    relevant_texts = [text_map[doc_key] for doc_key in doc_keys if doc_key in text_map]
    if not relevant_texts:
        return None
    
    combined_text = "\n\n".join(relevant_texts)
    
    # Use existing summarize_context function but with smaller text
    return summarize_context(combined_text, rag_config)


# PURPOSE: Aggregate entity extraction across campaign docs.
# DEPENDENCIES: entity_extractor.
# MODIFICATION NOTES: Returns per-category entity counts and unique lists.
def build_pattern_report(text_map: Dict[str, str], rag_config: Dict[str, Any]) -> Dict[str, Any]:
    combined_text = "\n\n".join(text_map.values())
    entities: Dict[str, List[str]] = {"NPCs": [], "Factions": [], "Locations": [], "Items": []}

    # Limit entity extraction for very large texts to prevent performance issues
    MAX_TEXT_FOR_ENTITY_EXTRACTION = 1000000  # 1M chars
    text_for_extraction = combined_text
    
    if len(combined_text) > MAX_TEXT_FOR_ENTITY_EXTRACTION:
        logger.warning(
            f"Text too large for entity extraction ({len(combined_text):,} chars > {MAX_TEXT_FOR_ENTITY_EXTRACTION:,}). "
            f"Sampling first {MAX_TEXT_FOR_ENTITY_EXTRACTION:,} characters."
        )
        text_for_extraction = combined_text[:MAX_TEXT_FOR_ENTITY_EXTRACTION]
        # #region agent log
        _debug_log("rag_pipeline.py:340", "Text truncated for entity extraction", {
            "original_length": len(combined_text),
            "truncated_length": len(text_for_extraction)
        }, "E")
        # #endregion

    if ENTITY_EXTRACTION_AVAILABLE and text_for_extraction.strip():
        extracted = extract_entities_from_text(
            text_for_extraction,
            use_llm=rag_config.get("entity_extraction", {}).get("use_llm", False),
            llm_provider=rag_config.get("entity_extraction", {}).get("llm_provider", "ollama"),
            llm_model=rag_config.get("entity_extraction", {}).get("llm_model", "llama2"),
            llm_api_key=rag_config.get("entity_extraction", {}).get("llm_api_key"),
        )
        entities = extracted or entities

    counts = {key: {name: entities[key].count(name) for name in set(entities[key])} for key in entities}
    themes = build_theme_counts(combined_text, rag_config.get("theme_keywords", []))
    
    source_docs_list = list(text_map.keys())
    # #region agent log
    _debug_log("rag_pipeline.py:237", "Building pattern report", {
        "total_sources": len(source_docs_list),
        "campaign_sources": len([k for k in source_docs_list if not k.startswith("[PDF]")]),
        "pdf_sources": len([k for k in source_docs_list if k.startswith("[PDF]")]),
        "sample_pdf_sources": [k for k in source_docs_list if k.startswith("[PDF]")][:3]
    }, "D")
    # #endregion

    return {
        "entities": entities,
        "entity_counts": counts,
        "themes": themes,
        "source_docs": source_docs_list,
    }


# PURPOSE: Summarize context for generation prompts.
# DEPENDENCIES: ai_summarizer.summarize_text.
# MODIFICATION NOTES: Returns None when summarization is unavailable.
def summarize_context(text: str, rag_config: Dict[str, Any]) -> Optional[str]:
    if not SUMMARIZATION_AVAILABLE or not text.strip():
        return None
    summary_cfg = rag_config.get("summarization", {})
    return summarize_text(
        text=text,
        provider=summary_cfg.get("provider", "ollama"),
        model=summary_cfg.get("model", "llama2"),
        api_key=summary_cfg.get("api_key"),
        max_tokens=summary_cfg.get("max_tokens", 500),
        temperature=summary_cfg.get("temperature", 0.7),
        rpg_mode=True,
        cache_dir=Path(summary_cfg.get("cache_dir")) if summary_cfg.get("cache_dir") else None,
        ollama_endpoint=summary_cfg.get("ollama_endpoint"),
    )
    # #region agent log
    elapsed = time.time() - start_time
    _debug_log("rag_pipeline.py:228", "Summarization complete", {"elapsed_seconds": elapsed, "result_length": len(result) if result else 0}, "C")
    # #endregion
    return result


# PURPOSE: Call LLM provider with a custom prompt for generation.
# DEPENDENCIES: ai_summarizer internal API helpers.
# MODIFICATION NOTES: Returns generated text or None if unavailable.
def generate_text(prompt: str, rag_config: Dict[str, Any]) -> Optional[str]:
    gen_cfg = rag_config.get("generation", {})
    provider = gen_cfg.get("provider", "ollama")
    model = gen_cfg.get("model", "llama2")
    max_tokens = gen_cfg.get("max_tokens", 800)
    temperature = gen_cfg.get("temperature", 0.8)
    api_key = gen_cfg.get("api_key")
    endpoint = gen_cfg.get("ollama_endpoint")

    if not SUMMARIZATION_AVAILABLE:
        logger.error("LLM helpers not available; cannot generate content")
        return None

    if provider == "openai":
        result, _ = _call_openai_api(prompt, model, api_key, max_tokens, temperature)
        return result
    if provider == "anthropic":
        result, _ = _call_anthropic_api(prompt, model, api_key, max_tokens, temperature)
        return result
    result, _ = _call_ollama_api(prompt, model, max_tokens, temperature, endpoint=endpoint)
    return result


# PURPOSE: Generate rules, adventure outline, and bios from context.
# DEPENDENCIES: generate_text.
# MODIFICATION NOTES: Returns a dict keyed by output type.
def generate_content_pack(context_summary: str, pattern_report: Dict[str, Any], rag_config: Dict[str, Any]) -> Dict[str, str]:
    context = context_summary or ""
    entities = pattern_report.get("entities", {})
    top_npcs = ", ".join(entities.get("NPCs", [])[:6])
    top_factions = ", ".join(entities.get("Factions", [])[:6])
    top_locations = ", ".join(entities.get("Locations", [])[:6])
    top_items = ", ".join(entities.get("Items", [])[:10]) if entities.get("Items") else "None mentioned in source"

    # Grounding instructions to prevent hallucinations
    grounding_instructions = (
        "CRITICAL GROUNDING RULES:\n"
        "- ONLY use entities, items, locations, and NPCs that appear in the context below.\n"
        "- Do NOT invent new items, artifacts, weapons, or entities.\n"
        "- If an item or entity is not mentioned in the context, do NOT include it in your response.\n"
        "- When mentioning entities, use their exact names as provided in the canonical lists below.\n"
        "- Do not create fictional artifacts, weapons, or magical items unless they are explicitly mentioned.\n\n"
    )

    rules_prompt = (
        "Draft a concise rules module for Wrath & Glory based ONLY on the provided context.\n\n"
        + grounding_instructions +
        f"Context summary: {context}\n\n"
        f"Canonical NPCs from source: {top_npcs}\n"
        f"Canonical Factions from source: {top_factions}\n"
        f"Canonical Locations from source: {top_locations}\n"
        f"Canonical Items from source: {top_items}\n\n"
        "Include: scope, mechanics, and example of play. Reference ONLY the entities listed above.\n"
        "Do not mention any items, weapons, or artifacts that are not in the canonical items list.\n"
    )
    adventure_prompt = (
        "Generate a 3-act adventure outline for Wrath & Glory based ONLY on the provided context.\n\n"
        + grounding_instructions +
        f"Context summary: {context}\n\n"
        f"Canonical NPCs from source: {top_npcs}\n"
        f"Canonical Factions from source: {top_factions}\n"
        f"Canonical Locations from source: {top_locations}\n"
        f"Canonical Items from source: {top_items}\n\n"
        "Include: hook, key scenes, adversaries, and fallout. Reference ONLY the entities listed above.\n"
        "Do not invent new locations, factions, or NPCs. Use only what is provided in the canonical lists.\n"
    )
    bios_prompt = (
        "Generate 3 NPC bios for Wrath & Glory based ONLY on the provided context.\n\n"
        + grounding_instructions +
        f"Context summary: {context}\n\n"
        f"Canonical NPCs from source: {top_npcs}\n"
        f"Canonical Factions from source: {top_factions}\n"
        f"Canonical Locations from source: {top_locations}\n"
        f"Canonical Items from source: {top_items}\n\n"
        "Each bio should include: role, motivation, secret, hook.\n"
        "Use ONLY NPCs, factions, and locations from the canonical lists above.\n"
        "Do not create new NPCs or reference entities not in the provided lists.\n"
    )

    return {
        "rules": generate_text(rules_prompt, rag_config) or "",
        "adventure": generate_text(adventure_prompt, rag_config) or "",
        "bios": generate_text(bios_prompt, rag_config) or "",
    }


# PURPOSE: Generate TTRPG storyboard from context and specifications.
# DEPENDENCIES: generate_text.
# MODIFICATION NOTES: Creates visual storyboard format for scene planning.
def generate_storyboard(
    context_summary: str,
    pattern_report: Dict[str, Any],
    rag_config: Dict[str, Any],
    specifications: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate a TTRPG storyboard from context and optional specifications.
    
    Args:
        context_summary: Summarized context from retrieved documents.
        pattern_report: Pattern analysis report with entities.
        rag_config: RAG configuration.
        specifications: Optional dict with keys like:
            - character_sheets: List of character names/descriptions
            - combat_specs: Combat encounter specifications
            - materials: Miniature/resources available
            - scene_type: Type of scene (chase, combat, social, etc.)
            - enemy_forces: Enemy unit specifications
            - foreshadowing: Elements to foreshadow
    
    Returns:
        Storyboard text in structured format.
    """
    context = context_summary or ""
    entities = pattern_report.get("entities", {})
    top_npcs = ", ".join(entities.get("NPCs", [])[:10])
    top_factions = ", ".join(entities.get("Factions", [])[:10])
    top_locations = ", ".join(entities.get("Locations", [])[:10])
    top_items = ", ".join(entities.get("Items", [])[:15]) if entities.get("Items") else "None mentioned in source"
    
    # Build specifications text
    specs_text = ""
    if specifications:
        if specifications.get("character_sheets"):
            specs_text += f"\n**Player Characters:**\n{specifications['character_sheets']}\n"
        if specifications.get("player_context"):
            specs_text += f"\n**Player Context:**\n{specifications['player_context']}\n"
        if specifications.get("setting_constraints"):
            specs_text += f"\n**Setting Constraints:**\n{specifications['setting_constraints']}\n"
        if specifications.get("combat_specs"):
            specs_text += f"\n**Combat Specifications:**\n{specifications['combat_specs']}\n"
        if specifications.get("materials"):
            specs_text += f"\n**Available Materials/Miniatures:**\n{specifications['materials']}\n"
        if specifications.get("enemy_forces"):
            specs_text += f"\n**Enemy Forces:**\n{specifications['enemy_forces']}\n"
        if specifications.get("scene_type"):
            specs_text += f"\n**Scene Type:** {specifications['scene_type']}\n"
        if specifications.get("foreshadowing"):
            specs_text += f"\n**Foreshadowing Elements:**\n{specifications['foreshadowing']}\n"
    
    grounding_instructions = (
        "CRITICAL GROUNDING RULES:\n"
        "- ONLY use entities, items, locations, and NPCs that appear in the context below.\n"
        "- DO NOT invent: Space Marines with players, space settings, asteroids, void travel\n"
        "- DO NOT assume: Players are Space Marines (they are Rogue Trader crew)\n"
        "- MUST reference: Character sheets provided, campaign context, Wrath & Glory rules\n"
        "- Setting MUST be: Land-based highway with rubble, train track alongside\n"
        "- Use Wrath & Glory mechanics: DN tests, Wrath dice, Shifts, Conditions\n"
        "- When mentioning entities, use their exact names as provided in the canonical lists below.\n\n"
    )
    
    storyboard_prompt = (
        "Generate a TTRPG storyboard for Wrath & Glory in the following format:\n\n"
        "## STORYBOARD: [Scene Title]\n\n"
        "### ABSTRACTION LEVEL\n"
        "[High-level overview of the scene's purpose, stakes, and flow]\n\n"
        "### SCENE BREAKDOWN\n"
        "**Setup:** [Initial conditions, where characters start]\n"
        "**Inciting Incident:** [What triggers the action]\n"
        "**Rising Action:** [Key beats and complications]\n"
        "**Climax:** [Peak tension moment]\n"
        "**Resolution:** [How the scene concludes]\n\n"
        "### MECHANICAL ELEMENTS\n"
        "- **Combat Encounters:** [If applicable, brief encounter design]\n"
        "- **Skill Challenges:** [If applicable, key skill checks]\n"
        "- **Environmental Hazards:** [Terrain, obstacles, etc.]\n"
        "- **NPCs Present:** [Who's involved]\n\n"
        "### WRATH & GLORY MECHANICS\n"
        "MUST include specific DN values and mechanics. Examples:\n"
        "- **Skill Tests:** 'Pilot (Agi) DN 3 to weave through rubble', 'Athletics (Str) DN 4 to board moving train'\n"
        "- **Combat:** 'Attack (BS) DN 4, Damage 1d6+3, AP 1', 'Melee (WS) DN 3, Damage 1d6+2'\n"
        "- **Vehicle Rules:** 'Ramming test DN 4', 'Handling test DN 3 for sharp turns', 'Boarding action requires Athletics (Str) DN 4'\n"
        "- **Environmental Hazards:** 'Rubble: -1 to Pilot tests, DN penalty +1', 'High speed: +1 DN to all vehicle tests'\n"
        "- **Wrath Points:** 'Spend 1 Wrath to reroll failed Pilot test', 'Spend 2 Wrath to add +1d6 to damage'\n\n"
        "### MINIATURE SETUP\n"
        "[How to arrange miniatures on the table, terrain requirements]\n\n"
        "### FORESHADOWING & HOOKS\n"
        "MUST include foreshadowing elements from specifications. Examples:\n"
        "- Subtle hints at Carcharodon Astra presence (distress signals, orbital signatures, mysterious support)\n"
        "- Elements that connect to future scenes or reveal information\n"
        "- Hooks for next session or campaign arcs\n\n"
        "### GM NOTES\n"
        "[Tips for running the scene, pacing, key decisions, important reminders]\n\n"
        "---\n\n"
        "CRITICAL CONSTRAINTS - DO NOT VIOLATE:\n"
        "- Setting is LAND-BASED: highway racing alongside train track, rubble obstacles\n"
        "- DO NOT mention space, asteroids, or void travel\n"
        "- Players are ROGUE TRADER CREW, NOT Space Marines\n"
        "- Carcharodon Astra are FORESHADOWED (hinted at), NOT with the players\n"
        "- Rogue Trader PC is protecting their family's Hive world\n"
        "- MUST include Wrath & Glory mechanics (DN tests, Wrath dice, Shifts, etc.)\n"
        "- Enemy type MUST match specifications (if Ork units are listed, enemies are Orks, NOT cults)\n"
        "- MUST mention character names from character sheets (Brawn Solo, Godwin, Tarquinius, etc.)\n"
        "- MUST complete ALL sections: ABSTRACTION LEVEL, SCENE BREAKDOWN, MECHANICAL ELEMENTS, WRATH & GLORY MECHANICS, MINIATURE SETUP, FORESHADOWING & HOOKS, GM NOTES\n\n"
        "CAMPAIGN CONTEXT:\n"
        "- Rogue Trader crew from Harbinger of Woe\n"
        "- Mission: Protect family's Hive world from cryo-plague and cult activity\n"
        "- Setting: Glacial hive world with mag-train lines and frozen plains\n"
        "- Argent Maw mag-train is the target\n\n"
        + grounding_instructions +
        f"**Context Summary:**\n{context}\n\n"
        f"**Canonical NPCs from source:** {top_npcs}\n"
        f"**Canonical Factions from source:** {top_factions}\n"
        f"**Canonical Locations from source:** {top_locations}\n"
        f"**Canonical Items from source:** {top_items}\n"
        f"{specs_text}\n\n"
        "REQUIREMENTS FOR COMPLETE STORYBOARD:\n"
        "1. ALL sections must be completed (no missing sections)\n"
        "2. Enemy type must match specifications exactly (if Ork units specified, enemies are Orks)\n"
        "3. Character names from character sheets MUST be mentioned (Brawn Solo, Godwin, Tarquinius, etc.)\n"
        "4. WRATH & GLORY MECHANICS section must include specific DN values (e.g., 'Pilot (Agi) DN 3')\n"
        "5. FORESHADOWING & HOOKS must include hints at Carcharodon Astra if specified\n"
        "6. GM NOTES must provide actionable guidance for running the scene\n\n"
        "Generate the storyboard using ONLY the entities listed above and the specifications provided.\n"
        "Focus on creating an abstraction that helps understand the scene's structure before drilling into specifics.\n"
        "Make it useful for a GM to visualize and run the scene.\n"
        "Include specific Wrath & Glory mechanics with DN values throughout (e.g., 'Pilot (Agi) DN 3', not just 'use DN tests').\n"
    )
    
    return generate_text(storyboard_prompt, rag_config) or ""


# PURPOSE: Retrieve relevant context for a query.
# DEPENDENCIES: campaign_kb search service (optional), DocumentIndex.
# MODIFICATION NOTES: Uses DocumentIndex when available; B3: accepts retrieval_mode and tag_filters.
def retrieve_context(
    query: str,
    rag_config: Dict[str, Any],
    doc_index: Optional[DocumentIndex] = None,
    text_map: Optional[Dict[str, str]] = None,
    retrieval_mode: Optional[str] = None,
    tag_filters: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    if not query.strip():
        return []

    campaign_kb_root = Path(rag_config["campaign_kb_root"])
    use_kb_search = rag_config.get("use_kb_search", True)
    search_cfg = rag_config.get("search", {})
    limit = search_cfg.get("limit", 8)
    query_mode = rag_config.get("query_mode", {})
    if retrieval_mode is None:
        retrieval_mode = query_mode.get("retrieval_mode", "Strict Canon")
    if tag_filters is None:
        tag_filters = query_mode.get("tag_filters")

    if use_kb_search:
        try:
            if str(campaign_kb_root) not in sys.path:
                sys.path.append(str(campaign_kb_root))
            from app.database import SessionLocal
            from app.search.service import search_sections

            with SessionLocal() as db:
                results = search_sections(
                    db,
                    query=query,
                    limit=limit,
                    source_name=search_cfg.get("source_name"),
                    doc_type=search_cfg.get("doc_type"),
                )
            # Check if KB search returned results; if not, fall back to text scanning
            if results:
                return [
                    {
                        "section_id": section.id,
                        "document_id": section.document_id,
                        "section_title": section.section_title,
                        "text": section.raw_text,
                        "score": rank,
                    }
                    for section, rank in results
                ]
            else:
                logger.info("KB search returned empty results, falling back to text scan")
        except Exception as exc:
            logger.warning(f"Campaign KB search failed, falling back to text scan: {exc}")

    # Fast path: Use DocumentIndex if available (no need to load full text)
    if doc_index and doc_index.index:
        relevant_doc_keys = doc_index.retrieve(
            query, top_k=limit, retrieval_mode=retrieval_mode, tag_filters=tag_filters
        )
        if relevant_doc_keys and text_map:
            # Load only the relevant documents
            scored: List[Tuple[str, float, str]] = []
            for doc_key in relevant_doc_keys:
                if doc_key in text_map:
                    text = text_map[doc_key]
                    # Use index score (approximate) or recalculate
                    query_lower = query.lower()
                    query_terms = [term.lower() for term in query.split() if len(term) > 2]
                    lowered = text.lower()
                    score = sum(lowered.count(term) for term in query_terms)
                    if score > 0:
                        scored.append((doc_key, float(score), text))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            return [
                {"source": item[0], "score": item[1], "text": item[2][:2000]}
                for item in scored[:limit]
            ]

    # Fallback: Full text scanning (slower but works without index)
    if text_map is None:
        doc_paths = resolve_campaign_docs(campaign_kb_root, rag_config["campaign_docs"])
        text_map = read_campaign_docs(doc_paths)
        
        # Add PDF content if enabled
        if rag_config.get("include_pdfs", True):
            pdf_dir = Path(rag_config.get("pdf_extraction_dir", "Sources/_extracted_text"))
            pdf_config = rag_config.get("pdf_ingestion", {})
            pdf_text_map = read_pdf_texts(
                pdf_dir,
                file_pattern=rag_config.get("pdf_file_pattern", "*.txt"),
                max_chunk_size=pdf_config.get("max_chunk_size", 50000),
                max_chunks_per_pdf=pdf_config.get("max_chunks_per_pdf", 10),
                max_total_text_chars=pdf_config.get("max_total_text_chars", 2000000),
            )
            text_map.update(pdf_text_map)
    
    scored: List[Tuple[str, float, str]] = []
    
    # Extract query terms and phrases
    query_lower = query.lower()
    query_terms = [term.lower() for term in query.split() if term.strip()]
    
    # Also check for multi-word phrases (2-3 word combinations)
    query_phrases = []
    words = query.split()
    for i in range(len(words) - 1):
        phrase = " ".join(words[i:i+2]).lower()
        if len(phrase) > 3:  # Skip very short phrases
            query_phrases.append(phrase)
    for i in range(len(words) - 2):
        phrase = " ".join(words[i:i+3]).lower()
        if len(phrase) > 5:  # Skip very short phrases
            query_phrases.append(phrase)
    
    for path_str, text in text_map.items():
        lowered = text.lower()
        
        # Score based on individual terms
        term_score = sum(lowered.count(term) for term in query_terms)
        
        # Boost score for phrase matches (phrase matches worth 3x a single term)
        phrase_score = sum(lowered.count(phrase) * 3 for phrase in query_phrases)
        
        total_score = term_score + phrase_score
        if total_score > 0:
            scored.append((path_str, total_score, text))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        {"source": item[0], "score": item[1], "text": item[2][:2000]}
        for item in scored[:limit]
    ]


# PURPOSE: Write pipeline outputs to disk.
# DEPENDENCIES: filesystem access.
# MODIFICATION NOTES: Produces both JSON and Markdown summaries, optionally storyboard.
def write_outputs(
    output_dir: Path,
    pattern_report: Dict[str, Any],
    content_pack: Dict[str, str],
    context_summary: Optional[str],
    sources: List[str],
    storyboard: Optional[str] = None,
) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: Dict[str, str] = {}

    patterns_path = output_dir / "rag_patterns.json"
    patterns_path.write_text(json.dumps(pattern_report, indent=2), encoding="utf-8")
    outputs["patterns_json"] = str(patterns_path)

    patterns_md = output_dir / "rag_patterns.md"
    patterns_md.write_text(
        "# RAG Pattern Report\n\n"
        f"Sources: {', '.join(sources)}\n\n"
        f"```json\n{json.dumps(pattern_report, indent=2)}\n```\n",
        encoding="utf-8",
    )
    outputs["patterns_md"] = str(patterns_md)

    if context_summary:
        summary_path = output_dir / "rag_context_summary.md"
        summary_path.write_text(
            "# RAG Context Summary\n\n"
            f"{context_summary}\n",
            encoding="utf-8",
        )
        outputs["context_summary"] = str(summary_path)

    for key, text in content_pack.items():
        if text:
            out_path = output_dir / f"rag_generated_{key}.md"
            out_path.write_text(f"# RAG Generated: {key}\n\n{text}\n", encoding="utf-8")
            outputs[f"generated_{key}"] = str(out_path)

    if storyboard:
        storyboard_path = output_dir / "rag_storyboard.md"
        storyboard_path.write_text(storyboard, encoding="utf-8")
        outputs["storyboard"] = str(storyboard_path)

    return outputs


# PURPOSE: Run the full RAG pipeline end-to-end with query mode detection.
# DEPENDENCIES: All helpers in this module, DocumentIndex, EntityCache.
# MODIFICATION NOTES: B3: accepts retrieval_mode and tag_filters; passes to retrieve_context.
def run_pipeline(
    config_path: Path,
    query: Optional[str] = None,
    retrieval_mode: Optional[str] = None,
    tag_filters: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]

    if not rag_config.get("enabled", True):
        return {"status": "disabled", "outputs": {}}

    # Detect query mode vs analysis mode
    is_query_mode = query is not None and query.strip() and rag_config.get("query_mode", {}).get("skip_full_analysis", True)
    
    # Initialize caching if enabled
    cache_config = rag_config.get("cache", {})
    doc_index = None
    entity_cache = None
    
    if cache_config.get("enabled", True):
        cache_dir = Path(rag_config.get("vault_root", Path.cwd())) / cache_config.get("cache_dir", "Campaigns/_rag_cache")
        index_cache_path = cache_dir / cache_config.get("index_cache", "document_index.json")
        doc_index = DocumentIndex(index_cache_path)
        entity_cache = EntityCache(cache_dir)

    campaign_root = Path(rag_config["campaign_kb_root"])
    doc_paths = resolve_campaign_docs(campaign_root, rag_config["campaign_docs"])
    text_map = read_campaign_docs(doc_paths)
    # #region agent log
    _debug_log("rag_pipeline.py:468", "Campaign docs loaded", {"count": len(text_map), "total_chars": sum(len(v) for v in text_map.values())}, "B")
    # #endregion

    # Add PDF content if enabled (incremental ingestion with chunking)
    if rag_config.get("include_pdfs", True):
        pdf_dir = Path(rag_config.get("pdf_extraction_dir", "Sources/_extracted_text"))
        pdf_config = rag_config.get("pdf_ingestion", {})
        pdf_text_map = read_pdf_texts(
            pdf_dir,
            file_pattern=rag_config.get("pdf_file_pattern", "*.txt"),
            max_chunk_size=pdf_config.get("max_chunk_size", 50000),
            max_chunks_per_pdf=pdf_config.get("max_chunks_per_pdf", 10),
            max_total_text_chars=pdf_config.get("max_total_text_chars", 2000000),
        )
        text_map.update(pdf_text_map)
        logger.info(f"Added {len(pdf_text_map)} PDF sources to text map")
        # #region agent log
        _debug_log("rag_pipeline.py:575", "PDFs added to text_map", {"pdf_count": len(pdf_text_map), "pdf_chars": sum(len(v) for v in pdf_text_map.values())}, "B")
        # #endregion

    # Build/update document index if caching enabled
    if doc_index and cache_config.get("enabled", True):
        doc_index.build(
            text_map,
            rag_config.get("theme_keywords", []),
            invalidate_on_mtime=cache_config.get("invalidate_on_mtime_change", True),
            chunk_tags_config=rag_config.get("chunk_tags", {}),
        )

    # Query mode: Fast path with lazy evaluation
    if is_query_mode:
        logger.info(f"Query mode: Processing query '{query}' with lazy evaluation")
        
        # Retrieve relevant documents first (fast)
        query_context = retrieve_context(
            query, rag_config, doc_index=doc_index, text_map=text_map,
            retrieval_mode=retrieval_mode, tag_filters=tag_filters,
        )
        relevant_doc_keys = [item["source"] for item in query_context]
        
        if not relevant_doc_keys:
            logger.warning("No relevant documents found for query")
            return {
                "status": "success",
                "outputs": {},
                "pattern_report": {},
                "context_summary": None,
                "content_pack": {},
                "query_context": query_context,
            }
        
        logger.info(f"Retrieved {len(relevant_doc_keys)} relevant documents for query")
        
        # Lazy entity extraction: Only from retrieved documents
        pattern_report = {}
        if rag_config.get("pattern_analysis_enabled") and rag_config.get("query_mode", {}).get("lazy_entity_extraction", True):
            entities = extract_entities_from_docs(relevant_doc_keys, text_map, rag_config, entity_cache=entity_cache)
            # Build minimal pattern report from subset
            combined_relevant = "\n\n".join([text_map[k] for k in relevant_doc_keys if k in text_map])
            counts = {key: {name: entities[key].count(name) for name in set(entities[key])} for key in entities}
            themes = build_theme_counts(combined_relevant, rag_config.get("theme_keywords", []))
            pattern_report = {
                "entities": entities,
                "entity_counts": counts,
                "themes": themes,
                "source_docs": relevant_doc_keys,
            }
        
        # Lazy summarization: Only from retrieved documents
        context_summary = None
        if rag_config.get("content_generation_enabled"):
            context_summary = summarize_context_from_docs(relevant_doc_keys, text_map, rag_config)
        
        # Generate content from focused context
        content_pack = (
            generate_content_pack(context_summary or "", pattern_report, rag_config)
            if rag_config.get("content_generation_enabled")
            else {}
        )
        
        outputs = write_outputs(
            output_dir=rag_config["output_dir"],
            pattern_report=pattern_report,
            content_pack=content_pack,
            context_summary=context_summary,
            sources=relevant_doc_keys,  # Only relevant sources
        )
        
        return {
            "status": "success",
            "outputs": outputs,
            "pattern_report": pattern_report,
            "context_summary": context_summary,
            "content_pack": content_pack,
            "query_context": query_context,
        }
    
    # Analysis mode: Full corpus processing
    else:
        logger.info("Analysis mode: Processing full corpus")
        combined_text = "\n\n".join(text_map.values())
        # #region agent log
        _debug_log("rag_pipeline.py:477", "Combined text created", {"total_sources": len(text_map), "combined_length": len(combined_text), "campaign_sources": len([k for k in text_map.keys() if not k.startswith("[PDF]")]), "pdf_sources": len([k for k in text_map.keys() if k.startswith("[PDF]")])}, "B")
        # #endregion

        pattern_report = build_pattern_report(text_map, rag_config) if rag_config.get("pattern_analysis_enabled") else {}
        context_summary = summarize_context(combined_text, rag_config) if rag_config.get("content_generation_enabled") else None
        content_pack = (
            generate_content_pack(context_summary or "", pattern_report, rag_config)
            if rag_config.get("content_generation_enabled")
            else {}
        )

        outputs = write_outputs(
            output_dir=rag_config["output_dir"],
            pattern_report=pattern_report,
            content_pack=content_pack,
            context_summary=context_summary,
            sources=list(text_map.keys()),
        )

        return {
            "status": "success",
            "outputs": outputs,
            "pattern_report": pattern_report,
            "context_summary": context_summary,
            "content_pack": content_pack,
            "query_context": retrieve_context(
                query, rag_config, doc_index=doc_index, text_map=text_map,
                retrieval_mode=retrieval_mode, tag_filters=tag_filters,
            ) if query else [],
        }


# PURPOSE: Answer a query with retrieved context.
# DEPENDENCIES: retrieve_context and generate_text.
# MODIFICATION NOTES: Uses retrieval results to build a grounded answer.
def answer_query(query: str, config_path: Path, top_k: int = 8) -> Dict[str, Any]:
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    rag_config["search"]["limit"] = top_k

    context_items = retrieve_context(query, rag_config)
    context_text = "\n\n".join(item.get("text", "") for item in context_items)
    prompt = (
        "Answer the query using only the provided context. "
        "If the context is insufficient, say so.\n"
        f"Query: {query}\n"
        f"Context:\n{context_text}\n"
    )
    answer = generate_text(prompt, rag_config) or ""
    return {"answer": answer, "sources": context_items}


# PURPOSE: Run pattern analysis as a standalone action.
# DEPENDENCIES: build_pattern_report.
# MODIFICATION NOTES: Returns pattern report with sources.
def analyze_patterns(config_path: Path) -> Dict[str, Any]:
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    campaign_root = Path(rag_config["campaign_kb_root"])
    doc_paths = resolve_campaign_docs(campaign_root, rag_config["campaign_docs"])
    text_map = read_campaign_docs(doc_paths)
    return build_pattern_report(text_map, rag_config)


# PURPOSE: Full corpus analysis for batch processing (separate from query mode).
# DEPENDENCIES: build_pattern_report, summarize_context, generate_content_pack.
# MODIFICATION NOTES: Processes entire corpus - use for background jobs, not queries.
def analyze_full_corpus(config_path: Path) -> Dict[str, Any]:
    """
    Analyze full corpus - slow path for batch analysis.
    Use this for background jobs or when you need complete corpus statistics.
    For queries, use run_pipeline() with a query parameter (fast path).
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Dictionary with pattern_report, context_summary, and content_pack.
    """
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]

    if not rag_config.get("enabled", True):
        return {"status": "disabled"}

    campaign_root = Path(rag_config["campaign_kb_root"])
    doc_paths = resolve_campaign_docs(campaign_root, rag_config["campaign_docs"])
    text_map = read_campaign_docs(doc_paths)

    # Add PDF content if enabled
    if rag_config.get("include_pdfs", True):
        pdf_dir = Path(rag_config.get("pdf_extraction_dir", "Sources/_extracted_text"))
        pdf_config = rag_config.get("pdf_ingestion", {})
        pdf_text_map = read_pdf_texts(
            pdf_dir,
            file_pattern=rag_config.get("pdf_file_pattern", "*.txt"),
            max_chunk_size=pdf_config.get("max_chunk_size", 50000),
            max_chunks_per_pdf=pdf_config.get("max_chunks_per_pdf", 10),
            max_total_text_chars=pdf_config.get("max_total_text_chars", 2000000),
        )
        text_map.update(pdf_text_map)

    combined_text = "\n\n".join(text_map.values())

    pattern_report = build_pattern_report(text_map, rag_config) if rag_config.get("pattern_analysis_enabled") else {}
    context_summary = summarize_context(combined_text, rag_config) if rag_config.get("content_generation_enabled") else None
    content_pack = (
        generate_content_pack(context_summary or "", pattern_report, rag_config)
        if rag_config.get("content_generation_enabled")
        else {}
    )

    return {
        "status": "success",
        "pattern_report": pattern_report,
        "context_summary": context_summary,
        "content_pack": content_pack,
        "sources": list(text_map.keys()),
    }


# PURPOSE: CLI entrypoint for pipeline execution.
# DEPENDENCIES: argparse, run_pipeline.
# MODIFICATION NOTES: Supports query-driven runs.
def main() -> None:
    parser = argparse.ArgumentParser(description="Wrath and Glory RAG pipeline")
    parser.add_argument("--config", default="ingest_config.json", help="Path to config file")
    parser.add_argument("--query", default=None, help="Optional query for context retrieval")
    args = parser.parse_args()

    config_path = Path(args.config)
    result = run_pipeline(config_path=config_path, query=args.query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
