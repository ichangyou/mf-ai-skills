#!/usr/bin/env python3
"""Save one round of mufeng-weread-x-writing candidates as a Markdown file.

Encodes two rules so they cannot be skipped by hand:

1. Target directory. cwd == "/" or cwd == $HOME is treated as the root
   directory and the file goes to ~/Downloads. Any other directory is treated
   as a project directory and the file goes there. No project marker such as
   .git or package.json is required.
2. No overwrite. weread-x-YYYY-MM-DD.md, then -2, -3, ... until a free name.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

FILE_STEM = "weread-x"


def resolve_dir(cwd: str | None) -> tuple[Path, str]:
    """Return (target directory, "root" | "project")."""
    here = Path(cwd).expanduser() if cwd else Path.cwd()
    here = here.resolve()
    home = Path.home().resolve()
    if here == Path("/") or here == home:
        return home / "Downloads", "root"
    return here, "project"


def resolve_path(directory: Path, day: date) -> Path:
    """First free weread-x-<day>[-n].md in directory. Never overwrites."""
    stamp = day.isoformat()
    candidate = directory / f"{FILE_STEM}-{stamp}.md"
    suffix = 2
    while candidate.exists():
        candidate = directory / f"{FILE_STEM}-{stamp}-{suffix}.md"
        suffix += 1
    return candidate


def build(body: str, day: date, count: int | None, status: str) -> str:
    now = datetime.now().astimezone()
    lines = [
        f"# 微信读书推文候选 {day.isoformat()}",
        "",
        f"生成时间：{now.strftime('%Y-%m-%d %H:%M')}（{now.strftime('%z')[:3]}:{now.strftime('%z')[3:]}）",
    ]
    if count is not None:
        lines.append(f"本轮候选：{count} 条 · 状态：{status}")
    lines += ["", "---", "", body.strip(), ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", help="Directory to judge against; defaults to the current one")
    parser.add_argument("--body", help="Markdown body; read from stdin when omitted")
    parser.add_argument("--date", help="YYYY-MM-DD; defaults to today")
    parser.add_argument("--count", type=int, help="Number of candidates this round")
    parser.add_argument("--status", default="generated（未发布）", help="Status line text")
    parser.add_argument("--dry-run", action="store_true", help="Report the path without writing")
    args = parser.parse_args()

    day = date.fromisoformat(args.date) if args.date else date.today()
    directory, kind = resolve_dir(args.cwd)
    path = resolve_path(directory, day)

    if args.dry_run:
        print(json.dumps({"path": str(path), "dir_kind": kind, "written": False}, ensure_ascii=False))
        return

    body = args.body if args.body is not None else sys.stdin.read()
    if not body.strip():
        raise SystemExit("Provide --body or Markdown through stdin.")

    try:
        directory.mkdir(parents=True, exist_ok=True)
        # "x" mode: fail rather than clobber if the name was taken since resolve_path.
        with path.open("x", encoding="utf-8") as handle:
            handle.write(build(body, day, args.count, args.status))
    except OSError as exc:
        raise SystemExit(f"Failed to write {path}: {exc}") from exc

    print(json.dumps(
        {"path": str(path), "dir_kind": kind, "written": True, "bytes": path.stat().st_size},
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
