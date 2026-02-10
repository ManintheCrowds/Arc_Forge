#!/usr/bin/env python3
# PURPOSE: Generate storyboard for first arc using RAG pipeline.
# DEPENDENCIES: rag_pipeline, pathlib.
# MODIFICATION NOTES: Standalone script for generating TTRPG storyboards with specifications.

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from rag_pipeline import (
    load_pipeline_config,
    run_pipeline,
    generate_storyboard,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def main():
    """Generate storyboard for first arc."""
    # Load config
    config_path = Path(__file__).parent / "ingest_config.json"
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    
    # Specifications for first arc
    specs: Dict[str, Any] = {
        "character_sheets": """
    - Brawn Solo (Number 12) - Ogryn Bullgryn, Tier 3, Death Korps of Krieg
    - Godwin of House ___ - [character details from extracted sheet]
    - Tarquinius Superbus - [character details from extracted sheet]
    """,
        "player_context": """
    Players are Rogue Trader crew from Harbinger of Woe.
    Rogue Trader PC is protecting their family's Hive world.
    NOT Space Marines - Carcharodon Astra are foreshadowed only (hint at presence, don't reveal fully).
    """,
        "setting_constraints": """
    LAND-BASED setting: Highway racing alongside train track.
    Rubble obstacles everywhere that players must weave through.
    NO space, NO asteroids, NO void travel.
    """,
        "combat_specs": """
    First important combats: Train hijacking chase sequence.
    Players approach using wartruck. High-speed vehicle combat and boarding actions.
    Land-based highway with rubble obstacles to navigate.
    """,
        "enemy_forces": """
    ENEMY TYPE: Ork Warband (NOT cult forces - these are Ork units)
    - 3 wartrucks (Ork vehicles)
    - 3 battlewagons (Ork vehicles)
    - 3 bikers (Ork riders)
    - 10 storm boy jump pack infantry (Ork jump pack troops)
    - 6 Squig hog boys (Ork cavalry)
    - 7 killa kopters (Ork aircraft)
    """,
        "materials": """
    All enemy forces available. Player wartruck. Train terrain.
    MISSING: One Ork Freebooter Nob with Snazzy Tricorn hat (work around this).
    """,
        "scene_type": "Chase scene, train hijacking sequence, vehicle combat, boarding action",
        "foreshadowing": "Carcharodon Astra Space Marine Vanguard Detachment (hint at presence, don't reveal fully)"
    }
    
    # Query for relevant context - include character names to retrieve character sheets
    query = "Brawn Solo Godwin Tarquinius train hijacking chase scene wartruck ork forces storm boys squig hogs killa kopters Rogue Trader Harbinger of Woe"
    
    logger.info(f"Running RAG pipeline with query: {query}")
    
    # Run pipeline with query
    result = run_pipeline(config_path, query=query)
    
    if result.get("status") != "success":
        logger.error(f"Pipeline failed: {result}")
        sys.exit(1)
    
    logger.info("Pipeline completed successfully")
    
    # Extract character context from retrieved documents
    query_context = result.get("query_context", [])
    character_context = ""
    for item in query_context:
        source = item.get("source", "")
        text = item.get("text", "")
        if any(name in source for name in ["Brawn", "Godwin", "Tarquinius"]):
            # Extract relevant character info (first 800 chars to avoid too much text)
            character_context += f"\n**Character Sheet Excerpt from {source}:**\n{text[:800]}...\n"
    
    # Add character context to specifications if found
    if character_context:
        if "character_sheets" in specs:
            specs["character_sheets"] += f"\n**Extracted Character Context:**{character_context}"
        logger.info("Character context extracted from retrieved documents")
    
    logger.info("Generating storyboard...")
    
    # Generate storyboard
    storyboard = generate_storyboard(
        result.get("context_summary", ""),
        result.get("pattern_report", {}),
        rag_config,
        specifications=specs
    )
    
    if not storyboard:
        logger.error("Storyboard generation returned empty result")
        sys.exit(1)
    
    # Save storyboard
    output_dir = Path(rag_config["output_dir"])
    if not output_dir.is_absolute():
        # Resolve relative to vault root if needed
        vault_root = Path(rag_config.get("vault_root", Path(__file__).parent.parent))
        output_dir = vault_root / output_dir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    storyboard_path = output_dir / "first_arc_storyboard.md"
    
    storyboard_path.write_text(storyboard, encoding="utf-8")
    logger.info(f"Storyboard saved to: {storyboard_path}")
    
    print(f"\n✓ Storyboard generated successfully!")
    print(f"  Location: {storyboard_path}")
    print(f"  Size: {len(storyboard)} characters\n")


if __name__ == "__main__":
    main()
