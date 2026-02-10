# PURPOSE: Build searchable index of all ingested PDF sources.
# DEPENDENCIES: ingest_config.json, source notes with YAML frontmatter.
# MODIFICATION NOTES: Generates Sources/Source_Index.md for analysis and brainstorming.

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils import get_config_path, load_config, truncate_text, validate_vault_path

try:
    import yaml
except ImportError:
    yaml = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


# PURPOSE: Parse YAML frontmatter from a markdown file.
# DEPENDENCIES: YAML frontmatter format (--- delimited).
# MODIFICATION NOTES: Returns dict of frontmatter fields or empty dict.
def parse_frontmatter(content: str) -> Tuple[Dict[str, object], str]:
    """Extract YAML frontmatter and return (metadata dict, body content)."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1].strip()
    body = parts[2] if len(parts) > 2 else ""
    
    if yaml:
        try:
            metadata = yaml.safe_load(frontmatter_text) or {}
            return metadata, body
        except Exception as e:
            logger.debug(f"YAML parsing failed, using fallback: {e}")
            pass
    
    # Fallback: simple regex parsing for common fields
    metadata = {}
    for line in frontmatter_text.split("\n"):
        match = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            # Try to parse as list
            if value.startswith("[") and value.endswith("]"):
                try:
                    value = json.loads(value)
                except Exception:
                    pass
            metadata[key] = value
    
    return metadata, body


# PURPOSE: Extract excerpt from source note body or linked extracted text.
# DEPENDENCIES: Source note format, extracted text directory.
# MODIFICATION NOTES: Returns excerpt string or empty.
def extract_excerpt(
    body: str,
    metadata: Dict[str, object],
    vault_root: Path,
    extracted_text_dir: str,
    max_chars: int = 300,
) -> str:
    """Extract excerpt from note body or linked extracted text file."""
    # Try to find excerpt in body
    excerpt_match = re.search(r"## Extracted Text Excerpt\s*\n\s*> (.+?)(?=\n\n|\n##|$)", body, re.DOTALL)
    if excerpt_match:
        excerpt = excerpt_match.group(1).strip()
        # Clean up whitespace
        excerpt = re.sub(r"\s+", " ", excerpt)
        excerpt = truncate_text(excerpt, max_chars)
        return excerpt
    
    # Try to read from linked extracted text file
    extracted_link_match = re.search(r"\[\[([^\]]+\.txt)\]\]", body)
    if extracted_link_match:
        text_path_str = extracted_link_match.group(1)
        # Convert to absolute path
        if not Path(text_path_str).is_absolute():
            text_path = vault_root / text_path_str
        else:
            text_path = Path(text_path_str)
        
        # Validate path is within vault
        try:
            text_path = validate_vault_path(vault_root, text_path.resolve())
        except ValueError as e:
            logger.warning(f"Invalid extracted text path: {e}")
            return ""
        
        if text_path.exists():
            try:
                text_content = text_path.read_text(encoding="utf-8", errors="replace")
                excerpt = text_content.strip().replace("\n", " ")
                excerpt = truncate_text(excerpt, max_chars)
                return excerpt
            except Exception as e:
                logger.warning(f"Failed to read extracted text file {text_path}: {e}")
                return ""
    
    return ""


# PURPOSE: Scan source notes directory and extract metadata.
# DEPENDENCIES: Sources directory structure.
# MODIFICATION NOTES: Returns list of source metadata dicts.
def scan_sources(
    sources_dir: Path,
    vault_root: Path,
    extracted_text_dir: str,
    exclude_dirs: List[str],
) -> List[Dict[str, object]]:
    """
    Scan Sources directory for markdown files and extract metadata.
    
    Args:
        sources_dir: Directory containing source notes.
        vault_root: Root directory of the vault.
        extracted_text_dir: Relative path to extracted text directory.
        exclude_dirs: List of directory names to exclude.
        
    Returns:
        List of source metadata dictionaries.
    """
    sources = []
    
    # Validate and build exclude paths
    exclude_paths = set()
    for d in exclude_dirs:
        try:
            exclude_path = sources_dir / d
            exclude_path = validate_vault_path(vault_root, exclude_path.resolve())
            exclude_paths.add(exclude_path)
        except ValueError as e:
            logger.warning(f"Invalid exclude directory '{d}': {e}")
            continue
    
    try:
        for md_file in sources_dir.rglob("*.md"):
            # Validate file is within vault
            try:
                md_file = validate_vault_path(vault_root, md_file.resolve())
            except ValueError as e:
                logger.warning(f"File outside vault root: {e}")
                continue
            
            # Skip excluded directories and the index itself
            if any(md_file.is_relative_to(exc) for exc in exclude_paths):
                continue
            if md_file.name == "Source_Index.md":
                continue
            
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                metadata, body = parse_frontmatter(content)
                
                if not metadata.get("title"):
                    # Use filename as fallback
                    metadata["title"] = md_file.stem
                
                # Extract excerpt
                excerpt = extract_excerpt(body, metadata, vault_root, extracted_text_dir)
                if excerpt:
                    metadata["excerpt"] = excerpt
                
                # Add file path for linking
                try:
                    metadata["note_path"] = md_file.relative_to(vault_root).as_posix()
                except ValueError:
                    # File not relative to vault (shouldn't happen after validation)
                    logger.warning(f"File {md_file} not relative to vault root")
                    continue
                
                metadata["file_name"] = md_file.name
                
                sources.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to process {md_file}: {e}")
                continue
    except PermissionError as e:
        logger.error(f"Permission denied accessing {sources_dir}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error scanning sources directory: {e}")
        raise
    
    return sources


# PURPOSE: Group sources by category (doc_type or default).
# DEPENDENCIES: Source metadata with doc_type field.
# MODIFICATION NOTES: Returns dict mapping category to source list.
def categorize_sources(sources: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    """Group sources by doc_type or default category."""
    categories = defaultdict(list)
    
    for source in sources:
        doc_type = source.get("doc_type", "unverified")
        if doc_type == "unverified" or not doc_type:
            category = "Uncategorized"
        else:
            category = str(doc_type).title()
        
        categories[category].append(source)
    
    # Sort sources within each category by created date (newest first)
    for category in categories:
        categories[category].sort(
            key=lambda s: s.get("created", ""),
            reverse=True
        )
    
    return dict(categories)


# PURPOSE: Generate markdown index content.
# DEPENDENCIES: Categorized sources, config.
# MODIFICATION NOTES: Returns complete index markdown string.
def generate_index_markdown(
    categories: Dict[str, List[Dict[str, object]]],
    total_count: int,
    last_updated: str,
) -> str:
    """Generate the index markdown content."""
    lines = [
        "---",
        "title: Source Index",
        "tags: [\"type/index\", \"meta/source-catalog\"]",
        "created: \"" + dt.date.today().isoformat() + "\"",
        "last_updated: \"" + last_updated + "\"",
        "---",
        "",
        "# Source Index",
        "",
        f"**Total Sources:** {total_count} | **Last Updated:** {last_updated}",
        "",
        "## Quick Links",
        "",
        "- [[Sources/]] - Browse all source notes",
        "- Filter by tag: `#type/source`",
        "- Search by doc_type in frontmatter",
        "",
        "## Table of Contents",
        "",
    ]
    
    # Add TOC entries
    for category in sorted(categories.keys()):
        count = len(categories[category])
        anchor = category.lower().replace(" ", "-")
        lines.append(f"- [{category}](#{anchor}) ({count} sources)")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Add categorized listings
    for category in sorted(categories.keys()):
        anchor = category.lower().replace(" ", "-")
        lines.append(f"## {category} {{#{anchor}}}")
        lines.append("")
        
        for source in categories[category]:
            title = source.get("title", "Untitled")
            note_path = source.get("note_path", "")
            created = source.get("created", "unknown")
            doc_type = source.get("doc_type", "unverified")
            tags = source.get("tags", [])
            excerpt = source.get("excerpt", "")
            
            # Build link
            if note_path:
                link_text = f"[[{note_path}|{title}]]"
            else:
                link_text = title
            
            lines.append(f"### {link_text}")
            lines.append("")
            
            # Metadata line
            meta_parts = []
            if created != "unknown":
                meta_parts.append(f"**Created:** {created}")
            if doc_type and doc_type != "unverified":
                meta_parts.append(f"**Type:** {doc_type}")
            if tags:
                tag_str = ", ".join(f"`{t}`" for t in tags if isinstance(t, str))
                if tag_str:
                    meta_parts.append(f"**Tags:** {tag_str}")
            
            if meta_parts:
                lines.append(" | ".join(meta_parts))
                lines.append("")
            
            # Excerpt
            if excerpt:
                lines.append(f"> {excerpt}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    return "\n".join(lines)


# PURPOSE: Load index build state (last build time, processed files).
# DEPENDENCIES: State file path.
# MODIFICATION NOTES: Returns dict with state or empty dict if not found.
def load_index_state(state_path: Path) -> Dict[str, object]:
    """Load index build state from disk."""
    if not state_path.exists():
        return {}
    
    try:
        with state_path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
        return state
    except Exception:
        return {}


# PURPOSE: Save index build state (last build time, processed files).
# DEPENDENCIES: State file path, state dict.
# MODIFICATION NOTES: Writes JSON state to disk.
def save_index_state(state_path: Path, state: Dict[str, object]) -> None:
    """Save index build state to disk."""
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with state_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save index state: {e}")


# PURPOSE: Get modification time of a file.
# DEPENDENCIES: File path.
# MODIFICATION NOTES: Returns ISO timestamp string or empty string.
def get_file_mtime(file_path: Path) -> str:
    """Get file modification time as ISO string."""
    try:
        return dt.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
    except Exception:
        return ""


# PURPOSE: Build the source index with incremental updates.
# DEPENDENCIES: Config, source notes directory.
# MODIFICATION NOTES: Writes Sources/Source_Index.md. Supports incremental builds.
def build_index(config: Dict[str, object], overwrite: bool = True, incremental: bool = True) -> None:
    """
    Build the source index with incremental updates.
    
    Args:
        config: Configuration dictionary.
        overwrite: Whether to overwrite existing index.
        incremental: Whether to use incremental building.
    """
    vault_root = Path(str(config["vault_root"]))
    vault_root = vault_root.resolve()
    
    # Validate and get paths from config
    try:
        sources_dir = get_config_path(vault_root, config, "source_notes_dir")
        extracted_text_dir = str(config["extracted_text_dir"])
    except (KeyError, ValueError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Index builder state file
    state_path = Path(__file__).parent / "index_build_state.json"
    
    # Get exclude dirs from config or use defaults
    exclude_dirs = config.get("index_builder", {}).get("exclude_dirs", ["_extracted_text", "PDFs"])
    if not isinstance(exclude_dirs, list):
        exclude_dirs = ["_extracted_text", "PDFs"]
        logger.warning("Invalid exclude_dirs in config, using defaults")
    
    # Load previous state for incremental builds
    previous_state = {}
    if incremental and not overwrite and state_path.exists():
        previous_state = load_index_state(state_path)
        last_build_time = previous_state.get("last_build_time", "")
        logger.info(f"Last index build: {last_build_time or 'never'}")
    
    logger.info(f"Scanning sources in: {sources_dir}")
    try:
        sources = scan_sources(sources_dir, vault_root, extracted_text_dir, exclude_dirs)
    except Exception as e:
        logger.error(f"Failed to scan sources: {e}")
        sys.exit(1)
    
    if not sources:
        logger.info("No source notes found.")
        return
    
    logger.info(f"Found {len(sources)} source notes.")
    
    # For incremental builds, only process new/changed files and handle deleted sources
    if incremental and not overwrite and previous_state:
        processed_files = previous_state.get("processed_files", {})
        last_build_time = previous_state.get("last_build_time", "")
        
        if last_build_time:
            try:
                last_build_dt = dt.datetime.fromisoformat(last_build_time)
                new_sources = []
                changed_sources = []
                deleted_sources = []
                
                # Track current source paths
                current_paths = set()
                
                for source in sources:
                    note_path_str = source.get("note_path", "")
                    if not note_path_str:
                        continue
                    
                    current_paths.add(note_path_str)
                    note_path = vault_root / note_path_str
                    if not note_path.exists():
                        continue
                    
                    current_mtime = get_file_mtime(note_path)
                    previous_mtime = processed_files.get(note_path_str, "")
                    
                    if not previous_mtime or current_mtime != previous_mtime:
                        if not previous_mtime:
                            new_sources.append(source)
                        else:
                            changed_sources.append(source)
                
                # Detect deleted sources (in previous state but not in current scan)
                for prev_path in processed_files.keys():
                    if prev_path not in current_paths:
                        deleted_sources.append(prev_path)
                
                if new_sources or changed_sources or deleted_sources:
                    logger.info(
                        f"Incremental update: {len(new_sources)} new, "
                        f"{len(changed_sources)} changed, {len(deleted_sources)} deleted"
                    )
                    # Continue with full rebuild (merge would be complex, full rebuild is simpler)
                else:
                    logger.info("No changes detected since last build. Use --overwrite to force rebuild.")
                    return
            except Exception as e:
                logger.warning(f"Incremental build failed, performing full scan: {e}")
    
    categories = categorize_sources(sources)
    last_updated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    index_content = generate_index_markdown(categories, len(sources), last_updated)
    
    index_path = sources_dir / "Source_Index.md"
    
    if index_path.exists() and not overwrite:
        logger.info(f"Index already exists at {index_path}. Use --overwrite to regenerate.")
        return
    
    try:
        # Validate index path is within vault
        index_path = validate_vault_path(vault_root, index_path.resolve())
        index_path.write_text(index_content, encoding="utf-8")
        logger.info(f"Index written to: {index_path}")
        
        # Save build state (only track existing files)
        processed_files = {}
        for source in sources:
            note_path_str = source.get("note_path", "")
            if note_path_str:
                note_path = vault_root / note_path_str
                if note_path.exists():
                    processed_files[note_path_str] = get_file_mtime(note_path)
                # Note: deleted files are automatically removed from state by not including them
        
        state = {
            "last_build_time": dt.datetime.now().isoformat(),
            "processed_files": processed_files,
            "total_sources": len(sources)
        }
        save_index_state(state_path, state)
        logger.info(f"Index build state saved: {len(processed_files)} files tracked")
    except Exception as e:
        logger.error(f"Failed to write index: {e}")
        sys.exit(1)


# PURPOSE: Parse CLI arguments.
# DEPENDENCIES: argparse.
# MODIFICATION NOTES: Supports config path, overwrite flag, and incremental mode.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build searchable index of PDF sources.")
    parser.add_argument(
        "--config",
        default="ingest_config.json",
        help="Path to ingestion config JSON.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing index (disables incremental mode).",
    )
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable incremental building (always full scan).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    
    args = parse_args()
    config_path = Path(args.config)
    
    if not config_path.is_absolute():
        script_dir = Path(__file__).parent
        config_path = script_dir / config_path
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        config = load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    incremental = not args.no_incremental
    build_index(config, overwrite=args.overwrite, incremental=incremental)
