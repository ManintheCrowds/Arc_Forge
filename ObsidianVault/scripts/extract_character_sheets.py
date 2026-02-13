# PURPOSE: Extract text from character sheet PDFs for RAG pipeline.
# DEPENDENCIES: extractors.extractor_chain, utils.load_config.
# MODIFICATION NOTES: Simple script to extract PC PDFs to extracted_text directory.

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from utils import load_config, validate_vault_path

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
    logger.warning("Extractor chain not available. Using fallback extraction.")

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf not available for fallback extraction.")


def extract_pdf_simple(pdf_path: Path) -> tuple[str, dict]:
    """
    Simple PDF extraction using pypdf as fallback.
    
    Args:
        pdf_path: Path to PDF file.
        
    Returns:
        Tuple of (extracted_text, metadata).
    """
    if not PYPDF_AVAILABLE:
        return "", {"method": "none", "error": "pypdf not available"}
    
    try:
        text_parts = []
        with open(pdf_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
        
        text = "\n".join(text_parts)
        return text, {"method": "pypdf", "pages": len(pdf_reader.pages)}
    except Exception as e:
        logger.error(f"pypdf extraction failed for {pdf_path.name}: {e}")
        return "", {"method": "pypdf", "error": str(e)}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem use.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename.
    """
    # Remove or replace problematic characters
    sanitized = filename.replace(" ", "_").replace("__", "_")
    # Remove special characters except underscores and hyphens
    sanitized = "".join(c if c.isalnum() or c in "._-" else "_" for c in sanitized)
    return sanitized


def extract_character_sheets(
    pc_dir: Path,
    output_dir: Path,
    config: Optional[dict] = None,
) -> int:
    """
    Extract text from character sheet PDFs.
    
    Args:
        pc_dir: Directory containing PC PDF files.
        output_dir: Directory to write extracted text files.
        config: Optional configuration dict.
        
    Returns:
        Number of successfully extracted files.
    """
    if not pc_dir.exists():
        logger.error(f"PC directory not found: {pc_dir}")
        return 0
    
    # Find PDF files
    pdf_files = list(pc_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {pc_dir}")
        return 0
    
    logger.info(f"Found {len(pdf_files)} PDF files in {pc_dir}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor chain if available
    extractor_chain = None
    if EXTRACTOR_CHAIN_AVAILABLE and config:
        try:
            extractor_chain = ExtractorChain(config)
            logger.info("Using extractor chain for extraction")
        except Exception as e:
            logger.warning(f"Failed to initialize extractor chain: {e}")
    
    # Get vault root from config or infer from output_dir
    vault_root = Path(config.get("vault_root", output_dir.parent.parent)) if config else output_dir.parent.parent
    
    extracted_count = 0
    
    for pdf_path in pdf_files:
        logger.info(f"Extracting: {pdf_path.name}")
        
        # Try extractor chain first
        text = ""
        metadata = {}
        
        if extractor_chain:
            try:
                text, source_path, metadata = extractor_chain.extract(pdf_path, vault_root)
                if not text.strip():
                    logger.warning(f"Extractor chain returned empty text for {pdf_path.name}")
            except Exception as e:
                logger.warning(f"Extractor chain failed for {pdf_path.name}: {e}")
        
        # Fallback to simple extraction
        if not text.strip():
            logger.info(f"Using fallback extraction for {pdf_path.name}")
            text, metadata = extract_pdf_simple(pdf_path)
        
        if not text.strip():
            logger.error(f"Failed to extract text from {pdf_path.name}")
            continue
        
        # Sanitize filename and write output
        sanitized_name = sanitize_filename(pdf_path.stem)
        output_path = output_dir / f"{sanitized_name}.txt"
        
        try:
            output_path.write_text(text, encoding="utf-8")
            logger.info(f"Extracted {len(text)} characters to {output_path.name}")
            extracted_count += 1
        except Exception as e:
            logger.error(f"Failed to write {output_path.name}: {e}")
    
    return extracted_count


def main():
    """Main entry point."""
    # Default paths
    pc_dir = Path("D:\\Arc_Forge\\PCs")
    config_path = Path(__file__).parent / "ingest_config.json"
    
    # Load config
    config = None
    if config_path.exists():
        try:
            config = load_config(config_path)
            logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    
    # Get output directory from config or use default
    if config:
        vault_root = Path(config.get("vault_root", "D:\\Arc_Forge\\ObsidianVault"))
        output_dir = vault_root / config.get("extracted_text_dir", "Sources/_extracted_text")
    else:
        vault_root = Path("D:\\Arc_Forge\\ObsidianVault")
        output_dir = vault_root / "Sources/_extracted_text"
    
    # Validate and resolve paths
    try:
        output_dir = validate_vault_path(vault_root, output_dir.resolve())
    except ValueError as e:
        logger.error(f"Invalid output directory: {e}")
        sys.exit(1)
    
    logger.info(f"PC directory: {pc_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Extract character sheets
    count = extract_character_sheets(pc_dir, output_dir, config)
    
    if count > 0:
        logger.info(f"Successfully extracted {count} character sheet(s)")
    else:
        logger.error("No character sheets extracted")
        sys.exit(1)


if __name__ == "__main__":
    main()
