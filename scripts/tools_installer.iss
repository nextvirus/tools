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
; 不设 [Types] 时仍显示「选择组件」页，逐项勾选各模块（Inno 会隐式创建 full 类型）
AlwaysShowComponentsOnSelectiveInstall=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Components]
Name: "runtime"; Description: "[1] Runtime / 运行环境 — app shell + shared libraries（约 {#SizeRuntimeMB} MB）"; Flags: fixed
Name: "pdf"; Description: "[2] PDF / 水印与导出图片 — PyMuPDF（约 {#SizePdfMB} MB）"
Name: "photo"; Description: "[3] Photo / 照片换底 — rembg + ONNX + portrait models（约 {#SizePhotoMB} MB）"
Name: "meeting"; Description: "[4] Meeting / 会议纪要 — microphone + Vosk offline Chinese ASR + DeepSeek tab（约 {#SizeMeetingMB} MB）"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\installer\win\runtime\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: runtime
Source: "..\dist\installer\win\pdf\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: pdf
Source: "..\dist\installer\win\photo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: photo
Source: "..\dist\installer\win\meeting\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: meeting

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
