# Dependency Installation Guide

This guide explains how to install dependencies for long-term enhancements.

## Core Dependencies

Core system requires:
- Python 3.8+
- `pypdf` or `pdfplumber` (optional, for fallback extraction)

## Enhancement Dependencies

### OCR Support (LTE1)

**System Requirements:**
- Tesseract OCR must be installed separately

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Tesseract
3. Add to PATH or configure `tesseract_path` in config

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Python Packages:**
```bash
pip install pytesseract pdf2image Pillow
```

### AI/LLM Support (LTE2, LTE6)

**OpenAI:**
```bash
pip install openai
# Set API key in config or environment variable
```

**Anthropic (Claude):**
```bash
pip install anthropic
```

**Ollama (Local):**
```bash
# Install Ollama from https://ollama.ai/
pip install ollama
```

### Table Extraction (LTE3)

**pdfplumber:**
```bash
pip install pdfplumber
```

**camelot-py:**
```bash
# Requires ghostscript
# Windows: Download from https://www.ghostscript.com/
# Linux: sudo apt-get install ghostscript
# macOS: brew install ghostscript

pip install "camelot-py[cv]"
```

**tabula-py:**
```bash
# Requires Java
pip install tabula-py
```

### Web API (LTE5)

```bash
pip install fastapi uvicorn pydantic
```

## Installation Script

Install all enhancement dependencies:
```bash
pip install -r requirements-enhancements.txt
```

## Verification

Test installations:
```python
# Test OCR
import pytesseract
pytesseract.get_tesseract_version()

# Test LLM
import openai
# or
import anthropic

# Test tables
import pdfplumber
# or
import camelot

# Test web API
import fastapi
```
