# PURPOSE: Unit tests for PDF extraction edge cases.
# DEPENDENCIES: pytest monkeypatch, app.ingest.pdf_ingest.
# MODIFICATION NOTES: Covers OpenDataLoader JSON shapes.

import json
import sys
from types import SimpleNamespace

from app.ingest.pdf_ingest import extract_pdf_sections_opendataloader


def test_opendataloader_list_output_defaults_page_when_child_lacks_page(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    def fake_convert(**kwargs):
        out_dir = kwargs["output_dir"]
        output = [{"type": "paragraph", "content": "  Useful text from PDF  "}]
        with open(f"{out_dir}/sample.json", "w", encoding="utf-8") as f:
            json.dump(output, f)

    fake_module = SimpleNamespace(convert=fake_convert)
    monkeypatch.setitem(sys.modules, "opendataloader_pdf", fake_module)

    sections = list(extract_pdf_sections_opendataloader(pdf_path))

    assert len(sections) == 1
    assert sections[0]["page_number"] == 1
    assert sections[0]["normalized_text"] == "Useful text from PDF"
