# PDF 工具

基于 Tk 的桌面小工具，当前提供三项能力：

| 功能 | 说明 |
|------|------|
| **文字水印** | 为 PDF 叠加平铺文字水印（可调字号、透明度、角度、间距、灰度等），另存为新 PDF。 |
| **导出图片** | 将 PDF 按页导出为 PNG / JPG 等常见格式，可选页码范围与 DPI。 |
| **照片换底** | 使用 rembg 人像分割，将照片人物抠出后合成 **红 / 蓝 / 白** 纯色证件照风格背景，支持另存路径与默认命名（如 `原名_蓝底.png`）。 |

## 运行方式

```bash
pip install -r requirements.txt
python pdf_gui.py
```

- **照片换底**依赖 `rembg[cpu]`（CPU 版 onnxruntime）。分割模型默认放在 `pdfgui/rembg_models/`；若目录里没有 `.onnx` 文件，可在项目根目录执行 `python scripts/fetch_rembg_models.py` 下载到本地（便于离线使用）。
- 部分能力也可在项目根目录用模块方式调用，例如：`python -m pdfgui.watermark_pdf`、`python -m pdfgui.pdf_to_img`（见 `pdf_gui.py` 顶部注释）。

## 打包（可选）

在本机生成带依赖与模型的安装目录时：

```bash
pip install -r requirements.txt
python scripts/package_tools.py
```

产出在 `dist/tools`。发布流程见仓库内 GitHub Actions（`.github/workflows/release.yml`）。
