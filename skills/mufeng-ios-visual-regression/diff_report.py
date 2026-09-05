#!/usr/bin/env python3
"""Diff current screenshots against baselines and emit an HTML report.

Generic engine, shared across projects. Project located via --project /
$VR_PROJECT / cwd; reads <project>/VisualRegression/{config.json,baselines,current}.

For each screen x language x style: computes changed-pixel %, boxes the changed
regions with a grid scan (no numpy), renders an overlay. Writes
<project>/VisualRegression/report/index.html + summary.json. Exits non-zero when
any screen regresses beyond diff_threshold_pct, or a baseline is missing/resized.
"""
import argparse
import glob
import html
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

PIX_TOL = 24     # per-channel diff below this is treated as noise
CELL = 48        # grid cell size for region boxing


def find_project(explicit):
    root = explicit or os.environ.get("VR_PROJECT") or os.getcwd()
    root = os.path.abspath(root)
    if not os.path.exists(os.path.join(root, "VisualRegression", "config.json")):
        sys.exit(f"No VisualRegression/config.json under {root}.")
    return root


def load_config(project):
    with open(os.path.join(project, "VisualRegression", "config.json")) as f:
        return json.load(f)


def rel(base, path):
    return os.path.relpath(path, base)


def changed_mask(base_img, cur_img):
    gray = ImageChops.difference(base_img, cur_img).convert("L")
    return gray.point(lambda p: 255 if p > PIX_TOL else 0)


def region_boxes(mask):
    w, h = mask.size
    boxes = []
    for y in range(0, h, CELL):
        for x in range(0, w, CELL):
            cell = mask.crop((x, y, min(x + CELL, w), min(y + CELL, h)))
            bb = cell.getbbox()
            if bb:
                boxes.append((x + bb[0], y + bb[1], x + bb[2], y + bb[3]))
    return boxes


def make_overlay(cur_img, boxes, dst):
    over = cur_img.convert("RGB").copy()
    draw = ImageDraw.Draw(over)
    for (x0, y0, x1, y1) in boxes:
        draw.rectangle([x0, y0, x1, y1], outline=(255, 40, 40), width=3)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    over.save(dst)


def compare_one(base_path, cur_path, overlay_path):
    base_img = Image.open(base_path).convert("RGB")
    cur_img = Image.open(cur_path).convert("RGB")
    if base_img.size != cur_img.size:
        return {"status": "size-mismatch", "pct": 100.0,
                "note": f"{base_img.size} -> {cur_img.size}"}
    mask = changed_mask(base_img, cur_img)
    w, h = mask.size
    changed = mask.histogram()[255]
    pct = 100.0 * changed / (w * h)
    boxes = region_boxes(mask) if changed else []
    if boxes:
        make_overlay(cur_img, boxes, overlay_path)
    return {"status": "compared", "pct": round(pct, 3),
            "overlay": overlay_path if boxes else None}


def collect(project):
    root = os.path.join(project, "VisualRegression")
    base_root = os.path.join(root, "baselines")
    cur_root = os.path.join(root, "current")
    report_dir = os.path.join(root, "report")
    diff_dir = os.path.join(report_dir, "diff")
    os.makedirs(report_dir, exist_ok=True)

    keys = set()
    for r in (base_root, cur_root):
        for p in glob.glob(os.path.join(r, "*", "*", "*.png")):
            keys.add(os.path.relpath(p, r))

    results = []
    for key in sorted(keys):
        base_path = os.path.join(base_root, key)
        cur_path = os.path.join(cur_root, key)
        overlay_path = os.path.join(diff_dir, key)
        item = {"key": key}
        if not os.path.exists(base_path):
            item.update(status="new", pct=None)
        elif not os.path.exists(cur_path):
            item.update(status="missing", pct=None)
        else:
            item.update(compare_one(base_path, cur_path, overlay_path))
        item["base"] = base_path if os.path.exists(base_path) else None
        item["cur"] = cur_path if os.path.exists(cur_path) else None
        results.append(item)
    return results, report_dir


def is_regression(item, threshold):
    if item["status"] in ("missing", "size-mismatch"):
        return True
    if item["status"] == "compared" and item["pct"] > threshold:
        return True
    return False


def render_html(results, report_dir, threshold):
    def cell_img(path):
        if not path:
            return '<div class="none">—</div>'
        return f'<img src="{html.escape(rel(report_dir, path))}">'

    ordered = sorted(results, key=lambda it: (
        0 if is_regression(it, threshold) else 1,
        -(it["pct"] or 0),
    ))
    regressions = [it for it in results if is_regression(it, threshold)]
    rows = []
    for it in ordered:
        st = it["status"]
        regressed = is_regression(it, threshold)
        badge = {
            "compared": f'{it["pct"]:.2f}%',
            "new": "NEW (no baseline)",
            "missing": "MISSING current",
            "size-mismatch": "SIZE CHANGED",
        }[st]
        cls = "bad" if regressed else ("warn" if st == "new" else "ok")
        overlay = it.get("overlay")
        rows.append(f"""
        <tr class="{cls}">
          <td class="key">{html.escape(it['key'])}<span class="badge">{badge}</span></td>
          <td>{cell_img(it['base'])}</td>
          <td>{cell_img(it['cur'])}</td>
          <td>{cell_img(overlay) if overlay else '<div class="none">no change</div>'}</td>
        </tr>""")

    summary = (f'{len(regressions)} regression(s)' if regressions else 'no regressions')
    color = "#c0392b" if regressions else "#2e7d32"
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Visual Regression</title>
<style>
  body {{ font-family: -apple-system, sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 20px; }}
  .status {{ font-weight: 600; color: {color}; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
  th {{ background: #fafafa; text-align: left; }}
  img {{ width: 240px; display: block; border: 1px solid #eee; }}
  .key {{ width: 220px; font: 12px monospace; }}
  .badge {{ display: block; margin-top: 6px; font: 11px sans-serif; color: #666; }}
  tr.bad .badge {{ color: #c0392b; font-weight: 700; }}
  tr.bad .key {{ background: #fdecea; }}
  tr.warn .key {{ background: #fff8e1; }}
  .none {{ color: #aaa; font-size: 12px; }}
</style></head><body>
<h1>Visual Regression</h1>
<p class="status">{summary}</p>
<p>threshold = {threshold}% changed pixels · {len(results)} screen states compared</p>
<table>
  <tr><th>screen / lang / style</th><th>baseline</th><th>current</th><th>diff overlay</th></tr>
  {''.join(rows)}
</table>
</body></html>"""
    with open(os.path.join(report_dir, "index.html"), "w") as f:
        f.write(doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    args = ap.parse_args()

    project = find_project(args.project)
    cfg = load_config(project)
    threshold = float(cfg["diff_threshold_pct"])
    results, report_dir = collect(project)
    if not results:
        sys.exit("No screenshots found. Run capture first.")

    render_html(results, report_dir, threshold)
    summary = {
        "threshold_pct": threshold,
        "items": results,
        "regressions": [it["key"] for it in results if is_regression(it, threshold)],
    }
    with open(os.path.join(report_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    regressions = summary["regressions"]
    print(f"report: {os.path.join(report_dir, 'index.html')}")
    if regressions:
        print(f"REGRESSIONS ({len(regressions)}):")
        for k in regressions:
            print(f"  - {k}")
        sys.exit(1)
    print("no regressions")


if __name__ == "__main__":
    main()
