"""照片换底：红 / 蓝 / 白纯色背景（rembg 人像分割）。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from pdfgui.ui import widgets


def build_tab(app, nb: ttk.Notebook) -> None:
    shell, canvas, tab = app.scroll_tab_shell(nb)
    nb.add(shell, text="  照片换底  ")

    app.ph_in = tk.StringVar()
    app.ph_out = tk.StringVar()
    app.ph_color = tk.StringVar(value="blue")

    def _ph_sync_out(*_args: object) -> None:
        app._maybe_fill_photo_out()

    app.ph_in.trace_add("write", _ph_sync_out)
    app.ph_color.trace_add("write", _ph_sync_out)

    r = 0
    sec_file = ttk.LabelFrame(tab, text=" 文件 ", style="Section.TLabelframe", padding=(16, 12))
    sec_file.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_file)

    e_in = widgets.entry_line(sec_file, textvariable=app.ph_in)
    b_in = ttk.Button(
        sec_file,
        text="浏览…",
        style="Secondary.TButton",
        command=app.pick_ph_in,
    )
    app.form_row(sec_file, 0, "照片路径", e_in, btn=b_in)

    def _browse_ph_save() -> None:
        from pdfgui.photo.photo_bg import default_output_path

        inp = app.ph_in.get().strip()
        bg = app.ph_color.get().strip().lower()
        sug = default_output_path(inp, bg) if inp and bg in ("red", "blue", "white") else None
        widgets.browse_save_image(app.ph_out, app.ph_in, suggested_path=sug)

    e_out = widgets.entry_line(sec_file, textvariable=app.ph_out)
    b_out = ttk.Button(
        sec_file,
        text="另存为…",
        style="Secondary.TButton",
        command=_browse_ph_save,
    )
    app.form_row(sec_file, 1, "输出路径", e_out, btn=b_out)

    sec_bg = ttk.LabelFrame(tab, text=" 新底色 ", style="Section.TLabelframe", padding=(16, 12))
    sec_bg.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    sec_bg.columnconfigure(1, weight=1)

    ttk.Label(sec_bg, text="选择底色", style="Card.TLabel", anchor=tk.W).grid(
        row=0, column=0, sticky=tk.W, padx=(0, 8), pady=10
    )
    row = ttk.Frame(sec_bg, style="Card.TFrame")
    row.grid(row=0, column=1, sticky=tk.W, pady=10)
    for text, val in (("红", "red"), ("蓝", "blue"), ("白", "white")):
        ttk.Radiobutton(row, text=text, variable=app.ph_color, value=val).pack(side=tk.LEFT, padx=(0, 16))

    hint = ttk.Label(
        sec_bg,
        text=(
            "使用 rembg（u2net_human_seg）。模型已随程序放在 rembg_models（安装包在 _internal 内），一般无需联网。"
            "第一次换底仍会较慢：要加载 onnxruntime、读入 ONNX 并做首次推理；启动约 1 秒后会自动在后台预加载，"
            "稍等再点「生成」会快很多。开发环境若缺模型请执行：python scripts/fetch_rembg_models.py"
        ),
        wraplength=400,
        style="Muted.TLabel",
    )
    hint.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(8, 0))

    _last_wrap_w = [0]

    def _sync_hint(_e=None):
        try:
            ww = max(tab.winfo_width() - 56, 200)
        except tk.TclError:
            return
        if abs(ww - _last_wrap_w[0]) < 8:
            return
        _last_wrap_w[0] = ww
        hint.configure(wraplength=ww)

    tab.bind("<Configure>", lambda e: _sync_hint(), add="+")
    app.after_idle(_sync_hint)

    ttk.Separator(tab, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, pady=(12, 4))
    r += 1

    foot = ttk.Frame(tab, style="Card.TFrame")
    foot.grid(row=r, column=0, sticky=tk.EW)
    foot.columnconfigure(0, weight=1)
    btn = ttk.Button(foot, text="生成换底照片", style="Primary.TButton", command=app.run_photo_bg)
    btn.grid(row=0, column=0, sticky=tk.EW, pady=(8, 0))
    app._ph_btn = btn

    tab.columnconfigure(0, weight=1)
    app.bind_scroll_wheel(tab, canvas)
