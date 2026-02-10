# PURPOSE: Enhanced metadata and citation extraction (Phase 2).
# DEPENDENCIES: pypdf, requests (for API calls), python-dateutil.
# MODIFICATION NOTES: Phase 2 - Enhanced metadata extraction with citation parsing and API integration.

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Try to import dependencies
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dateutil import parser as date_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False


def extract_pdf_metadata(pdf_path: Path) -> Dict[str, str]:
    """
    Extract comprehensive PDF metadata.
    
    Args:
        pdf_path: Path to PDF file.
        
    Returns:
        Dictionary with metadata keys: title, author, subject, creator, creation_date, modification_date.
    """
    metadata = {}
    
    if not PYPDF_AVAILABLE:
        logger.warning("pypdf not available for metadata extraction")
        return metadata
    
    try:
        reader = PdfReader(str(pdf_path))
        pdf_metadata = reader.metadata
        
        if pdf_metadata:
            # Extract standard metadata fields
            if pdf_metadata.get("/Title"):
                metadata["title"] = pdf_metadata["/Title"]
            if pdf_metadata.get("/Author"):
                metadata["author"] = pdf_metadata["/Author"]
            if pdf_metadata.get("/Subject"):
                metadata["subject"] = pdf_metadata["/Subject"]
            if pdf_metadata.get("/Creator"):
                metadata["creator"] = pdf_metadata["/Creator"]
            if pdf_metadata.get("/Producer"):
                metadata["producer"] = pdf_metadata["/Producer"]
            
            # Parse dates
            if pdf_metadata.get("/CreationDate"):
                try:
                    creation_date = _parse_pdf_date(pdf_metadata["/CreationDate"])
                    if creation_date:
                        metadata["creation_date"] = creation_date.isoformat()
                except Exception as e:
                    logger.debug(f"Failed to parse creation date: {e}")
            
            if pdf_metadata.get("/ModDate"):
                try:
                    mod_date = _parse_pdf_date(pdf_metadata["/ModDate"])
                    if mod_date:
                        metadata["modification_date"] = mod_date.isoformat()
                except Exception as e:
                    logger.debug(f"Failed to parse modification date: {e}")
        
        # Extract number of pages
        metadata["page_count"] = str(len(reader.pages))
        
    except Exception as e:
        logger.warning(f"Error extracting PDF metadata: {e}")
    
    return metadata


def _parse_pdf_date(date_str: str) -> Optional[datetime]:
    """
    Parse PDF date string (D:YYYYMMDDHHmmSSOHH'mm' format).
    
    Args:
        date_str: PDF date string.
        
    Returns:
        Parsed datetime or None.
    """
    try:
        # PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
        if date_str.startswith("D:"):
            date_str = date_str[2:]
        
        # Try to parse with dateutil first
        if DATEUTIL_AVAILABLE:
            try:
                return date_parser.parse(date_str)
            except Exception:
                pass
        
        # Fallback: manual parsing
        if len(date_str) >= 8:
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            hour = int(date_str[8:10]) if len(date_str) >= 10 else 0
            minute = int(date_str[10:12]) if len(date_str) >= 12 else 0
            second = int(date_str[12:14]) if len(date_str) >= 14 else 0
            return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        logger.debug(f"Failed to parse PDF date '{date_str}': {e}")
    
    return None


def extract_citations(text: str) -> Dict[str, List[str]]:
    """
    Extract citations from text (DOI, ISBN, URLs).
    
    Args:
        text: Text to search for citations.
        
    Returns:
        Dictionary with citation types as keys and lists of citations as values.
    """
    citations = {
        "doi": [],
        "isbn": [],
        "urls": [],
        "other": [],
    }
    
    # DOI pattern: doi:10.xxxx/xxxxx or https://doi.org/10.xxxx/xxxxx
    doi_pattern = r'(?:doi:)?(?:https?://(?:dx\.)?doi\.org/)?(10\.\d+/[^\s\)]+)'
    doi_matches = re.finditer(doi_pattern, text, re.IGNORECASE)
    for match in doi_matches:
        doi = match.group(1).strip().rstrip('.,;:')
        if doi and doi not in citations["doi"]:
            citations["doi"].append(doi)
    
    # ISBN pattern: ISBN-13: 978-xxxxx or ISBN: xxxxx
    isbn_pattern = r'ISBN(?:-13)?:?\s*([0-9\-X]{10,17})'
    isbn_matches = re.finditer(isbn_pattern, text, re.IGNORECASE)
    for match in isbn_matches:
        isbn = match.group(1).strip().rstrip('.,;:')
        if isbn and isbn not in citations["isbn"]:
            citations["isbn"].append(isbn)
    
    # URL pattern (publication URLs)
    url_pattern = r'https?://[^\s\)]+'
    url_matches = re.finditer(url_pattern, text, re.IGNORECASE)
    for match in url_matches:
        url = match.group(0).strip().rstrip('.,;:)')
        # Filter out common non-publication URLs
        if not any(skip in url.lower() for skip in ['google.com', 'amazon.com', 'wikipedia.org']):
            if url not in citations["urls"]:
                citations["urls"].append(url)
    
    return citations


def query_crossref_api(doi: str) -> Optional[Dict[str, str]]:
    """
    Query CrossRef API for DOI metadata.
    
    Args:
        doi: DOI identifier.
        
    Returns:
        Dictionary with metadata or None if not found.
    """
    if not REQUESTS_AVAILABLE:
        logger.debug("requests not available for CrossRef API")
        return None
    
    try:
        # Remove doi: prefix if present
        clean_doi = doi.replace("doi:", "").strip()
        url = f"https://api.crossref.org/works/{clean_doi}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            
            metadata = {}
            if message.get("title"):
                title = message["title"][0] if isinstance(message["title"], list) else message["title"]
                metadata["title"] = title
            if message.get("author"):
                authors = message["author"]
                author_names = []
                for author in authors:
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if given or family:
                        author_names.append(f"{given} {family}".strip())
                if author_names:
                    metadata["authors"] = ", ".join(author_names)
            if message.get("published-print") or message.get("published-online"):
                pub_date = message.get("published-print") or message.get("published-online")
                if pub_date and pub_date.get("date-parts"):
                    date_parts = pub_date["date-parts"][0]
                    if len(date_parts) >= 1:
                        metadata["publication_year"] = str(date_parts[0])
            if message.get("container-title"):
                container = message["container-title"][0] if isinstance(message["container-title"], list) else message["container-title"]
                metadata["journal"] = container
            
            logger.debug(f"Retrieved metadata from CrossRef for DOI: {clean_doi}")
            return metadata
        else:
            logger.debug(f"CrossRef API returned status {response.status_code} for DOI: {clean_doi}")
            return None
            
    except Exception as e:
        logger.warning(f"Error querying CrossRef API: {e}")
        return None


def enrich_metadata_with_citations(pdf_metadata: Dict[str, str], text: str) -> Dict[str, str]:
    """
    Enrich PDF metadata with citation information.
    
    Args:
        pdf_metadata: Existing PDF metadata.
        text: Document text to search for citations.
        
    Returns:
        Enriched metadata dictionary.
    """
    enriched = pdf_metadata.copy()
    
    # Extract citations from text
    citations = extract_citations(text)
    
    # Add DOI if found
    if citations["doi"]:
        enriched["doi"] = citations["doi"][0]  # Use first DOI
        
        # Try to enrich with CrossRef API
        if REQUESTS_AVAILABLE:
            crossref_metadata = query_crossref_api(citations["doi"][0])
            if crossref_metadata:
                # Merge CrossRef metadata (don't overwrite existing)
                for key, value in crossref_metadata.items():
                    if key not in enriched or not enriched[key]:
                        enriched[key] = value
    
    # Add ISBN if found
    if citations["isbn"]:
        enriched["isbn"] = citations["isbn"][0]  # Use first ISBN
    
    # Add URLs if found
    if citations["urls"]:
        enriched["urls"] = citations["urls"]
    
    return enriched
