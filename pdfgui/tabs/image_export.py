"""PDF 导出为图片功能页。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from pdfgui.ui import theme, widgets


def build_tab(app, nb: ttk.Notebook) -> None:
    shell, canvas, tab = app.scroll_tab_shell(nb)
    nb.add(shell, text="  导出图片  ")

    app.im_in = tk.StringVar()
    app.im_out = tk.StringVar()
    app.im_fmt = tk.StringVar(value="png")
    app.im_pages = tk.StringVar()
    app.im_dpi = tk.IntVar(value=150)
    app.im_jpgq = tk.IntVar(value=90)

    r = 0
    sec_file = ttk.LabelFrame(tab, text=" 文件位置 ", style="Section.TLabelframe", padding=(16, 12))
    sec_file.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_file)

    e_in = widgets.entry_line(sec_file, textvariable=app.im_in)
    b_in = ttk.Button(sec_file, text="浏览…", style="Secondary.TButton", command=app.pick_im_in)
    app.form_row(sec_file, 0, "输入 PDF", e_in, btn=b_in)

    e_out = widgets.entry_line(sec_file, textvariable=app.im_out)
    b_out = ttk.Button(
        sec_file, text="浏览…", style="Secondary.TButton", command=lambda: widgets.browse_dir(app.im_out)
    )
    app.form_row(sec_file, 1, "输出目录", e_out, btn=b_out)

    sec_opt = ttk.LabelFrame(tab, text=" 导出范围与格式 ", style="Section.TLabelframe", padding=(16, 12))
    sec_opt.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_opt)
    sec_opt.columnconfigure(1, weight=1)

    cb = ttk.Combobox(
        sec_opt,
        textvariable=app.im_fmt,
        values=("png", "jpg", "jpeg", "webp", "bmp", "tif"),
        width=theme.ENTRY_CHAR_WIDTH,
        state="readonly",
        font=theme.FONT_ENTRY,
        foreground=theme.U_TEXT,
    )
    widgets.bind_combobox_popdown_font(cb, theme.FONT_ENTRY)
    app.form_row(sec_opt, 0, "图片格式", cb, entry_sticky=tk.EW)

    e_pages = widgets.entry_line(sec_opt, textvariable=app.im_pages)
    ttk.Label(sec_opt, text="页码范围", style="Card.TLabel", anchor=tk.W).grid(
        row=1, column=0, sticky=tk.NW, pady=10, padx=(0, 8)
    )
    e_pages.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=(0, 0), pady=10)
    im_hint = ttk.Label(
        sec_opt,
        text="留空为全部页。示例：1,3,5-8",
        wraplength=400,
        style="Muted.TLabel",
    )
    im_hint.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=(0, 4))

    def _sync_im_wrap(_event: object | None = None) -> None:
        try:
            ww = max(tab.winfo_width() - 56, 200)
        except tk.TclError:
            return
        im_hint.configure(wraplength=ww)

    tab.bind("<Configure>", lambda e: _sync_im_wrap(), add="+")
    app.after_idle(_sync_im_wrap)

    sec_q = ttk.LabelFrame(tab, text=" 图像质量 ", style="Section.TLabelframe", padding=(16, 12))
    sec_q.grid(row=r, column=0, sticky=tk.EW, pady=(0, 8))
    sec_q.columnconfigure(0, weight=1)
    sec_q.rowconfigure(0, weight=1)
    r += 1

    qrow = ttk.Frame(sec_q, style="Card.TFrame")
    qrow.grid(row=0, column=0, sticky=tk.NSEW)
    qrow.columnconfigure(0, weight=1)
    qrow.columnconfigure(1, weight=1)

    q_left = ttk.Frame(qrow, style="Card.TFrame", padding=(0, 0, 12, 0))
    q_left.grid(row=0, column=0, sticky=tk.NSEW)
    q_right = ttk.Frame(qrow, style="Card.TFrame", padding=(12, 0, 0, 0))
    q_right.grid(row=0, column=1, sticky=tk.NSEW)
    q_left.columnconfigure(1, weight=1)
    q_right.columnconfigure(1, weight=1)

    app.slider_row(q_left, 0, app.im_dpi, 72, 400, 1, lambda v: f"清晰度 DPI：{int(v)}")
    app.slider_row(q_right, 0, app.im_jpgq, 60, 100, 1, lambda v: f"JPEG 质量：{int(v)}")
    app.attach_scale_resize(q_left, reserve=200)
    app.attach_scale_resize(q_right, reserve=200)

    ttk.Separator(tab, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, pady=(12, 4))
    r += 1

    foot = ttk.Frame(tab, style="Card.TFrame")
    foot.grid(row=r, column=0, sticky=tk.EW)
    foot.columnconfigure(0, weight=1)
    btn = ttk.Button(foot, text="导出图片", style="Primary.TButton", command=app.run_image)
    btn.grid(row=0, column=0, sticky=tk.EW, pady=(8, 0))
    app._im_btn = btn

    tab.columnconfigure(0, weight=1)
    app.bind_scroll_wheel(tab, canvas)
