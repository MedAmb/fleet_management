; build/windows/installer.iss  (UTF-8 w/o BOM)
[Setup]
AppId={{9C38A7E9-F7B2-42B4-9A3A-123456789ABC}}    ; keep constant for upgrades
AppName=Fleet Manager
AppVersion={#MyVersion}
AppPublisher=AMB Software
DefaultDirName={autopf}\FleetManager
DefaultGroupName=Fleet Manager
Compression=lzma
SolidCompression=yes
OutputBaseFilename=FleetManager-Setup
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=yes

[Files]
Source: ""..\..\dist\FleetManager.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Fleet Manager"; Filename: "{app}\FleetManager.exe"
Name: "{commondesktop}\Fleet Manager"; Filename: "{app}\FleetManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le bureau"; Flags: unchecked
