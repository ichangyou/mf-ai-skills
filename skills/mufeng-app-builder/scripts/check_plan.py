#!/usr/bin/env python3
"""Check tasks/tasks.json and docs/ACCEPTANCE.md of a bootstrapped project.

Deterministic checks only: IDs, references, dependency cycles, P0 coverage.
Whether the documents describe the right product still needs human review.
"""

import argparse
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path
import sys

PRIORITIES = {"P0", "P1", "P2"}
STATUSES = {"PENDING", "RUNNING", "VERIFYING", "RECOVERING", "SUCCESS", "BLOCKED", "SKIPPED"}


def check(plan, acceptance_text=None):
    """Return (errors, warnings, order). order is empty when the graph is invalid."""
    errors, warnings = [], []
    features = plan.get("features")
    tasks = plan.get("tasks")
    if not isinstance(features, list) or not isinstance(tasks, list):
        return ["tasks.json must contain 'features' and 'tasks' lists"], warnings, []

    feature_ids = {}
    for feature in features:
        fid = feature.get("id")
        if not fid:
            errors.append(f"feature without id: {feature}")
            continue
        if fid in feature_ids:
            errors.append(f"duplicate feature id {fid}")
        if feature.get("priority") not in PRIORITIES:
            errors.append(f"{fid}: priority must be one of {sorted(PRIORITIES)}")
        feature_ids[fid] = feature

    graph, by_id = {}, {}
    for task in tasks:
        tid = task.get("id")
        if not tid:
            errors.append(f"task without id: {task.get('title', task)}")
            continue
        if tid in by_id:
            errors.append(f"duplicate task id {tid}")
        by_id.setdefault(tid, task)
        graph.setdefault(tid, set()).update(task.get("dependencies", []))
        if task.get("feature_id") not in feature_ids:
            errors.append(f"{tid}: unknown feature_id {task.get('feature_id')!r}")
        if task.get("priority") not in PRIORITIES:
            errors.append(f"{tid}: priority must be one of {sorted(PRIORITIES)}")
        if task.get("status", "PENDING") not in STATUSES:
            errors.append(f"{tid}: status must be one of {sorted(STATUSES)}")
        for field in ("acceptance", "verification"):
            if not task.get(field):
                errors.append(f"{tid}: missing {field}")

    for tid, deps in graph.items():
        for dep in sorted(deps):
            if dep not in graph:
                errors.append(f"{tid}: depends on missing task {dep}")
            elif by_id[tid].get("priority") == "P0" and by_id[dep].get("priority") != "P0":
                warnings.append(f"{tid}: P0 task depends on {by_id[dep].get('priority')} task {dep}")

    for fid, feature in feature_ids.items():
        if feature.get("priority") != "P0":
            continue
        if not any(t.get("feature_id") == fid for t in by_id.values()):
            errors.append(f"{fid}: P0 feature has no task")
        if acceptance_text is not None and fid not in acceptance_text:
            errors.append(f"{fid}: P0 feature is not referenced in docs/ACCEPTANCE.md")

    order = []
    if not any("missing task" in e for e in errors):
        try:
            order = list(TopologicalSorter(graph).static_order())
        except CycleError as exc:
            errors.append(f"circular task dependency: {' -> '.join(exc.args[1])}")
    return errors, warnings, order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Project root containing tasks/tasks.json")
    args = parser.parse_args()
    tasks_path = args.project / "tasks" / "tasks.json"
    acceptance_path = args.project / "docs" / "ACCEPTANCE.md"
    if not tasks_path.is_file():
        sys.exit(f"Missing {tasks_path}")
    try:
        plan = json.loads(tasks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        sys.exit(f"{tasks_path}: invalid JSON: {error}")
    acceptance = acceptance_path.read_text(encoding="utf-8") if acceptance_path.is_file() else None
    errors, warnings, order = check(plan, acceptance)
    if acceptance is None:
        errors.append("missing docs/ACCEPTANCE.md")
    for line in errors:
        print(f"ERROR   {line}")
    for line in warnings:
        print(f"WARNING {line}")
    if order and not errors:
        print("ORDER   " + " -> ".join(order))
    print(f"{'FAILED' if errors else 'PASSED'}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
