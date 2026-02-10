# PURPOSE: Ingest PDFs into Obsidian source/atomic notes using PDF++ outputs.
# DEPENDENCIES: PDF++ extracted text cache (when available); optional pypdf/pdfplumber.
# MODIFICATION NOTES: Initial ingestion pipeline with external PDF links.

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote as url_quote

from utils import (
    get_config_path,
    load_config,
    sanitize_cache_dir,
    truncate_text,
    validate_file_size,
    validate_vault_path,
)

# Configure logging early so logger is available for import error handling
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

try:
    from extractors.extractor_chain import ExtractorChain
    EXTRACTOR_CHAIN_AVAILABLE = True
except ImportError:
    EXTRACTOR_CHAIN_AVAILABLE = False
    logger.warning("Extractor chain not available. Using legacy extraction.")

try:
    from entity_extractor import extract_entities_from_text, get_extractor
    ENTITY_EXTRACTION_AVAILABLE = True
except ImportError:
    ENTITY_EXTRACTION_AVAILABLE = False
    logger.warning("Entity extraction not available. Install spaCy for automatic entity extraction.")

try:
    from error_handling import ErrorCollector, retry_with_backoff, with_fallback
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False
    # Create minimal fallbacks
    class ErrorCollector:
        def __init__(self): pass
        def add_error(self, *args, **kwargs): pass
        def add_warning(self, *args, **kwargs): pass
        def print_summary(self): pass
    def retry_with_backoff(*args, **kwargs):
        def decorator(func): return func
        return decorator
    def with_fallback(*args, **kwargs):
        def decorator(func): return func
        return decorator

try:
    from performance_profiler import (
        profile_operation,
        record_io_read,
        record_io_write,
        get_collector,
        export_results,
        print_summary,
        reset_collector,
    )
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    # Create no-op functions if profiler not available
    def profile_operation(name: str, enable_memory: bool = True):
        from contextlib import nullcontext
        return nullcontext()
    def record_io_read(path: str, bytes_read: int) -> None:
        pass
    def record_io_write(path: str, bytes_written: int) -> None:
        pass
    def get_collector():
        return None
    def export_results(json_path=None, csv_path=None) -> None:
        pass
    def print_summary() -> None:
        pass
    def reset_collector() -> None:
        pass


# PURPOSE: Validate template file exists and contains required placeholders.
# DEPENDENCIES: Template file path, expected placeholders.
# MODIFICATION NOTES: Raises ValueError if template is invalid.
def validate_template(template_path: Path, required_placeholders: List[str]) -> None:
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    try:
        content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"Failed to read template file {template_path}: {e}") from e
    
    missing_placeholders = []
    for placeholder in required_placeholders:
        if f"{{{{{placeholder}}}}}" not in content:
            missing_placeholders.append(placeholder)
    
    if missing_placeholders:
        raise ValueError(
            f"Template {template_path} missing required placeholders: {', '.join(missing_placeholders)}"
        )


# PURPOSE: Ensure required directories exist.
# DEPENDENCIES: Path write access on vault.
# MODIFICATION NOTES: Creates directories if missing.
def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


# PURPOSE: Find all PDFs under the configured root.
# DEPENDENCIES: Local filesystem.
# MODIFICATION NOTES: Returns sorted list of Paths. Validates file sizes.
def list_pdfs(pdf_root: Path, max_size_mb: int = 100) -> List[Path]:
    """
    Find all PDF files in the configured root directory.
    
    Args:
        pdf_root: Root directory to search for PDFs.
        max_size_mb: Maximum file size in megabytes (default: 100MB).
        
    Returns:
        Sorted list of PDF file paths.
    """
    with profile_operation("list_pdfs", enable_memory=False):
        pdfs = []
        try:
            for pdf_path in pdf_root.rglob("*.pdf"):
                try:
                    validate_file_size(pdf_path, max_size_mb)
                    pdfs.append(pdf_path)
                except ValueError as e:
                    logger.warning(f"Skipping {pdf_path.name}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error checking {pdf_path.name}: {e}")
                    continue
        except PermissionError as e:
            logger.error(f"Permission denied accessing {pdf_root}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scanning PDF directory: {e}")
            raise
        
        return sorted(pdfs)


# PURPOSE: Normalize a filename to a safe Obsidian note name.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Removes illegal characters and trims whitespace.
def safe_note_name(stem: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", " ", stem).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


# PURPOSE: Convert a local path to a file:// URL.
# DEPENDENCIES: urllib.parse.quote for encoding.
# MODIFICATION NOTES: Uses forward slashes and URL-encodes spaces. Validates path.
def to_file_url(path: Path, vault_root: Optional[Path] = None) -> str:
    """
    Convert a local path to a file:// URL.
    
    Args:
        path: Path to convert to URL.
        vault_root: Optional vault root for validation.
        
    Returns:
        file:// URL string.
    """
    resolved = path.resolve()
    
    # Validate path is within vault if vault_root provided
    if vault_root:
        try:
            resolved = validate_vault_path(vault_root, resolved)
        except ValueError as e:
            logger.warning(f"Path validation failed for {path}: {e}")
            # Continue anyway but log the warning
    
    normalized = resolved.as_posix()
    return f"file:///{url_quote(normalized)}"


# PURPOSE: Find extracted text produced by PDF++ if present.
# DEPENDENCIES: PDF++ cache directories (configurable).
# MODIFICATION NOTES: Searches by PDF stem in configured cache paths. Validates paths.
def find_pdfplus_text(
    pdf_path: Path,
    vault_root: Path,
    cache_dirs: Iterable[str],
    extensions: Iterable[str],
) -> Optional[Path]:
    """
    Find extracted text file for a PDF in PDF++ cache directories.
    
    Args:
        pdf_path: Path to the PDF file.
        vault_root: Root directory of the vault.
        cache_dirs: List of relative cache directory names.
        extensions: List of file extensions to search for.
        
    Returns:
        Path to extracted text file if found, None otherwise.
    """
    with profile_operation(f"find_pdfplus_text({pdf_path.name})", enable_memory=False):
        stem = pdf_path.stem
        for rel_dir in cache_dirs:
            try:
                # Sanitize directory name to prevent path traversal
                sanitized_dir = sanitize_cache_dir(rel_dir)
                cache_root = vault_root / sanitized_dir
                cache_root = validate_vault_path(vault_root, cache_root.resolve())
                
                if not cache_root.exists():
                    continue
                
                for ext in extensions:
                    # Validate extension doesn't contain path separators
                    if "/" in ext or "\\" in ext:
                        logger.warning(f"Invalid extension contains path separator: {ext}")
                        continue
                    
                    candidates = list(cache_root.rglob(f"{stem}{ext}"))
                    if candidates:
                        # Validate the found file is within vault
                        found_path = validate_vault_path(vault_root, candidates[0])
                        return found_path
            except ValueError as e:
                logger.warning(f"Invalid cache directory '{rel_dir}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Error searching cache directory '{rel_dir}': {e}")
                continue
        return None


# PURPOSE: Extract text for a PDF using extractor chain (PDF++ → pypdf → pdfplumber → OCR).
# DEPENDENCIES: Extractor chain module.
# MODIFICATION NOTES: Phase 1 - Refactored to use pluggable extractor architecture.
def extract_text(
    pdf_path: Path,
    vault_root: Path,
    extractor_chain=None,
    cache_dirs: Optional[Iterable[str]] = None,
    extensions: Optional[Iterable[str]] = None,
    config: Optional[Dict[str, object]] = None,
) -> Tuple[str, Optional[Path], dict]:
    """
    Extract text from a PDF file using extractor chain.
    
    Uses extractor chain with fallback: PDF++ cache → pypdf → pdfplumber → OCR (if enabled).
    Falls back to legacy extraction if extractor chain not available.
    
    Args:
        pdf_path: Path to the PDF file.
        vault_root: Root directory of the vault.
        extractor_chain: ExtractorChain instance (optional).
        cache_dirs: List of relative cache directory names (legacy fallback).
        extensions: List of file extensions to search for (legacy fallback).
        config: Optional configuration dictionary (legacy fallback).
        
    Returns:
        Tuple of (extracted_text, source_path, metadata).
        - extracted_text: Extracted text content
        - source_path: Path to source file if using cache, None otherwise
        - metadata: Dict with extraction metadata (method, confidence, etc.)
    """
    with profile_operation(f"extract_text({pdf_path.name})", enable_memory=True):
        # Use extractor chain if available
        if extractor_chain and EXTRACTOR_CHAIN_AVAILABLE:
            text, source_path, metadata = extractor_chain.extract(pdf_path, vault_root)
            
            # Record I/O if we read from a file
            if source_path:
                try:
                    bytes_read = len(text.encode('utf-8'))
                    record_io_read(str(source_path), bytes_read)
                except Exception:
                    pass
            elif text:
                # Record PDF read if we extracted directly
                try:
                    pdf_size = pdf_path.stat().st_size
                    record_io_read(str(pdf_path), pdf_size)
                except Exception:
                    pass
            
            return text, source_path, metadata
        
        # Legacy fallback if extractor chain not available
        if cache_dirs is None or extensions is None:
            logger.warning("Legacy extraction requires cache_dirs and extensions")
            return "", None, {"method": "none", "error": "Missing parameters"}
        
        pdfplus_text = find_pdfplus_text(pdf_path, vault_root, cache_dirs, extensions)
        if pdfplus_text and pdfplus_text.exists():
            try:
                text = pdfplus_text.read_text(encoding="utf-8", errors="replace")
                record_io_read(str(pdfplus_text), len(text.encode('utf-8')))
                return text, pdfplus_text, {"method": "pdfplus", "cache_hit": True}
            except Exception as e:
                logger.warning(f"Failed to read PDF++ cache for {pdf_path.name}: {e}")

        # Fallback to pypdf
        try:
            from pypdf import PdfReader  # type: ignore

            pdf_size = pdf_path.stat().st_size
            record_io_read(str(pdf_path), pdf_size)
            reader = PdfReader(str(pdf_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                logger.info(f"Extracted text using pypdf for {pdf_path.name}")
                return text, None, {"method": "pypdf", "success": True}
        except ImportError:
            logger.debug("pypdf not available")
        except Exception as e:
            logger.warning(f"pypdf extraction failed for {pdf_path.name}: {e}")

        # Fallback to pdfplumber
        try:
            import pdfplumber  # type: ignore

            pdf_size = pdf_path.stat().st_size
            record_io_read(str(pdf_path), pdf_size)
            with pdfplumber.open(str(pdf_path)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                logger.info(f"Extracted text using pdfplumber for {pdf_path.name}")
                return text, None, {"method": "pdfplumber", "success": True}
        except ImportError:
            logger.debug("pdfplumber not available")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {pdf_path.name}: {e}")
        
        logger.warning(f"No text extraction method succeeded for {pdf_path.name}")
        return "", None, {"method": "none", "error": "All extractors failed"}


# PURPOSE: Write extracted text to a dedicated text file in the vault.
# DEPENDENCIES: Vault write access.
# MODIFICATION NOTES: Returns the path to the written file or None.
def write_extracted_text(text: str, out_dir: Path, stem: str) -> Optional[Path]:
    if not text.strip():
        return None
    with profile_operation(f"write_extracted_text({stem})", enable_memory=False):
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{stem}.txt"
        out_path.write_text(text, encoding="utf-8")
        bytes_written = len(text.encode('utf-8'))
        record_io_write(str(out_path), bytes_written)
        return out_path


# Template cache to avoid repeated file reads
_template_cache: Dict[Path, str] = {}


# PURPOSE: Read and apply a simple template with placeholders.
# DEPENDENCIES: Template file path.
# MODIFICATION NOTES: Supports {{key}} placeholders. Uses caching to avoid repeated reads.
def render_template(template_path: Path, values: Dict[str, str]) -> str:
    # Use cached template if available
    if template_path not in _template_cache:
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        try:
            content = template_path.read_text(encoding="utf-8")
            _template_cache[template_path] = content
            record_io_read(str(template_path), len(content.encode('utf-8')))
        except Exception as e:
            raise IOError(f"Failed to read template file {template_path}: {e}") from e
    else:
        content = _template_cache[template_path]
    
    # Create a copy to avoid modifying cached content
    content = content
    for key, value in values.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content


# PURPOSE: Inject source path/link YAML fields into a note.
# DEPENDENCIES: YAML frontmatter in the template.
# MODIFICATION NOTES: Inserts fields after source_file.
def inject_source_fields(content: str, source_path: str, source_link: str) -> str:
    pattern = r"(source_file: .+)"
    return re.sub(
        pattern,
        lambda match: (
            f"{match.group(1)}\n"
            f"source_path: \"{source_path}\"\n"
            f"source_link: \"{source_link}\""
        ),
        content,
        count=1,
    )


# PURPOSE: Extract PDF metadata (title, author, creation date).
# DEPENDENCIES: pypdf library.
# MODIFICATION NOTES: Returns dict with metadata or empty dict on failure.
def extract_pdf_metadata(pdf_path: Path, text: Optional[str] = None) -> Dict[str, str]:
    """
    Extract metadata from PDF file with optional citation enrichment (Phase 2).
    
    Args:
        pdf_path: Path to PDF file.
        text: Optional document text for citation extraction.
        
    Returns:
        Dictionary with metadata keys: title, author, subject, creator, creation_date, doi, isbn, etc.
    """
    try:
        from metadata_extractor import extract_pdf_metadata as extract_metadata, enrich_metadata_with_citations
        
        metadata = extract_metadata(pdf_path)
        
        # Enrich with citations if text provided
        if text:
            metadata = enrich_metadata_with_citations(metadata, text)
        
        return metadata
    except ImportError:
        # Fallback to basic extraction
        logger.debug("metadata_extractor not available, using basic extraction")
        return _extract_pdf_metadata_basic(pdf_path)


def _extract_pdf_metadata_basic(pdf_path: Path) -> Dict[str, str]:
    """Basic PDF metadata extraction (fallback)."""
    metadata = {}
    
    try:
        from pypdf import PdfReader  # type: ignore
        
        reader = PdfReader(str(pdf_path))
        pdf_metadata = reader.metadata
        
        if pdf_metadata:
            if pdf_metadata.get("/Title"):
                metadata["title"] = pdf_metadata["/Title"].strip()
            if pdf_metadata.get("/Author"):
                metadata["author"] = pdf_metadata["/Author"].strip()
            if pdf_metadata.get("/Subject"):
                metadata["subject"] = pdf_metadata["/Subject"].strip()
            if pdf_metadata.get("/Creator"):
                metadata["creator"] = pdf_metadata["/Creator"].strip()
            if pdf_metadata.get("/CreationDate"):
                # Parse PDF date format (D:YYYYMMDDHHmmSSOHH'mm')
                try:
                    date_str = pdf_metadata["/CreationDate"]
                    if date_str.startswith("D:"):
                        date_str = date_str[2:]
                    # Extract year, month, day
                    if len(date_str) >= 8:
                        year = date_str[0:4]
                        month = date_str[4:6]
                        day = date_str[6:8]
                        metadata["creation_date"] = f"{year}-{month}-{day}"
                except Exception:
                    pass
            
            # Get page count
            if hasattr(reader, "pages"):
                metadata["page_count"] = str(len(reader.pages))
        
    except ImportError:
        logger.debug("pypdf not available for metadata extraction")
    except Exception as e:
        logger.debug(f"Failed to extract PDF metadata: {e}")
    
    return metadata


# PURPOSE: Build source note content for a PDF.
# DEPENDENCIES: Template schema and extracted text.
# MODIFICATION NOTES: Adds summary lines, entities, metadata, AI summary, and a source link.
def build_source_note(
    template_path: Path,
    title: str,
    source_file: str,
    source_link: str,
    excerpt: str,
    extracted_text_path: Optional[Path],
    created: str,
    entities: Optional[Dict[str, List[str]]] = None,
    pdf_metadata: Optional[Dict[str, str]] = None,
    text: str = "",
    config: Optional[Dict[str, object]] = None,
    tables: Optional[List[Dict[str, Any]]] = None,
) -> str:
    # Use PDF title if available, otherwise use filename
    display_title = pdf_metadata.get("title", title) if pdf_metadata else title
    
    # Determine page count
    page_count = pdf_metadata.get("page_count", "unknown") if pdf_metadata else "unknown"
    if page_count == "unknown":
        page_count = "unknown (PDF++ extraction pending)"
    
    values = {
        "title": display_title,
        "source_file": source_file,
        "source_pages": page_count,
        "doc_type": "unverified",
        "date": created,
    }
    content = render_template(template_path, values)
    content = inject_source_fields(content, source_file, source_link)
    
    # Inject PDF metadata into frontmatter if available
    if pdf_metadata:
        metadata_fields = []
        if pdf_metadata.get("author"):
            metadata_fields.append(f"author: \"{pdf_metadata['author']}\"")
        if pdf_metadata.get("subject"):
            metadata_fields.append(f"subject: \"{pdf_metadata['subject']}\"")
        if pdf_metadata.get("creation_date"):
            metadata_fields.append(f"pdf_creation_date: \"{pdf_metadata['creation_date']}\"")
        
        if metadata_fields:
            # Insert after date field
            content = re.sub(
                r"(date: .+\n)",
                r"\1" + "\n".join(metadata_fields) + "\n",
                content,
                count=1,
            )

    summary_lines = []
    if extracted_text_path:
        summary_lines.append(f"- Extracted text saved to: [[{extracted_text_path.as_posix()}]]")
    else:
        summary_lines.append("- Extracted text not found. Open PDF in Obsidian PDF++ and run extraction.")
    if excerpt:
        summary_lines.append("- Excerpt captured for quick review.")

    content = content.replace("## Summary\n\n- ", "## Summary\n\n" + "\n".join(summary_lines) + "\n\n")

    if excerpt:
        excerpt_block = f"\n## Extracted Text Excerpt\n\n> {excerpt}\n"
        content = content + excerpt_block

    # Add extracted entities section if available
    if entities:
        entity_section = "\n## Extracted Entities\n\n"
        entity_labels = ["NPCs", "Factions", "Locations", "Items", "Rules/Mechanics"]
        for label in entity_labels:
            entity_list = entities.get(label, [])
            if entity_list:
                entity_str = ", ".join(entity_list)
                entity_section += f"- {label}: {entity_str}\n"
        
        if entity_section != "\n## Extracted Entities\n\n":
            content = content + entity_section + "\n"
    
    # Add AI summary if enabled
    if config and config.get("features", {}).get("ai_summarization_enabled", False) and text:
        try:
            from ai_summarizer import summarize_text, get_cached_summary, save_summary_cache
            import hashlib
            
            # Get text hash for caching
            text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
            
            # Get cache directory from config
            ai_config = config.get("ai_summarization", {})
            cache_dir_str = ai_config.get("cache_dir", "Sources/_summaries")
            
            # Resolve cache directory - need to get vault_root from config
            try:
                vault_root_path = Path(str(config.get("vault_root", "")))
                if vault_root_path.exists():
                    cache_dir = vault_root_path / cache_dir_str
                    cache_dir = validate_vault_path(vault_root_path, cache_dir.resolve())
                else:
                    # Fallback: use relative path (will be resolved later if needed)
                    cache_dir = Path(cache_dir_str)
            except Exception as e:
                logger.warning(f"Failed to resolve cache directory: {e}")
                cache_dir = Path(cache_dir_str)
            
            # Generate summary (caching is handled internally by summarize_text)
            logger.info(f"Generating AI summary for {title}")
            
            # Get provider and determine if we need api_key
            provider = ai_config.get("provider", "ollama")
            model = ai_config.get("model", "llama2" if provider == "ollama" else "gpt-4")
            
            # Only pass api_key for API-based providers (not Ollama)
            api_key = None
            if provider in ("openai", "anthropic"):
                api_key = ai_config.get("api_key")
            
            # Get Ollama endpoint if configured
            ollama_endpoint = None
            if provider == "ollama":
                ollama_endpoint = ai_config.get("ollama_endpoint")
            
            summary = summarize_text(
                text,
                provider=provider,
                model=model,
                api_key=api_key,  # None for Ollama
                max_tokens=ai_config.get("max_tokens", 500),
                temperature=ai_config.get("temperature", 0.7),
                rpg_mode=True,  # Use RPG-specific prompts
                cache_dir=cache_dir,  # Pass cache_dir for automatic caching
                ollama_endpoint=ollama_endpoint,  # Pass Ollama endpoint if configured
            )
            
            if summary:
                logger.info(f"AI summary generated for {title}")
            else:
                logger.warning(f"Failed to generate AI summary for {title}")
            
            # Add summary section to content
            if summary:
                content += f"\n## AI Summary\n\n{summary}\n"
        except ImportError:
            logger.debug("AI summarization module not available")
        except Exception as e:
            logger.warning(f"AI summarization failed: {e}")
        
        # Add tables section if tables extracted
        if tables:
            tables_section = "\n## Extracted Tables\n\n"
            for table in tables:
                page = table.get("page", 0)
                table_index = table.get("table_index", 0)
                caption = table.get("caption")
                markdown = table.get("markdown", "")
                
                tables_section += f"### Table {table_index} (Page {page})\n\n"
                if caption:
                    tables_section += f"*{caption}*\n\n"
                tables_section += markdown + "\n\n"
            
            content = content + tables_section
            logger.debug(f"Added {len(tables)} tables to source note")

    source_section = f"\n## Source\n\n- [Open PDF]({source_link})\n"
    if "## Source" not in content:
        content = content + source_section

    return content


# PURPOSE: Parse entity lists from a source note.
# DEPENDENCIES: Source note format in Templates/source_note.md.
# MODIFICATION NOTES: Extracts entries from the Extracted Entities section.
def parse_entities(source_content: str) -> Dict[str, List[str]]:
    entity_map = {
        "NPCs": [],
        "Factions": [],
        "Locations": [],
        "Items": [],
        "Rules/Mechanics": [],
    }
    for label in entity_map.keys():
        match = re.search(rf"- {re.escape(label)}:\s*(.*)", source_content)
        if not match:
            continue
        raw = match.group(1).strip()
        if not raw:
            continue
        parts = [p.strip() for p in re.split(r"[;,]", raw) if p.strip()]
        entity_map[label].extend(parts)
    return entity_map


# PURPOSE: Build a rule note content.
# DEPENDENCIES: Vault rule schema from 00_VAULT_RULES.md.
# MODIFICATION NOTES: Creates a draft rule note linked to source.
def build_rule_note(title: str, rule_type: str, source_ref: str, created: str) -> str:
    return (
        "<!--\n"
        f"# PURPOSE: Atomic rule note for {title}.\n"
        f"# DEPENDENCIES: {source_ref}\n"
        "# MODIFICATION NOTES: Auto-created from source; pending review.\n"
        "-->\n\n"
        "---\n"
        f"title: \"{title}\"\n"
        f"rule_type: \"{rule_type}\"\n"
        f"created: \"{created}\"\n"
        "tags: [\"type/rule\", \"status/draft\"]\n"
        f"source_refs: [\"{source_ref}\"]\n"
        "---\n\n"
        "## Summary\n\n"
        "- Pending review.\n\n"
        "## Details\n\n"
        "- \n"
    )


# PURPOSE: Build an entity note content from the entity template.
# DEPENDENCIES: Templates/entity_note.md.
# MODIFICATION NOTES: Populates minimal fields and links to source.
def build_entity_note(
    template_path: Path,
    title: str,
    entity_type: str,
    source_ref: str,
    created: str,
) -> str:
    values = {
        "title": title,
        "entity_type": entity_type,
        "date": created,
    }
    content = render_template(template_path, values)
    content = content.replace(
        "source_refs: []",
        f"source_refs: [\"{source_ref}\"]",
    )
    return content


# PURPOSE: Write a note if it does not already exist.
# DEPENDENCIES: Filesystem write access.
# MODIFICATION NOTES: Optional overwrite behavior.
def write_note(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    with profile_operation(f"write_note({path.name})", enable_memory=False):
        path.write_text(content, encoding="utf-8")
        bytes_written = len(content.encode('utf-8'))
        record_io_write(str(path), bytes_written)


# PURPOSE: Process a single PDF and create its notes.
# DEPENDENCIES: Config paths, templates, and PDF text extraction.
# MODIFICATION NOTES: Extracted from ingest_pdfs for parallel processing.
def process_single_pdf(
    pdf_path: Path,
    vault_root: Path,
    source_notes_dir: Path,
    rules_dir: Path,
    npcs_dir: Path,
    factions_dir: Path,
    locations_dir: Path,
    items_dir: Path,
    extracted_text_dir: Path,
    template_source: Path,
    template_entity: Path,
    extractor_chain=None,
    cache_dirs: Optional[Iterable[str]] = None,
    extensions: Optional[Iterable[str]] = None,
    max_excerpt_chars: int = 2000,
    created: str = "",
    overwrite: bool = False,
    config: Optional[Dict[str, object]] = None,
) -> Tuple[bool, Optional[str]]:
    """Process a single PDF and return (success, error_message)."""
    try:
        title = safe_note_name(pdf_path.stem)
        source_note_path = source_notes_dir / f"{title}.md"
        source_link = to_file_url(pdf_path, vault_root)
        source_file = pdf_path.as_posix()

        try:
            text, source_path, metadata = extract_text(
                pdf_path,
                vault_root,
                extractor_chain=extractor_chain,
                cache_dirs=cache_dirs,
                extensions=extensions,
                config=config,  # Pass config for OCR support
            )
            # Log extraction method if available
            if metadata and metadata.get("method"):
                logger.debug(f"Extracted text using {metadata.get('method')} for {pdf_path.name}")
        except Exception as e:
            logger.warning(f"Failed to extract text from {pdf_path.name}: {e}")
            text = ""
            source_path = None
            metadata = {}
            source_path = None
            metadata = {}

        excerpt = truncate_text(text.strip().replace("\n", " "), max_excerpt_chars) if text else ""
        
        try:
            extracted_text_path = write_extracted_text(text, extracted_text_dir, title)
        except Exception as e:
            logger.warning(f"Failed to write extracted text for {pdf_path.name}: {e}")
            extracted_text_path = None

        # Extract PDF metadata (with citation enrichment if text available)
        pdf_metadata = None
        try:
            pdf_metadata = extract_pdf_metadata(pdf_path, text=text)
            if pdf_metadata:
                logger.debug(f"Extracted metadata from {pdf_path.name}: {list(pdf_metadata.keys())}")
        except Exception as e:
            logger.debug(f"Failed to extract metadata from {pdf_path.name}: {e}")

        # Extract tables if enabled
        tables = []
        if config and config.get("features", {}).get("table_extraction_enabled", False):
            try:
                from table_extractor import extract_tables
                table_config = config.get("table_extraction", {})
                tables = extract_tables(
                    pdf_path,
                    method=table_config.get("method", "pdfplumber"),
                    fallback_method=table_config.get("fallback_method", "camelot"),
                )
                if tables:
                    logger.info(f"Extracted {len(tables)} tables from {pdf_path.name}")
            except Exception as e:
                logger.warning(f"Failed to extract tables from {pdf_path.name}: {e}")

        # Extract entities automatically if available
        extracted_entities = None
        if ENTITY_EXTRACTION_AVAILABLE and text:
            try:
                extractor = get_extractor()
                if extractor.is_available():
                    extracted_entities = extract_entities_from_text(text)
                    logger.info(
                        f"Auto-extracted entities from {pdf_path.name}: "
                        f"{sum(len(v) for v in extracted_entities.values())} total"
                    )
            except Exception as e:
                logger.warning(f"Failed to extract entities from {pdf_path.name}: {e}")

        try:
            source_content = build_source_note(
                template_source,
                title,
                source_file,
                source_link,
                excerpt,
                extracted_text_path,
                created,
                entities=extracted_entities,
                pdf_metadata=pdf_metadata,
                text=text,  # Pass text for AI summarization
                config=config,  # Pass config for AI summarization
                tables=tables,  # Pass tables for table section
            )
        except Exception as e:
            logger.error(f"Failed to build source note for {pdf_path.name}: {e}")
            return False, str(e)

        try:
            write_note(source_note_path, source_content, overwrite)
        except Exception as e:
            logger.error(f"Failed to write source note for {pdf_path.name}: {e}")
            return False, str(e)

        # Parse entities from source note (combines manual and auto-extracted)
        entities = parse_entities(source_content)
        
        # Merge with auto-extracted entities if available
        if extracted_entities:
            for key in entities:
                if key in extracted_entities and extracted_entities[key]:
                    # Add auto-extracted entities that aren't already in the list
                    existing = set(entities[key])
                    new_entities = [e for e in extracted_entities[key] if e not in existing]
                    entities[key].extend(new_entities)
        
        source_ref = f"[[{title}]]"

        # Process rules
        for rule_name in entities.get("Rules/Mechanics", []):
            if not rule_name:
                continue
            try:
                rule_title = safe_note_name(rule_name)
                rule_path = rules_dir / f"{rule_title}.md"
                rule_content = build_rule_note(rule_title, "rule", source_ref, created)
                write_note(rule_path, rule_content, overwrite)
            except Exception as e:
                logger.warning(f"Failed to create rule note for {rule_name}: {e}")

        # Process entities
        entity_targets = [
            ("NPCs", npcs_dir, "npc"),
            ("Factions", factions_dir, "faction"),
            ("Locations", locations_dir, "location"),
            ("Items", items_dir, "item"),
        ]
        for label, target_dir, entity_type in entity_targets:
            for entity_name in entities.get(label, []):
                if not entity_name:
                    continue
                try:
                    entity_title = safe_note_name(entity_name)
                    entity_path = target_dir / f"{entity_title}.md"
                    entity_content = build_entity_note(
                        template_entity, entity_title, entity_type, source_ref, created
                    )
                    write_note(entity_path, entity_content, overwrite)
                except Exception as e:
                    logger.warning(f"Failed to create entity note for {entity_name}: {e}")
        
        return True, None
    except Exception as e:
        logger.error(f"Unexpected error processing {pdf_path.name}: {e}", exc_info=True)
        return False, str(e)


# PURPOSE: Create source notes and derived atomic notes from PDFs.
# DEPENDENCIES: Config, templates, and PDF text extraction.
# MODIFICATION NOTES: Orchestrates ingestion pipeline.
def ingest_pdfs(config: Dict[str, object], overwrite: bool) -> None:
    """
    Create source notes and derived atomic notes from PDFs.
    
    Args:
        config: Configuration dictionary.
        overwrite: Whether to overwrite existing notes.
    """
    vault_root = Path(str(config["vault_root"]))
    vault_root = vault_root.resolve()
    
    # Validate and get all paths from config
    try:
        pdf_root = get_config_path(vault_root, config, "pdf_root")
        source_notes_dir = get_config_path(vault_root, config, "source_notes_dir")
        rules_dir = get_config_path(vault_root, config, "rules_dir")
        npcs_dir = get_config_path(vault_root, config, "npcs_dir")
        factions_dir = get_config_path(vault_root, config, "factions_dir")
        locations_dir = get_config_path(vault_root, config, "locations_dir")
        items_dir = get_config_path(vault_root, config, "items_dir")
        extracted_text_dir = get_config_path(vault_root, config, "extracted_text_dir")
        template_source = get_config_path(vault_root, config, "templates.source_note")
        template_entity = get_config_path(vault_root, config, "templates.entity_note")
    except (KeyError, ValueError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Validate templates before processing and pre-load into cache
    try:
        validate_template(template_source, ["title", "source_file", "source_pages", "doc_type", "date"])
        validate_template(template_entity, ["title", "entity_type", "date"])
        # Pre-load templates into cache to avoid repeated reads
        _template_cache[template_source] = template_source.read_text(encoding="utf-8")
        _template_cache[template_entity] = template_entity.read_text(encoding="utf-8")
        record_io_read(str(template_source), len(_template_cache[template_source].encode('utf-8')))
        record_io_read(str(template_entity), len(_template_cache[template_entity].encode('utf-8')))
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"ERROR: Template validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    cache_dirs = config.get("pdf_text_cache_dirs", [])
    extensions = config.get("pdf_text_cache_extensions", [".txt", ".md"])
    max_excerpt_chars = int(config.get("max_excerpt_chars", 2000))
    
    # Initialize extractor chain if available
    extractor_chain = None
    if EXTRACTOR_CHAIN_AVAILABLE:
        try:
            extractor_chain = ExtractorChain(config)
            logger.info("Extractor chain initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize extractor chain: {e}. Using legacy extraction.")

    # Ensure directories exist with error handling
    try:
        ensure_directories(
            [
                source_notes_dir,
                rules_dir,
                npcs_dir,
                factions_dir,
                locations_dir,
                items_dir,
                extracted_text_dir,
            ]
        )
    except Exception as e:
        print(f"ERROR: Failed to create required directories: {e}", file=sys.stderr)
        sys.exit(1)

    created = dt.date.today().isoformat()
    
    # Get max file size from config (default 100MB)
    max_pdf_size_mb = int(config.get("max_pdf_size_mb", 100))
    
    try:
        pdfs = list_pdfs(pdf_root, max_size_mb=max_pdf_size_mb)
    except Exception as e:
        logger.error(f"Failed to list PDFs: {e}")
        sys.exit(1)
    
    if not pdfs:
        logger.info("No PDFs found in configured directory.")
        return
    
    logger.info(f"Found {len(pdfs)} PDFs to process")
    
    # Initialize error collector for summary reporting
    error_collector = ErrorCollector() if ERROR_HANDLING_AVAILABLE else None
    
    # Thread-safe counters for parallel processing
    processed_count = 0
    error_count = 0
    progress_lock = Lock()
    
    # Use parallel processing if max_workers > 1
    max_workers = config.get("max_workers", 1)
    
    # Limit max_workers to prevent resource exhaustion
    # Cap at 8 workers and ensure we don't exceed CPU count
    import os
    cpu_count = os.cpu_count() or 4
    if max_workers > 1:
        max_workers = min(max_workers, 8, cpu_count)
        logger.info(f"Worker pool limited to {max_workers} workers (CPU count: {cpu_count})")
    
    if max_workers > 1 and len(pdfs) > 1:
        logger.info(f"Processing {len(pdfs)} PDFs with {max_workers} workers")
        start_time = dt.datetime.now()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    process_single_pdf,
                    pdf_path,
                    vault_root,
                    source_notes_dir,
                    rules_dir,
                    npcs_dir,
                    factions_dir,
                    locations_dir,
                    items_dir,
                    extracted_text_dir,
                    template_source,
                    template_entity,
                    extractor_chain,
                    cache_dirs,
                    extensions,
                    max_excerpt_chars,
                    created,
                    overwrite,
                    config,  # Pass config for OCR and AI summarization
                ): pdf_path
                for pdf_path in pdfs
            }
            
            for future in as_completed(futures):
                pdf_path = futures[future]
                try:
                    success, error_msg = future.result(timeout=300)  # 5 minute timeout per PDF
                    with progress_lock:
                        if success:
                            processed_count += 1
                        else:
                            error_count += 1
                            if error_msg:
                                logger.error(f"Failed to process {pdf_path.name}: {error_msg}")
                                if error_collector:
                                    error_collector.add_error(
                                        f"Process PDF: {pdf_path.name}",
                                        Exception(error_msg),
                                        {"pdf_path": str(pdf_path)}
                                    )
                        
                        total_processed = processed_count + error_count
                        if total_processed % 10 == 0 or total_processed == len(pdfs):
                            elapsed = (dt.datetime.now() - start_time).total_seconds()
                            rate = total_processed / elapsed if elapsed > 0 else 0
                            remaining = len(pdfs) - total_processed
                            eta_seconds = remaining / rate if rate > 0 else 0
                            logger.info(
                                f"Progress: {total_processed}/{len(pdfs)} PDFs processed "
                                f"({processed_count} succeeded, {error_count} failed) "
                                f"- Rate: {rate:.2f} PDFs/sec, ETA: {eta_seconds:.0f}s"
                            )
                except Exception as e:
                    with progress_lock:
                        error_count += 1
                    logger.error(f"Unexpected error processing {pdf_path.name}: {e}", exc_info=True)
                    if error_collector:
                        error_collector.add_error(
                            f"Process PDF: {pdf_path.name}",
                            e,
                            {"pdf_path": str(pdf_path)}
                        )
    else:
        # Sequential processing
        start_time = dt.datetime.now()
        for pdf_path in pdfs:
            try:
                success, error_msg = process_single_pdf(
                    pdf_path,
                    vault_root,
                    source_notes_dir,
                    rules_dir,
                    npcs_dir,
                    factions_dir,
                    locations_dir,
                    items_dir,
                    extracted_text_dir,
                    template_source,
                    template_entity,
                    extractor_chain,
                    cache_dirs,
                    extensions,
                    max_excerpt_chars,
                    created,
                    overwrite,
                    config,  # Pass config for OCR and AI summarization
                )
                if success:
                    processed_count += 1
                else:
                    error_count += 1
                    if error_msg:
                        logger.error(f"Failed to process {pdf_path.name}: {error_msg}")
                
                if processed_count % 10 == 0:
                    elapsed = (dt.datetime.now() - start_time).total_seconds()
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"Progress: {processed_count}/{len(pdfs)} PDFs processed "
                        f"(Rate: {rate:.2f} PDFs/sec)"
                    )
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing {pdf_path.name}: {e}", exc_info=True)
                if error_collector:
                    error_collector.add_error(
                        f"Process PDF: {pdf_path.name}",
                        e,
                        {"pdf_path": str(pdf_path)}
                    )
    
    logger.info(f"Processed {processed_count} PDFs successfully.")
    if error_count > 0:
        logger.warning(f"Encountered {error_count} errors during processing.")
    
    # Print error summary if available
    if error_collector:
        error_collector.print_summary()


# PURPOSE: Parse CLI arguments for ingestion.
# DEPENDENCIES: argparse.
# MODIFICATION NOTES: Supports overwrite flag and config path.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest PDFs into Obsidian notes.")
    parser.add_argument(
        "--config",
        default="ingest_config.json",
        help="Path to ingestion config JSON.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing notes.",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable performance profiling.",
    )
    parser.add_argument(
        "--profile-output",
        type=str,
        default=None,
        help="Output path for profiling results (JSON).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers for PDF processing (default: 1, sequential).",
    )
    return parser.parse_args()


# PURPOSE: Entry point for ingestion script execution.
# DEPENDENCIES: Configuration file in scripts folder.
# MODIFICATION NOTES: Loads config and runs ingestion.
def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_path
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    
    # Get max_workers from config or args (default: 1 for sequential)
    max_workers = args.workers
    if max_workers < 1:
        max_workers = 1
    if max_workers > 8:
        logger.warning(f"Max workers limited to 8 (requested: {max_workers})")
        max_workers = 8
    
    if args.profile and PROFILING_AVAILABLE:
        reset_collector()
    
    # Pass max_workers to config for ingest_pdfs to use
    config["max_workers"] = max_workers
    ingest_pdfs(config, overwrite=args.overwrite)
    
    if args.profile and PROFILING_AVAILABLE:
        if args.profile_output:
            output_path = Path(args.profile_output)
            export_results(json_path=output_path)
            print(f"Performance profile exported to: {output_path}", file=sys.stderr)
        else:
            print_summary()


if __name__ == "__main__":
    main()
