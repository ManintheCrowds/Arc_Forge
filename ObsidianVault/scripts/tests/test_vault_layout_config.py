import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_index as build_index_module
from utils import get_config_path


VAULT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = SCRIPTS_DIR / "ingest_config.json"


def load_ingest_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    config["vault_root"] = str(VAULT_ROOT)
    return config


def test_checked_in_ingest_config_targets_campaign_vault_layout():
    config = load_ingest_config()

    existing_dirs = {
        "source_notes_dir": "Campaigns/Sources",
        "rules_dir": "Campaigns/Rules",
        "npcs_dir": "Campaigns/NPCs",
        "factions_dir": "Campaigns/Factions",
        "locations_dir": "Campaigns/Locations",
    }
    for key, expected in existing_dirs.items():
        assert config[key] == expected
        assert get_config_path(VAULT_ROOT, config, key).is_dir()

    source_dir = get_config_path(VAULT_ROOT, config, "source_notes_dir")
    generated_source_paths = [
        "extracted_text_dir",
        "ocr.output_dir",
        "ai_summarization.cache_dir",
        "table_extraction.output_dir",
        "rag_pipeline.summarization.cache_dir",
        "rag_pipeline.pdf_extraction_dir",
    ]
    for key in generated_source_paths:
        path = get_config_path(VAULT_ROOT, config, key)
        assert path.parent == source_dir

    index_path = get_config_path(VAULT_ROOT, config, "index_builder.output_path")
    assert index_path == source_dir / "TTRPG_Source_Index.md"


def test_build_index_writes_configured_campaign_index(tmp_path, monkeypatch):
    vault_root = tmp_path / "vault"
    source_dir = vault_root / "Campaigns" / "Sources"
    extracted_text_dir = source_dir / "_extracted_text"
    source_dir.mkdir(parents=True)
    extracted_text_dir.mkdir()

    (source_dir / "Book.md").write_text(
        "---\n"
        "title: Book\n"
        "doc_type: rules\n"
        "---\n\n"
        "Useful source content.\n",
        encoding="utf-8",
    )
    (source_dir / "Source_Index.md").write_text("# Legacy index\n", encoding="utf-8")
    target_index = source_dir / "TTRPG_Source_Index.md"
    target_index.write_text("# Old index\n", encoding="utf-8")

    config = {
        "vault_root": str(vault_root),
        "source_notes_dir": "Campaigns/Sources",
        "extracted_text_dir": "Campaigns/Sources/_extracted_text",
        "index_builder": {
            "output_path": "Campaigns/Sources/TTRPG_Source_Index.md",
            "exclude_dirs": ["_extracted_text"],
        },
    }

    monkeypatch.setattr(build_index_module, "__file__", str(tmp_path / "build_index.py"))
    build_index_module.build_index(config, overwrite=True, incremental=False)

    content = target_index.read_text(encoding="utf-8")
    assert "# Source Index" in content
    assert "[[Campaigns/Sources/Book.md|Book]]" in content
    assert "Legacy index" not in content
    assert not (vault_root / "Source_Index.md").exists()
