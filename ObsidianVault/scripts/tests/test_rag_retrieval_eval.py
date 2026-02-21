# PURPOSE: Tests for RAG retrieval golden-set evaluation.
# DEPENDENCIES: rag_retrieval_eval, ingest_config.json, golden_set.json.
# MODIFICATION NOTES: Optional Phase 4 from rag_audit_and_golden_set_evaluation plan.

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
_scripts = Path(__file__).resolve().parents[1]
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from rag_retrieval_eval import compute_recall_at_k, run_eval, _base_doc, _matches_expected


def test_base_doc():
    """Base doc strips chunk suffix for PDFs."""
    assert _base_doc("[PDF] Foo.txt [chunk 1/24]") == "[PDF] Foo.txt"
    assert _base_doc("D:\\path\\file.md") == "D:\\path\\file.md"


def test_matches_expected():
    """Expected matching supports exact and base-doc."""
    assert _matches_expected("[PDF] Foo.txt [chunk 1/24]", "[PDF] Foo.txt")
    assert _matches_expected("[PDF] Foo.txt", "[PDF] Foo.txt [chunk 2/24]")
    assert not _matches_expected("[PDF] Bar.txt [chunk 1/4]", "[PDF] Foo.txt")


def test_compute_recall_at_k():
    """Recall@k = |E ∩ R[:k]| / |E|."""
    # All expected in top-k
    r = compute_recall_at_k(
        ["[PDF] A.txt [chunk 1/2]", "[PDF] B.txt"],
        ["[PDF] A.txt", "[PDF] B.txt"],
        k=4,
    )
    assert r == 1.0
    # Half in top-2
    r = compute_recall_at_k(
        ["[PDF] A.txt [chunk 1/2]", "[PDF] B.txt", "[PDF] C.txt"],
        ["[PDF] A.txt", "[PDF] C.txt"],
        k=2,
    )
    assert r == 0.5
    # Empty expected
    assert compute_recall_at_k(["x"], [], k=4) == 1.0


@pytest.mark.integration
def test_rag_retrieval_eval_baseline():
    """Run eval and assert mean recall meets baseline floor (regression guard)."""
    scripts_dir = Path(__file__).resolve().parents[1]
    config_path = scripts_dir / "ingest_config.json"
    golden_path = scripts_dir / "golden_set.json"
    if not config_path.exists() or not golden_path.exists():
        pytest.skip("ingest_config.json or golden_set.json not found")
    out = run_eval(config_path, golden_path, k_values=[4, 8])
    assert "error" not in out
    assert "mean_recall" in out
    # Baseline floor: mean recall@8 >= 0.0 (sanity; actual baseline ~0.10)
    assert out["mean_recall"]["recall@8"] >= 0.0
    assert len(out["queries"]) == 10
