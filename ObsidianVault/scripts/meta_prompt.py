# PURPOSE: CLI for meta-prompt (VIII) — evaluate campaign state, suggest smallest high-impact change.
# DEPENDENCIES: pathlib; rag_pipeline (load_pipeline_config, generate_text).
# MODIFICATION NOTES: Phase 1 Track C; spine + meta-prompt text + campaign state → generate_text.

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

_DEFAULT_SPINE_PATH = (
    Path(__file__).resolve().parent.parent / "Campaigns" / "docs" / "prompts" / "system_prompt_spine.md"
)

META_PROMPT_INSTRUCTION = (
    "Evaluate current campaign state. Identify narrative entropy. "
    "Propose the smallest change that produces the largest future divergence. Explain reasoning."
)


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


def run_meta_prompt(
    campaign_state: str,
    config_path: Path,
    output_path: Optional[Path] = None,
    system_prompt_path: Optional[Path] = None,
) -> str:
    """
    Build prompt = spine + meta-prompt instruction + campaign state; call generate_text; return or write result.
    """
    from rag_pipeline import load_pipeline_config, generate_text

    config_path = Path(config_path)
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    spine = _load_system_prompt_spine(system_prompt_path)
    prompt = (
        (spine + "\n\n" if spine else "")
        + META_PROMPT_INSTRUCTION
        + "\n\nCampaign state:\n"
        + campaign_state
    )
    out = generate_text(prompt, rag_config)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(out or "", encoding="utf-8")
    return out or ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meta-prompt (VIII): evaluate campaign state, suggest smallest high-impact change."
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=None,
        help="Path to campaign state markdown (e.g. Workbench, archivist output). If omitted, read stdin.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to ingest/RAG config (e.g. ingest_config.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write result to file; default is stdout only",
    )
    parser.add_argument(
        "--spine",
        type=Path,
        default=None,
        help="Path to system_prompt_spine.md (optional)",
    )
    args = parser.parse_args()

    if args.context is not None:
        if not args.context.exists():
            print("Error: context file not found:", args.context, file=sys.stderr)
            sys.exit(1)
        campaign_state = args.context.read_text(encoding="utf-8")
    else:
        campaign_state = sys.stdin.read()

    scripts_dir = Path(__file__).resolve().parent
    config_candidates = [
        scripts_dir / "ingest_config.json",
        scripts_dir.parent / "Campaigns" / "ingest_config.json",
    ]
    default_config = None
    for c in config_candidates:
        if c.exists():
            default_config = c
            break
    config_path = args.config or default_config
    if config_path is None or not config_path.exists():
        print("Error: no config file found. Pass --config path/to/ingest_config.json", file=sys.stderr)
        sys.exit(1)

    result = run_meta_prompt(
        campaign_state,
        config_path,
        output_path=args.output,
        system_prompt_path=args.spine,
    )
    if args.output is None:
        print(result)
    else:
        print("Written to:", args.output)
        print(result)


if __name__ == "__main__":
    main()
