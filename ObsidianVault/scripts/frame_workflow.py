# PURPOSE: Frame (Story Architect) — propose 3 session frameworks from premise + arc state.
# DEPENDENCIES: pathlib; rag_pipeline (load_pipeline_config, generate_text).
# MODIFICATION NOTES: Phase 2 Track A; output matches frame_output_format.md.

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_SPINE_PATH = (
    Path(__file__).resolve().parent.parent / "Campaigns" / "docs" / "prompts" / "system_prompt_spine.md"
)

STORY_ARCHITECT_TASK = (
    "Task: Propose exactly 3 session frameworks. No prose. "
    "Each framework: title, one-line hook, 2–3 beats (bullets). "
    "Output structure: see Campaigns/docs/frame_output_format.md."
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


def run_story_architect(
    premise_path: Path,
    arc_state_path: Path,
    config_path: Path,
    output_path: Optional[Path] = None,
    system_prompt_path: Optional[Path] = None,
    tone_sliders: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load spine, build Role: Story Architect + task + premise + arc state (+ optional tone);
    call generate_text, write to output_path. Returns status dict.
    """
    from rag_pipeline import load_pipeline_config, generate_text

    premise_path = Path(premise_path)
    arc_state_path = Path(arc_state_path)
    config_path = Path(config_path)
    if not premise_path.exists():
        return {"status": "error", "reason": f"Premise file not found: {premise_path}"}
    if not arc_state_path.exists():
        return {"status": "error", "reason": f"Arc state file not found: {arc_state_path}"}

    premise = premise_path.read_text(encoding="utf-8").strip()
    arc_state = arc_state_path.read_text(encoding="utf-8").strip()

    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    spine = _load_system_prompt_spine(system_prompt_path)

    prompt_parts = [
        "Role: Story Architect\n\n",
        (spine + "\n\n") if spine else "",
        STORY_ARCHITECT_TASK,
        "\n\nCampaign premise:\n",
        premise[:8000],
        "\n\nCurrent arc state:\n",
        arc_state[:8000],
    ]
    if tone_sliders:
        prompt_parts.append("\n\nTone sliders (constraints):\n")
        prompt_parts.append(tone_sliders.strip()[:500])
    prompt = "".join(prompt_parts)

    out = generate_text(prompt, rag_config)
    if not out:
        return {"status": "error", "reason": "generate_text returned empty"}

    if output_path is None:
        from datetime import datetime
        vault_root = Path(__file__).resolve().parent.parent
        out_dir = vault_root / "Campaigns" / "_rag_outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = out_dir / f"frame_{date_str}.md"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(out, encoding="utf-8")
    return {
        "status": "success",
        "output_path": str(output_path),
        "premise_path": str(premise_path),
        "arc_state_path": str(arc_state_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Frame (Story Architect): propose 3 session frameworks from premise + arc state."
    )
    parser.add_argument("--premise", type=Path, required=True, help="Path to campaign premise markdown")
    parser.add_argument("--arc-state", type=Path, required=True, help="Path to current arc state markdown")
    parser.add_argument("--config", type=Path, default=None, help="Path to ingest/RAG config (e.g. ingest_config.json)")
    parser.add_argument("--output", type=Path, default=None, help="Output path (default: Campaigns/_rag_outputs/frame_YYYY-MM-DD.md)")
    parser.add_argument("--spine", type=Path, default=None, help="Path to system_prompt_spine.md (optional)")
    parser.add_argument("--tone", type=str, default=None, help="Tone sliders, e.g. 'grim, lethal' (optional)")
    args = parser.parse_args()

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
        print("Error: no config file found. Pass --config path/to/ingest_config.json")
        return

    result = run_story_architect(
        args.premise,
        args.arc_state,
        config_path,
        output_path=args.output,
        system_prompt_path=args.spine,
        tone_sliders=args.tone,
    )
    print(result.get("status", "unknown"))
    if result.get("output_path"):
        print("Output:", result["output_path"])
    if result.get("reason"):
        print("Reason:", result["reason"])


if __name__ == "__main__":
    main()
