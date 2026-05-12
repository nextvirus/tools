# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('pdfgui/photo/rembg_models/u2net_human_seg.onnx', 'pdfgui/photo/rembg_models'), ('pdfgui/photo/rembg_models/u2net.onnx', 'pdfgui/photo/rembg_models'), ('pdfgui/meeting/vosk_models/vosk-model-small-cn-0.22', 'pdfgui/meeting/vosk_models')]
binaries = []
hiddenimports = ['pdfgui.tabs.watermark', 'pdfgui.tabs.image_export', 'pdfgui.tabs.photo_background', 'pdfgui.tabs.meeting_minutes', 'rembg.bg', 'rembg.session_factory', 'rembg.sessions.base', 'rembg.sessions.u2net', 'rembg.sessions.u2net_human_seg', 'onnxruntime', 'PIL._imagingtk', 'PIL._tkinter_finder', 'pdfgui.core.app', 'pdfgui.ui.theme', 'pdfgui.ui.widgets', 'pdfgui.pdf.watermark_pdf', 'pdfgui.pdf.pdf_to_img', 'pdfgui.photo.photo_bg', 'pdfgui.meeting.settings', 'pdfgui.meeting.deepseek', 'pdfgui.meeting.mic', 'pdfgui.meeting.vosk_config', 'scipy.io.wavfile', 'vosk']
tmp_ret = collect_all('pymupdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rembg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('onnxruntime')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pymatting')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pooch')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jsonschema')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tqdm')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sounddevice')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('vosk')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['E:\\pdf\\pdf_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'jupyter', 'IPython', 'pytest', 'doctest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tools',
)
