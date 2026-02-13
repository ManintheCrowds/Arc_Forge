# Integration Points for Long-Term Enhancements

This document describes where and how to integrate long-term enhancements into the existing PDF ingestion system.

## Overview

Each long-term enhancement has specific integration points in the codebase. This document maps each enhancement to its integration location and provides implementation guidance.

---

## LTE1: OCR for Scanned PDFs

### Integration Point: `ingest_pdfs.py` - `extract_text()` function

**Location:** `D:\Arc_Forge\ObsidianVault\scripts\ingest_pdfs.py`, line ~228

**Current Flow:**
1. Try PDF++ cache
2. Fallback to pypdf
3. Fallback to pdfplumber
4. Return empty text if all fail

**Integration:**
```python
def extract_text(...):
    # ... existing code ...
    
    # Add OCR as final fallback
    if not text and config.get("features", {}).get("ocr_enabled", False):
        from ocr_processor import extract_text_with_ocr, is_scanned_pdf
        
        if is_scanned_pdf(pdf_path):
            text, ocr_path = extract_text_with_ocr(
                pdf_path,
                language=config.get("ocr", {}).get("language", "eng")
            )
            if text:
                return text, ocr_path
    
    return text, None
```

**Configuration:**
- Enable via `config["features"]["ocr_enabled"]`
- Configure in `config["ocr"]` section

**Dependencies:**
- `ocr_processor.py` module
- Tesseract OCR installed
- `pytesseract`, `pdf2image`, `Pillow` packages

---

## LTE2: AI-Powered Summarization

### Integration Point: `ingest_pdfs.py` - `build_source_note()` function

**Location:** `D:\Arc_Forge\ObsidianVault\scripts\ingest_pdfs.py`, line ~364

**Current Flow:**
1. Build source note from template
2. Add excerpt
3. Add entities
4. Add source link

**Integration:**
```python
def build_source_note(..., text: str = ""):
    # ... existing code ...
    
    # Add AI summary if enabled
    summary = None
    if config.get("features", {}).get("ai_summarization_enabled", False):
        from ai_summarizer import summarize_text, get_cached_summary, save_summary_cache
        import hashlib
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_dir = Path(config.get("ai_summarization", {}).get("cache_dir", "Sources/_summaries"))
        
        summary = get_cached_summary(text_hash, cache_dir)
        if not summary:
            summary = summarize_text(
                text,
                provider=config.get("ai_summarization", {}).get("provider", "openai"),
                model=config.get("ai_summarization", {}).get("model", "gpt-4"),
                api_key=config.get("ai_summarization", {}).get("api_key"),
            )
            if summary:
                save_summary_cache(text_hash, summary, cache_dir)
        
        if summary:
            content += f"\n## AI Summary\n\n{summary}\n"
    
    return content
```

**Configuration:**
- Enable via `config["features"]["ai_summarization_enabled"]`
- Configure in `config["ai_summarization"]` section

**Dependencies:**
- `ai_summarizer.py` module
- LLM API access (OpenAI, Anthropic, or Ollama)

---

## LTE3: Table and Figure Extraction

### Integration Point: `ingest_pdfs.py` - `process_single_pdf()` function

**Location:** `D:\Arc_Forge\ObsidianVault\scripts\ingest_pdfs.py`, line ~481

**Current Flow:**
1. Extract text
2. Create source note
3. Parse entities
4. Create entity notes

**Integration:**
```python
def process_single_pdf(...):
    # ... existing code ...
    
    # Extract tables and figures if enabled
    if config.get("features", {}).get("table_extraction_enabled", False):
        from table_extractor import extract_tables, extract_figures
        
        tables = extract_tables(
            pdf_path,
            method=config.get("table_extraction", {}).get("method", "pdfplumber"),
            fallback_method=config.get("table_extraction", {}).get("fallback_method", "camelot")
        )
        
        figures = extract_figures(pdf_path)
        
        # Add tables and figures to source note
        if tables or figures:
            content += "\n## Tables and Figures\n\n"
            for table in tables:
                content += f"### Table {table['table_index']} (Page {table['page']})\n\n"
                content += table["markdown"] + "\n\n"
            
            for figure in figures:
                content += f"### Figure {figure['figure_index']} (Page {figure['page']})\n\n"
                if figure.get("caption"):
                    content += f"*{figure['caption']}*\n\n"
                content += f"![Figure]({figure['image_path']})\n\n"
```

**Configuration:**
- Enable via `config["features"]["table_extraction_enabled"]`
- Configure in `config["table_extraction"]` section

**Dependencies:**
- `table_extractor.py` module
- `pdfplumber`, `camelot-py`, or `tabula-py` packages

---

## LTE4: Rich Annotations with Backlinks

### Integration Point: `ingest_pdfs.py` - `process_single_pdf()` function

**Location:** `D:\Arc_Forge\ObsidianVault\scripts\ingest_pdfs.py`, line ~481

**Current Flow:**
1. Extract text
2. Create source note
3. Parse entities

**Integration:**
```python
def process_single_pdf(...):
    # ... existing code ...
    
    # Extract annotations if enabled
    if config.get("features", {}).get("annotation_extraction_enabled", False):
        from annotation_extractor import extract_annotations, create_annotation_section
        
        annotations = extract_annotations(
            pdf_path,
            vault_root,
            config.get("annotation_extraction", {}).get("pdfplus_cache_dirs", [])
        )
        
        if annotations:
            annotation_section = create_annotation_section(annotations)
            source_content += annotation_section
            
            # Link annotations to entity notes
            for ann in annotations:
                # Extract entities from annotation text
                # Create links to relevant entity notes
                pass
```

**Configuration:**
- Enable via `config["features"]["annotation_extraction_enabled"]`
- Configure in `config["annotation_extraction"]` section

**Dependencies:**
- `annotation_extractor.py` module
- PDF++ plugin cache access

---

## LTE5: Web API and Dashboard

### Integration Point: Standalone service

**Location:** New service entry point

**Implementation:**
- Run as separate service: `python web_api.py`
- Integrates with existing ingestion functions
- Provides REST API for all operations

**Integration with Existing Code:**
```python
# web_api.py
from ingest_pdfs import ingest_pdfs, process_single_pdf
from build_index import build_index

@app.post("/api/ingest")
async def trigger_ingestion(config: ConfigUpdate):
    # Load config
    # Call ingest_pdfs()
    # Return job ID
    pass

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    # Return ingestion status
    pass
```

**Configuration:**
- Enable via `config["features"]["web_api_enabled"]`
- Configure in `config["web_api"]` section

**Dependencies:**
- `web_api.py` module
- `fastapi`, `uvicorn`, `pydantic` packages

---

## LTE6: Advanced Entity Extraction with LLM

### Integration Point: `entity_extractor.py` - `extract_entities()` function

**Location:** `D:\Arc_Forge\ObsidianVault\scripts\entity_extractor.py`, line ~60

**Current Flow:**
1. Use spaCy NER for basic extraction
2. Map entity types
3. Return entities

**Integration:**
```python
def extract_entities(self, text: str) -> Dict[str, List[str]]:
    # ... existing NER code ...
    
    # Enhance with LLM if enabled
    if config.get("features", {}).get("llm_entity_extraction_enabled", False):
        from ai_summarizer import summarize_text  # Reuse LLM infrastructure
        
        # Use LLM to extract RPG-specific entities
        llm_prompt = f"""
        Extract RPG entities from the following text. Return JSON with:
        - NPCs: character names
        - Factions: organizations, groups
        - Locations: places, planets, cities
        - Items: weapons, equipment, artifacts
        - Rules: game mechanics, rules
        
        Text: {text[:4000]}  # Limit to avoid token limits
        """
        
        llm_result = summarize_text(
            llm_prompt,
            provider=config.get("ai_summarization", {}).get("provider", "openai"),
            model=config.get("ai_summarization", {}).get("model", "gpt-4"),
        )
        
        # Parse LLM result and merge with NER results
        # Combine both for hybrid approach
    
    return entities
```

**Configuration:**
- Enable via `config["features"]["llm_entity_extraction_enabled"]`
- Uses `config["ai_summarization"]` for LLM settings

**Dependencies:**
- Enhanced `entity_extractor.py`
- LLM API access (same as LTE2)

---

## Implementation Checklist

For each enhancement:

- [ ] Enable feature flag in config
- [ ] Install required dependencies
- [ ] Implement core functionality in stub module
- [ ] Integrate at specified integration point
- [ ] Add error handling
- [ ] Add logging
- [ ] Test with sample PDFs
- [ ] Update documentation
- [ ] Add configuration examples

---

## Testing Integration Points

Each integration point should be tested:

1. **Unit tests** for the enhancement module
2. **Integration tests** at the integration point
3. **End-to-end tests** with full workflow
4. **Performance tests** to ensure no degradation

---

## Notes

- All enhancements are optional and controlled by feature flags
- Enhancements should gracefully degrade if dependencies are missing
- Error handling should not break existing functionality
- Logging should indicate when enhancements are active/inactive
