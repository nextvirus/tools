#!/usr/bin/env python3
"""将 rembg 用到的 ONNX 权重下载到 pdfgui/photo/rembg_models/，便于离线使用与打包。"""

from __future__ import annotations

import hashlib
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "pdfgui" / "photo" / "rembg_models"


def _reconfigure_stdio() -> None:
    """避免 Windows 控制台默认 cp1252 导致中文 print 触发 UnicodeEncodeError（含 GitHub Actions）。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass

# 与 rembg 内置 pooch URL / 校验一致（见 rembg.sessions.u2net_human_seg / u2net）
MODELS: list[tuple[str, str, str]] = [
    (
        "u2net_human_seg.onnx",
        "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx",
        "c09ddc2e0104f800e3e1bb4652583d1f",
    ),
    (
        "u2net.onnx",
        "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx",
        "60024c5c889badc19c04ad937298a77b",
    ),
]


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp, tmp.open("wb") as out:
            shutil.copyfileobj(resp, out, length=1 << 20)
        tmp.replace(dest)
    except BaseException:
        if tmp.is_file():
            tmp.unlink(missing_ok=True)
        raise


def main() -> int:
    _reconfigure_stdio()
    DEST.mkdir(parents=True, exist_ok=True)
    for name, url, expect_md5 in MODELS:
        target = DEST / name
        if target.is_file() and _md5(target) == expect_md5:
            print(f"OK (已有) {target}")
            continue
        print(f"下载 {name} …")
        _download(url, target)
        got = _md5(target)
        if got != expect_md5:
            target.unlink(missing_ok=True)
            print(f"MD5 不匹配: 期望 {expect_md5} 得到 {got}", file=sys.stderr)
            return 1
        print(f"已保存 {target}")
    print(f"完成。换底程序会将 U2NET_HOME 指向: {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
