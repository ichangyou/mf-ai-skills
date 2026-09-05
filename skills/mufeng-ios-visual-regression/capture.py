#!/usr/bin/env python3
"""Capture visual-regression screenshots for an iOS project.

Generic engine, shared across projects. It drives a per-project DEBUG harness
(VisualRegressionHarness.swift) that renders one screen in isolation: for every
screen x language x style it launches the app with `-VRScreen/-VRLang/-VRStyle`,
waits for the layout to settle, and grabs a screenshot via `simctl`.

The project is located via --project / $VR_PROJECT / cwd. Its config lives at
<project>/VisualRegression/config.json and its output under <project>/VisualRegression/.

Usage:
    capture.py --project <dir> --mode baseline
    capture.py --project <dir> --mode current [--build]
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time


def find_project(explicit):
    root = explicit or os.environ.get("VR_PROJECT") or os.getcwd()
    root = os.path.abspath(root)
    if not os.path.exists(os.path.join(root, "VisualRegression", "config.json")):
        sys.exit(
            f"No VisualRegression/config.json under {root}.\n"
            f"Run `run.sh init` in the project root first, or pass --project."
        )
    return root


def load_config(project):
    with open(os.path.join(project, "VisualRegression", "config.json")) as f:
        return json.load(f)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def container_args(project, cfg):
    """xcodebuild container: -workspace if configured, else -project."""
    if cfg.get("workspace"):
        return ["-workspace", os.path.join(project, cfg["workspace"])]
    if cfg.get("xcodeproj"):
        return ["-project", os.path.join(project, cfg["xcodeproj"])]
    sys.exit("config needs either 'workspace' or 'xcodeproj'")


def resolve_languages(project, cfg):
    langs = cfg.get("languages")
    if langs != "auto":
        return langs
    source_dir = cfg.get("source_dir", "")
    base = os.path.join(project, source_dir) if source_dir else project
    found = []
    for path in glob.glob(os.path.join(base, "*.lproj")):
        code = os.path.basename(path)[: -len(".lproj")]
        if code != "Base":
            found.append(code)
    found.sort(key=lambda c: (c != "en", c))
    if not found:
        sys.exit(f"languages=auto but no *.lproj found under {base}. "
                 f"Set source_dir in config, or list languages explicitly.")
    return found


def resolve_device(cfg):
    booted = run(["xcrun", "simctl", "list", "devices", "booted", "-j"])
    data = json.loads(booted.stdout or "{}")
    for devs in data.get("devices", {}).values():
        for d in devs:
            if d.get("state") == "Booted":
                print(f"[device] using already-booted {d['name']} ({d['udid']})")
                return d["udid"]

    avail = json.loads(run(["xcrun", "simctl", "list", "devices", "available", "-j"]).stdout)
    want = cfg["simulator_name"]
    candidate = None
    for devs in avail.get("devices", {}).values():
        for d in devs:
            if d.get("isAvailable") and d["name"] == want:
                candidate = d
                break
    if candidate is None:
        for devs in avail.get("devices", {}).values():
            for d in devs:
                if d.get("isAvailable") and d["name"].startswith("iPhone"):
                    candidate = d
                    break
            if candidate:
                break
    if candidate is None:
        sys.exit("No available iPhone simulator found. Create one in Xcode > Devices.")
    udid = candidate["udid"]
    print(f"[device] booting {candidate['name']} ({udid})")
    run(["xcrun", "simctl", "boot", udid])
    run(["xcrun", "simctl", "bootstatus", udid, "-b"])
    return udid


def locate_app(project, cfg, udid):
    out = run([
        "xcodebuild", *container_args(project, cfg),
        "-scheme", cfg["scheme"], "-configuration", cfg["configuration"],
        "-destination", f"id={udid}", "-showBuildSettings",
    ]).stdout
    products_dir = product_name = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("BUILT_PRODUCTS_DIR ="):
            products_dir = line.split("=", 1)[1].strip()
        elif line.startswith("FULL_PRODUCT_NAME ="):
            product_name = line.split("=", 1)[1].strip()
    if products_dir and product_name:
        return os.path.join(products_dir, product_name)
    return None


def build_app(project, cfg, udid):
    print("[build] xcodebuild (Debug, simulator)...")
    r = run([
        "xcodebuild", *container_args(project, cfg),
        "-scheme", cfg["scheme"], "-configuration", cfg["configuration"],
        "-destination", f"id={udid}", "CODE_SIGNING_ALLOWED=NO", "build",
    ])
    ok = "** BUILD SUCCEEDED **" in r.stdout
    if not ok:
        print("\n".join((r.stdout + r.stderr).splitlines()[-25:]))
    return ok


def ensure_app(project, cfg, udid, force_build):
    app = locate_app(project, cfg, udid)
    if force_build or not app or not os.path.isdir(app):
        if not build_app(project, cfg, udid):
            app = locate_app(project, cfg, udid)
            if not app or not os.path.isdir(app):
                sys.exit(
                    "\nCLI build failed and no built .app was found.\n"
                    "This is usually the 'Embed Pods Frameworks / rsync Operation "
                    "not permitted' sandbox error.\n"
                    "Fix: open the workspace in Xcode, pick the pinned simulator, "
                    "press Cmd-B once, then re-run (it reuses the Xcode-built app)."
                )
    app = locate_app(project, cfg, udid)
    print(f"[app] {app}")
    return app


def freeze_status_bar(udid):
    run(["xcrun", "simctl", "status_bar", udid, "override",
         "--time", "9:41", "--batteryLevel", "100",
         "--batteryState", "charged", "--cellularBars", "4",
         "--dataNetwork", "wifi", "--wifiBars", "3"])


def capture_all(project, cfg, udid, app, mode):
    bid = cfg["bundle_id"]
    root = os.path.join(project, "VisualRegression",
                        "baselines" if mode == "baseline" else "current")
    langs = resolve_languages(project, cfg)
    styles = cfg.get("styles", ["light"])
    settle = float(cfg["settle_seconds"])

    run(["xcrun", "simctl", "install", udid, app])
    freeze_status_bar(udid)
    print(f"[capture] mode={mode} langs={langs} styles={styles} "
          f"screens={len(cfg['screens'])}")

    total = 0
    for lang in langs:
        for style in styles:
            out_dir = os.path.join(root, lang, style)
            os.makedirs(out_dir, exist_ok=True)
            for scr in cfg["screens"]:
                sid = scr["id"]
                run(["xcrun", "simctl", "terminate", udid, bid])
                launch = ["xcrun", "simctl", "launch", udid, bid,
                          "-VRScreen", sid, "-VRLang", lang, "-VRStyle", style]
                r = run(launch)
                if r.returncode != 0:
                    print(f"  ! launch failed {lang}/{style}/{sid}: {r.stderr.strip()}")
                    continue
                time.sleep(settle)
                dst = os.path.join(out_dir, f"{sid}.png")
                run(["xcrun", "simctl", "io", udid, "screenshot", dst])
                total += 1
                print(f"  captured {lang}/{style}/{sid}")
    run(["xcrun", "simctl", "terminate", udid, bid])
    print(f"[capture] wrote {total} screenshots under {root}")
    return root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    ap.add_argument("--mode", choices=["baseline", "current"], required=True)
    ap.add_argument("--build", action="store_true", help="force xcodebuild first")
    args = ap.parse_args()

    project = find_project(args.project)
    cfg = load_config(project)
    udid = resolve_device(cfg)
    app = ensure_app(project, cfg, udid, args.build)
    capture_all(project, cfg, udid, app, args.mode)


if __name__ == "__main__":
    main()
