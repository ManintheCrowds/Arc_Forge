# PURPOSE: Load gui_audit_tasks.yaml, build DAG, compute parallel/serial batches, print schedule.
# DEPENDENCIES: pathlib, yaml (PyYAML).
# MODIFICATION NOTES: No AI invocation; no file writes. Pure spec validation and schedule output.

from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required: pip install pyyaml")


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_spec(spec_path: Path) -> dict:
    with open(spec_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_batches(tasks: dict) -> list[list[str]]:
    """Build DAG from tasks and depends_on; return level-by-level batches (roots = batch 1)."""
    task_ids = list(tasks.keys())
    dep_map = {tid: list(tasks[tid].get("depends_on") or []) for tid in task_ids}
    in_degree = {tid: len([d for d in dep_map[tid] if d in task_ids]) for tid in task_ids}
    batches = []
    done = set()
    while len(done) < len(task_ids):
        ready = [tid for tid in task_ids if tid not in done and in_degree[tid] == 0]
        if not ready:
            break
        batches.append(sorted(ready))
        for tid in ready:
            done.add(tid)
            for t in task_ids:
                if t not in done and tid in dep_map[t]:
                    in_degree[t] -= 1
    return batches


def main() -> None:
    script_dir = _script_dir()
    spec_path = script_dir / "gui_audit_tasks.yaml"
    if not spec_path.exists():
        raise SystemExit(f"Spec not found: {spec_path}")
    spec = load_spec(spec_path)
    workflow = spec.get("workflow")
    tasks = spec.get("tasks") or {}
    if workflow != "gui_audit":
        raise SystemExit(f"Unexpected workflow: {workflow}")
    batches = compute_batches(tasks)
    for i, batch in enumerate(batches, start=1):
        print(f"Batch {i}: {', '.join(batch)}")
    print()
    print("Parallel: batch 1 (T1, T2); Serial: then T3, T4, T5, T6.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
