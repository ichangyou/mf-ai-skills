#!/usr/bin/env python3
"""Build a .skill archive from the maintained source, without committing stale bundles."""

import argparse
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", help="Skill directory name")
    args = parser.parse_args()
    source = ROOT / "skills" / args.skill
    if source.parent != ROOT / "skills" or not (source / "SKILL.md").is_file():
        parser.error("Choose an existing skill directory name")
    destination = ROOT / "dist" / f"{args.skill}.skill"
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or any(part in {"__pycache__", ".temp", "tests"} for part in path.parts) or path.name == ".DS_Store" or path.suffix == ".pyc":
                continue
            archive.write(path, Path(args.skill) / path.relative_to(source))
    print(destination)


if __name__ == "__main__":
    main()
