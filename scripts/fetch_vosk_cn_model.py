#!/usr/bin/env python3
"""下载并解压 Vosk 中文 small 模型到 pdfgui/meeting/vosk_models/（不入 Git，打包前 CI 拉取）。"""

from __future__ import annotations

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# 与 pdfgui/meeting/vosk_config.py 中 VOSK_CN_MODEL_NAME 保持一致
VOSK_CN_MODEL_NAME = "vosk-model-small-cn-0.22"
VOSK_MODEL_DOWNLOAD_URL = f"https://alphacephei.com/vosk/models/{VOSK_CN_MODEL_NAME}.zip"

ROOT = Path(__file__).resolve().parent.parent
DEST_PARENT = ROOT / "pdfgui" / "meeting" / "vosk_models"
MODEL_DIR = DEST_PARENT / VOSK_CN_MODEL_NAME
MARKER = MODEL_DIR / "am" / "final.mdl"


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _download(url: str, dest_zip: Path) -> None:
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest_zip.with_suffix(dest_zip.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=300) as resp, tmp.open("wb") as out:
            shutil.copyfileobj(resp, out, length=1 << 20)
        tmp.replace(dest_zip)
    except BaseException:
        if tmp.is_file():
            tmp.unlink(missing_ok=True)
        raise


def main() -> int:
    _reconfigure_stdio()
    if MARKER.is_file():
        print(f"OK (已有) {MODEL_DIR}")
        return 0

    DEST_PARENT.mkdir(parents=True, exist_ok=True)
    zip_path = DEST_PARENT / f"{VOSK_CN_MODEL_NAME}.zip"
    print(f"下载 {VOSK_MODEL_DOWNLOAD_URL} …")
    _download(VOSK_MODEL_DOWNLOAD_URL, zip_path)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)
        extracted = tmp / VOSK_CN_MODEL_NAME
        if not extracted.is_dir():
            subs = [p for p in tmp.iterdir() if p.is_dir()]
            if len(subs) == 1:
                extracted = subs[0]
        if not (extracted / "am" / "final.mdl").is_file():
            print("解压后未找到 am/final.mdl，压缩包结构异常。", file=sys.stderr)
            return 1
        if MODEL_DIR.exists():
            shutil.rmtree(MODEL_DIR)
        shutil.move(str(extracted), str(MODEL_DIR))

    zip_path.unlink(missing_ok=True)
    if not MARKER.is_file():
        print("模型安装失败。", file=sys.stderr)
        return 1
    print(f"已解压到 {MODEL_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
