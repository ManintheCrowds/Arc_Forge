# PURPOSE: Heuristic evaluation of RAG-generated content per 06_rag_evaluation rubric.
# DEPENDENCIES: rag_pipeline.generate_text (optional, for LLM coherence).
# MODIFICATION NOTES: Optional hook; scores are heuristic-based (1-5 scale).

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def _score_citation_density(text: str, canonical_entities: List[str]) -> float:
    """Count canonical entity mentions; map to 1-5 scale."""
    if not text or not canonical_entities:
        return 1.0
    text_lower = text.lower()
    mentions = sum(1 for e in canonical_entities if e and e.lower() in text_lower)
    # 0 -> 1, 1-2 -> 2, 3-4 -> 3, 5-7 -> 4, 8+ -> 5
    if mentions >= 8:
        return 5.0
    if mentions >= 5:
        return 4.0
    if mentions >= 3:
        return 3.0
    if mentions >= 1:
        return 2.0
    return 1.0


def _score_structure(text: str, required_sections: List[str]) -> float:
    """Check presence of required structural elements via regex (## Scope, ### Mechanics); map to 1-5 scale."""
    if not text:
        return 1.0
    if not required_sections:
        return 3.0
    text_lower = text.lower()
    found = 0
    for section in required_sections:
        section_lower = section.lower()
        if re.search(r"^#{1,4}\s+" + re.escape(section_lower), text_lower, re.MULTILINE | re.IGNORECASE):
            found += 1
        elif section_lower in text_lower:
            found += 1
    ratio = found / len(required_sections)
    if ratio >= 1.0:
        return 5.0
    if ratio >= 0.75:
        return 4.0
    if ratio >= 0.5:
        return 3.0
    if ratio >= 0.25:
        return 2.0
    return 1.0


def _score_tone_fit(text: str, tone_keywords: List[str]) -> float:
    """Check presence of tone-related keywords; map to 1-5 scale."""
    if not text or not tone_keywords:
        return 3.0
    text_lower = text.lower()
    matches = sum(1 for kw in tone_keywords if kw.lower() in text_lower)
    if matches >= 3:
        return 5.0
    if matches >= 2:
        return 4.0
    if matches >= 1:
        return 3.0
    return 2.0


def _score_coherence_llm(text: str, rag_config: Dict[str, Any], output_type: str) -> float:
    """Optional LLM-based coherence scoring; returns 1-5 or 3.0 on failure."""
    try:
        from rag_pipeline import generate_text
        prompt = (
            f"Rate the coherence of this {output_type} text from 1 to 5 "
            "(1=incoherent, 5=highly coherent). Reply with only a single number.\n\n"
            f"Text:\n{text[:2000]}\n\nScore (1-5):"
        )
        out = generate_text(prompt, rag_config)
        if out:
            match = re.search(r"[1-5]", str(out).strip())
            if match:
                return float(match.group())
    except Exception:
        pass
    return 3.0


def evaluate_content_pack(
    content_pack: Dict[str, str],
    pattern_report: Dict[str, Any],
    theme_keywords: Optional[List[str]] = None,
    rag_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Heuristic evaluation of RAG content pack per 06_rag_evaluation rubric.
    Returns scores (1-5) for Coherence, Canon Reuse, Citation Density, Tone Fit, Utility.
    When evaluation.coherence_method is "llm" and rag_config provided, uses LLM for coherence.
    """
    entities = pattern_report.get("entities", {})
    canonical = (
        entities.get("NPCs", [])[:15]
        + entities.get("Factions", [])[:10]
        + entities.get("Locations", [])[:10]
        + entities.get("Items", [])[:15]
    )
    canonical = [str(e) for e in canonical if e]

    theme_keywords = theme_keywords or ["faith", "entropy", "grimdark", "heresy", "void"]
    eval_cfg = (rag_config or {}).get("evaluation", {})
    coherence_method = eval_cfg.get("coherence_method", "placeholder")

    def _coherence(text: str, output_type: str) -> float:
        if coherence_method == "llm" and rag_config:
            return _score_coherence_llm(text, rag_config, output_type)
        return 3.0

    results: Dict[str, Dict[str, float]] = {}

    # Rules: scope, mechanics, example of play (regex for ## Scope, ### Mechanics)
    rules = content_pack.get("rules", "")
    results["rules"] = {
        "coherence": _coherence(rules, "rules"),
        "canon_reuse": _score_citation_density(rules, canonical),
        "citation_density": _score_citation_density(rules, canonical),
        "tone_fit": _score_tone_fit(rules, theme_keywords),
        "utility": _score_structure(rules, ["scope", "mechanics", "example"]),
    }

    # Adventure: hook, adversaries, fallout
    adventure = content_pack.get("adventure", "")
    results["adventure"] = {
        "coherence": _coherence(adventure, "adventure"),
        "canon_reuse": _score_citation_density(adventure, canonical),
        "citation_density": _score_citation_density(adventure, canonical),
        "tone_fit": _score_tone_fit(adventure, theme_keywords),
        "utility": _score_structure(adventure, ["hook", "adversaries", "fallout"]),
    }

    # Bios: role, motivation, secret, hook
    bios = content_pack.get("bios", "")
    results["bios"] = {
        "coherence": _coherence(bios, "bios"),
        "canon_reuse": _score_citation_density(bios, canonical),
        "citation_density": _score_citation_density(bios, canonical),
        "tone_fit": _score_tone_fit(bios, theme_keywords),
        "utility": _score_structure(bios, ["role", "motivation", "secret", "hook"]),
    }

    return {
        "scores": results,
        "canonical_entities_count": len(canonical),
    }
