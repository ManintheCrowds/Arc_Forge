# PURPOSE: Benchmark PDF ingestion performance with synthetic test data.
# DEPENDENCIES: ingest_pdfs.py, performance_profiler, pypdf (for synthetic PDFs).
# MODIFICATION NOTES: Creates test PDFs and measures ingestion performance.

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

try:
    from pypdf import PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    print("WARNING: pypdf not available. Cannot generate synthetic PDFs.", file=sys.stderr)

from performance_profiler import (
    get_collector,
    reset_collector,
    export_results,
    print_summary,
)


def create_synthetic_pdf(output_path: Path, pages: int = 10, text_per_page: str = "Sample text") -> None:
    """Create a synthetic PDF file for testing."""
    if not PYPDF_AVAILABLE:
        raise ImportError("pypdf required for synthetic PDF generation")
    
    writer = PdfWriter()
    
    # Create pages with text
    for i in range(pages):
        from pypdf.generic import DictionaryObject, ArrayObject, NameObject, NumberObject, TextStringObject
        from pypdf import PageObject
        
        page = PageObject.create_blank_page(width=612, height=792)
        # Add simple text content
        content = f"Page {i+1}\n{text_per_page}\n" * 20
        # Note: This is a simplified approach. Real PDFs would need proper content streams.
        writer.add_page(page)
    
    with output_path.open("wb") as f:
        writer.write(f)


def create_test_pdfs(pdf_dir: Path, count: int, pages_per_pdf: int = 50) -> List[Path]:
    """Create synthetic PDF files for benchmarking."""
    pdfs = []
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {count} synthetic PDFs...", file=sys.stderr)
    for i in range(count):
        pdf_path = pdf_dir / f"test_pdf_{i:04d}.pdf"
        try:
            create_synthetic_pdf(pdf_path, pages=pages_per_pdf)
            pdfs.append(pdf_path)
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1}/{count} PDFs...", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to create {pdf_path.name}: {e}", file=sys.stderr)
    
    return pdfs


def create_test_config(vault_root: Path, pdf_root: Path, output_dir: Path) -> Path:
    """Create a test configuration file."""
    config = {
        "vault_root": str(vault_root),
        "pdf_root": str(pdf_root),
        "source_notes_dir": "Sources",
        "rules_dir": "Rules",
        "npcs_dir": "NPCs",
        "factions_dir": "Factions",
        "locations_dir": "Locations",
        "items_dir": "Items",
        "templates": {
            "source_note": "Templates/source_note.md",
            "entity_note": "Templates/entity_note.md",
        },
        "extracted_text_dir": "Sources/_extracted_text",
        "pdf_text_cache_dirs": [],
        "pdf_text_cache_extensions": [".txt", ".md"],
        "max_excerpt_chars": 2000,
        "max_pdf_size_mb": 100,
    }
    
    config_path = output_dir / "benchmark_config.json"
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    return config_path


def run_benchmark(
    pdf_count: int,
    pages_per_pdf: int = 50,
    output_dir: Path | None = None,
    cleanup: bool = True,
) -> Dict:
    """Run a benchmark with the specified number of PDFs."""
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="pdf_ingest_benchmark_"))
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    vault_root = output_dir / "vault"
    pdf_root = output_dir / "pdfs"
    scripts_dir = Path(__file__).parent
    
    # Create test structure
    vault_root.mkdir(parents=True, exist_ok=True)
    (vault_root / "Templates").mkdir(parents=True, exist_ok=True)
    
    # Copy templates if they exist
    source_template = scripts_dir.parent / "Templates" / "source_note.md"
    entity_template = scripts_dir.parent / "Templates" / "entity_note.md"
    
    if source_template.exists():
        shutil.copy(source_template, vault_root / "Templates" / "source_note.md")
    else:
        # Create minimal template
        (vault_root / "Templates" / "source_note.md").write_text(
            "---\n"
            "title: \"{{title}}\"\n"
            "source_file: \"{{source_file}}\"\n"
            "source_pages: \"{{source_pages}}\"\n"
            "doc_type: \"{{doc_type}}\"\n"
            "created: \"{{date}}\"\n"
            "---\n\n"
            "## Summary\n\n- \n"
        )
    
    if entity_template.exists():
        shutil.copy(entity_template, vault_root / "Templates" / "entity_note.md")
    else:
        # Create minimal template
        (vault_root / "Templates" / "entity_note.md").write_text(
            "---\n"
            "title: \"{{title}}\"\n"
            "entity_type: \"{{entity_type}}\"\n"
            "created: \"{{date}}\"\n"
            "source_refs: []\n"
            "---\n\n"
            "## Summary\n\n- \n"
        )
    
    # Create test PDFs
    print(f"\n=== Benchmark: {pdf_count} PDFs ===", file=sys.stderr)
    pdfs = create_test_pdfs(pdf_root, pdf_count, pages_per_pdf)
    
    if not pdfs:
        print("ERROR: No PDFs created for benchmark", file=sys.stderr)
        return {}
    
    # Create config
    config_path = create_test_config(vault_root, pdf_root, output_dir)
    
    # Import and run ingestion
    sys.path.insert(0, str(scripts_dir))
    from ingest_pdfs import ingest_pdfs, load_config
    
    # Reset profiler
    reset_collector()
    
    # Load config
    config = load_config(config_path)
    
    # Run ingestion
    print(f"Running ingestion for {len(pdfs)} PDFs...", file=sys.stderr)
    ingest_pdfs(config, overwrite=True)
    
    # Get results
    collector = get_collector()
    collector.finish()
    
    results = collector.to_dict()
    results["pdf_count"] = len(pdfs)
    results["pages_per_pdf"] = pages_per_pdf
    
    # Cleanup
    if cleanup:
        print("Cleaning up test files...", file=sys.stderr)
        shutil.rmtree(output_dir, ignore_errors=True)
    
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark PDF ingestion performance.")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        type=int,
        default=[10, 100],
        help="PDF counts to test (default: 10 100)",
    )
    parser.add_argument(
        "--pages-per-pdf",
        type=int,
        default=50,
        help="Number of pages per synthetic PDF (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for benchmark results (default: temp directory)",
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't cleanup test files after benchmark",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Export results to JSON file",
    )
    
    args = parser.parse_args()
    
    if not PYPDF_AVAILABLE:
        print("ERROR: pypdf is required for benchmark. Install with: pip install pypdf", file=sys.stderr)
        sys.exit(1)
    
    all_results = []
    
    for pdf_count in args.scenarios:
        try:
            results = run_benchmark(
                pdf_count=pdf_count,
                pages_per_pdf=args.pages_per_pdf,
                output_dir=Path(args.output) if args.output else None,
                cleanup=not args.no_cleanup,
            )
            all_results.append(results)
            
            print(f"\n=== Results for {pdf_count} PDFs ===", file=sys.stderr)
            print_summary()
            
        except Exception as e:
            print(f"ERROR: Benchmark failed for {pdf_count} PDFs: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            continue
    
    # Export combined results
    if args.json_output:
        output_path = Path(args.json_output)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nBenchmark results exported to: {output_path}", file=sys.stderr)
    
    # Print summary
    print("\n=== Benchmark Summary ===", file=sys.stderr)
    for result in all_results:
        pdf_count = result.get("pdf_count", 0)
        duration = result.get("total_duration_seconds", 0)
        ops = result.get("operation_count", 0)
        io_stats = result.get("io_stats", {})
        print(
            f"{pdf_count} PDFs: {duration:.2f}s total, {ops} operations, "
            f"{io_stats.get('read_count', 0)} reads, {io_stats.get('write_count', 0)} writes",
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
