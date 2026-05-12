"""
将 PDF 按页渲染为位图，可选择格式、DPI、页码范围。

命令行（在项目根目录）:
  python -m pdfgui.pdf.pdf_to_img 报告.pdf -o ./out/
  python -m pdfgui.pdf.pdf_to_img 报告.pdf -o ./out/ --format jpg --dpi 200 --pages 1,3-5
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import fitz  # PyMuPDF

# 用户 --format 与文件扩展名
_FORMAT_EXT = {
    "png": "png",
    "jpg": "jpg",
    "jpeg": "jpg",
    "webp": "webp",
    "bmp": "bmp",
    "tif": "tif",
    "tiff": "tif",
}


def parse_pages(spec: str | None, page_count: int) -> list[int]:
    """
    解析页码表达式，返回 0-based 页索引列表（已去重、升序）。
    规则：1 表示第一页；支持逗号与连字符，如 1,3,5-7。
    """
    if not spec or not spec.strip():
        return list(range(page_count))
    seen: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo = int(a.strip())
            hi = int(b.strip())
            if lo > hi:
                lo, hi = hi, lo
            for p in range(lo, hi + 1):
                idx = p - 1
                if 0 <= idx < page_count:
                    seen.add(idx)
        else:
            p = int(part)
            idx = p - 1
            if 0 <= idx < page_count:
                seen.add(idx)
    if not seen:
        raise ValueError("页码解析结果为空，请检查 --pages 与 PDF 总页数")
    return sorted(seen)


def _dpi_matrix(dpi: float) -> fitz.Matrix:
    z = max(1.0, dpi) / 72.0
    return fitz.Matrix(z, z)


def _save_pixmap(
    pix: fitz.Pixmap,
    path: Path,
    fmt: str,
    *,
    jpg_quality: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = fmt.lower()
    if fmt in ("jpg", "jpeg"):
        if pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(str(path), jpg_quality=jpg_quality)
    else:
        pix.save(str(path))


def pdf_to_images(
    input_pdf: str | Path,
    out_dir: str | Path,
    *,
    image_format: str = "png",
    dpi: float = 150,
    pages_spec: str | None = None,
    filename_pattern: str = "{stem}_p{n:04d}.{ext}",
    jpg_quality: int = 90,
) -> list[Path]:
    """
    将 PDF 页面导出为图片。

    image_format: png / jpg / webp / bmp / tiff 等（见 _FORMAT_EXT）。
    filename_pattern: 可用占位符 stem=原文件名不含扩展名, n=从1开始的页码, ext=扩展名。
    """
    pdf = Path(input_pdf)
    if not pdf.is_file():
        raise FileNotFoundError(f"找不到 PDF: {pdf}")

    fmt = image_format.lower().strip(".")
    if fmt not in _FORMAT_EXT:
        raise ValueError(f"不支持的格式 {image_format!r}，可选: {', '.join(sorted(_FORMAT_EXT))}")

    ext = _FORMAT_EXT[fmt]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    try:
        indices = parse_pages(pages_spec, doc.page_count)
        mat = _dpi_matrix(dpi)
        stem = pdf.stem
        saved: list[Path] = []
        for idx in indices:
            page = doc[idx]
            pix = page.get_pixmap(matrix=mat, alpha=(ext == "png"))
            n = idx + 1
            name = filename_pattern.format(stem=stem, n=n, ext=ext)
            if not re.match(r"^[^\\/:*?\"<>|]+$", name) or "/" in name or "\\" in name:
                raise ValueError(f"非法文件名 pattern 结果: {name!r}")
            dest = out / name
            _save_pixmap(pix, dest, "jpeg" if ext in ("jpg", "jpeg") else ext, jpg_quality=jpg_quality)
            saved.append(dest)
        return saved
    finally:
        doc.close()


def main() -> None:
    p = argparse.ArgumentParser(description="PDF 转图片（可选格式、DPI、页码）")
    p.add_argument("input", type=Path, help="输入 PDF")
    p.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        required=True,
        help="输出目录（不存在会自动创建）",
    )
    p.add_argument(
        "--format",
        "-f",
        default="png",
        help=f"图片格式（默认 png）: {', '.join(sorted(set(_FORMAT_EXT)))}",
    )
    p.add_argument("--dpi", type=float, default=150, help="渲染分辨率 DPI（默认 150）")
    p.add_argument(
        "--pages",
        default=None,
        help='要导出的页，1 起算；例: "1" "1,3,5" "2-5" 留空表示全部',
    )
    p.add_argument(
        "--pattern",
        default="{stem}_p{n:04d}.{ext}",
        help='文件名模板，占位符: {stem} {n} {ext}，默认 "{stem}_p{n:04d}.{ext}"',
    )
    p.add_argument(
        "--jpg-quality",
        type=int,
        default=90,
        help="jpg/jpeg 质量 1-100（默认 90）",
    )
    args = p.parse_args()

    paths = pdf_to_images(
        args.input,
        args.out_dir,
        image_format=args.format,
        dpi=args.dpi,
        pages_spec=args.pages,
        filename_pattern=args.pattern,
        jpg_quality=max(1, min(100, args.jpg_quality)),
    )
    print(f"共导出 {len(paths)} 张 -> {args.out_dir.resolve()}")
    for path in paths[:5]:
        print(f"  {path.name}")
    if len(paths) > 5:
        print(f"  ... 另有 {len(paths) - 5} 个文件")


if __name__ == "__main__":
    main()
