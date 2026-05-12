#!/usr/bin/env python3
"""
打包后校验：dist 内必须能找到 rembg 用的两个 ONNX（与运行时 U2NET_HOME 一致的路径）。

失败则 exit 1，避免「安装包里没有模型」仍被发布。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("u2net_human_seg.onnx", "u2net.onnx")


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
        raise FileNotFoundError(f"未找到打包目录：{repo / 'dist' / 'tools'} 或 tools.app，请先执行 PyInstaller。")

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
            "打包校验失败：以下模型未出现在 dist 内的 pdfgui/rembg_models 路径下：\n  "
            + "\n  ".join(missing)
            + f"\n已检查目录: {[str(r) for r in roots]}\n"
            "请确认 package_tools 中 --add-data 仍指向 pdfgui/rembg_models 下的 onnx，且 fetch_rembg_models 已成功。"
        )
        raise FileNotFoundError(msg)


def main() -> int:
    try:
        verify_bundled_rembg_models()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("OK: dist 内已包含 rembg 模型文件 (pdfgui/rembg_models/*.onnx)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
