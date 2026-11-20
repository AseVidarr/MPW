#define AppVersion "2.2.0"
#define Root AddBackslash(SourcePath) + ".."
[Setup]
AppId={{A7C8E6D3-3D46-48A9-B2E7-62B1877F91C1}
AppName=Music Production Workstation
AppVersion={#AppVersion}
DefaultDirName={autopf}\Music Production Workstation
DefaultGroupName=Music Production Workstation
OutputDir={#Root}\dist
OutputBaseFilename=MPW_Setup_v2.2.0_RC2
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayName=Music Production Workstation
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64os
CloseApplications=yes
CloseApplicationsFilter=MPW.exe
; Inno Setup Restart Manager fragt bei laufender MPW.exe vor dem Schliessen nach.
; Bei Ablehnung nicht gewaltsam beenden; Setup kann die Installation abbrechen.
RestartApplications=no
[Files]
Source: "{#Root}\dist\MPW\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Music Production Workstation"; Filename: "{app}\MPW.exe"
Name: "{group}\MPW im Browser"; Filename: "{app}\MPW-Web.exe"; Comment: "MPW lokal im Browser (gleiche Daten)"
Name: "{autodesktop}\Music Production Workstation"; Filename: "{app}\MPW.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Desktop-Verknüpfung erstellen"; Flags: unchecked
[Run]
Filename: "{app}\MPW.exe"; Description: "MPW starten"; Flags: nowait postinstall skipifsilent
; No data paths, registry data locators, or media directories are touched by setup/uninstall.
