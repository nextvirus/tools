; Inno Setup 6 — 将 dist\installer\win 下按模块拆分的目录合并安装到 {app}
; 构建：python scripts/package_tools.py（会生成 staging）后，再运行 build_windows_installer.ps1
; 命令行覆盖版本： ISCC /DMyAppVersion=0.2.0 tools_installer.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

#include "..\dist\installer\win\component_sizes.inc"

#define MyAppName "tools"
#define MyAppPublisher "tools"
#define MyAppExeName "tools.exe"

[Setup]
AppId={{B4E2C8D1-5F3A-4E9B-8C7D-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\tools
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=tools-windows-amd64-setup
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
CloseApplications=no
; 仅定义一个 iscustom 的 [Types]，避免出现 Full / Compact / Custom 下拉；安装逻辑等同「只选组件」
AlwaysShowComponentsList=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "custom"; Description: "Optional modules / 可选模块（主程序与运行底座将始终安装）"; Flags: iscustom

[Components]
; 不含 runtime：tools.exe 与运行底座见下方 [Files]（无 Components），始终安装，避免用户取消勾选后无主程序
Name: "pdf"; Description: "[1] PDF / 水印与导出图片 — PyMuPDF（约 {#SizePdfMB} MB）"; Types: custom
Name: "photo"; Description: "[2] Photo / 照片换底 — rembg + ONNX + portrait models（约 {#SizePhotoMB} MB）"; Types: custom
Name: "meeting"; Description: "[3] Meeting / 会议纪要 — microphone + Vosk offline Chinese ASR + DeepSeek tab（约 {#SizeMeetingMB} MB）"; Types: custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 运行底座始终安装（不写 Components），与 zip 完整包一致；仅 PDF / 照片 / 会议为可选模块
; 根目录 tools.exe 单独列出，避免仅用 runtime\* + recursesubdirs 时漏装主程序
Source: "..\dist\installer\win\runtime\tools.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\installer\win\runtime\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "tools.exe"
Source: "..\dist\installer\win\pdf\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: pdf
Source: "..\dist\installer\win\photo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: photo
Source: "..\dist\installer\win\meeting\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: meeting

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent skipifdoesntexist
