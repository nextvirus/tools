"""照片换底：rembg 人像分割 + 红 / 蓝 / 白纯色底合成。"""

from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps


def _rembg_models_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "pdfgui" / "rembg_models"
    return Path(__file__).resolve().parent / "rembg_models"


def _apply_u2net_home() -> None:
    root = _rembg_models_dir()
    root.mkdir(parents=True, exist_ok=True)
    if getattr(sys, "frozen", False):
        os.environ["U2NET_HOME"] = str(root)
    else:
        os.environ.setdefault("U2NET_HOME", str(root))


_apply_u2net_home()

BgKey = Literal["red", "blue", "white"]

BG_RGB: dict[BgKey, tuple[int, int, int]] = {
    "red": (230, 55, 55),
    "blue": (67, 142, 219),
    "white": (255, 255, 255),
}

_session = None


def _get_session():
    """u2net_human_seg 偏人像；权重放在 pdfgui/rembg_models（见 scripts/fetch_rembg_models.py）。"""
    global _session
    if _session is not None:
        return _session
    from rembg import new_session

    try:
        _session = new_session("u2net_human_seg")
    except Exception:
        _session = new_session("u2net")
    return _session


def default_output_path(input_path: str | Path, bg: BgKey) -> str:
    p = Path(input_path)
    suf = {"red": "_红底", "blue": "_蓝底", "white": "_白底"}[bg]
    return str(p.parent / f"{p.stem}{suf}.png")


def replace_photo_background(
    input_path: str | Path,
    output_path: str | Path,
    bg: BgKey,
) -> None:
    try:
        from rembg import remove
    except ImportError as e:
        raise ImportError('请安装：pip install "rembg[cpu]"') from e

    inp = Path(input_path)
    if not inp.is_file():
        raise FileNotFoundError(f"找不到图片: {inp}")
    if bg not in BG_RGB:
        raise ValueError(f"不支持的底色: {bg!r}")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    src = Image.open(inp)
    try:
        src = ImageOps.exif_transpose(src)
    except Exception:
        pass
    src = src.convert("RGBA")
    session = _get_session()
    buf = BytesIO()
    src.save(buf, format="PNG")
    cut = remove(buf.getvalue(), session=session)
    fg = Image.open(BytesIO(cut)).convert("RGBA")
    if fg.size != src.size:
        fg = fg.resize(src.size, Image.Resampling.LANCZOS)

    rgb = BG_RGB[bg]
    canvas = Image.new("RGB", fg.size, rgb)
    canvas.paste(fg, (0, 0), fg.split()[3])

    suf = out.suffix.lower()
    if suf in (".jpg", ".jpeg"):
        canvas.save(out, format="JPEG", quality=95)
    else:
        canvas.save(out, format="PNG")
