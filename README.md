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

产出在 `dist/tools`（内含 `tools.exe` 与 `_internal`，**必须同目录**，不能只复制单个 exe）。因照片换底依赖 rembg 整条链（onnxruntime、numpy、scipy、scikit-image、pymatting 等），**体积会明显变大**，属正常现象。

### Windows：安装包（推荐）

单独把 `tools.exe` 拷到别处而未带上同级 `_internal` 时，会报找不到 `python312.dll`（依赖与 Python 运行时在 `_internal` 内）。**推荐**使用 Inno 安装包，一键装到 `%LocalAppData%\Programs\pdf-tools` 并可选桌面快捷方式：

1. 先执行上面的 `python scripts/package_tools.py`。
2. 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)，或执行 `choco install innosetup -y`。
3. 在项目根目录执行：

```powershell
./scripts/build_windows_installer.ps1 -Version 0.2.0
```

生成 `dist/tools-windows-amd64-setup.exe`。GitHub Release 里也会附带该文件与便携 zip。

### Windows：便携 zip

解压 `tools-windows-amd64.zip` 后进入 **`tools` 文件夹**（与 `_internal` 同级）再双击 `tools.exe`。

发布流程见 `.github/workflows/release.yml`。
