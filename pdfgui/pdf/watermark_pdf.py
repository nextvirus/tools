"""
给 PDF 添加文字水印（斜向平铺，支持透明度与字号等）。

安装: pip install -r requirements.txt
命令行（在项目根目录）: python -m pdfgui.pdf.watermark_pdf 输入.pdf 输出.pdf -t "内部资料"
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import fitz  # PyMuPDF


def _text_needs_cjk_font(text: str) -> bool:
    return any(ord(ch) > 0x7F for ch in text)


def _embed_font_resource_name(fontfile: str | Path) -> str:
    """PDF 资源名：与 Base14 / 内置 CJK 别名不可冲突，否则 insert_font 会忽略 fontfile。"""
    h = hashlib.md5(
        str(Path(fontfile).resolve()).encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()[:10]
    return f"f0wm{h}"


def _resolve_font(
    fontname: str,
    fontfile: str | Path | None,
    text: str,
) -> tuple[str, str | None]:
    """
    使用自定义 fontfile 时禁止使用 helv/tiro 等 Base14 名字，否则实际仍嵌入 Helvetica，中文乱码。
    无 fontfile 且含非 ASCII 时，用内置 china-ss（简体）。
    """
    if fontfile:
        path = Path(fontfile)
        if not path.is_file():
            raise FileNotFoundError(f"找不到字体文件: {path}")
        base14 = getattr(fitz, "Base14_fontdict", {})
        cjk_aliases = {
            "china-t",
            "china-s",
            "japan",
            "korea",
            "china-ts",
            "china-ss",
            "japan-s",
            "korea-s",
        }
        lower = fontname.lower()
        if lower in base14 or lower in cjk_aliases:
            return _embed_font_resource_name(path), str(path)
        return fontname, str(path)
    base14 = getattr(fitz, "Base14_fontdict", {})
    if _text_needs_cjk_font(text) and fontname.lower() in base14:
        return "china-ss", None
    return fontname, None


def add_watermark(
    input_path: str | Path,
    output_path: str | Path,
    text: str,
    *,
    fontname: str = "helv",
    fontfile: str | None = None,
    fontsize: float = 44,
    opacity: float = 0.15,
    angle: float = -35,
    color: tuple[float, float, float] = (0.55, 0.55, 0.55),
    gap_x: float = 160,
    gap_y: float = 130,
) -> None:
    """
    在每一页上平铺文字水印。

    color: RGB，每项 0~1。
    opacity: 0~1，越大越不透明。
    中文等字符需使用支持的字体内置名（如 china-ss）或传入 fontfile 指向 .ttf/.otf。
    """
    src = Path(input_path)
    if not src.is_file():
        raise FileNotFoundError(f"找不到文件: {src}")

    fname, ffile = _resolve_font(fontname, fontfile, text)

    doc = fitz.open(src)
    try:
        for page in doc:
            rect = page.rect
            w, h = rect.width, rect.height
            diag = (w * w + h * h) ** 0.5

            rot = fitz.Matrix(1, 1).prerotate(angle)
            y = -diag * 0.3
            while y < h + diag * 0.3:
                x = -diag * 0.3
                while x < w + diag * 0.3:
                    p = fitz.Point(x, y)
                    kw: dict = dict(
                        fontsize=fontsize,
                        fontname=fname,
                        color=color,
                        rotate=0,
                        morph=(p, rot),
                        render_mode=0,
                        fill_opacity=opacity,
                        stroke_opacity=opacity,
                        overlay=True,
                    )
                    if ffile:
                        kw["fontfile"] = ffile
                    page.insert_text(p, text, **kw)
                    x += gap_x
                y += gap_y

        doc.save(Path(output_path), garbage=4, deflate=True, clean=True)
    finally:
        doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="给 PDF 添加文字水印")
    parser.add_argument("input", type=Path, help="输入 PDF 路径")
    parser.add_argument("output", type=Path, help="输出 PDF 路径")
    parser.add_argument("-t", "--text", default="内部资料", help="水印文字")
    parser.add_argument(
        "--font",
        default="helv",
        help="字体：helv/tiro/cour 等；中文可试 china-ss（取决于 PyMuPDF 内置数据）",
    )
    parser.add_argument(
        "--fontfile",
        type=Path,
        default=None,
        help="自定义字体文件路径（.ttf/.otf），用于中文或特殊字形",
    )
    parser.add_argument("--size", type=float, default=44, help="字号")
    parser.add_argument("--opacity", type=float, default=0.15, help="不透明度 0~1")
    parser.add_argument("--angle", type=float, default=-35, help="旋转角度（度）")
    parser.add_argument("--gap-x", type=float, default=160, help="水平间距")
    parser.add_argument("--gap-y", type=float, default=130, help="垂直间距")
    parser.add_argument("--gray", type=float, default=None, help="灰色水印：0黑 1白；不设则用 RGB")
    parser.add_argument("--r", type=float, default=0.55, help="红色分量 0~1（未指定 --gray 时）")
    parser.add_argument("--g", type=float, default=0.55, help="绿色分量 0~1")
    parser.add_argument("--b", type=float, default=0.55, help="蓝色分量 0~1")
    args = parser.parse_args()

    if args.gray is not None:
        g = max(0.0, min(1.0, args.gray))
        color = (g, g, g)
    else:
        color = (
            max(0.0, min(1.0, args.r)),
            max(0.0, min(1.0, args.g)),
            max(0.0, min(1.0, args.b)),
        )

    add_watermark(
        args.input,
        args.output,
        args.text,
        fontname=args.font,
        fontfile=args.fontfile,
        fontsize=args.size,
        opacity=max(0.0, min(1.0, args.opacity)),
        angle=args.angle,
        color=color,
        gap_x=args.gap_x,
        gap_y=args.gap_y,
    )
    print(f"已保存: {args.output.resolve()}")


if __name__ == "__main__":
    main()
