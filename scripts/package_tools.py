#!/usr/bin/env python3
"""
本地 / CI 统一打包入口：拉取 rembg ONNX、Vosk 中文模型，再 PyInstaller 打进 dist。

大文件不入 Git；CI / 本机打包前由脚本下载并随 --add-data 打入安装包。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# 与 pdfgui.meeting.vosk_config.VOSK_CN_MODEL_NAME 保持一致
_VOSK_CN_MODEL = "vosk-model-small-cn-0.22"

# rembg 会拉 onnxruntime / numpy / scipy / skimage 等；collect rembg + onnxruntime 后由 PyInstaller 分析子依赖。
# 不再对 numpy/scipy/skimage 单独 collect-all，可显著减小重复打入的体积（若换底运行报错再恢复）。
_COLLECT_ALL_PACKAGES = (
    "pymupdf",
    "rembg",
    "onnxruntime",
    "pymatting",
    "pooch",
    "jsonschema",
    "tqdm",
    "sounddevice",
    "vosk",
)

# 常见误收集的大型/测试模块，排除后通常不影响本工具
_PYINSTALLER_EXCLUDES = (
    "matplotlib",
    "pandas",
    "jupyter",
    "IPython",
    "pytest",
    "doctest",
)

_HIDDEN_IMPORTS = (
    "rembg.bg",
    "rembg.session_factory",
    "rembg.sessions.base",
    "rembg.sessions.u2net",
    "rembg.sessions.u2net_human_seg",
    "onnxruntime",
    "PIL._imagingtk",
    "PIL._tkinter_finder",
    "pdfgui.core.app",
    "pdfgui.ui.theme",
    "pdfgui.ui.widgets",
    "pdfgui.pdf.watermark_pdf",
    "pdfgui.pdf.pdf_to_img",
    "pdfgui.photo.photo_bg",
    "pdfgui.meeting.settings",
    "pdfgui.meeting.deepseek",
    "pdfgui.meeting.mic",
    "pdfgui.meeting.vosk_config",
    "pdfgui.runtime_modules",
    "scipy.io.wavfile",
    "vosk",
)


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def _copy_vosk_models_into_dist(repo: Path) -> None:
    """将源码树中的 vosk_models 同步进 dist 内每个 _internal（Win/Linux/macOS 通用）。

    部分环境下 PyInstaller 对整目录 --add-data 不可靠，构建后强制复制，避免校验与运行时缺模型。
    """
    src = repo / "pdfgui" / "meeting" / "vosk_models"
    if not (src / _VOSK_CN_MODEL / "am" / "final.mdl").is_file():
        return
    dist = repo / "dist"
    if not dist.is_dir():
        return
    internal_roots = sorted({p for p in dist.rglob("_internal") if p.is_dir()})
    if not internal_roots:
        print("错误: dist 下未找到 _internal 目录，无法同步 Vosk（需 PyInstaller onedir / macOS .app 布局）。", file=sys.stderr)
        raise SystemExit(1)
    for internal in internal_roots:
        dst = internal / "pdfgui" / "meeting" / "vosk_models"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    print(f"已同步 Vosk 模型到 {len(internal_roots)} 个 _internal 目录。")


def main() -> int:
    _reconfigure_stdio()
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    subprocess.check_call(
        [sys.executable, str(ROOT / "scripts" / "fetch_rembg_models.py")],
        cwd=ROOT,
        env=env,
    )
    subprocess.check_call(
        [sys.executable, str(ROOT / "scripts" / "fetch_vosk_cn_model.py")],
        cwd=ROOT,
        env=env,
    )

    hseg = ROOT / "pdfgui" / "photo" / "rembg_models" / "u2net_human_seg.onnx"
    u2 = ROOT / "pdfgui" / "photo" / "rembg_models" / "u2net.onnx"
    if not hseg.is_file() or not u2.is_file():
        print("缺少 onnx，无法打包。", file=sys.stderr)
        return 1

    vosk_mdl = ROOT / "pdfgui" / "meeting" / "vosk_models" / _VOSK_CN_MODEL / "am" / "final.mdl"
    if not vosk_mdl.is_file():
        print("缺少 Vosk 中文模型，无法打包。", file=sys.stderr)
        return 1

    sep = ";" if sys.platform == "win32" else ":"
    add_human = f"pdfgui/photo/rembg_models/u2net_human_seg.onnx{sep}pdfgui/photo/rembg_models"
    add_u2 = f"pdfgui/photo/rembg_models/u2net.onnx{sep}pdfgui/photo/rembg_models"
    vosk_src = Path("pdfgui/meeting/vosk_models") / _VOSK_CN_MODEL
    # 使用相对仓库根的路径，避免 macOS BUNDLE 下绝对路径偶发未打进 TOC；cwd 已为 ROOT
    add_vosk = f"{vosk_src.as_posix()}{sep}pdfgui/meeting/vosk_models"

    head: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
    ]
    if sys.platform == "darwin":
        head += ["--osx-bundle-identifier", "com.tools.app"]

    tail: list[str] = [
        "--name",
        "tools",
        "--hidden-import=pdfgui.tabs.watermark",
        "--hidden-import=pdfgui.tabs.image_export",
        "--hidden-import=pdfgui.tabs.photo_background",
        "--hidden-import=pdfgui.tabs.meeting_minutes",
    ]
    for mod in _HIDDEN_IMPORTS:
        tail.append(f"--hidden-import={mod}")
    for pkg in _COLLECT_ALL_PACKAGES:
        tail.extend(["--collect-all", pkg])
    for mod in _PYINSTALLER_EXCLUDES:
        tail.append(f"--exclude-module={mod}")
    tail.extend(
        [
            "--add-data",
            add_human,
            "--add-data",
            add_u2,
            "--add-data",
            add_vosk,
            str(ROOT / "pdf_gui.py"),
        ]
    )
    cmd = head + tail

    print("运行:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT, env=env)

    _copy_vosk_models_into_dist(ROOT)

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "verify_bundled_rembg_models.py")], cwd=ROOT, env=env)
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "verify_bundled_vosk_models.py")], cwd=ROOT, env=env)
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "stage_installer_components.py"),
            "--platform",
            sys.platform,
        ],
        cwd=ROOT,
        env=env,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
