# PURPOSE: Storyboard-to-Encounter workflow stages (decomposition, drafts, refinement, export).
# DEPENDENCIES: pathlib, json, re; optional yaml, rag_pipeline.
# MODIFICATION NOTES: Implements plan stages 1–5; interface-ready for future GUI/CLI.
# Narrative workbench: optional system prompt spine + Role: Encounter Designer (Phase 3).

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Default path to system prompt spine (Campaigns/docs/prompts/system_prompt_spine.md).
_DEFAULT_SPINE_PATH = (
    Path(__file__).resolve().parent.parent / "Campaigns" / "docs" / "prompts" / "system_prompt_spine.md"
)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "encounter"


def _parse_storyboard_sections(text: str) -> List[Dict[str, Any]]:
    """Extract numbered sections (I. … II. … III. …) from storyboard text."""
    sections: List[Dict[str, Any]] = []
    # Match "I. Title" or "III. First Combat (Highway Chase)"
    pattern = re.compile(r"^([IVX]+)\.\s+(.+?)(?=\n|$)", re.MULTILINE | re.IGNORECASE)
    for m in pattern.finditer(text):
        num = m.group(1).upper()
        title = m.group(2).strip()
        sections.append({"num": num, "title": title, "raw": m.group(0)})
    return sections


def _infer_encounters_from_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map storyboard sections to encounter list. Human can edit output granularity."""
    encounters: List[Dict[str, Any]] = []
    seq = 0
    prev_id: Optional[str] = None
    for s in sections:
        title = s["title"]
        tlower = title.lower()
        if "introduction" in tlower or "setup" in tlower or "conclusion" in tlower:
            continue
        if "combat" in tlower or "hijack" in tlower or "boarding" in tlower or "chase" in tlower:
            seq += 1
            eid = _slug(title)
            encounters.append({
                "id": eid,
                "name": title,
                "type": "combat" if ("combat" in tlower or "chase" in tlower or "boarding" in tlower) else "environmental",
                "sequence": seq,
                "storyboard_section": f"{s['num']}. {title}",
                "after": prev_id,
                "before": None,
            })
            prev_id = eid
    for i in range(len(encounters) - 1):
        encounters[i]["before"] = encounters[i + 1]["id"]
    return encounters


def run_stage_1(
    storyboard_path: Path,
    arc_id: str,
    output_dir: Path,
    storyboard_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Stage 1: Storyboard → Task Decomposition.
    Reads storyboard, proposes encounters/opportunities, writes task_decomposition.md and .yaml.
    """
    output_dir = output_dir / arc_id
    output_dir.mkdir(parents=True, exist_ok=True)

    text = storyboard_path.read_text(encoding="utf-8")
    sections = _parse_storyboard_sections(text)
    encounters = _infer_encounters_from_sections(sections)
    opportunities: List[Dict[str, Any]] = []  # Optional; human can add in YAML later.

    try:
        ref = storyboard_ref or str(storyboard_path.relative_to(output_dir.parent.parent))
    except ValueError:
        ref = storyboard_ref or storyboard_path.name
    constraints: List[str] = []
    for i, e in enumerate(encounters):
        if e.get("after"):
            constraints.append(f"{e.get('after', '')} before {e['id']}")

    data: Dict[str, Any] = {
        "arc_id": arc_id,
        "storyboard_ref": ref,
        "encounters": encounters,
        "opportunities": opportunities,
        "sequence_constraints": constraints,
    }

    # Write Markdown
    md_path = output_dir / "task_decomposition.md"
    lines = [
        f"# Task Decomposition: {arc_id}",
        "",
        f"**Storyboard:** {ref}",
        "",
        "## Encounters",
        "",
    ]
    for e in encounters:
        lines.append(f"- **{e['name']}** (id: `{e['id']}`, type: {e['type']}, sequence: {e['sequence']})")
        lines.append(f"  - Section: {e.get('storyboard_section', '')}")
        lines.append("")
    if opportunities:
        lines.append("## Opportunities")
        lines.append("")
        for o in opportunities:
            lines.append(f"- **{o.get('name', o.get('id', ''))}** (id: `{o.get('id', '')}`)")
            lines.append("")
    lines.append("## Sequence constraints")
    lines.append("")
    for c in constraints:
        lines.append(f"- {c}")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # Write YAML or JSON mirror
    data_path = output_dir / "task_decomposition.yaml"
    if HAS_YAML:
        with open(data_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        data_path = output_dir / "task_decomposition.json"
        data_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"status": "success", "encounters": encounters, "opportunities": opportunities, "md_path": str(md_path), "data_path": str(data_path)}


def _load_task_decomposition(path: Path) -> Dict[str, Any]:
    """Load task decomposition from .yaml or .json."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml") and HAS_YAML:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _read_kb_sections(md_path: Path, max_chars: int = 8000) -> str:
    """Read markdown and return content up to max_chars. Fallback for NPC/location lookup."""
    if not md_path.exists():
        return f"[File not found: {md_path.name} – see campaign_kb]"
    s = md_path.read_text(encoding="utf-8")
    return s[:max_chars] + ("…" if len(s) > max_chars else "")


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


def _encounter_designer_prefix(system_prompt_path: Optional[Path] = None) -> str:
    """Prefix for Encounter Designer role + spine. Prepend to user prompt when calling LLM."""
    spine = _load_system_prompt_spine(system_prompt_path)
    if not spine:
        return ""
    return "Role: Encounter Designer\n\n" + spine + "\n\n"


def draft_encounter(
    encounter_spec: Dict[str, Any],
    storyboard_text: str,
    rag_config: Dict[str, Any],
    campaign_kb_root: Path,
    config_path: Path,
    system_prompt_path: Optional[Path] = None,
    retrieval_mode: Optional[str] = None,
    tag_filters: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate one encounter draft using RAG (W&G mechanics) and campaign_kb (NPCs, locations).
    Fallbacks: generic DN hints if RAG fails; placeholder if NPC/location not found.
    When system_prompt_path is set (or default spine exists), prepends Role: Encounter Designer + spine.
    Optional retrieval_mode (Strict Canon / Loose Canon / Inspired By) and tag_filters passed to run_pipeline (B4).
    """
    from rag_pipeline import (
        load_pipeline_config,
        run_pipeline,
        generate_text,
    )
    eid = encounter_spec.get("id", "encounter")
    name = encounter_spec.get("name", eid)
    etype = encounter_spec.get("type", "combat")
    section = encounter_spec.get("storyboard_section", "")
    story_excerpt = storyboard_text[:3000] if len(storyboard_text) > 3000 else storyboard_text

    # RAG: query for mechanics (B4: optional retrieval_mode from encounter_spec or rag_config)
    if retrieval_mode is None:
        retrieval_mode = encounter_spec.get("retrieval_mode") or (rag_config.get("query_mode") or {}).get("retrieval_mode")
    if tag_filters is None:
        tag_filters = encounter_spec.get("tag_filters") or (rag_config.get("query_mode") or {}).get("tag_filters")
    query = f"Wrath and Glory {etype} encounter skill test DN pilot vehicle combat"
    if "chase" in name.lower() or "highway" in name.lower():
        query += " pilot agility rubble vehicle"
    if "boarding" in name.lower():
        query += " boarding agility athletics"
    result = run_pipeline(config_path, query=query, retrieval_mode=retrieval_mode, tag_filters=tag_filters)
    context_summary = result.get("context_summary") or ""
    if not context_summary:
        context_summary = "Use DN 3–5 for routine tests, DN 4 for combat. Pilot (Agi), Athletics (Str), Melee (WS), Ballistic Skill (BS) are common."

    # campaign_kb excerpts
    npcs_path = campaign_kb_root / "campaign" / "03_npcs.md"
    locs_path = campaign_kb_root / "campaign" / "02_locations.md"
    npc_excerpt = _read_kb_sections(npcs_path)
    loc_excerpt = _read_kb_sections(locs_path)

    prompt = (
        "Write a short Wrath & Glory encounter draft in markdown.\n\n"
        f"**Encounter:** {name} (id: {eid}, type: {etype})\n"
        f"**Storyboard section:** {section}\n\n"
        f"**Storyboard excerpt:**\n{story_excerpt}\n\n"
        f"**Mechanics context (use or adapt):**\n{context_summary[:rag_config.get('search', {}).get('max_chunk_chars', 2000)]}\n\n"
        f"**NPC reference (link or paraphrase):**\n{npc_excerpt[:1500]}\n\n"
        f"**Location reference:**\n{loc_excerpt[:1500]}\n\n"
        "Output format:\n"
        "## [Encounter name]\n"
        "### Setup\n[1–2 sentences]\n"
        "### Mechanics\n- List skill tests with DN (e.g. Pilot (Agi) DN 3).\n"
        "### NPCs / Locations\n[Refs to 03_npcs, 02_locations or placeholders]\n"
        "Keep it under 600 words."
    )
    full_prompt = _encounter_designer_prefix(system_prompt_path) + prompt
    out = generate_text(full_prompt, rag_config)
    return out or f"## {name}\n\n*Draft placeholder: edit from storyboard section {section}.*"


def run_stage_2(
    task_decomposition_path: Path,
    storyboard_path: Path,
    arc_id: str,
    config_path: Path,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Stage 2: Task Decomposition → Encounter Drafts.
    Loads decomposition, runs draft_encounter for each encounter/opportunity, writes _draft_v1.md.
    """
    from rag_pipeline import load_pipeline_config

    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    campaign_kb_root = Path(rag_config["campaign_kb_root"])
    storyboard_text = storyboard_path.read_text(encoding="utf-8")
    data = _load_task_decomposition(task_decomposition_path)
    arc_id = data.get("arc_id", arc_id)
    encounters = data.get("encounters", [])
    opportunities = data.get("opportunities", [])

    base = output_dir or task_decomposition_path.parent
    enc_dir = base / "encounters"
    opp_dir = base / "opportunities"
    enc_dir.mkdir(parents=True, exist_ok=True)
    opp_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []

    for spec in encounters:
        draft = draft_encounter(spec, storyboard_text, rag_config, campaign_kb_root, config_path)
        slug = spec.get("id", _slug(spec.get("name", "encounter")))
        p = enc_dir / f"{slug}_draft_v1.md"
        p.write_text(draft, encoding="utf-8")
        written.append(str(p))

    for spec in opportunities:
        draft = draft_encounter(spec, storyboard_text, rag_config, campaign_kb_root, config_path)
        slug = spec.get("id", _slug(spec.get("name", "opportunity")))
        p = opp_dir / f"{slug}_draft_v1.md"
        p.write_text(draft, encoding="utf-8")
        written.append(str(p))

    return {"status": "success", "written": written, "encounters": len(encounters), "opportunities": len(opportunities)}


def _load_feedback(path: Path) -> Dict[str, Any]:
    """Load structured feedback from .yaml or .json."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml") and HAS_YAML:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _feedback_for_encounter(feedback_data: Dict[str, Any], encounter_id: str) -> List[Dict[str, Any]]:
    """Get feedback list for one encounter from loaded feedback data."""
    for enc in feedback_data.get("encounters", []):
        if enc.get("id") == encounter_id:
            return enc.get("feedback", [])
    return []


def _format_feedback_for_prompt(feedback_list: List[Dict[str, Any]]) -> str:
    """Turn structured feedback into instruction text for the LLM."""
    lines = []
    for i, fb in enumerate(feedback_list, 1):
        t = fb.get("type", "other")
        if t == "expand":
            lines.append(f"{i}. EXPAND: {fb.get('target', '')} – {fb.get('instruction', '')}")
        elif t == "change":
            lines.append(f"{i}. CHANGE: {fb.get('target', '')} from {fb.get('from')} to {fb.get('to')}")
        elif t == "add_mechanic":
            lines.append(f"{i}. ADD MECHANIC: {fb.get('detail', '')}")
        elif t == "remove":
            lines.append(f"{i}. REMOVE: {fb.get('target', fb.get('instruction', ''))}")
        elif t == "link_npc":
            lines.append(f"{i}. LINK NPC: {fb.get('npc_id', '')} – {fb.get('instruction', '')}")
        elif t == "link_location":
            lines.append(f"{i}. LINK LOCATION: {fb.get('location_id', '')} – {fb.get('instruction', '')}")
        else:
            lines.append(f"{i}. OTHER: {fb.get('instruction', fb.get('detail', ''))}")
    return "\n".join(lines) if lines else "No structured feedback."


def refine_encounter(
    draft_path: Path,
    feedback_path: Path,
    rag_config: Dict[str, Any],
    output_path: Optional[Path] = None,
    system_prompt_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Stage 4: Human Review → Refined Encounter.
    Reads draft and structured feedback, produces next draft version (e.g. _draft_v2).
    When system_prompt_path is set (or default spine exists), prepends Role: Encounter Designer + spine.
    """
    from rag_pipeline import generate_text

    draft_path = Path(draft_path)
    feedback_path = Path(feedback_path)
    draft_text = draft_path.read_text(encoding="utf-8")
    feedback_data = _load_feedback(feedback_path)

    # Infer encounter_id from filename: "highway_chase_draft_v1" -> "highway_chase"
    stem = draft_path.stem
    encounter_id = stem
    if "_draft_v" in stem:
        encounter_id = stem.rsplit("_draft_v", 1)[0]

    feedback_list = _feedback_for_encounter(feedback_data, encounter_id)
    if not feedback_list:
        return {"status": "skipped", "reason": f"No feedback for encounter id {encounter_id}"}

    # Next version number
    next_v = 2
    if "_draft_v" in stem:
        try:
            next_v = int(stem.rsplit("_draft_v", 1)[1]) + 1
        except ValueError:
            pass
    out_dir = output_path or draft_path.parent
    out_file = out_dir / f"{encounter_id}_draft_v{next_v}.md"
    if output_path and output_path.suffix:
        out_file = Path(output_path)

    instructions = _format_feedback_for_prompt(feedback_list)
    prompt = (
        "You are revising a Wrath & Glory encounter draft using the following feedback.\n\n"
        "**Current draft:**\n"
        f"{draft_text}\n\n"
        "**Structured feedback – apply these changes:**\n"
        f"{instructions}\n\n"
        "Output the revised encounter draft in markdown. Keep the same structure (Setup, Mechanics, NPCs/Locations). "
        "Apply every feedback item. Do not add commentary, only the revised draft."
    )
    full_prompt = _encounter_designer_prefix(system_prompt_path) + prompt
    revised = generate_text(full_prompt, rag_config)
    if not revised:
        return {"status": "error", "reason": "generate_text returned empty"}
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(revised, encoding="utf-8")
    return {"status": "success", "output_path": str(out_file), "encounter_id": encounter_id, "version": next_v}


def _collect_final_encounter_files(arc_dir: Path) -> List[tuple[str, Path]]:
    """Collect (slug, path) for final encounter/opportunity docs. Prefer slug.md, else latest _draft_vN."""
    out: List[tuple[str, Path]] = []
    for sub in ("encounters", "opportunities"):
        d = arc_dir / sub
        if not d.exists():
            continue
        seen: Dict[str, Path] = {}
        for f in d.glob("*.md"):
            stem = f.stem
            if "_draft_v" in stem:
                base = stem.rsplit("_draft_v", 1)[0]
                # keep latest draft per base
                if base not in seen or f.stat().st_mtime > seen[base].stat().st_mtime:
                    seen[base] = f
            else:
                seen[stem] = f
        for slug, p in seen.items():
            out.append((slug, p))
    # Sort by slug for stable ordering
    out.sort(key=lambda x: x[0])
    return out


def export_final_specs(
    arc_id: str,
    arc_dir: Path,
    campaign_kb_path: Path,
    storyboard_path: Optional[Path] = None,
    vault_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Stage 5: Refined Encounters → Final Specs.
    Produces: (1) hierarchical final .md, (2) expanded storyboard, (3) first_arc_encounters.json,
    (4) campaign_kb/04_missions_{arc}_encounters.md with links to 03_npcs, 02_locations.
    """
    arc_dir = Path(arc_dir)
    campaign_kb_path = Path(campaign_kb_path)
    vault_root = vault_root or arc_dir.parent
    collected = _collect_final_encounter_files(arc_dir)
    if not collected:
        return {"status": "error", "reason": "No encounter/opportunity files found in arc dir"}

    # (1) Ensure final filenames: copy to {slug}.md if not already
    final_specs: List[tuple[str, Path]] = []
    for slug, src in collected:
        dest = src.parent / f"{slug}.md"
        if src != dest:
            dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        final_specs.append((slug, dest))

    # (2) Expanded storyboard: storyboard + concatenated encounter text
    expanded_lines = []
    if storyboard_path and storyboard_path.exists():
        expanded_lines.append(storyboard_path.read_text(encoding="utf-8"))
        expanded_lines.append("\n---\n\n# Expanded encounter specs\n\n")
    for slug, p in final_specs:
        expanded_lines.append(f"## {slug}\n\n")
        expanded_lines.append(p.read_text(encoding="utf-8"))
        expanded_lines.append("\n\n")
    expanded_path = arc_dir / f"{arc_id}_expanded_storyboard.md"
    expanded_path.write_text("".join(expanded_lines), encoding="utf-8")

    # (3) JSON: id, name, type, sequence, npc_refs, location_refs, mechanics, flavour
    json_entries = []
    for i, (slug, p) in enumerate(final_specs, 1):
        raw = p.read_text(encoding="utf-8")
        json_entries.append({
            "id": slug,
            "name": slug.replace("_", " ").title(),
            "type": "combat" if "encounters" in str(p) else "opportunity",
            "sequence": i,
            "npc_refs": [],
            "location_refs": [],
            "mechanics": "",
            "flavour": raw[:500] + ("…" if len(raw) > 500 else ""),
        })
    json_path = arc_dir / f"{arc_id}_encounters.json"
    json_path.write_text(json.dumps({"arc_id": arc_id, "encounters": json_entries}, indent=2), encoding="utf-8")

    # (4) campaign_kb: 04_missions_{arc}_encounters.md
    kb_campaign = campaign_kb_path / "campaign" if (campaign_kb_path / "campaign").exists() else campaign_kb_path
    missions_file = kb_campaign / f"04_missions_{arc_id}_encounters.md"
    rel_enc = arc_dir.relative_to(vault_root) if vault_root in arc_dir.parents else arc_dir
    md_lines = [
        f"# Mission encounters: {arc_id}",
        "",
        "Generated from storyboard workflow. Links to encounter files and campaign_kb NPCs/locations.",
        "",
        "## Encounters",
        "",
    ]
    for slug, p in final_specs:
        rel_path = p.relative_to(vault_root) if vault_root in p.parents else p
        md_lines.append(f"- **{slug}**: [{slug}]({rel_path})\n")
    md_lines.append("\n## NPC / Location links\n")
    md_lines.append("- NPCs: [campaign/03_npcs](campaign/03_npcs.md)\n")
    md_lines.append("- Locations: [campaign/02_locations](campaign/02_locations.md)\n")
    missions_file.parent.mkdir(parents=True, exist_ok=True)
    missions_file.write_text("".join(md_lines), encoding="utf-8")

    return {
        "status": "success",
        "final_md": [str(p) for _, p in final_specs],
        "expanded_storyboard": str(expanded_path),
        "json_path": str(json_path),
        "campaign_kb_path": str(missions_file),
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Storyboard-to-Encounter workflow")
    ap.add_argument("storyboard", type=Path, nargs="?", help="Path to storyboard .md (stage 1 and 2)")
    ap.add_argument("--arc-id", default="first_arc", help="Arc identifier")
    ap.add_argument("--output-dir", type=Path, help="Campaigns root (default: vault/Campaigns)")
    ap.add_argument("--storyboard-ref", default=None, help="Storyboard path for docs (stage 1)")
    ap.add_argument("--stage", type=int, default=1, choices=[1, 2, 4, 5], help="Stage to run")
    ap.add_argument("--task-decomp", type=Path, help="Path to task_decomposition.yaml (stage 2)")
    ap.add_argument("--config", type=Path, default=None, help="ingest_config.json (stage 2, 4)")
    ap.add_argument("--draft", type=Path, help="Draft .md path (stage 4)")
    ap.add_argument("--feedback", type=Path, help="Feedback .yaml/.json path (stage 4)")
    ap.add_argument("--arc-dir", type=Path, help="Arc dir e.g. Campaigns/first_arc (stage 5)")
    ap.add_argument("--campaign-kb", type=Path, help="campaign_kb root (stage 5)")
    args = ap.parse_args()
    scripts_dir = Path(__file__).resolve().parent
    vault = scripts_dir.parent
    out = args.output_dir or (vault / "Campaigns")

    if args.stage == 1:
        if not args.storyboard:
            ap.error("storyboard path required for stage 1")
        res = run_stage_1(Path(args.storyboard).resolve(), args.arc_id, out.resolve(), args.storyboard_ref)
    elif args.stage == 2:
        if not args.task_decomp or not args.storyboard:
            ap.error("--task-decomp and storyboard required for stage 2")
        cfg = args.config or (scripts_dir / "ingest_config.json")
        res = run_stage_2(
            Path(args.task_decomp).resolve(),
            Path(args.storyboard).resolve(),
            args.arc_id,
            cfg.resolve(),
            output_dir=(out / args.arc_id).resolve(),
        )
    elif args.stage == 4:
        if not args.draft or not args.feedback:
            ap.error("--draft and --feedback required for stage 4")
        from rag_pipeline import load_pipeline_config
        cfg = args.config or (scripts_dir / "ingest_config.json")
        rag_config = load_pipeline_config(cfg)["rag"]
        res = refine_encounter(
            Path(args.draft).resolve(),
            Path(args.feedback).resolve(),
            rag_config,
        )
    elif args.stage == 5:
        arc_dir = args.arc_dir or (out / args.arc_id)
        kb = args.campaign_kb or (vault.parent / "campaign_kb")
        sb = (out / "_rag_outputs" / "first_arc_storyboard.md") if args.arc_id == "first_arc" else None
        if not sb or not sb.exists():
            sb = None
        res = export_final_specs(
            args.arc_id,
            arc_dir.resolve(),
            kb.resolve(),
            storyboard_path=sb,
            vault_root=vault,
        )
    else:
        res = {"status": "error", "reason": "unknown stage"}
    print(json.dumps(res, indent=2))
