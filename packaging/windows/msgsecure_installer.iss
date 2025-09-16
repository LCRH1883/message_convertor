; MsgSecure Windows Installer (Inno Setup)
#define AppName "MsgSecure"
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#ifndef AppFileVersion
  #define AppFileVersion AppVersion + ".0"
#endif
#define AppPublisher "MsgSecure Project"
#define AppURL "https://github.com/LCRH1883/message_convertor"
#define RepoRoot "..\\.."
#define BuildDir RepoRoot + "\\dist"
#define PortableExeName "msgsecure-win-gui.exe"
#define OutputBaseName "MsgSecure-" + AppVersion + "-setup"

[Setup]
AppId={{B27D5D71-035A-478C-8BEA-1A9AE2AA9B43}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#BuildDir}
OutputBaseFilename={#OutputBaseName}
LicenseFile={#RepoRoot}\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#PortableExeName}
VersionInfoVersion={#AppFileVersion}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#BuildDir}\{#PortableExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#RepoRoot}\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#RepoRoot}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#PortableExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#PortableExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#PortableExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
