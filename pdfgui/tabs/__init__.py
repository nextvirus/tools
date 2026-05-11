"""
各功能以独立模块实现 `build_tab(app, notebook)`，并在 `TAB_BUILDERS` 中登记顺序。

新增功能：新建 `pdfgui/tabs/your_feature.py` 实现 `build_tab`，再在本文件 `TAB_BUILDERS` 追加即可。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from tkinter import ttk

from . import image_export, photo_background, watermark

if TYPE_CHECKING:
    from ..app import PdfToolsApp

TabBuilder = Callable[["PdfToolsApp", ttk.Notebook], None]

TAB_BUILDERS: Sequence[TabBuilder] = (
    watermark.build_tab,
    image_export.build_tab,
    photo_background.build_tab,
)


def mount_all_tabs(app: PdfToolsApp, notebook: ttk.Notebook) -> None:
    for build in TAB_BUILDERS:
        build(app, notebook)
