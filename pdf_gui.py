"""
tools：文字水印、PDF 转图片、照片换底、会议纪要（DeepSeek）。
界面：现代浅色扁平风格（白卡片 + 灰底 + 蓝色主操作），易读易点。

依赖: pip install -r requirements.txt
运行: python pdf_gui.py

实现位于 `pdfgui` 包：按子目录分模块（`pdfgui/ui`、`pdfgui/pdf`、`pdfgui/photo`、`pdfgui/meeting`、`pdfgui/core`、`pdfgui/tabs`）。
命令行（在项目根目录执行）: `python -m pdfgui.pdf.watermark_pdf`、`python -m pdfgui.pdf.pdf_to_img`。
"""

from pdfgui import main

if __name__ == "__main__":
    main()
