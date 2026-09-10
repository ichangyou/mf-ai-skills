---
name: mufeng-ios-visual-regression
description: Visual regression testing for iOS apps (UIKit or SwiftUI). Use after ANY UI change (layout, colors, spacing, fonts, dark-mode, localization strings) to screenshot each top-level screen in every supported language and appearance via the simulator, diff against committed baselines, and produce an HTML report boxing the changed regions. Shared engine; each project supplies its own config + in-app DEBUG harness. Also use to scaffold a new project (`init`) or regenerate baselines. Triggers include "视觉回归", "visual regression", "截图对比", "UI 改动后检查", "screenshot diff", "did my UI change break anything".
---

# Visual Regression (shared engine)

Screenshot diffing for an iOS app's top-level screens across languages and
light/dark. This skill is the **shared engine**; each project supplies its own
`VisualRegression/config.json` and a DEBUG-only in-app harness that renders one
screen in isolation with seeded fixtures — no manual navigation, no network.

Located project = `$VR_PROJECT` or the current working directory (must contain
`VisualRegression/config.json`).

## Command (run from the project root)

```bash
~/.claude/skills/mufeng-ios-visual-regression/run.sh check       # after a UI change
~/.claude/skills/mufeng-ios-visual-regression/run.sh baseline    # accept current UI as truth
~/.claude/skills/mufeng-ios-visual-regression/run.sh open        # reopen last report
~/.claude/skills/mufeng-ios-visual-regression/run.sh init        # scaffold a NEW project
```

Add `--build` to `check`/`baseline` to force a clean `xcodebuild` first. `check`
exits non-zero when any screen regresses past `diff_threshold_pct`.

Per project, everything lives under `<project>/VisualRegression/`:
- `config.json` — scheme, workspace, bundle_id, source_dir, screens, styles
- `baselines/<lang>/<style>/<screen>.png` — committed source of truth
- `current/`, `report/` — transient (gitignore them)

## Mandatory workflow after a UI change

After you modify any UI code, BEFORE reporting "done":

1. Run `run.sh check` from the project root.
2. Open `VisualRegression/report/index.html`; read `summary.json`. Every `bad`
   row is a changed region.
3. For each regression decide **intended** vs **self-introduced bug**. Fix
   unintended ones and re-run `check` until only intended changes remain.
4. Only then report, and show the user the report. Do NOT run `baseline` to
   bless changes without the user's sign-off.

## Onboarding a NEW project

1. `cd <project> && ~/.claude/skills/mufeng-ios-visual-regression/run.sh init`.
2. Edit `VisualRegression/config.json`: `scheme`, the build container
   (`workspace` for a CocoaPods/`.xcworkspace` project, or `xcodeproj` for a
   plain `.xcodeproj`), `bundle_id`, `source_dir` (the folder holding your
   `*.lproj`), `simulator_name`, and `screens[]`.
3. Move `VisualRegression/VisualRegressionHarness.swift.template` into the app
   source (e.g. `<App>/DevSupport/VisualRegressionHarness.swift`), fill the
   `registry` with your view controllers + light fixtures, add it to the app
   target. **This step is inherently per-app and hand-written** — the harness
   knows your VCs, initializers, localization and display-style mechanisms.
4. Wire `SceneDelegate` (or your window setup) with the `#if DEBUG` early return
   shown in the template.
5. `run.sh baseline`, then commit `VisualRegression/baselines/`.

## Determinism notes

- Status bar is frozen (`simctl status_bar override`, 9:41).
- The device is restarted once per run and the app's TCC state reset, so no
  leftover system permission alert or stale Allow/Deny bleeds into the shots.
  A stuck alert is drawn by SpringBoard, so relaunching the app does not clear
  it — it dims every screenshot that follows. Opt out per project with
  `"reboot_simulator": false` / `"reset_privacy": false`.
- A harness that renders a screen touching Photos/Contacts/etc. should avoid the
  real framework under VR (fixtures + an `isActive` flag), or it will raise the
  very prompt that pollutes the run.
- Animations disabled; use fixed dates/fixtures for any date-bearing screen.
  Prefer **midday UTC** — a near-midnight fixture renders a different calendar
  day depending on the capturing machine's time zone.
- Use the SAME simulator device+OS for baseline and check (pin via
  `simulator_name`). Pixel diffs are resolution-sensitive.
- Threshold default 0.5% (the home-indicator anti-aliasing is a ~0.2% noise
  floor). Raise per project if a screen has unavoidable dynamic content.
- **Dead-frame sentinel.** Capture races the app: shooting before it is
  foregrounded yields the springboard wallpaper, shooting before it renders
  yields a flat colour. Both used to be written into `baselines/` silently and
  then served as the "correct answer" on every later check. Each shot is now
  validated (unique-colour count + mean saturation over the content area);
  a bad frame is retried up to twice with a longer settle, and if it still
  fails the whole run exits non-zero rather than storing garbage. Opt out with
  `"dead_frame_check": false`. Needs Pillow; the check silently no-ops without it.
  Seeing this fire means `settle_seconds` is too low for the machine — raise it.

## Known failure

CLI `xcodebuild` can hit `Embed Pods Frameworks / rsync … Operation not
permitted` (sandbox). If capture reports a build failure, open the workspace in
Xcode, build once (Cmd-B) for the pinned simulator, then re-run — it reuses the
Xcode-built app.
