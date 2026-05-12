"""
各功能以独立模块实现 `build_tab(app, notebook)`。

照片换底、会议纪要、PDF 水印与导出图片均依赖可选安装组件，由 `mount_all_tabs` 在探测通过后动态挂载。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from tkinter import ttk

if TYPE_CHECKING:
    from pdfgui.core.app import PdfToolsApp

TabBuilder = Callable[["PdfToolsApp", ttk.Notebook], None]

TAB_BUILDERS: Sequence[TabBuilder] = ()


def mount_all_tabs(app: "PdfToolsApp", notebook: ttk.Notebook) -> None:
    from pdfgui.runtime_modules import meeting_module_available, pdf_module_available, photo_module_available

    for build in TAB_BUILDERS:
        build(app, notebook)
    if pdf_module_available():
        from . import image_export, watermark

        watermark.build_tab(app, notebook)
        image_export.build_tab(app, notebook)
    if photo_module_available():
        from .photo_background import build_tab as build_photo_tab

        build_photo_tab(app, notebook)
    if meeting_module_available():
        from .meeting_minutes import build_tab as build_meeting_tab

        build_meeting_tab(app, notebook)
