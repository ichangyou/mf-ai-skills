#!/usr/bin/env python3
"""Install the shared skills into Codex and/or Claude Code discovery paths."""

import argparse
import os
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = {"codex": ".agents", "claude": ".claude"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["codex", "claude", "both"], default="both")
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project", type=Path, help="Target project; requires --scope project")
    parser.add_argument("--skill", action="append", help="Install only this skill (repeatable)")
    parser.add_argument("--mode", choices=["link", "copy"], default="link")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.project and args.scope != "project":
        parser.error("--project requires --scope project")
    base = Path.home() if args.scope == "user" else (args.project or Path.cwd()).expanduser().resolve()
    if args.scope == "project" and not base.is_dir():
        parser.error(f"Target project does not exist: {base}")
    available = {p.parent.name: p.parent for p in sorted((ROOT / "skills").glob("*/SKILL.md"))}
    selected = sorted(set(args.skill or available))
    unknown = set(selected) - available.keys()
    if unknown:
        parser.error("Unknown skills: " + ", ".join(sorted(unknown)))
    platforms = PLATFORMS if args.platform == "both" else [args.platform]
    pending = []
    for platform in platforms:
        for name in selected:
            source = available[name]
            target = base / PLATFORMS[platform] / "skills" / name
            if args.mode == "link" and target.is_symlink() and target.resolve() == source.resolve():
                print(f"Already installed: {target}")
                continue
            if target.exists() or target.is_symlink():
                parser.error(f"Refusing to overwrite existing skill: {target}. Move it aside first.")
            pending.append((source, target))
    for source, target in pending:
        print(f"{'Would install' if args.dry_run else 'Install'} ({args.mode}): {target}")
        if args.dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if args.mode == "link":
            # Relative links keep repo-scoped installs portable when a checkout moves.
            target.symlink_to(os.path.relpath(source, target.parent), target_is_directory=True)
        else:
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".temp"))
    print(f"{'Planned' if args.dry_run else 'Installed'} {len(pending)} entries. Reload skills or restart the client if needed.")


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"Installation failed: {error}. On Windows, try --mode copy.", file=sys.stderr)
        sys.exit(1)
