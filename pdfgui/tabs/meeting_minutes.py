"""会议纪要整理（DeepSeek API）。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from pdfgui.meeting.deepseek import DEFAULT_MODEL, MEETING_MODEL_OPTIONS
from pdfgui.meeting.settings import load_settings, save_settings
from pdfgui.ui import theme, widgets


def build_tab(app, nb: ttk.Notebook) -> None:
    shell, canvas, tab = app.scroll_tab_shell(nb)
    nb.add(shell, text="  会议纪要  ")

    saved = load_settings()
    app.mm_api_key = tk.StringVar(value=str(saved.get("deepseek_api_key", "") or ""))
    _saved_model = str(saved.get("deepseek_model", "") or "").strip()
    if _saved_model not in MEETING_MODEL_OPTIONS:
        _saved_model = DEFAULT_MODEL
    app.mm_model = tk.StringVar(value=_saved_model)

    r = 0
    sec_api = ttk.LabelFrame(tab, text=" API 配置 ", style="Section.TLabelframe", padding=(16, 12))
    sec_api.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    app.config_form_columns(sec_api)
    sec_api.columnconfigure(1, weight=1)

    ttk.Label(sec_api, text="服务商", style="Card.TLabel", anchor=tk.W).grid(
        row=0, column=0, sticky=tk.W, padx=(0, 8), pady=10
    )
    ttk.Label(sec_api, text="DeepSeek（OpenAI 兼容）", style="Card.TLabel", anchor=tk.W).grid(
        row=0, column=1, sticky=tk.W, pady=10
    )

    ttk.Label(sec_api, text="API Key", style="Card.TLabel", anchor=tk.W).grid(
        row=1, column=0, sticky=tk.W, padx=(0, 8), pady=10
    )
    key_entry = ttk.Entry(
        sec_api,
        textvariable=app.mm_api_key,
        show="*",
        font=theme.FONT_ENTRY,
        width=theme.ENTRY_CHAR_WIDTH + 24,
    )
    key_entry.grid(row=1, column=1, sticky=tk.EW, padx=(0, 8), pady=10)

    def _save_mm_settings() -> None:
        data = load_settings()
        data["deepseek_api_key"] = app.mm_api_key.get().strip()
        data["deepseek_model"] = app.mm_model.get().strip() or DEFAULT_MODEL
        save_settings(data)
        messagebox.showinfo("已保存", "API 配置已写入本机用户目录（不上传仓库）。")

    btn_save = ttk.Button(
        sec_api,
        text="保存配置",
        style="Secondary.TButton",
        command=_save_mm_settings,
    )
    btn_save.grid(row=1, column=2, sticky=tk.E, padx=(4, 0), pady=10)

    ttk.Label(sec_api, text="模型", style="Card.TLabel", anchor=tk.W).grid(
        row=2, column=0, sticky=tk.W, padx=(0, 8), pady=10
    )
    cb_model = ttk.Combobox(
        sec_api,
        textvariable=app.mm_model,
        values=MEETING_MODEL_OPTIONS,
        width=theme.ENTRY_CHAR_WIDTH + 8,
        state="readonly",
        font=theme.FONT_ENTRY,
        foreground=theme.U_TEXT,
    )
    cb_model.grid(row=2, column=1, sticky=tk.W, padx=(0, 8), pady=10)
    widgets.bind_combobox_popdown_font(cb_model, theme.FONT_ENTRY)

    api_hint = ttk.Label(
        sec_api,
        text=(
            "在 DeepSeek 开放平台创建 API Key：https://platform.deepseek.com 。"
            "密钥保存在本机（Windows：%APPDATA%\\tools\\meeting_settings.json），请妥善保管。"
        ),
        wraplength=400,
        style="Muted.TLabel",
    )
    api_hint.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(4, 0))

    _last_api_wrap = [0]

    def _sync_api_hint(_e=None):
        try:
            ww = max(tab.winfo_width() - 56, 200)
        except tk.TclError:
            return
        if abs(ww - _last_api_wrap[0]) < 8:
            return
        _last_api_wrap[0] = ww
        api_hint.configure(wraplength=ww)

    tab.bind("<Configure>", lambda e: _sync_api_hint(), add="+")
    app.after_idle(_sync_api_hint)

    sec_mic = ttk.LabelFrame(tab, text=" 麦克风采集（当前会议） ", style="Section.TLabelframe", padding=(16, 12))
    sec_mic.grid(row=r, column=0, sticky=tk.EW, pady=(0, 12))
    r += 1
    sec_mic.columnconfigure(1, weight=1)

    app.mm_rec_status = tk.StringVar(value="就绪：可分段录音，每段结束后自动转写并追加到下方正文。")
    mic_row = ttk.Frame(sec_mic, style="Card.TFrame")
    mic_row.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
    btn_rec_start = ttk.Button(
        mic_row,
        text="开始录音",
        style="Secondary.TButton",
        command=app.mm_start_recording,
    )
    btn_rec_start.pack(side=tk.LEFT, padx=(0, 8))
    btn_rec_stop = ttk.Button(
        mic_row,
        text="结束并识别",
        style="Secondary.TButton",
        command=app.mm_stop_recording,
        state=tk.DISABLED,
    )
    btn_rec_stop.pack(side=tk.LEFT, padx=(0, 8))
    app._mm_btn_rec_start = btn_rec_start
    app._mm_btn_rec_stop = btn_rec_stop

    mic_status_lab = ttk.Label(sec_mic, textvariable=app.mm_rec_status, style="Muted.TLabel", wraplength=520, justify=tk.LEFT)
    mic_status_lab.grid(row=1, column=0, columnspan=3, sticky=tk.EW)

    mic_hint = ttk.Label(
        sec_mic,
        text=(
            "使用系统默认麦克风；转写在本地通过 Vosk（中文）完成，无需外网。"
            "首次使用请执行 python scripts/fetch_vosk_cn_model.py 下载模型（安装包已内置则跳过）。"
            "识别质量与音量、环境噪声有关，可多次「开始→结束」分段录制后拼接。"
        ),
        wraplength=400,
        style="Muted.TLabel",
    )
    mic_hint.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=(8, 0))

    _last_mic_wrap = [0]

    def _sync_mic_hint(_e=None):
        try:
            ww = max(tab.winfo_width() - 56, 200)
        except tk.TclError:
            return
        if abs(ww - _last_mic_wrap[0]) < 8:
            return
        _last_mic_wrap[0] = ww
        mic_hint.configure(wraplength=ww)
        mic_status_lab.configure(wraplength=ww)

    tab.bind("<Configure>", lambda e: _sync_mic_hint(), add="+")
    app.after_idle(_sync_mic_hint)

    sec_in = ttk.LabelFrame(tab, text=" 会议原始内容 ", style="Section.TLabelframe", padding=(16, 12))
    sec_in.grid(row=r, column=0, sticky=tk.NSEW, pady=(0, 12))
    r += 1
    tab.rowconfigure(r - 1, weight=1)
    sec_in.columnconfigure(0, weight=1)
    sec_in.rowconfigure(0, weight=1)

    app.mm_in = tk.Text(
        sec_in,
        height=10,
        wrap=tk.WORD,
        font=theme.FONT_ENTRY,
        bg=theme.U_LOG_BG,
        fg=theme.U_TEXT,
        relief=tk.FLAT,
        padx=10,
        pady=8,
    )
    app.mm_in.grid(row=0, column=0, sticky=tk.NSEW)

    sec_out = ttk.LabelFrame(tab, text=" 整理结果 ", style="Section.TLabelframe", padding=(16, 12))
    sec_out.grid(row=r, column=0, sticky=tk.NSEW, pady=(0, 12))
    r += 1
    tab.rowconfigure(r - 1, weight=2)
    sec_out.columnconfigure(0, weight=1)
    sec_out.rowconfigure(0, weight=1)

    app.mm_out = tk.Text(
        sec_out,
        height=14,
        wrap=tk.WORD,
        font=theme.FONT_ENTRY,
        bg=theme.U_LOG_BG,
        fg=theme.U_TEXT,
        relief=tk.FLAT,
        padx=10,
        pady=8,
        state=tk.DISABLED,
    )
    app.mm_out.grid(row=0, column=0, sticky=tk.NSEW)

    ttk.Separator(tab, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, pady=(12, 4))
    r += 1

    foot = ttk.Frame(tab, style="Card.TFrame")
    foot.grid(row=r, column=0, sticky=tk.EW)
    foot.columnconfigure(0, weight=1)
    btn = ttk.Button(foot, text="整理会议纪要", style="Primary.TButton", command=app.run_meeting_summarize)
    btn.grid(row=0, column=0, sticky=tk.EW, pady=(8, 0))
    app._mm_btn = btn

    tab.columnconfigure(0, weight=1)
    app.bind_scroll_wheel(tab, canvas)
    app.bind_scroll_wheel(sec_mic, canvas)
    app.bind_scroll_wheel(app.mm_in, canvas)
    app.bind_scroll_wheel(app.mm_out, canvas)
