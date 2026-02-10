# PURPOSE: Session ingestion — Archivist and Foreshadowing Engine (Phase 4).
# DEPENDENCIES: pathlib; rag_pipeline (load_pipeline_config, generate_text).
# MODIFICATION NOTES: Phase 4 Session Memory; extract Session Summary, run Archivist/Foreshadowing.

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_SPINE_PATH = (
    Path(__file__).resolve().parent.parent / "Campaigns" / "docs" / "prompts" / "system_prompt_spine.md"
)


def extract_session_summary(md_path: Path) -> str:
    """
    Extract the "Session Summary (for Archivist)" block from a session note.
    Returns content from that section until the next ## or end of file; "" if section missing.
    """
    path = Path(md_path)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    marker = "## Session Summary (for Archivist)"
    start = text.find(marker)
    if start < 0:
        return ""
    start += len(marker)
    nl = text.find("\n", start)
    if nl >= 0:
        start = nl + 1
    end = text.find("\n## ", start)
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def _load_system_prompt_spine(path: Optional[Path] = None) -> str:
    """Load Block 1 (Immutable Spine) from system_prompt_spine.md. Returns '' if missing."""
    p = Path(path) if path is not None else _DEFAULT_SPINE_PATH
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    start = text.find("## Block 1:")
    if start < 0:
        start = text.find("## Block 1 ")
    if start < 0:
        return ""
    end = text.find("## Block 2", start)
    if end < 0:
        end = text.find("---", start + 10)
    if end < 0:
        end = len(text)
    block = text[start:end].strip()
    if block.startswith("## Block 1"):
        first_newline = block.find("\n")
        if first_newline >= 0:
            block = block[first_newline + 1 :].strip()
    return block


def run_archivist(
    session_note_path: Path,
    config_path: Path,
    output_path: Optional[Path] = None,
    system_prompt_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run Archivist: read Session Summary from session note, call LLM (Role: Archivist + spine),
    write canonical timeline entries, flagged future consequences, retrieval anchors to output_path.
    """
    from rag_pipeline import load_pipeline_config, generate_text

    session_note_path = Path(session_note_path)
    config_path = Path(config_path)
    summary = extract_session_summary(session_note_path)
    if not summary.strip():
        return {"status": "skipped", "reason": "No Session Summary (for Archivist) block in session note"}

    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    spine = _load_system_prompt_spine(system_prompt_path)
    prompt = (
        "Role: Archivist\n\n"
        + (spine + "\n\n" if spine else "")
        + "Task: Convert the following Session Summary into canonical timeline entries, "
        "flagged future consequences, and retrieval anchors. Use the structure in docs/archivist_output_format.md.\n\n"
        "Session Summary:\n"
        + summary
    )
    out = generate_text(prompt, rag_config)
    if not out:
        return {"status": "error", "reason": "generate_text returned empty"}

    if output_path is None:
        from datetime import datetime
        vault_root = Path(__file__).resolve().parent.parent
        memory_dir = vault_root / "Campaigns" / "_session_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = memory_dir / f"{date_str}_archivist.md"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(out, encoding="utf-8")
    return {"status": "success", "output_path": str(output_path), "session_note": str(session_note_path)}


def run_foreshadowing(
    context_path: Path,
    config_path: Path,
    output_path: Optional[Path] = None,
    system_prompt_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run Foreshadowing Engine: read context (Archivist output or session summary), call LLM
    (Role: Foreshadowing Engine + spine), append up to 5 delayed consequences to threads.md.
    """
    from rag_pipeline import load_pipeline_config, generate_text
    from datetime import datetime

    context_path = Path(context_path)
    config_path = Path(config_path)
    if not context_path.exists():
        return {"status": "error", "reason": f"Context file not found: {context_path}"}
    context_text = context_path.read_text(encoding="utf-8")

    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    spine = _load_system_prompt_spine(system_prompt_path)
    prompt = (
        "Role: Foreshadowing Engine\n\n"
        + (spine + "\n\n" if spine else "")
        + "Task: Identify delayed consequences likely to emerge in 2–5 sessions. Limit 5 items. "
        "Provide a short probability estimate per item.\n\n"
        "Context:\n"
        + context_text[:8000]
    )
    out = generate_text(prompt, rag_config)
    if not out:
        return {"status": "error", "reason": "generate_text returned empty"}

    vault_root = Path(__file__).resolve().parent.parent
    memory_dir = vault_root / "Campaigns" / "_session_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    threads_file = output_path if output_path is not None else memory_dir / "threads.md"

    threads_file = Path(threads_file)
    threads_file.parent.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"\n\n---\n\n## {date_str}\n\n{out.strip()}\n"
    if threads_file.exists():
        block = block.lstrip()
    with open(threads_file, "a", encoding="utf-8") as f:
        f.write(block)
    return {"status": "success", "output_path": str(threads_file), "context_path": str(context_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Session ingestion: Archivist and Foreshadowing Engine")
    parser.add_argument("--session", type=Path, help="Path to session note (for Archivist)")
    parser.add_argument("--config", type=Path, default=None, help="Path to ingest/RAG config (e.g. ingest_config.json)")
    parser.add_argument("--output", type=Path, default=None, help="Output path for Archivist (default: Campaigns/_session_memory/YYYY-MM-DD_archivist.md)")
    parser.add_argument("--foreshadow", action="store_true", help="Run Foreshadowing Engine instead of Archivist")
    parser.add_argument("--context", type=Path, default=None, help="Context file for Foreshadowing (Archivist output or session note)")
    parser.add_argument("--spine", type=Path, default=None, help="Path to system_prompt_spine.md (optional)")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    config_candidates = [scripts_dir / "ingest_config.json", scripts_dir.parent / "Campaigns" / "ingest_config.json"]
    default_config = None
    for c in config_candidates:
        if c.exists():
            default_config = c
            break
    config_path = args.config or default_config
    if config_path is None or not config_path.exists():
        print("Error: no config file found. Pass --config path/to/ingest_config.json")
        return

    if args.foreshadow:
        context = args.context
        if context is None and args.session is not None:
            context = args.session
        if context is None:
            print("Error: --foreshadow requires --context or --session")
            return
        result = run_foreshadowing(context, config_path, args.output, args.spine)
    else:
        if args.session is None:
            print("Error: --session path/to/session.md required for Archivist")
            return
        result = run_archivist(args.session, config_path, args.output, args.spine)

    print(result.get("status", "unknown"))
    if result.get("output_path"):
        print("Output:", result["output_path"])
    if result.get("reason"):
        print("Reason:", result["reason"])


if __name__ == "__main__":
    main()
