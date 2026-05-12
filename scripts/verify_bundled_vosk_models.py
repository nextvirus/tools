#!/usr/bin/env python3
"""
Post-build: Vosk CN model must appear under dist as
pdfgui/meeting/vosk_models/<model>/am/final.mdl
"""

from __future__ import annotations

import sys
from pathlib import Path

# 与 pdfgui/meeting/vosk_config.py 中 VOSK_CN_MODEL_NAME 保持一致
VOSK_CN_MODEL_NAME = "vosk-model-small-cn-0.22"

ROOT = Path(__file__).resolve().parent.parent


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _dist_roots(repo: Path) -> list[Path]:
    out: list[Path] = []
    d = repo / "dist" / "tools"
    if d.is_dir():
        out.append(d)
    app = repo / "dist" / "tools.app"
    if app.is_dir():
        out.append(app)
    return out


def verify(repo: Path = ROOT) -> None:
    roots = _dist_roots(repo)
    if not roots:
        raise FileNotFoundError("No dist/tools or dist/tools.app found.")

    needle = VOSK_CN_MODEL_NAME.lower()
    for tree in roots:
        for p in tree.rglob("final.mdl"):
            if not p.is_file():
                continue
            parts = {x.lower() for x in p.parts}
            if needle in parts and "vosk_models" in parts and "meeting" in parts:
                return
    raise FileNotFoundError(
        f"Vosk model check FAILED: expected .../pdfgui/meeting/vosk_models/{VOSK_CN_MODEL_NAME}/am/final.mdl in dist."
    )


def main() -> int:
    _reconfigure_stdio()
    try:
        verify()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(f"OK: Vosk model {VOSK_CN_MODEL_NAME} found in dist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
