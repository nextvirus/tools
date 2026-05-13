"""
各功能以独立模块实现 `build_tab(app, notebook)`。

照片换底、会议纪要、PDF 水印与导出图片均依赖可选安装组件；可渐进挂载（各 `mount_*` 带防重入），
或由 `mount_all_tabs` 根据完整 `OptionalModulesProbe` 一次挂载。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from tkinter import ttk

from pdfgui.runtime_modules import OptionalModulesProbe

if TYPE_CHECKING:
    from pdfgui.core.app import PdfToolsApp

TabBuilder = Callable[["PdfToolsApp", ttk.Notebook], None]

TAB_BUILDERS: Sequence[TabBuilder] = ()


def mount_pdf_tabs(app: "PdfToolsApp", notebook: ttk.Notebook) -> None:
    if getattr(app, "_mount_pdf_tabs_done", False):
        return
    app._mount_pdf_tabs_done = True
    from . import image_export, watermark

    watermark.build_tab(app, notebook)
    image_export.build_tab(app, notebook)


def mount_photo_tab(app: "PdfToolsApp", notebook: ttk.Notebook) -> None:
    if getattr(app, "_mount_photo_tab_done", False):
        return
    app._mount_photo_tab_done = True
    from .photo_background import build_tab as build_photo_tab

    build_photo_tab(app, notebook)


def mount_meeting_tab(app: "PdfToolsApp", notebook: ttk.Notebook) -> None:
    if getattr(app, "_mount_meeting_tab_done", False):
        return
    app._mount_meeting_tab_done = True
    from .meeting_minutes import build_tab as build_meeting_tab

    build_meeting_tab(app, notebook)


def mount_all_tabs(app: "PdfToolsApp", notebook: ttk.Notebook, probe: OptionalModulesProbe) -> None:
    for build in TAB_BUILDERS:
        build(app, notebook)
    if probe.pdf:
        mount_pdf_tabs(app, notebook)
    if probe.photo:
        mount_photo_tab(app, notebook)
    if probe.meeting:
        mount_meeting_tab(app, notebook)
