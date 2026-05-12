"""颜色、字体与 ttk 主题（clam）。"""

from __future__ import annotations

from pathlib import Path

import tkinter as tk
from tkinter import ttk

U_BG = "#eef1f6"
U_CARD = "#ffffff"
U_BORDER = "#d8dee4"
U_BORDER_STRONG = "#c9d1d9"
U_TEXT = "#1f2328"
U_TEXT_SEC = "#596069"
U_PRIMARY = "#0969da"
U_PRIMARY_HOVER = "#0550ae"
U_PRIMARY_MUTED = "#80ccff"
U_FIELD = "#ffffff"
U_LOG_BG = "#f6f8fa"
U_SLIDER_TROUGH = "#3d4b5c"
U_SLIDER_THUMB = "#0969da"
U_SLIDER_THUMB_HI = "#2188ff"

_WIN_SIMFANG = Path(r"C:\Windows\Fonts\simfang.ttf")
_WIN_MSYH = Path(r"C:\Windows\Fonts\msyh.ttc")

FONT_UI = ("Microsoft YaHei UI", 14)
FONT_TITLE = ("Microsoft YaHei UI", 28, "bold")
FONT_SUB = ("Microsoft YaHei UI", 14)
FONT_SLIDER_LAB = ("Microsoft YaHei UI", 14, "bold")
FONT_ENTRY = FONT_UI
ENTRY_CHAR_WIDTH = 12
FIELD_PAD_X = 6
FIELD_PAD_Y = 4


def default_chinese_font_path() -> str:
    if _WIN_SIMFANG.is_file():
        return str(_WIN_SIMFANG)
    if _WIN_MSYH.is_file():
        return str(_WIN_MSYH)
    return ""


def apply_ttk_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=U_BG, foreground=U_TEXT, font=FONT_UI)
    style.configure("TFrame", background=U_BG)
    style.configure("Card.TFrame", background=U_CARD, relief="flat")
    style.configure("TLabel", background=U_BG, foreground=U_TEXT, font=FONT_UI)
    style.configure("Card.TLabel", background=U_CARD, foreground=U_TEXT, font=FONT_UI)
    style.configure("Muted.TLabel", background=U_CARD, foreground=U_TEXT_SEC, font=FONT_UI)
    style.configure("TitleBar.TFrame", background=U_CARD, relief="flat")

    style.configure(
        "Section.TLabelframe",
        background=U_CARD,
        foreground=U_TEXT,
        borderwidth=1,
        relief="solid",
        bordercolor=U_BORDER,
    )
    style.configure(
        "Section.TLabelframe.Label",
        background=U_CARD,
        foreground=U_TEXT,
        font=("Microsoft YaHei UI", 14, "bold"),
    )

    style.configure(
        "SliderLab.TLabel",
        background=U_CARD,
        foreground="#0d1117",
        font=FONT_SLIDER_LAB,
    )

    style.configure(
        "TEntry",
        fieldbackground=U_FIELD,
        foreground=U_TEXT,
        insertcolor=U_PRIMARY,
        bordercolor=U_BORDER_STRONG,
        lightcolor=U_BORDER,
        darkcolor=U_BORDER_STRONG,
        font=FONT_UI,
        padding=(FIELD_PAD_X, FIELD_PAD_Y),
    )
    style.map(
        "TEntry",
        selectbackground=[("!disabled", U_PRIMARY)],
        selectforeground=[("!disabled", "#ffffff")],
    )
    style.configure(
        "TCombobox",
        fieldbackground=U_FIELD,
        background=U_FIELD,
        foreground=U_TEXT,
        arrowcolor=U_TEXT_SEC,
        bordercolor=U_BORDER_STRONG,
        lightcolor=U_BORDER,
        darkcolor=U_BORDER_STRONG,
        font=FONT_ENTRY,
        padding=(FIELD_PAD_X, FIELD_PAD_Y),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", U_FIELD)],
        foreground=[("readonly", U_TEXT), ("!disabled", U_TEXT)],
    )

    style.configure(
        "TNotebook",
        background=U_BG,
        borderwidth=0,
        tabmargins=[8, 4, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background="#e4e9ef",
        foreground=U_TEXT_SEC,
        padding=[20, 10],
        font=FONT_UI,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", U_CARD), ("active", "#dde5ef")],
        foreground=[("selected", U_TEXT), ("active", U_TEXT)],
        font=[("selected", (FONT_UI[0], FONT_UI[1], "bold"))],
    )

    style.configure(
        "Primary.TButton",
        background=U_PRIMARY,
        foreground="#ffffff",
        font=("Microsoft YaHei UI", 14, "bold"),
        padding=[28, 14],
        borderwidth=0,
        focuscolor=U_PRIMARY_MUTED,
    )
    style.map(
        "Primary.TButton",
        background=[("active", U_PRIMARY_HOVER), ("disabled", "#8c959f")],
        foreground=[("disabled", "#f0f0f0")],
    )

    style.configure(
        "Secondary.TButton",
        background=U_CARD,
        foreground=U_TEXT,
        font=FONT_UI,
        padding=[18, 11],
        borderwidth=1,
        relief="solid",
        bordercolor=U_BORDER_STRONG,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", U_LOG_BG)],
        foreground=[("active", U_TEXT)],
    )
