@echo off
REM 在项目根目录执行：下载 rembg onnx、Vosk 中文模型后 PyInstaller 打包 dist\tools
cd /d "%~dp0.."
python scripts\package_tools.py
exit /b %ERRORLEVEL%
