#!/usr/bin/env python3
"""Validate skill metadata, repository discovery entries and local references."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit("Missing PyYAML. Install development dependencies: python3 -m pip install -r requirements-dev.txt")


ROOT = Path(__file__).resolve().parents[1]


def validate(root):
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        return ["No skills found"]
    names = {p.parent.name for p in skills}
    for path in skills:
        label = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        if not match:
            errors.append(f"{label}: missing YAML frontmatter")
            continue
        try:
            meta = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            errors.append(f"{label}: invalid YAML: {error}")
            continue
        if not isinstance(meta, dict):
            errors.append(f"{label}: frontmatter must be a mapping")
            continue
        allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        unknown = set(meta) - allowed
        if unknown:
            errors.append(f"{label}: non-portable frontmatter fields {sorted(unknown)}; put custom fields under metadata")
        metadata = meta.get("metadata", {})
        if not isinstance(metadata, dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in metadata.items()):
            errors.append(f"{label}: metadata must map string keys to string values")
        name = meta.get("name")
        if name != path.parent.name or not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{label}: name must match its directory and use lowercase kebab-case (<=64 characters)")
        description = meta.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{label}: description must be a non-empty string (<=1024 characters)")
        compatibility = meta.get("compatibility", "")
        if not isinstance(compatibility, str) or len(compatibility) > 500:
            errors.append(f"{label}: compatibility must be a string (<=500 characters)")
        if "README.md" not in {p.name for p in path.parent.iterdir()}:
            errors.append(f"{label}: missing user-facing README.md")
        ui = path.parent / "agents" / "openai.yaml"
        if ui.is_file():
            try:
                data = yaml.safe_load(ui.read_text(encoding="utf-8"))
                interface = data.get("interface", {})
                prompt = interface.get("default_prompt", "")
                if f"${name}" not in prompt:
                    errors.append(f"{ui.relative_to(root)}: default_prompt must mention ${name}")
                for key in ("icon_small", "icon_large"):
                    if key in interface and not (path.parent / interface[key]).is_file():
                        errors.append(f"{ui.relative_to(root)}: missing {key} asset")
            except (yaml.YAMLError, AttributeError, TypeError) as error:
                errors.append(f"{ui.relative_to(root)}: invalid UI metadata: {error}")
    for platform in (".agents", ".claude"):
        directory = root / platform / "skills"
        actual = {p.name for p in directory.iterdir()} if directory.is_dir() else set()
        if actual != names:
            errors.append(f"{platform}/skills: missing={sorted(names - actual)}, extra={sorted(actual - names)}")
        for name in names & actual:
            entry = directory / name
            if not entry.is_symlink() or entry.resolve() != (root / "skills" / name).resolve():
                errors.append(f"{platform}/skills/{name}: must link to the canonical skills/{name}")
    if (root / ".codex" / "skills").exists():
        errors.append("Legacy .codex/skills exists; use the maintained .agents/skills entrypoint")
    documents = [root / "README.md", root / "CONTRIBUTING.md"]
    for directory in ("docs", "skills", "examples"):
        documents.extend((root / directory).rglob("*.md"))
    for path in documents:
        if not path.is_file():
            errors.append(f"Missing document: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"/(?:Users|home)/[A-Za-z0-9_.-]+/", text):
            errors.append(f"{path.relative_to(root)}: contains a personal absolute path")
        # Only actual Markdown links, excluding illustrative fenced code blocks.
        prose = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", text, flags=re.M | re.S)
        for target in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", prose):
            target = target.strip()
            if target.startswith("<"):
                target = target.split(">", 1)[0][1:]
            else:
                target = target.split(' "', 1)[0]
            if not target or target.startswith("#") or urlsplit(target).scheme:
                continue
            local = unquote(target.split("#", 1)[0])
            if not (path.parent / local).exists():
                errors.append(f"{path.relative_to(root)}: broken local link {target}")
    readme = (root / "README.md").read_text(encoding="utf-8")
    declared = re.search(r"共\s*(\d+)\s*个", readme)
    if declared and int(declared.group(1)) != len(names):
        errors.append(f"README.md: declared count {declared.group(1)} differs from {len(names)} skills")
    for name in names:
        if f"skills/{name}/README.md" not in readme:
            errors.append(f"README.md: missing catalog link for {name}")
    for path in (root / "skills").rglob("*"):
        if path.is_file() and path.suffix in {".py", ".sh"} and "tests" not in path.parts:
            if re.search(r"/(?:Users|home)/[A-Za-z0-9_.-]+/", path.read_text(encoding="utf-8")):
                errors.append(f"{path.relative_to(root)}: contains a personal absolute path")
        if path.is_file() and (".temp" in path.parts or path.suffix == ".skill"):
            errors.append(f"{path.relative_to(root)}: runtime state/packages belong outside skill source")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository to validate")
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        sys.exit(1)
    count = len(list((root / "skills").glob("*/SKILL.md")))
    print(f"Validated {count} skills: YAML, both discovery entrypoints, UI metadata, catalog and local links.")
    print("This is static validation; it does not verify host invocation, external credentials or generated artwork quality.")


if __name__ == "__main__":
    main()
