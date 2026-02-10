# Extended Configuration Guide

Guide for configuring long-term enhancement features.

## Feature Flags

Control enhancements via `features` section:
```json
{
  "features": {
    "ocr_enabled": false,
    "ai_summarization_enabled": false,
    "table_extraction_enabled": false,
    "annotation_extraction_enabled": false,
    "web_api_enabled": false
  }
}
```

## OCR Configuration

**Status:** ✅ Implemented

OCR is automatically used as a fallback when text extraction fails and a PDF is detected as scanned.

```json
{
  "features": {
    "ocr_enabled": true
  },
  "ocr": {
    "language": "eng",
    "preprocessing": {
      "deskew": true,
      "denoise": true,
      "contrast_enhancement": true
    },
    "output_dir": "Sources/_ocr"
  }
}
```

**Notes:**
- OCR runs automatically when text extraction fails and PDF is detected as scanned
- Results are cached to avoid re-processing
- Processing time: ~2 minutes per scanned PDF page
- Requires Tesseract OCR to be installed on the system

## AI Summarization Configuration

**Status:** ✅ Implemented

AI summaries are automatically generated and added to source notes when enabled.

```json
{
  "features": {
    "ai_summarization_enabled": true
  },
  "ai_summarization": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-...",
    "max_tokens": 500,
    "temperature": 0.7,
    "cache_dir": "Sources/_summaries"
  }
}
```

**Supported Providers:**
- `openai` - OpenAI GPT models (requires `openai` package)
- `anthropic` - Anthropic Claude models (requires `anthropic` package)
- `ollama` - Local Ollama models (requires `ollama` package and Ollama installed)

**Notes:**
- Summaries are automatically cached to reduce API calls
- Large documents are automatically chunked
- Uses RPG-specific prompts for better summaries
- Processing time: ~1 minute per PDF
- Cost: Varies by provider/model (typically $0.05-$0.10 per PDF)

## RAG Pipeline Configuration

**Status:** ✅ Implemented

RAG orchestration combines retrieval, pattern analysis, and content generation (rules/adventures/bios).

```json
{
  "rag_pipeline": {
    "enabled": true,
    "campaign_kb_root": "D:\\Arc_Forge\\campaign_kb",
    "campaign_docs": [
      "campaign/00_overview.md",
      "campaign/01_factions.md"
    ],
    "output_dir": "Campaigns/_rag_outputs",
    "pattern_analysis_enabled": true,
    "content_generation_enabled": true,
    "use_kb_search": true,
    "search": {
      "limit": 8,
      "source_name": null,
      "doc_type": null
    },
    "summarization": {
      "provider": "ollama",
      "model": "llama2",
      "max_tokens": 500,
      "temperature": 0.7
    },
    "generation": {
      "provider": "ollama",
      "model": "llama2",
      "max_tokens": 800,
      "temperature": 0.8
    },
    "pdf_extraction_dir": "Sources/_extracted_text",
    "include_pdfs": true,
    "pdf_file_pattern": "*.txt"
  }
}
```

**PDF Integration Settings:**
- `pdf_extraction_dir`: Directory containing extracted PDF text files (relative to vault_root). Default: `"Sources/_extracted_text"`
- `include_pdfs`: Boolean to enable/disable PDF inclusion in RAG analysis. Default: `true`
- `pdf_file_pattern`: File pattern to match PDF text files. Default: `"*.txt"`

**Notes:**
- `campaign_docs` are relative to `campaign_kb_root`
- Output files are written under the vault (`output_dir`)
- If `use_kb_search` is true, the pipeline uses `campaign_kb` search first
- Generation prompts are controlled inside `rag_pipeline.py`
- PDF sources are tagged with `[PDF]` prefix in outputs to distinguish from campaign docs
- PDF content is included in pattern analysis, context retrieval, and content generation

## Table Extraction Configuration

```json
{
  "table_extraction": {
    "enabled": true,
    "method": "pdfplumber",
    "fallback_method": "camelot",
    "output_format": "markdown",
    "output_dir": "Sources/_tables"
  }
}
```

## Annotation Extraction Configuration

```json
{
  "annotation_extraction": {
    "enabled": true,
    "pdfplus_cache_dirs": [
      ".obsidian/plugins/pdf-plus"
    ],
    "preserve_metadata": true
  }
}
```

## Web API Configuration

```json
{
  "web_api": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8000,
    "auth_enabled": false,
    "api_key": null,
    "cors_enabled": true,
    "cors_origins": ["http://localhost:3000"]
  }
}
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive config
- Enable authentication for web API in production
