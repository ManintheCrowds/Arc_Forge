# PURPOSE: Extract text sections from PDF files.
# DEPENDENCIES: pdfplumber, app.utils.text, app.config; optional opendataloader-pdf (JDK 11+)
# MODIFICATION NOTES: pdf_backend pdfplumber | opendataloader via Settings.

from __future__ import annotations

import importlib
import json
import tempfile
from pathlib import Path
from typing import Any, Iterable

import pdfplumber

from app.config import settings
from app.utils.text import normalize_text


def extract_pdf_sections(pdf_path: Path) -> Iterable[dict[str, Any]]:
    # PURPOSE: Dispatch to pdfplumber or OpenDataLoader based on settings.pdf_backend.
    if settings.pdf_backend == "opendataloader":
        yield from extract_pdf_sections_opendataloader(pdf_path)
    else:
        yield from extract_pdf_sections_pdfplumber(pdf_path)


def extract_pdf_sections_pdfplumber(pdf_path: Path) -> Iterable[dict[str, Any]]:
    # PURPOSE: Yield page-level sections from a PDF file (MVP).
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            normalized = normalize_text(raw_text)
            if not normalized:
                continue
            yield {
                "page_number": page_index,
                "section_title": f"Page {page_index}",
                "raw_text": raw_text,
                "normalized_text": normalized,
                "bounding_box": None,
            }


def extract_pdf_sections_opendataloader(pdf_path: Path) -> Iterable[dict[str, Any]]:
    # PURPOSE: Layout-aware extraction via opendataloader-pdf JSON; one section per element.
    try:
        opendataloader_pdf = importlib.import_module("opendataloader_pdf")
    except ImportError as e:
        raise RuntimeError(
            "PDF_BACKEND=opendataloader requires: pip install opendataloader-pdf (JDK 11+ on PATH). "
        ) from e

    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        kwargs: dict[str, Any] = {
            "input_path": [str(pdf_path)],
            "output_dir": str(out_dir),
            "format": "json",
            "quiet": True,
            "sanitize": settings.pdf_sanitize,
        }
        if settings.pdf_hybrid:
            kwargs["hybrid"] = settings.pdf_hybrid
        if settings.pdf_hybrid_mode:
            kwargs["hybrid_mode"] = settings.pdf_hybrid_mode
        if settings.pdf_hybrid_url:
            kwargs["hybrid_url"] = settings.pdf_hybrid_url
        if settings.pdf_hybrid_timeout:
            kwargs["hybrid_timeout"] = settings.pdf_hybrid_timeout
        kwargs["hybrid_fallback"] = settings.pdf_hybrid_fallback

        opendataloader_pdf.convert(**kwargs)

        jpath = out_dir / f"{pdf_path.stem}.json"
        if not jpath.is_file():
            jsons = sorted(out_dir.glob("*.json"))
            if not jsons:
                return
            jpath = jsons[0]

        data = json.loads(jpath.read_text(encoding="utf-8"))
        if isinstance(data, list):
            kids = data
        else:
            kids = data.get("kids") or []
        parent_page = data.get("page number") if isinstance(data, dict) else None

        for el in kids:
            if not isinstance(el, dict):
                continue
            raw = el.get("content") or el.get("description") or ""
            normalized = normalize_text(raw)
            if not normalized:
                continue
            page = int(el.get("page number") or parent_page or 1)
            el_type = el.get("type") or "block"
            yield {
                "page_number": page,
                "section_title": f"{el_type} (p{page})",
                "raw_text": raw,
                "normalized_text": normalized,
                "bounding_box": el.get("bounding box"),
            }
