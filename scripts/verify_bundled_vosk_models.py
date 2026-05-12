#!/usr/bin/env python3
"""
Post-build: Vosk CN model must appear under dist/ (任意布局，含 macOS .app)：
存在目录 .../pdfgui/meeting/vosk_models/<model>/ 且含 am/final.mdl
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


def verify(repo: Path = ROOT) -> None:
    dist = repo / "dist"
    if not dist.is_dir():
        raise FileNotFoundError("No dist/ directory.")

    for d in dist.rglob(VOSK_CN_MODEL_NAME):
        if not d.is_dir():
            continue
        if not (d / "am" / "final.mdl").is_file():
            continue
        pos = d.as_posix().lower()
        if "pdfgui" in pos and "meeting" in pos and "vosk_models" in pos:
            return

    for p in dist.rglob("final.mdl"):
        if not p.is_file():
            continue
        s = p.as_posix().lower()
        if (
            VOSK_CN_MODEL_NAME.lower() in s
            and "vosk_models" in s
            and "pdfgui" in s
            and "meeting" in s
        ):
            return

    # 便于 CI 排查：列出 dist 下含 vosk 的路径
    hints = [p.as_posix() for p in dist.rglob("*vosk*")][:40]
    extra = "\n".join(hints) if hints else "(未找到任何路径名含 vosk)"
    raise FileNotFoundError(
        f"Vosk model check FAILED: expected .../pdfgui/meeting/vosk_models/{VOSK_CN_MODEL_NAME}/am/final.mdl under dist/.\n"
        f"Sample paths containing 'vosk':\n{extra}"
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
