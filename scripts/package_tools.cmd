@echo off
REM 在项目根目录执行：先下载 onnx 到 pdfgui\rembg_models，再打包进 dist\tools
cd /d "%~dp0.."
python scripts\package_tools.py
exit /b %ERRORLEVEL%
