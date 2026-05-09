# PURPOSE: Regression tests for optional OpenDataLoader PDF extraction.
# DEPENDENCIES: pytest, app.ingest.pdf_ingest

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from app.ingest.pdf_ingest import extract_pdf_sections_opendataloader


def _fake_opendataloader(monkeypatch, payload):
    def convert(*, output_dir: str, **_kwargs):
        Path(output_dir, "sample.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setitem(sys.modules, "opendataloader_pdf", SimpleNamespace(convert=convert))


def test_opendataloader_list_output_without_page_number_uses_default_page(monkeypatch, tmp_path):
    _fake_opendataloader(monkeypatch, [{"content": "List-shaped output text"}])

    sections = list(extract_pdf_sections_opendataloader(tmp_path / "sample.pdf"))

    assert len(sections) == 1
    assert sections[0]["page_number"] == 1
    assert sections[0]["normalized_text"] == "List-shaped output text"


def test_opendataloader_uses_description_when_content_is_missing(monkeypatch, tmp_path):
    _fake_opendataloader(
        monkeypatch,
        {
            "kids": [
                {
                    "type": "picture",
                    "page number": 2,
                    "description": "Chart summary from hybrid extraction",
                }
            ]
        },
    )

    sections = list(extract_pdf_sections_opendataloader(tmp_path / "sample.pdf"))

    assert len(sections) == 1
    assert sections[0]["page_number"] == 2
    assert sections[0]["normalized_text"] == "Chart summary from hybrid extraction"
