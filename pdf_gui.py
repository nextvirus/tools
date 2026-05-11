"""
PDF 小工具：文字水印、PDF 转图片。
界面：现代浅色扁平风格（白卡片 + 灰底 + 蓝色主操作），易读易点。

依赖: pip install -r requirements.txt
运行: python pdf_gui.py

实现位于 `pdfgui` 包：主题、通用控件、PDF 逻辑（`pdfgui.watermark_pdf` / `pdfgui.pdf_to_img`）、
各 `pdfgui/tabs/` 功能页；新增功能请在 `tabs/` 登记 `TAB_BUILDERS`。
命令行（在项目根目录执行）: `python -m pdfgui.watermark_pdf`、`python -m pdfgui.pdf_to_img`。
"""

from pdfgui import main

if __name__ == "__main__":
    main()
