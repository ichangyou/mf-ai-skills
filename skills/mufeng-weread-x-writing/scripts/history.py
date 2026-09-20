#!/usr/bin/env python3
"""Maintain local JSONL memory for mufeng-weread-x-writing."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_HISTORY = Path.home() / ".codex" / "mufeng-weread-x" / "history.jsonl"
VALID_STATUS = {"generated", "saved", "published"}


def history_path(value: str | None) -> Path:
    if value:
        return Path(value).expanduser()
    root = os.environ.get("MUFENG_WEREAD_X_HOME")
    return Path(root).expanduser() / "history.jsonl" if root else DEFAULT_HISTORY


def ensure_history(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load(path: Path) -> list[dict[str, Any]]:
    ensure_history(path)
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON on {path}:{number}: {exc}") from exc
        if isinstance(value, dict):
            records.append(value)
    return records


def normalize(record: dict[str, Any], index: int) -> dict[str, Any]:
    if not str(record.get("text", "")).strip():
        raise SystemExit("Each record requires non-empty 'text'.")
    now = datetime.now().astimezone()
    item = dict(record)
    item.setdefault("created_at", now.isoformat(timespec="seconds"))
    item.setdefault("id", f"{now.strftime('%Y%m%dT%H%M%S')}-{index:02d}")
    item.setdefault("status", "generated")
    if item["status"] not in VALID_STATUS:
        raise SystemExit(f"Invalid status: {item['status']}")
    for key in ("topics", "source_books", "source_materials", "keywords"):
        item.setdefault(key, [])
        if not isinstance(item[key], list):
            raise SystemExit(f"'{key}' must be an array.")
    item.setdefault("insight", "")
    item.setdefault("structure", "")
    return item


def read_input(raw_json: str | None) -> list[dict[str, Any]]:
    raw = raw_json if raw_json is not None else sys.stdin.read()
    if not raw.strip():
        raise SystemExit("Provide --json or JSON through stdin.")
    value = json.loads(raw)
    values = value if isinstance(value, list) else [value]
    if not all(isinstance(item, dict) for item in values):
        raise SystemExit("Input must be a JSON object or array of objects.")
    return values


def recent(records: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    selected = []
    for record in records:
        try:
            created = parse_time(str(record["created_at"]))
            if created.tzinfo is None:
                created = created.astimezone()
            if created >= cutoff:
                selected.append(record)
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(selected, key=lambda item: item.get("created_at", ""), reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", help="Path to history.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    p_recent = sub.add_parser("recent")
    p_recent.add_argument("--days", type=int, default=30)
    p_stats = sub.add_parser("stats")
    p_stats.add_argument("--days", type=int, default=30)
    p_add = sub.add_parser("add")
    p_add.add_argument("--json")
    args = parser.parse_args()

    path = history_path(args.history)
    records = load(path)

    if args.command == "init":
        print(path)
        return

    if args.command == "recent":
        print(json.dumps(recent(records, args.days), ensure_ascii=False, indent=2))
        return

    if args.command == "stats":
        items = recent(records, args.days)
        topics = Counter(topic for item in items for topic in item.get("topics", []))
        structures = Counter(item.get("structure") for item in items if item.get("structure"))
        print(json.dumps({"days": args.days, "count": len(items), "topics": topics, "structures": structures}, ensure_ascii=False, indent=2))
        return

    incoming = read_input(args.json)
    existing_text = {str(item.get("text", "")).strip() for item in records}
    added = []
    with path.open("a", encoding="utf-8") as handle:
        for index, raw in enumerate(incoming, 1):
            item = normalize(raw, index)
            if item["text"].strip() in existing_text:
                continue
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
            existing_text.add(item["text"].strip())
            added.append(item)
    print(json.dumps({"history": str(path), "added": len(added)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
