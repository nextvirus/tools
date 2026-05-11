#!/usr/bin/env python3
"""
本地 / CI 统一打包入口：先把 rembg 模型拉到 pdfgui/rembg_models/，再 PyInstaller 打进 dist。

模型不入 GitHub；编译时写入本机目录并随 --add-data 打进安装包。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main() -> int:
    _reconfigure_stdio()
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    subprocess.check_call(
        [sys.executable, str(ROOT / "scripts" / "fetch_rembg_models.py")],
        cwd=ROOT,
        env=env,
    )

    hseg = ROOT / "pdfgui" / "rembg_models" / "u2net_human_seg.onnx"
    u2 = ROOT / "pdfgui" / "rembg_models" / "u2net.onnx"
    if not hseg.is_file() or not u2.is_file():
        print("缺少 onnx，无法打包。", file=sys.stderr)
        return 1

    sep = ";" if sys.platform == "win32" else ":"
    add_human = f"pdfgui/rembg_models/u2net_human_seg.onnx{sep}pdfgui/rembg_models"
    add_u2 = f"pdfgui/rembg_models/u2net.onnx{sep}pdfgui/rembg_models"

    head: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
    ]
    if sys.platform == "darwin":
        head += ["--osx-bundle-identifier", "com.tools.app"]

    tail: list[str] = [
        "--name",
        "tools",
        "--hidden-import=pdfgui.tabs.watermark",
        "--hidden-import=pdfgui.tabs.image_export",
        "--hidden-import=pdfgui.watermark_pdf",
        "--hidden-import=pdfgui.pdf_to_img",
        "--hidden-import=pdfgui.tabs.photo_background",
        "--hidden-import=pdfgui.photo_bg",
        "--collect-all",
        "pymupdf",
        "--collect-all",
        "rembg",
        "--collect-all",
        "onnxruntime",
        "--add-data",
        add_human,
        "--add-data",
        add_u2,
        str(ROOT / "pdf_gui.py"),
    ]
    cmd = head + tail

    print("运行:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT, env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
