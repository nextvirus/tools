#Requires -Version 5.1
<#
.SYNOPSIS
  在已存在 dist\tools（PyInstaller 输出）的前提下，用 Inno Setup 生成 Windows 安装包。
.DESCRIPTION
  输出：dist\tools-windows-amd64-setup.exe（与 tools.exe、_internal 分离：用户运行安装包，程序装到「开始」菜单目录，勿只复制单个 exe）。
  需先安装 Inno Setup 6：https://jrsoftware.org/isdl.php
  或：choco install innosetup -y
#>
param(
    [string]$Version = "0.0.0"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $Root "dist\tools\tools.exe"))) {
    Write-Error "未找到 dist\tools\tools.exe。请先在仓库根目录执行: python scripts/package_tools.py"
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python (Join-Path $Root "scripts\verify_bundled_rembg_models.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python (Join-Path $Root "scripts\verify_bundled_vosk_models.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python (Join-Path $Root "scripts\stage_installer_components.py") --platform win32
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$candidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$iscc = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    Write-Error "未找到 ISCC.exe。请安装 Inno Setup 6，或执行: choco install innosetup -y"
}

$ver = $Version.Trim()
if ($ver -match '^v(\d+\.\d+\.\d+.*)$') { $ver = $Matches[1] }
if ($ver -notmatch '^\d') { $ver = "0.0.0" }

& $iscc "/DMyAppVersion=$ver" (Join-Path $PSScriptRoot "tools_installer.iss")
if (-not (Test-Path (Join-Path $Root "dist\tools-windows-amd64-setup.exe"))) {
    Write-Error "安装包未生成，请检查 Inno 编译日志。"
}
Write-Host "OK: dist\tools-windows-amd64-setup.exe"
