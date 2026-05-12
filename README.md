# tools

基于 Tk 的桌面小工具，当前提供四项能力：

| 功能 | 说明 |
|------|------|
| **文字水印** | 为 PDF 叠加平铺文字水印（可调字号、透明度、角度、间距、灰度等），另存为新 PDF。 |
| **导出图片** | 将 PDF 按页导出为 PNG / JPG 等常见格式，可选页码范围与 DPI。 |
| **照片换底** | 使用 rembg 人像分割，将照片人物抠出后合成 **红 / 蓝 / 白** 纯色证件照风格背景，支持另存路径与默认命名（如 `原名_蓝底.png`）。 |
| **会议纪要** | 麦克风**分段录音**（`sounddevice`）→ 本地 **Vosk** 中文转写（离线），再用 **DeepSeek** 整理成纪要（需配置 API Key 与网络）。 |

## 运行方式

```bash
pip install -r requirements.txt
python pdf_gui.py
```

- **会议纪要**：录音转写使用本地 **Vosk**（中文 small 模型，Apache-2.0）；首次使用前请在项目根目录执行 `python scripts/fetch_vosk_cn_model.py` 下载模型（打包时 CI 会自动拉取）。**整理纪要**仍调用 DeepSeek API，需联网。配置写入 `%APPDATA%\tools\meeting_settings.json`（Windows）或 `~/.config/tools/`（其他系统）。
- **照片换底**依赖 `rembg[cpu]`（CPU 版 onnxruntime）。模型文件会打进安装包/绿色版目录（`pdfgui/photo/rembg_models` 下的 `.onnx`）；**第一次换底仍可能较慢**（加载 onnxruntime、读入 ONNX、首次推理），第二次起会快很多；程序启动后会在后台尝试预加载模型以缩短首次等待。
- 部分能力也可在项目根目录用模块方式调用，例如：`python -m pdfgui.pdf.watermark_pdf`、`python -m pdfgui.pdf.pdf_to_img`（见 `pdf_gui.py` 顶部注释）。

## 打包（可选）

在本机生成带依赖与模型的安装目录时：

```bash
pip install -r requirements.txt
python scripts/package_tools.py
```

产出在 `dist/tools`（内含 `tools.exe` 与 `_internal`，**必须同目录**，不能只复制单个 exe）。`package_tools.py` 会先拉取 **Vosk 中文模型**（`scripts/fetch_vosk_cn_model.py`），再跑 PyInstaller（含 `--add-data`）；构建结束后会**再整目录拷贝** `pdfgui/meeting/vosk_models/` 到 `dist` 下每个 `_internal/`，避免 Windows/Linux/macOS 上目录型 `--add-data` 未生效导致缺模型。运行时从 `sys._MEIPASS` 读取。打包结束后会校验 rembg 的 `.onnx` 与 Vosk 的 `am/final.mdl` 是否已在 `dist` 内；**缺失任一则失败退出**。因照片换底依赖 rembg 整条链（onnxruntime、numpy、scipy、scikit-image、pymatting 等），**体积会明显变大**；打包脚本已减少对 numpy/scipy/skimage 的重复 `collect-all` 并排除常见无关大包（如 matplotlib），在可运行前提下尽量缩小体积。

### Windows：安装包（推荐）

单独把 `tools.exe` 拷到别处而未带上同级 `_internal` 时，会报找不到 `python312.dll`（依赖与 Python 运行时在 `_internal` 内）。**推荐**使用 Inno 安装包，一键装到 `%LocalAppData%\Programs\tools` 并可选桌面快捷方式。安装向导中可选择 **安装类型**：「全部模块」或「仅核心（PDF 水印 + 导出图片）」；在自定义界面可分别勾选 **照片换底**、**会议纪要**。各组件旁显示的数字为 **解压后占用磁盘约值（MB）**，由 `scripts/stage_installer_components.py` 在打包后按文件路径归类统计，供参考。

1. 先执行上面的 `python scripts/package_tools.py`。
2. 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)，或执行 `choco install innosetup -y`。
3. 在项目根目录执行：

```powershell
./scripts/build_windows_installer.ps1 -Version 0.2.0
```

生成 `dist/tools-windows-amd64-setup.exe`（安装向导为**英文**，以便 GitHub Actions 等精简 Inno 环境也能编译）。GitHub Release 里也会附带该文件与便携 zip。

### Windows：便携 zip

解压 `tools-windows-amd64.zip` 后进入 **`tools` 文件夹**（与 `_internal` 同级）再双击 `tools.exe`。

### macOS：zip、pkg 与 dmg

- **`tools-macos.zip`**：里面是完整的 **`tools.app`**，解压后双击即可用（与很多人习惯的「dmg 里拖一个 app」**效果相同**，只是少了一层磁盘映像外壳）。
- **`tools-macos-selectable.pkg`**：苹果原生的**安装包向导**，用来实现「安装时勾选核心 / 换底 / 会议纪要」并显示各模块约占用体积；**不是 dmg**，因为 **`.pkg` 才支持**这种分组件安装流程。
- **`.dmg`**：本质是**磁盘映像**，常见用法是把 `.app` 放进 dmg 里方便用户拖到「应用程序」。本仓库 **CI 未自动生成 dmg**（避免多一步签名与体积）；若你需要 dmg，可在本机用 `hdiutil` 或 [create-dmg](https://github.com/create-dmg/create-dmg) 把解压出的 `tools.app` 打成镜像即可。

#### 可选模块安装包（.pkg）详情

Release 除 `tools-macos.zip` 外，还提供 **`tools-macos-selectable.pkg`**：安装器中会列出 **Core（必选）**、**Photo / 照片换底**、**Meeting / 会议纪要** 三个子包，可取消勾选不需要的模块；说明文字中的 MB 数为 **解压后约占用**，与 Windows 同源脚本统计。未安装的模块在应用内不会显示对应标签页。

本地构建：在 macOS 上先执行 `python scripts/package_tools.py`，再执行 `bash scripts/build_macos_modular_pkg.sh 0.2.0`（脚本内会再次执行 `stage_installer_components.py` 并写入与版本一致的 `distribution.xml`）。若仅双击 `.app` 使用便携 zip，则始终为完整功能。

发布流程见 `.github/workflows/release.yml`。
