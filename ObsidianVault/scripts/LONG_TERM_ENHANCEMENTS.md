# Long-Term Enhancements Overview

This document provides an overview of planned long-term enhancements for the PDF ingestion system.

## Enhancement Status

All enhancements are currently **stub implementations** with clear TODOs. They are controlled by feature flags in `ingest_config.json`.

## LTE1: OCR for Scanned PDFs

**Status:** ✅ **IMPLEMENTED**  
**Priority:** High  
**Module:** `ocr_processor.py`

Enables processing of scanned/image-based PDFs using Tesseract OCR. Fully implemented with preprocessing, caching, and error handling.

**Dependencies:**
- Tesseract OCR (system installation)
- `pytesseract`, `pdf2image`, `Pillow`

**Configuration:**
```json
{
  "features": {"ocr_enabled": true},
  "ocr": {
    "language": "eng",
    "preprocessing": {"deskew": true, "denoise": true}
  }
}
```

## LTE2: AI-Powered Summarization

**Status:** ✅ **IMPLEMENTED**  
**Priority:** High  
**Module:** `ai_summarizer.py`

Generates automatic document summaries using LLM APIs. Fully implemented with support for OpenAI, Anthropic, and Ollama, including caching and chunking.

**Dependencies:**
- `openai`, `anthropic`, or `ollama`

**Configuration:**
```json
{
  "features": {"ai_summarization_enabled": true},
  "ai_summarization": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-key"
  }
}
```

## LTE3: Table and Figure Extraction

**Status:** Stub implementation  
**Priority:** Medium  
**Module:** `table_extractor.py`

Extracts tables and figures from PDFs, converts to Markdown.

**Dependencies:**
- `pdfplumber`, `camelot-py`, or `tabula-py`

## LTE4: Rich Annotations with Backlinks

**Status:** Stub implementation  
**Priority:** Medium  
**Module:** `annotation_extractor.py`

Extracts PDF++ annotations and creates bidirectional links.

## LTE5: Web API and Dashboard

**Status:** Stub implementation  
**Priority:** Low  
**Module:** `web_api.py`

REST API and web dashboard for managing ingestion.

**Dependencies:**
- `fastapi`, `uvicorn`, `pydantic`

## LTE6: Advanced Entity Extraction with LLM

**Status:** Stub implementation  
**Priority:** Medium  
**Module:** Enhanced `entity_extractor.py`

Enhances NER with LLM for RPG-specific entities.

## Implementation Notes

- All enhancements are optional and disabled by default
- Feature flags control activation
- Dependencies are documented in `requirements-enhancements.txt`
- Integration points are documented in `INTEGRATION_POINTS.md`
