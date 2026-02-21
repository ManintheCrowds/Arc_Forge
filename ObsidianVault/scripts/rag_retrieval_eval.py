# PURPOSE: Golden-set recall@k evaluation for RAG retrieval.
# DEPENDENCIES: rag_pipeline (retrieve_context, load_pipeline_config, stage_ingest, stage_index), DocumentIndex.
# MODIFICATION NOTES: Baseline eval per rag_audit_and_golden_set_evaluation plan.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add scripts dir for imports
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from rag_pipeline import (
    DocumentIndex,
    load_pipeline_config,
    retrieve_context,
    stage_ingest,
    stage_index,
)


def _base_doc(source: str) -> str:
    """Extract base doc key from source (strip chunk suffix for PDFs)."""
    if " [chunk " in source:
        return source.split(" [chunk ")[0]
    return source


def _matches_expected(retrieved: str, expected: str) -> bool:
    """Check if retrieved source matches expected doc_key (exact or base-doc)."""
    ret_base = _base_doc(retrieved)
    exp_base = _base_doc(expected)
    return (
        retrieved == expected
        or ret_base == exp_base
        or ret_base == expected
        or retrieved == exp_base
    )


def compute_recall_at_k(
    retrieved_sources: List[str],
    expected_doc_keys: List[str],
    k: int,
) -> float:
    """
    Recall@k = |E ∩ R[:k]| / |E|.
    E = expected docs; R[:k] = top-k retrieved.
    Base-doc matching: if expected is base doc, any chunk from that doc counts.
    """
    if not expected_doc_keys:
        return 1.0
    r_k = retrieved_sources[:k]
    hit = 0
    for exp in expected_doc_keys:
        exp_base = _base_doc(exp)
        if any(_matches_expected(ret, exp) for ret in r_k):
            hit += 1
    return hit / len(expected_doc_keys)


def run_eval(
    config_path: Path,
    golden_path: Path,
    k_values: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Load golden set, run retrieve_context for each query, compute recall@k."""
    k_values = k_values or [4, 8]

    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    queries = golden.get("queries", [])
    if not queries:
        return {"error": "No queries in golden set", "queries": []}

    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"]
    # Ensure we retrieve enough for max k
    max_k = max(k_values)
    rag_config.setdefault("search", {})["limit"] = max(rag_config.get("search", {}).get("limit", 8), max_k)

    cache_config = rag_config.get("cache", {})
    doc_index = None
    if cache_config.get("enabled", True):
        cache_dir = Path(rag_config.get("vault_root", Path.cwd())) / cache_config.get("cache_dir", "Campaigns/_rag_cache")
        index_cache_path = cache_dir / cache_config.get("index_cache", "document_index.json")
        doc_index = DocumentIndex(index_cache_path)

    text_map = stage_ingest(rag_config)
    stage_index(text_map, doc_index, rag_config, cache_config)

    results: List[Dict[str, Any]] = []
    by_type: Dict[str, List[float]] = {}

    for q in queries:
        query = q.get("query", "")
        qtype = q.get("type", "unknown")
        expected = q.get("expected_doc_keys", [])

        items = retrieve_context(
            query,
            rag_config,
            doc_index=doc_index,
            text_map=text_map,
        )
        sources = [item.get("source", "") for item in items if item.get("source")]

        recalls = {}
        for k in k_values:
            recalls[f"recall@{k}"] = compute_recall_at_k(sources, expected, k)

        results.append({
            "query": query,
            "type": qtype,
            "recalls": recalls,
            "retrieved_count": len(sources),
            "expected_count": len(expected),
        })

        for k in k_values:
            key = f"recall@{k}"
            by_type.setdefault(qtype, {}).setdefault(key, []).append(recalls[key])

    # Aggregate
    mean_overall = {}
    for k in k_values:
        key = f"recall@{k}"
        vals = [r["recalls"][key] for r in results]
        mean_overall[key] = sum(vals) / len(vals) if vals else 0.0

    mean_by_type = {}
    for t, k_dict in by_type.items():
        mean_by_type[t] = {
            k: sum(vals) / len(vals) if vals else 0.0
            for k, vals in k_dict.items()
        }

    return {
        "queries": results,
        "mean_recall": mean_overall,
        "mean_by_type": mean_by_type,
        "k_values": k_values,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RAG retrieval recall@k evaluation")
    parser.add_argument("--config", default="ingest_config.json", help="Path to ingest config")
    parser.add_argument("--golden", default="golden_set.json", help="Path to golden set JSON")
    parser.add_argument("--k", type=int, nargs="+", default=[4, 8], help="k values for recall@k")
    parser.add_argument("--json", action="store_true", help="Output full JSON")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = _scripts_dir / config_path
    golden_path = Path(args.golden)
    if not golden_path.is_absolute():
        golden_path = _scripts_dir / golden_path

    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        return 1
    if not golden_path.exists():
        print(f"Golden set not found: {golden_path}", file=sys.stderr)
        return 1

    out = run_eval(config_path, golden_path, k_values=args.k)

    if "error" in out:
        print(out["error"], file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print("=== RAG Retrieval Recall@k Baseline ===")
        print(f"Mean recall: {out['mean_recall']}")
        print("\nPer query:")
        for r in out["queries"]:
            print(f"  {r['query']} ({r['type']}): {r['recalls']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
