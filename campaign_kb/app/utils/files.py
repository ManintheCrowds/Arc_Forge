# PURPOSE: File discovery helpers for ingestion.
# DEPENDENCIES: pathlib
# MODIFICATION NOTES: MVP file utilities.

from pathlib import Path


_TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".html", ".htm"}


def _list_files_by_extension(root: Path, extensions: set[str], recursive: bool) -> list[Path]:
    # PURPOSE: Enumerate files by extension under a directory.
    # DEPENDENCIES: pathlib
    # MODIFICATION NOTES: Shared helper for PDF/text file discovery.
    if not root.exists():
        return []
    globber = root.rglob if recursive else root.glob
    files = [path for path in globber("*") if path.is_file() and path.suffix.lower() in extensions]
    return sorted(files)


def list_pdf_files(pdf_root: Path, recursive: bool = False) -> list[Path]:
    # PURPOSE: Enumerate PDF files under a directory.
    # DEPENDENCIES: pathlib
    # MODIFICATION NOTES: Optional recursive search for nested PDFs.
    return _list_files_by_extension(pdf_root, {".pdf"}, recursive=recursive)


def list_text_files(root: Path, recursive: bool = True) -> list[Path]:
    # PURPOSE: Enumerate text/markdown/html files under a directory.
    # DEPENDENCIES: pathlib
    # MODIFICATION NOTES: Recursive by default for docs folders.
    return _list_files_by_extension(root, _TEXT_EXTENSIONS, recursive=recursive)
