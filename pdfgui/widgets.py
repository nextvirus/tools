"""表单控件、文件对话框、组合框弹出层字体等可复用片段。"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .theme import ENTRY_CHAR_WIDTH, FONT_ENTRY

__all__ = [
    "entry_line",
    "font_to_tcl_descriptor",
    "bind_combobox_popdown_font",
    "bind_slider_label",
    "browse_pdf",
    "browse_save_pdf",
    "browse_font",
    "browse_dir",
    "browse_raster_image",
    "pick_raster_image_path",
]


def entry_line(parent, *, textvariable: tk.Variable | None = None, width: int | None = None, **kw) -> ttk.Entry:
    w = ENTRY_CHAR_WIDTH if width is None else width
    return ttk.Entry(
        parent,
        textvariable=textvariable,
        font=FONT_ENTRY,
        width=w,
        **kw,
    )


def font_to_tcl_descriptor(ft) -> str:
    if isinstance(ft, (tuple, list)) and len(ft) >= 2:
        fn = str(ft[0]).replace("{", "").replace("}", "")
        sz = int(ft[1])
        rest = [str(x) for x in ft[2:]]
        return " ".join([f"{{{fn}}}", str(sz), *rest])
    return str(ft)


def bind_combobox_popdown_font(cb: ttk.Combobox, font) -> None:
    lb_path_tail = ".f.l"
    desc = font_to_tcl_descriptor(font)

    def _patch_listbox(_event: object | None = None) -> None:
        def inner() -> None:
            try:
                pd = str(cb.tk.call("ttk::combobox::PopdownWindow", str(cb)))
            except tk.TclError:
                return
            if not pd or pd == "0":
                return
            path = f"{pd}{lb_path_tail}"
            try:
                cb.tk.call(path, "configure", "-font", desc)
            except tk.TclError:
                pass

        cb.after_idle(inner)
        cb.after(20, inner)

    for seq in ("<ButtonPress-1>", "<KeyPress-Down>", "<KeyPress-space>"):
        cb.bind(seq, _patch_listbox, add="+")


def bind_slider_label(var: tk.Variable, label: ttk.Label, fmt) -> None:
    def upd(*_):
        try:
            label.configure(text=fmt(var.get()))
        except (tk.TclError, ValueError, TypeError):
            pass

    var.trace_add("write", lambda *_: upd())
    upd()


def browse_pdf(var: tk.StringVar) -> None:
    p = filedialog.askopenfilename(
        title="选择 PDF",
        filetypes=[("PDF", "*.pdf"), ("全部", "*.*")],
    )
    if p:
        var.set(p)


def browse_save_pdf(var: tk.StringVar, src_var: tk.StringVar) -> None:
    initial = Path(src_var.get()) if src_var.get().strip() else Path.home()
    stem = initial.stem if initial.suffix.lower() == ".pdf" else "output"
    initialfile = f"{stem}_watermarked.pdf"
    p = filedialog.asksaveasfilename(
        title="保存为",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=initialfile,
        initialdir=str(initial.parent) if initial.parent.exists() else None,
    )
    if p:
        var.set(p)


def browse_font(var: tk.StringVar) -> None:
    p = filedialog.askopenfilename(
        title="选择中文字体",
        filetypes=[("字体", "*.ttf *.otf *.ttc"), ("全部", "*.*")],
    )
    if p:
        var.set(p)


def browse_dir(var: tk.StringVar) -> None:
    p = filedialog.askdirectory(title="选择输出文件夹")
    if p:
        var.set(p)


def pick_raster_image_path() -> str | None:
    p = filedialog.askopenfilename(
        title="选择照片",
        filetypes=[
            ("图片", "*.png *.jpg *.jpeg *.webp *.bmp *.tif"),
            ("全部", "*.*"),
        ],
    )
    return p if p else None


def browse_raster_image(var: tk.StringVar) -> None:
    p = pick_raster_image_path()
    if p:
        var.set(p)


def browse_save_image(
    var: tk.StringVar,
    src_var: tk.StringVar,
    *,
    suggested_path: str | None = None,
) -> None:
    if suggested_path and str(suggested_path).strip():
        sp = Path(suggested_path)
        ext = sp.suffix.lower() if sp.suffix else ".png"
        if ext not in (".png", ".jpg", ".jpeg"):
            ext = ".png"
        defaultextension = ext
        initialfile = sp.name
        initialdir = str(sp.parent) if sp.parent.exists() else None
    else:
        initial = Path(src_var.get()) if src_var.get().strip() else Path.home() / "output.png"
        stem = initial.stem if initial.suffix else "output"
        ext = initial.suffix.lower() if initial.suffix.lower() in (".png", ".jpg", ".jpeg") else ".png"
        defaultextension = ext
        initialfile = f"{stem}{ext}"
        initialdir = str(initial.parent) if initial.parent.exists() else None
    p = filedialog.asksaveasfilename(
        title="保存为",
        defaultextension=defaultextension,
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")],
        initialfile=initialfile,
        initialdir=initialdir,
    )
    if p:
        var.set(p)
