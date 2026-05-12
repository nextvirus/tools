#!/usr/bin/env python3
"""
Post-build check: rembg ONNX files must appear under dist as pdfgui/rembg_models/*.onnx
(same layout as runtime U2NET_HOME). Exits 1 if missing.

Console output is ASCII-only so Windows/GitHub Actions (cp1252) never raises UnicodeEncodeError.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("u2net_human_seg.onnx", "u2net.onnx")


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _dist_candidates(repo: Path) -> list[Path]:
    out: list[Path] = []
    d = repo / "dist" / "tools"
    if d.is_dir():
        out.append(d)
    app = repo / "dist" / "tools.app"
    if app.is_dir():
        out.append(app)
    return out


def verify_bundled_rembg_models(repo: Path = ROOT) -> None:
    roots = _dist_candidates(repo)
    if not roots:
        raise FileNotFoundError(
            f"No dist output found (expected {repo / 'dist' / 'tools'} or dist/tools.app). Run PyInstaller first."
        )

    missing: list[str] = []
    for name in REQUIRED:
        found = False
        for tree in roots:
            for p in tree.rglob(name):
                if not p.is_file():
                    continue
                parts = {x.lower() for x in p.parts}
                if "rembg_models" in parts and "pdfgui" in parts:
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(name)

    if missing:
        msg = (
            "Bundled rembg model check FAILED. Missing under dist with path pdfgui/rembg_models/: "
            + ", ".join(missing)
            + f"\nSearched roots: {[str(r) for r in roots]}\n"
            "Ensure package_tools.py --add-data still ships pdfgui/rembg_models/*.onnx and fetch_rembg_models.py ran."
        )
        raise FileNotFoundError(msg)


def main() -> int:
    _reconfigure_stdio()
    try:
        verify_bundled_rembg_models()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("OK: rembg ONNX models found in dist (pdfgui/rembg_models/*.onnx)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
