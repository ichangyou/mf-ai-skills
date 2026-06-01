#!/usr/bin/env python3
"""
Export a markdown research report.

Default behavior: generates both HTML and PDF alongside the input .md file.

Usage:
    python3 export.py <input.md>                  # → HTML + PDF (default)
    python3 export.py <input.md> --format html    # → HTML only
    python3 export.py <input.md> --format pdf     # → PDF only
    python3 export.py <input.md> --format docx    # → Word only
    python3 export.py <input.md> --output <dir>   # custom output directory
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

GITHUB_CSS = """
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
               "Microsoft YaHei", "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #24292e;
  max-width: 900px;
  margin: 40px auto;
  padding: 0 24px;
}
h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #dfe2e5; padding: 8px 12px; }
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(even) { background: #f6f8fa; }
code { background: #f3f4f5; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }
pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
blockquote { border-left: 4px solid #dfe2e5; margin: 0; padding: 0 16px; color: #6a737d; }
hr { border: none; border-top: 2px solid #eaecef; margin: 24px 0; }
"""


def check_pandoc():
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: pandoc is not installed. Run: brew install pandoc", file=sys.stderr)
        sys.exit(1)


def export_html(input_path: Path, output_path: Path):
    css_path = output_path.with_suffix(".css")
    css_path.write_text(GITHUB_CSS)
    cmd = [
        "pandoc", str(input_path), "-o", str(output_path),
        "--standalone",
        "--css", str(css_path),
        "--metadata", "charset=utf-8",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    css_path.unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"HTML export failed:\n{result.stderr}", file=sys.stderr)
        return False
    print(f"  HTML → {output_path}")
    return True


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "google-chrome",
        "chromium",
        "microsoft-edge",
    ]
    for c in candidates:
        try:
            subprocess.run([c, "--version"], capture_output=True, check=True)
            return c
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def export_pdf_via_chrome(html_path: Path, pdf_path: Path, chrome: str) -> bool:
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",
        str(html_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not pdf_path.exists():
        # Try legacy headless flag
        cmd[1] = "--headless"
        result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0 and pdf_path.exists()


def export_pdf_via_pandoc(input_path: Path, pdf_path: Path) -> bool:
    engines = [
        (["wkhtmltopdf", "--version"], ["--pdf-engine=wkhtmltopdf"]),
        (["weasyprint", "--version"], ["--pdf-engine=weasyprint"]),
        (["xelatex", "--version"], [
            "--pdf-engine=xelatex",
            "-V", "mainfont=Arial",
            "-V", "CJKmainfont=PingFang SC",
            "-V", "geometry:margin=2.5cm",
        ]),
    ]
    for check_cmd, extra_args in engines:
        try:
            subprocess.run(check_cmd, capture_output=True, check=True)
            cmd = ["pandoc", str(input_path), "-o", str(pdf_path)] + extra_args
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return False


def export_pdf(input_path: Path, pdf_path: Path, html_path: Optional[Path] = None) -> bool:
    # Prefer Chrome headless (no LaTeX dependency, handles Chinese fonts)
    chrome = find_chrome()
    if chrome:
        # Chrome needs an HTML source; generate a temp one if needed
        tmp_html = None
        if html_path is None or not html_path.exists():
            tmp_html = pdf_path.with_suffix(".tmp.html")
            if not export_html(input_path, tmp_html):
                tmp_html = None
            source_html = tmp_html
        else:
            source_html = html_path

        if source_html and source_html.exists():
            ok = export_pdf_via_chrome(source_html, pdf_path, chrome)
            if tmp_html:
                tmp_html.unlink(missing_ok=True)
            if ok:
                print(f"  PDF  → {pdf_path}")
                return True

    # Fallback: pandoc PDF engines
    if export_pdf_via_pandoc(input_path, pdf_path):
        print(f"  PDF  → {pdf_path}")
        return True

    print("  PDF  → skipped (no PDF engine found; install Chrome or run: brew install wkhtmltopdf)",
          file=sys.stderr)
    return False


def export_docx(input_path: Path, output_path: Path) -> bool:
    cmd = ["pandoc", str(input_path), "-o", str(output_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"DOCX export failed:\n{result.stderr}", file=sys.stderr)
        return False
    print(f"  DOCX → {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Export markdown report to HTML+PDF (default), PDF, HTML, or DOCX")
    parser.add_argument("input", help="Input markdown file path")
    parser.add_argument("--format", choices=["both", "html", "pdf", "docx"], default="both",
                        help="Output format: both=HTML+PDF (default), html, pdf, docx")
    parser.add_argument("--output", help="Output directory (defaults to same directory as input)")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output).expanduser().resolve() if args.output else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem

    check_pandoc()

    print(f"Exporting: {input_path.name}")

    if args.format == "both":
        html_path = out_dir / f"{stem}.html"
        pdf_path = out_dir / f"{stem}.pdf"
        export_html(input_path, html_path)
        export_pdf(input_path, pdf_path, html_path)

    elif args.format == "html":
        export_html(input_path, out_dir / f"{stem}.html")

    elif args.format == "pdf":
        pdf_path = out_dir / f"{stem}.pdf"
        export_pdf(input_path, pdf_path)

    elif args.format == "docx":
        export_docx(input_path, out_dir / f"{stem}.docx")


if __name__ == "__main__":
    main()
