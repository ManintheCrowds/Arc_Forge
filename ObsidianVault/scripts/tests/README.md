# PDF Ingestion System Tests

## Overview

This directory contains comprehensive tests for the PDF ingestion system, including unit tests, integration tests, and security tests.

## Test Structure

- `test_utils.py` - Unit tests for shared utility functions
- `test_security.py` - Security tests for path traversal, malicious config, etc.
- `test_ingest_pdfs.py` - Integration tests for the PDF ingestion pipeline
- `conftest.py` - Shared pytest fixtures

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Security tests only
pytest -m security

# Integration tests only
pytest -m integration
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

## Test Coverage

The test suite covers:

1. **Utility Functions** (`test_utils.py`)
   - Config loading and validation
   - Path validation and traversal protection
   - Text truncation
   - File size validation
   - Cache directory sanitization

2. **Security** (`test_security.py`)
   - Path traversal attack prevention
   - Malicious configuration handling
   - Large file handling (DoS prevention)
   - Symlink handling
   - Input sanitization

3. **Integration** (`test_ingest_pdfs.py`)
   - PDF discovery and listing
   - Text extraction (PDF++ cache and fallbacks)
   - Entity parsing
   - Source note generation
   - File writing operations

## Writing New Tests

When adding new functionality:

1. Add unit tests for new utility functions in `test_utils.py`
2. Add security tests for any path/file operations in `test_security.py`
3. Add integration tests for end-to-end workflows in `test_ingest_pdfs.py`

## Test Fixtures

Common fixtures available in `conftest.py`:

- `tmp_path` - Temporary directory for test files

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- After refactoring
- When adding new features
