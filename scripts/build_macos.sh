#!/usr/bin/env bash
# 在 macOS 本机生成 PdfTools.app（Docker 无法提供 macOS 基础镜像，必须本机打包）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "请在 macOS 上执行本脚本。" >&2
  exit 1
fi

python3 -m venv .venv-build
# shellcheck disable=SC1091
source .venv-build/bin/activate
pip install -U pip
pip install -r requirements.txt

pyinstaller \
  --noconfirm --clean \
  --windowed \
  --name PdfTools \
  --osx-bundle-identifier "com.local.pdftools" \
  --hidden-import=pdfgui.tabs.watermark \
  --hidden-import=pdfgui.tabs.image_export \
  --hidden-import=pdfgui.watermark_pdf \
  --hidden-import=pdfgui.pdf_to_img \
  --collect-all pymupdf \
  pdf_gui.py

mkdir -p release
rm -rf release/PdfTools.app
cp -R dist/PdfTools.app release/
echo "已生成 release/PdfTools.app，可直接双击或拖入「应用程序」。"
