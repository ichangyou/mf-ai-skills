#!/usr/bin/env python3
"""Upload PNG images to a GitHub repository and print raw URLs."""

from __future__ import annotations

import argparse
import base64
import json
import os
import posixpath
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def run_gh(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["gh", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"gh {' '.join(args)} failed: {details}")
    return result


def is_png(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(8) == PNG_SIGNATURE


def safe_filename(path: Path) -> str:
    name = path.name
    stem = path.stem
    suffix = path.suffix.lower() or ".png"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._")
    if not stem:
        stem = "image"
    if suffix != ".png":
        suffix = ".png"
    return f"{stem}{suffix}"


def normalize_remote_dir(raw: str) -> str:
    cleaned = raw.strip().strip("/")
    if not cleaned:
        return "images"
    return posixpath.normpath(cleaned).lstrip("/")


def content_endpoint(repo: str, remote_path: str, branch: str | None = None) -> str:
    endpoint = f"repos/{repo}/contents/{quote(remote_path, safe='/')}"
    if branch:
        endpoint += f"?ref={quote(branch, safe='')}"
    return endpoint


def get_existing_sha(repo: str, remote_path: str, branch: str) -> str | None:
    result = run_gh(["api", content_endpoint(repo, remote_path, branch)], check=False)
    if result.returncode != 0:
        return None
    try:
        payload: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    sha = payload.get("sha")
    return sha if isinstance(sha, str) and sha else None


def choose_remote_path(repo: str, branch: str, desired: str, overwrite: bool) -> tuple[str, str | None]:
    existing_sha = get_existing_sha(repo, desired, branch)
    if existing_sha is None:
        return desired, None
    if overwrite:
        return desired, existing_sha

    directory = posixpath.dirname(desired)
    filename = posixpath.basename(desired)
    stem, ext = posixpath.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for index in range(1, 100):
        suffix = timestamp if index == 1 else f"{timestamp}-{index}"
        candidate = posixpath.join(directory, f"{stem}-{suffix}{ext}")
        if get_existing_sha(repo, candidate, branch) is None:
            return candidate, None
    raise RuntimeError(f"Could not find a unique remote path for {desired}")


def upload_one(
    *,
    repo: str,
    branch: str,
    remote_dir: str,
    image_path: Path,
    message: str,
    overwrite: bool,
) -> dict[str, str]:
    remote_name = safe_filename(image_path)
    desired_remote_path = posixpath.join(remote_dir, remote_name)
    remote_path, sha = choose_remote_path(repo, branch, desired_remote_path, overwrite)
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")

    args = [
        "api",
        content_endpoint(repo, remote_path),
        "--method",
        "PUT",
        "--field",
        f"message={message}",
        "--field",
        f"content={encoded}",
        "--field",
        f"branch={branch}",
    ]
    if sha:
        args.extend(["--field", f"sha={sha}"])

    run_gh(args)
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{quote(remote_path, safe='/')}"
    return {
        "local_path": str(image_path),
        "remote_path": remote_path,
        "raw_url": raw_url,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="PNG image files to upload")
    parser.add_argument("--repo", default=os.getenv("MUFENG_GITHUB_IMAGE_REPO"), help="GitHub repo as owner/name")
    parser.add_argument("--branch", default=os.getenv("MUFENG_GITHUB_IMAGE_BRANCH", "main"))
    parser.add_argument("--remote-dir", default=os.getenv("MUFENG_GITHUB_IMAGE_DIR", "images/mufeng"))
    parser.add_argument("--message", default="add mufeng article images")
    parser.add_argument("--json-out", help="Optional JSON output path")
    parser.add_argument("--overwrite", action="store_true", help="Update existing files instead of adding timestamp suffixes")
    parser.add_argument("--allow-non-png", action="store_true", help="Skip PNG signature validation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.repo:
        print("error: --repo or MUFENG_GITHUB_IMAGE_REPO is required", file=sys.stderr)
        return 2
    if "/" not in args.repo:
        print("error: repo must be in owner/name form", file=sys.stderr)
        return 2

    remote_dir = normalize_remote_dir(args.remote_dir)
    image_paths = [Path(item).expanduser().resolve() for item in args.images]

    for image_path in image_paths:
        if not image_path.exists():
            print(f"error: image not found: {image_path}", file=sys.stderr)
            return 2
        if image_path.stat().st_size == 0:
            print(f"error: image is empty: {image_path}", file=sys.stderr)
            return 2
        if not args.allow_non_png and not is_png(image_path):
            print(f"error: not a PNG file: {image_path}", file=sys.stderr)
            return 2

    uploaded = [
        upload_one(
            repo=args.repo,
            branch=args.branch,
            remote_dir=remote_dir,
            image_path=image_path,
            message=args.message,
            overwrite=args.overwrite,
        )
        for image_path in image_paths
    ]

    payload = json.dumps(uploaded, ensure_ascii=False, indent=2)
    print(payload)

    if args.json_out:
        output_path = Path(args.json_out).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
