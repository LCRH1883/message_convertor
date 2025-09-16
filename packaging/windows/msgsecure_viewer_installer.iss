; MsgSecure Viewer Windows Installer (Inno Setup)
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
#define BrandingDir RepoRoot + "\\branding"
#define ViewerAssetDir RepoRoot + "\\packaging\\windows\\assets"
#define ViewerDistDir RepoRoot + "\\dist\\viewer\\" + AppVersion
#define ViewerPublishDir ViewerDistDir + "\\publish"
#define OutputBaseName "MsgSecure-" + AppVersion + "-setup"

[Setup]
AppId={{6E531480-D216-4225-980F-CD1CE8A74AAA}}
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
OutputDir={#ViewerDistDir}
OutputBaseFilename={#OutputBaseName}
SetupIconFile={#BrandingDir}\msgsecure_logo.ico
LicenseFile={#ViewerAssetDir}\MSGSecure-Viewer-EULA.txt
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\MsgSecure.exe
SetupLogging=yes
VersionInfoVersion={#AppFileVersion}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#ViewerPublishDir}\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#RepoRoot}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ViewerAssetDir}\MSGSecure-Viewer-EULA.txt"; DestDir: "{app}"; DestName: "MSGSecure-Viewer-EULA.txt"; Flags: ignoreversion
Source: "{#ViewerAssetDir}\MSGSecure-Viewer-README.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\MsgSecure.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\MsgSecure.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MsgSecure.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
