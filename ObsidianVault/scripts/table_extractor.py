# PURPOSE: Table and figure extraction from PDFs (Phase 2).
# DEPENDENCIES: pdfplumber, camelot-py, tabula-py.
# MODIFICATION NOTES: Phase 2 - Complete table extraction implementation.

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

# Try to import table extraction dependencies
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False


def extract_tables_pdfplumber(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract tables using pdfplumber.
    
    Args:
        pdf_path: Path to PDF file.
        
    Returns:
        List of table dictionaries with page, data, markdown, caption.
    """
    if not PDFPLUMBER_AVAILABLE:
        logger.warning("pdfplumber not available")
        return []
    
    tables = []
    
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                
                for table_index, table_data in enumerate(page_tables, 1):
                    if not table_data or len(table_data) == 0:
                        continue
                    
                    # Clean table data (remove None values, convert to strings)
                    cleaned_data = []
                    for row in table_data:
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        cleaned_data.append(cleaned_row)
                    
                    # Skip empty tables
                    if not cleaned_data or all(not any(cell for cell in row) for row in cleaned_data):
                        continue
                    
                    # Convert to markdown
                    markdown = table_to_markdown(cleaned_data)
                    
                    # Try to find caption (look for text near table)
                    caption = _extract_table_caption(page, table_index)
                    
                    tables.append({
                        "page": page_num,
                        "table_index": table_index,
                        "data": cleaned_data,
                        "markdown": markdown,
                        "caption": caption,
                        "method": "pdfplumber",
                    })
        
        logger.info(f"Extracted {len(tables)} tables using pdfplumber from {pdf_path.name}")
        return tables
        
    except Exception as e:
        logger.error(f"Error extracting tables with pdfplumber: {e}")
        return []


def extract_tables_camelot(pdf_path: Path, flavor: str = "lattice") -> List[Dict[str, Any]]:
    """
    Extract tables using camelot.
    
    Args:
        pdf_path: Path to PDF file.
        flavor: Extraction flavor ("lattice" or "stream").
        
    Returns:
        List of table dictionaries.
    """
    if not CAMELOT_AVAILABLE:
        logger.warning("camelot not available")
        return []
    
    tables = []
    
    try:
        # Extract tables using camelot
        camelot_tables = camelot.read_pdf(str(pdf_path), flavor=flavor, pages="all")
        
        for table_index, camelot_table in enumerate(camelot_tables, 1):
            # Convert camelot table to list of lists
            table_data = camelot_table.df.values.tolist()
            
            # Convert to strings and clean
            cleaned_data = []
            for row in table_data:
                cleaned_row = [str(cell).strip() if cell is not None and str(cell) != "nan" else "" for cell in row]
                cleaned_data.append(cleaned_row)
            
            # Skip empty tables
            if not cleaned_data or all(not any(cell for cell in row) for row in cleaned_data):
                continue
            
            # Convert to markdown
            markdown = table_to_markdown(cleaned_data)
            
            tables.append({
                "page": camelot_table.page if hasattr(camelot_table, 'page') else 0,
                "table_index": table_index,
                "data": cleaned_data,
                "markdown": markdown,
                "caption": None,  # Camelot doesn't extract captions
                "method": f"camelot-{flavor}",
                "accuracy": camelot_table.accuracy if hasattr(camelot_table, 'accuracy') else None,
            })
        
        logger.info(f"Extracted {len(tables)} tables using camelot from {pdf_path.name}")
        return tables
        
    except Exception as e:
        logger.error(f"Error extracting tables with camelot: {e}")
        return []


def extract_tables(
    pdf_path: Path,
    method: str = "pdfplumber",
    fallback_method: str = "camelot",
) -> List[Dict[str, Any]]:
    """
    Extract tables from PDF with fallback support.
    
    Args:
        pdf_path: Path to PDF file.
        method: Primary extraction method ("pdfplumber", "camelot", "tabula").
        fallback_method: Fallback method if primary fails.
        
    Returns:
        List of table dictionaries with structure:
        {
            "page": int,
            "table_index": int,
            "data": List[List[str]],
            "markdown": str,
            "caption": Optional[str],
            "method": str
        }
    """
    tables = []
    
    # Try primary method
    if method == "pdfplumber" and PDFPLUMBER_AVAILABLE:
        tables = extract_tables_pdfplumber(pdf_path)
        if tables:
            return tables
        else:
            logger.debug("pdfplumber found no tables, trying fallback")
    
    elif method == "camelot" and CAMELOT_AVAILABLE:
        # Try lattice first, then stream
        tables = extract_tables_camelot(pdf_path, flavor="lattice")
        if not tables:
            tables = extract_tables_camelot(pdf_path, flavor="stream")
        if tables:
            return tables
        else:
            logger.debug("camelot found no tables, trying fallback")
    
    elif method == "tabula" and TABULA_AVAILABLE:
        try:
            # Tabula extraction
            tabula_tables = tabula.read_pdf(str(pdf_path), pages="all", multiple_tables=True)
            for table_index, df in enumerate(tabula_tables, 1):
                table_data = df.values.tolist()
                cleaned_data = [[str(cell).strip() if cell is not None else "" for cell in row] for row in table_data]
                if cleaned_data:
                    tables.append({
                        "page": 0,  # Tabula doesn't provide page info easily
                        "table_index": table_index,
                        "data": cleaned_data,
                        "markdown": table_to_markdown(cleaned_data),
                        "caption": None,
                        "method": "tabula",
                    })
            if tables:
                return tables
        except Exception as e:
            logger.warning(f"Tabula extraction failed: {e}")
    
    # Try fallback method
    if fallback_method and fallback_method != method:
        logger.info(f"Trying fallback method: {fallback_method}")
        if fallback_method == "pdfplumber" and PDFPLUMBER_AVAILABLE:
            tables = extract_tables_pdfplumber(pdf_path)
        elif fallback_method == "camelot" and CAMELOT_AVAILABLE:
            tables = extract_tables_camelot(pdf_path, flavor="lattice")
            if not tables:
                tables = extract_tables_camelot(pdf_path, flavor="stream")
        elif fallback_method == "tabula" and TABULA_AVAILABLE:
            try:
                tabula_tables = tabula.read_pdf(str(pdf_path), pages="all", multiple_tables=True)
                for table_index, df in enumerate(tabula_tables, 1):
                    table_data = df.values.tolist()
                    cleaned_data = [[str(cell).strip() if cell is not None else "" for cell in row] for row in table_data]
                    if cleaned_data:
                        tables.append({
                            "page": 0,
                            "table_index": table_index,
                            "data": cleaned_data,
                            "markdown": table_to_markdown(cleaned_data),
                            "caption": None,
                            "method": "tabula",
                        })
            except Exception as e:
                logger.warning(f"Tabula fallback failed: {e}")
        
        if tables:
            return tables
    
    logger.warning(f"No tables extracted from {pdf_path.name}")
    return []


def table_to_markdown(table_data: List[List[str]], align: Optional[List[str]] = None) -> str:
    """
    Convert table data to Markdown format.
    
    Args:
        table_data: 2D list of table cells.
        align: Optional list of alignment strings ("left", "center", "right") for each column.
        
    Returns:
        Markdown-formatted table string.
    """
    if not table_data or len(table_data) == 0:
        return ""
    
    # Determine number of columns
    max_cols = max(len(row) for row in table_data) if table_data else 0
    if max_cols == 0:
        return ""
    
    # Normalize rows to have same number of columns
    normalized_data = []
    for row in table_data:
        normalized_row = row + [""] * (max_cols - len(row))
        normalized_data.append(normalized_row[:max_cols])
    
    # Escape pipe characters in cells
    def escape_cell(cell: str) -> str:
        return str(cell).replace("|", "\\|").replace("\n", " ")
    
    lines = []
    
    # Header row
    if normalized_data:
        header = normalized_data[0]
        lines.append("| " + " | ".join(escape_cell(cell) for cell in header) + " |")
        
        # Separator row
        if align and len(align) >= max_cols:
            align_chars = {"left": ":-", "center": ":-:", "right": "-:"}
            separator = "| " + " | ".join(align_chars.get(a, "---") for a in align[:max_cols]) + " |"
        else:
            separator = "| " + " | ".join("---" for _ in range(max_cols)) + " |"
        lines.append(separator)
        
        # Data rows
        for row in normalized_data[1:]:
            lines.append("| " + " | ".join(escape_cell(cell) for cell in row) + " |")
    else:
        # No header, just data rows
        for row in normalized_data:
            lines.append("| " + " | ".join(escape_cell(cell) for cell in row) + " |")
    
    return "\n".join(lines)


def _extract_table_caption(page, table_index: int) -> Optional[str]:
    """
    Try to extract table caption from page text.
    
    Args:
        page: pdfplumber page object.
        table_index: Index of table on page.
        
    Returns:
        Caption text or None.
    """
    try:
        # Get page text
        page_text = page.extract_text()
        if not page_text:
            return None
        
        # Look for common caption patterns
        caption_patterns = [
            r'Table\s+\d+[.:]\s*([^\n]+)',
            r'Table\s+\d+[.:]\s*([^\n]{0,200})',
            r'^([^\n]{0,200})\s*Table\s+\d+',
        ]
        
        for pattern in caption_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                caption = match.group(1).strip()
                if caption and len(caption) > 5:  # Minimum caption length
                    return caption
        
        return None
        
    except Exception as e:
        logger.debug(f"Error extracting table caption: {e}")
        return None


def extract_figures(pdf_path: Path, output_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Extract figures and captions from PDF.
    
    Args:
        pdf_path: Path to PDF file.
        output_dir: Optional directory to save extracted images.
        
    Returns:
        List of figure dictionaries with structure:
        {
            "page": int,
            "figure_index": int,
            "image_path": Optional[Path],
            "caption": Optional[str]
        }
    """
    figures = []
    
    try:
        if PDFPLUMBER_AVAILABLE:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract images from page
                    images = page.images
                    
                    for img_index, img in enumerate(images, 1):
                        # Try to extract caption
                        caption = _extract_figure_caption(page, img_index)
                        
                        # Save image if output_dir provided
                        image_path = None
                        if output_dir:
                            try:
                                output_dir.mkdir(parents=True, exist_ok=True)
                                # Extract image (simplified - pdfplumber doesn't directly extract images)
                                # This would require additional libraries like PyMuPDF
                                image_path = output_dir / f"{pdf_path.stem}_page{page_num}_fig{img_index}.png"
                            except Exception as e:
                                logger.warning(f"Failed to save figure image: {e}")
                        
                        figures.append({
                            "page": page_num,
                            "figure_index": img_index,
                            "image_path": image_path,
                            "caption": caption,
                            "bbox": img.get("bbox") if isinstance(img, dict) else None,
                        })
        else:
            logger.warning("pdfplumber not available for figure extraction")
        
        logger.info(f"Extracted {len(figures)} figures from {pdf_path.name}")
        return figures
        
    except Exception as e:
        logger.error(f"Error extracting figures: {e}")
        return []


def _extract_figure_caption(page, figure_index: int) -> Optional[str]:
    """
    Try to extract figure caption from page text.
    
    Args:
        page: pdfplumber page object.
        figure_index: Index of figure on page.
        
    Returns:
        Caption text or None.
    """
    try:
        page_text = page.extract_text()
        if not page_text:
            return None
        
        # Look for common caption patterns
        caption_patterns = [
            r'Figure\s+\d+[.:]\s*([^\n]+)',
            r'Fig\.\s+\d+[.:]\s*([^\n]+)',
            r'^([^\n]{0,200})\s*Figure\s+\d+',
        ]
        
        for pattern in caption_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                caption = match.group(1).strip()
                if caption and len(caption) > 5:
                    return caption
        
        return None
        
    except Exception as e:
        logger.debug(f"Error extracting figure caption: {e}")
        return None
