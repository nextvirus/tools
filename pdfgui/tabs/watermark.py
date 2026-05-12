"""文字水印功能页。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from pdfgui.ui import theme, widgets


def build_tab(app, nb: ttk.Notebook) -> None:
    shell, canvas, tab = app.scroll_tab_shell(nb)
    nb.add(shell, text="  文字水印  ")

    app.wm_in = tk.StringVar()
    app.wm_out = tk.StringVar()
    app.wm_text = tk.StringVar(value="内部资料")
    app.wm_fontfile = tk.StringVar(value=theme.default_chinese_font_path())

    app.wm_size = tk.DoubleVar(value=44)
    app.wm_opacity = tk.DoubleVar(value=0.15)
    app.wm_angle = tk.DoubleVar(value=-35)
    app.wm_gapx = tk.DoubleVar(value=160)
    app.wm_gapy = tk.DoubleVar(value=130)
    app.wm_gray = tk.DoubleVar(value=0.55)

    r = 0
    sec_file = ttk.LabelFrame(tab, text=" PDF 文件 ", style="Section.TLabelframe", padding=(16, 12))
    sec_file.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_file)

    e_in = widgets.entry_line(sec_file, textvariable=app.wm_in)
    b_in = ttk.Button(sec_file, text="浏览…", style="Secondary.TButton", command=app.pick_wm_in)
    app.form_row(sec_file, 0, "输入 PDF", e_in, btn=b_in)

    e_out = widgets.entry_line(sec_file, textvariable=app.wm_out)
    b_out = ttk.Button(
        sec_file,
        text="另存为…",
        style="Secondary.TButton",
        command=lambda: widgets.browse_save_pdf(app.wm_out, app.wm_in),
    )
    app.form_row(sec_file, 1, "输出 PDF", e_out, btn=b_out)

    sec_txt = ttk.LabelFrame(tab, text=" 水印与字体 ", style="Section.TLabelframe", padding=(16, 12))
    sec_txt.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_txt)
    sec_txt.columnconfigure(1, weight=1)

    e_txt = widgets.entry_line(sec_txt, textvariable=app.wm_text)
    ttk.Label(sec_txt, text="水印文字", style="Card.TLabel", anchor=tk.W).grid(
        row=0, column=0, sticky=tk.NW, pady=10, padx=(0, 8)
    )
    e_txt.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=(0, 0), pady=10)

    e_font = widgets.entry_line(sec_txt, textvariable=app.wm_fontfile)
    bf = ttk.Frame(sec_txt, style="Card.TFrame")
    ttk.Button(bf, text="浏览…", style="Secondary.TButton", command=lambda: widgets.browse_font(app.wm_fontfile)).pack(
        side=tk.LEFT, padx=(0, 6)
    )
    ttk.Button(bf, text="仿宋", style="Secondary.TButton", command=app.fill_simfang).pack(side=tk.LEFT, padx=(0, 6))
    ttk.Button(bf, text="雅黑", style="Secondary.TButton", command=app.fill_msyh).pack(side=tk.LEFT)
    ttk.Label(sec_txt, text="中文字体", style="Card.TLabel", anchor=tk.W).grid(
        row=1, column=0, sticky=tk.NW, pady=10, padx=(0, 8)
    )
    e_font.grid(row=1, column=1, sticky=tk.EW, padx=(0, 8), pady=10)
    bf.grid(row=1, column=2, sticky=tk.E, pady=10)

    wm_hint = ttk.Label(
        sec_txt,
        text="优先系统仿宋 / 雅黑；路径留空则用内置简体字形。水印内容可直接输入中文。",
        wraplength=400,
        style="Muted.TLabel",
    )
    wm_hint.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=(4, 0))

    def _sync_wm_wrap(_event: object | None = None) -> None:
        try:
            ww = max(tab.winfo_width() - 56, 200)
        except tk.TclError:
            return
        wm_hint.configure(wraplength=ww)

    tab.bind("<Configure>", lambda e: _sync_wm_wrap(), add="+")
    app.after_idle(_sync_wm_wrap)

    sec_layout = ttk.LabelFrame(tab, text=" 版式（拖动滑块） ", style="Section.TLabelframe", padding=(16, 12))
    sec_layout.grid(row=r, column=0, sticky=tk.EW, pady=(0, 8))
    sec_layout.columnconfigure(0, weight=1)
    sec_layout.rowconfigure(0, weight=1)
    r += 1

    twin = ttk.Frame(sec_layout, style="Card.TFrame")
    twin.grid(row=0, column=0, sticky=tk.NSEW)
    twin.columnconfigure(0, weight=1)
    twin.columnconfigure(1, weight=1)

    left = ttk.Frame(twin, style="Card.TFrame", padding=(0, 0, 12, 0))
    left.grid(row=0, column=0, sticky=tk.NSEW)
    right = ttk.Frame(twin, style="Card.TFrame", padding=(12, 0, 0, 0))
    right.grid(row=0, column=1, sticky=tk.NSEW)
    left.columnconfigure(1, weight=1)
    right.columnconfigure(1, weight=1)

    sr = 0
    app.slider_row(left, sr, app.wm_size, 18, 72, 1, lambda v: f"字号：{int(float(v))} 磅")
    sr += 1
    app.slider_row(left, sr, app.wm_angle, -75, 0, 1, lambda v: f"倾斜角度：{int(float(v))}°")
    sr += 1
    app.slider_row(left, sr, app.wm_gapy, 60, 260, 5, lambda v: f"纵向间距：{int(float(v))}")

    ir = 0
    app.slider_row(
        right,
        ir,
        app.wm_opacity,
        0.05,
        0.55,
        0.01,
        lambda v: f"不透明度：{float(v):.2f}",
    )
    ir += 1
    app.slider_row(right, ir, app.wm_gapx, 80, 280, 5, lambda v: f"横向间距：{int(float(v))}")
    ir += 1
    app.slider_row(right, ir, app.wm_gray, 0.2, 0.85, 0.01, lambda v: f"灰度：{float(v):.2f}")

    app.attach_scale_resize(left, reserve=200)
    app.attach_scale_resize(right, reserve=200)

    ttk.Separator(tab, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, pady=(12, 4))
    r += 1

    foot = ttk.Frame(tab, style="Card.TFrame")
    foot.grid(row=r, column=0, sticky=tk.EW)
    foot.columnconfigure(0, weight=1)
    btn = ttk.Button(foot, text="生成水印 PDF", style="Primary.TButton", command=app.run_watermark)
    btn.grid(row=0, column=0, sticky=tk.EW, pady=(8, 0))
    app._wm_btn = btn

    tab.columnconfigure(0, weight=1)
    app.bind_scroll_wheel(tab, canvas)
