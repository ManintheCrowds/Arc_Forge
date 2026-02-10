# Quick dependency check
import sys
print(f"Python {sys.version}")

try:
    from pypdf import PdfReader
    print("pypdf: Available")
except ImportError:
    print("pypdf: Not installed (optional)")

try:
    import pdfplumber
    print("pdfplumber: Available")
except ImportError:
    print("pdfplumber: Not installed (optional)")

try:
    import yaml
    print("PyYAML: Available")
except ImportError:
    print("PyYAML: Not installed (optional, fallback regex used)")
