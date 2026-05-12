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
        return Path(sys._MEIPASS) / "pdfgui" / "photo" / "rembg_models"
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


def models_dir() -> Path:
    """当前使用的 rembg 模型目录（开发为 photo/rembg_models；打包在 _MEIPASS/pdfgui/photo/rembg_models）。"""
    return _rembg_models_dir()


def _human_seg_model_path() -> Path:
    return _rembg_models_dir() / "u2net_human_seg.onnx"


def _u2net_model_path() -> Path:
    return _rembg_models_dir() / "u2net.onnx"


def _ensure_model_files() -> None:
    """避免缺失 onnx 时 rembg 走网络下载导致长时间卡住。"""
    root = _rembg_models_dir()
    human = _human_seg_model_path()
    fallback = _u2net_model_path()
    if not human.is_file() and not fallback.is_file():
        loc = root
        raise FileNotFoundError(
            f"未找到换底模型（需要 u2net_human_seg.onnx 或 u2net.onnx）。目录: {loc}。"
            "安装包应已内置；若缺失请重新用 scripts/package_tools.py 打包。"
            "开发环境请执行: python scripts/fetch_rembg_models.py"
        )


def warmup_rembg_session() -> None:
    """在后台预先加载 ONNX 会话，减轻用户第一次点「生成换底」时的等待（仍会占用几秒 CPU/磁盘）。"""
    try:
        _ensure_model_files()
        _get_session()
    except Exception:
        pass


def _get_session():
    """u2net_human_seg 偏人像；权重放在 photo/rembg_models（见 scripts/fetch_rembg_models.py）。"""
    global _session
    if _session is not None:
        return _session
    _ensure_model_files()
    from rembg import new_session

    if _human_seg_model_path().is_file():
        try:
            _session = new_session("u2net_human_seg")
        except Exception:
            _session = new_session("u2net")
    else:
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
        hint = '请安装：pip install "rembg[cpu]"'
        if getattr(sys, "frozen", False):
            hint += f"（安装包内 rembg 依赖不完整，请用仓库内 scripts/package_tools.py 重新打包。详情: {e}）"
        raise ImportError(hint) from e

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
