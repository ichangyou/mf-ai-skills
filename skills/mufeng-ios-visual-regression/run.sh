#!/usr/bin/env bash
# Visual-regression command surface (shared engine, per-project config).
#
# Run from an iOS project root (or set $VR_PROJECT):
#   run.sh init                 scaffold config + harness template into this project
#   run.sh baseline [--build]   capture and store baselines/
#   run.sh check    [--build]   capture current/, diff vs baselines, open report
#   run.sh open                 open the last HTML report
#
# `check` exits non-zero when any screen regresses beyond the threshold.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${VR_PROJECT:-$PWD}"
PY="python3"
VRDIR="$PROJECT/VisualRegression"
REPORT="$VRDIR/report/index.html"

cmd="${1:-}"; shift || true

case "$cmd" in
  init)
    mkdir -p "$VRDIR"
    if [ -f "$VRDIR/config.json" ]; then
      echo "config exists: $VRDIR/config.json (left untouched)"
    else
      cp "$HERE/templates/config.template.json" "$VRDIR/config.json"
      echo "wrote  $VRDIR/config.json  (edit: scheme, workspace, bundle_id, source_dir, screens)"
    fi
    cp "$HERE/templates/VisualRegressionHarness.swift.template" \
       "$VRDIR/VisualRegressionHarness.swift.template"
    echo "wrote  $VRDIR/VisualRegressionHarness.swift.template  (move into your app + fill registry)"
    if [ -f "$PROJECT/.gitignore" ] && ! grep -q "^VisualRegression/current" "$PROJECT/.gitignore"; then
      {
        echo ""
        echo "# Visual regression: keep baselines, ignore transient captures + reports"
        echo "VisualRegression/current/"
        echo "VisualRegression/report/"
      } >> "$PROJECT/.gitignore"
      echo "appended VisualRegression ignores to .gitignore"
    fi
    cat <<'EOF'

Next (per-project, done once):
  1. Move VisualRegression/VisualRegressionHarness.swift.template into your app
     source (e.g. <App>/DevSupport/VisualRegressionHarness.swift), fill in the
     screen `registry` with your VCs, and add it to the app target.
  2. In SceneDelegate.scene(_:willConnectTo:), right after you create the window,
     add (guarded by #if DEBUG):
        if let w = window, VisualRegressionHarness.activateIfRequested(on: w) {
            w.makeKeyAndVisible(); return
        }
  3. Make config.json screens[] ids match the registry keys.
  4. run.sh baseline   # then commit VisualRegression/baselines/
EOF
    ;;
  baseline)
    "$PY" "$HERE/capture.py" --project "$PROJECT" --mode baseline "$@"
    echo "baselines updated."
    ;;
  check)
    "$PY" "$HERE/capture.py" --project "$PROJECT" --mode current "$@"
    set +e
    "$PY" "$HERE/diff_report.py" --project "$PROJECT"
    code=$?
    set -e
    [ -f "$REPORT" ] && open "$REPORT" || true
    exit $code
    ;;
  open)
    [ -f "$REPORT" ] && open "$REPORT" || { echo "no report yet; run: $0 check"; exit 1; }
    ;;
  *)
    echo "usage: $0 {init|baseline|check|open} [--build]   (run from project root or set \$VR_PROJECT)"
    exit 2
    ;;
esac
