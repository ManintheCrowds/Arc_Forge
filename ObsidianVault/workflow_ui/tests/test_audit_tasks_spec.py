# PURPOSE: Validate gui_audit_tasks.yaml: load, DAG acyclic, T1/T2 roots, batch order, handoff paths.
# DEPENDENCIES: pytest, PyYAML; run_audit_tasks (docs) for load_spec and compute_batches.

import sys
from pathlib import Path

import pytest

# Resolve workflow_ui/docs so we can import run_audit_tasks
WORKFLOW_UI_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = WORKFLOW_UI_ROOT / "docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

import run_audit_tasks as run_mod

YAML_PATH = DOCS_DIR / "gui_audit_tasks.yaml"


def _load_spec():
    return run_mod.load_spec(YAML_PATH)


def _tasks():
    spec = _load_spec()
    return spec.get("tasks") or {}


@pytest.fixture(scope="module")
def spec():
    return _load_spec()


@pytest.fixture(scope="module")
def tasks(spec):
    return spec.get("tasks") or {}


def test_load_yaml_workflow_and_tasks(spec):
    assert spec.get("workflow") == "gui_audit"
    task_ids = list(spec.get("tasks", {}).keys())
    assert set(task_ids) == {"T1", "T2", "T3", "T4", "T5", "T6"}


def test_dag_depends_on_reference_existing_tasks(tasks):
    task_ids = set(tasks.keys())
    for tid, t in tasks.items():
        deps = t.get("depends_on") or []
        for d in deps:
            assert d in task_ids, f"{tid} depends_on unknown task {d}"


def test_dag_acyclic(tasks):
    """Traverse from roots; assert no back-edge (no cycle)."""
    task_ids = list(tasks.keys())
    dep_map = {tid: list(tasks[tid].get("depends_on") or []) for tid in task_ids}
    visited = set()
    rec_stack = set()

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        for d in dep_map.get(node, []):
            if d not in visited:
                if has_cycle(d):
                    return True
            elif d in rec_stack:
                return True
        rec_stack.discard(node)
        return False

    for tid in task_ids:
        if tid not in visited and has_cycle(tid):
            pytest.fail("Cycle detected in depends_on graph")
    rec_stack.clear()


def test_parallel_roots_t1_t2_no_deps(tasks):
    assert tasks["T1"].get("depends_on") == []
    assert tasks["T2"].get("depends_on") == []


def test_schedule_structure_batches(tasks):
    batches = run_mod.compute_batches(tasks)
    assert len(batches) == 5
    assert set(batches[0]) == {"T1", "T2"}
    assert batches[1] == ["T3"]
    assert batches[2] == ["T4"]
    assert batches[3] == ["T5"]
    assert batches[4] == ["T6"]


def test_handoff_t4_output_t5_input(tasks):
    t4_outputs = [o for o in tasks["T4"].get("outputs") or [] if "_audit_raw_output" in o]
    t5_inputs = [i for i in tasks["T5"].get("inputs") or [] if "_audit_raw_output" in i]
    assert len(t4_outputs) >= 1, "T4 must output _audit_raw_output.md"
    assert len(t5_inputs) >= 1, "T5 must have _audit_raw_output.md as input"
    assert any("_audit_raw_output.md" in o for o in tasks["T4"].get("outputs") or [])
    assert any("_audit_raw_output.md" in i for i in tasks["T5"].get("inputs") or [])
