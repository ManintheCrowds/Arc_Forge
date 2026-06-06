from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import build_index as build_index_module


def test_build_index_uses_configured_output_path(tmp_path, monkeypatch):
    """Configured index path should be written and excluded from source scanning."""
    monkeypatch.setattr(build_index_module, "save_index_state", lambda *_args, **_kwargs: None)

    vault_root = tmp_path / "vault"
    sources_dir = vault_root / "Campaigns" / "Sources"
    sources_dir.mkdir(parents=True)

    (sources_dir / "actual-source.md").write_text(
        "---\n"
        "title: Actual Source\n"
        "doc_type: rules\n"
        "created: 2026-04-21\n"
        "---\n\n"
        "## Extracted Text Excerpt\n"
        "> Combat reference text.\n",
        encoding="utf-8",
    )
    configured_index = sources_dir / "TTRPG_Source_Index.md"
    configured_index.write_text(
        "---\n"
        "title: Old Index\n"
        "doc_type: index\n"
        "---\n\n"
        "This stale index should not be scanned as a source.",
        encoding="utf-8",
    )

    config = {
        "vault_root": str(vault_root),
        "source_notes_dir": "Campaigns/Sources",
        "extracted_text_dir": "Campaigns/Sources/_extracted_text",
        "index_builder": {
            "output_path": "Campaigns/Sources/TTRPG_Source_Index.md",
            "exclude_dirs": ["_extracted_text", "PDFs"],
        },
    }

    build_index_module.build_index(config, overwrite=True, incremental=False)

    assert configured_index.exists()
    content = configured_index.read_text(encoding="utf-8")
    assert "Actual Source" in content
    assert "Old Index" not in content
    assert not (sources_dir / "Source_Index.md").exists()
