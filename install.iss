[Setup]
AppName=Noise Reduction Tool
AppVersion=1.0
AppPublisher=Dhairya Jain
AppPublisherURL=https://jaindhairyahere.github.io
DefaultDirName={pf}\NoiseReductionTool
DefaultGroupName=Noise Reduction Tool
OutputBaseFilename=install
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=noise_reduction_tool.ico

[Files]
Source: "package\noise_reduction_tool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "package\noise_reduction_tool.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "package\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "package\noise_reduction_tool.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Noise Reduction Tool"; Filename: "{app}\noise_reduction_tool.exe"; IconFilename: "{app}\noise_reduction_tool.ico"
Name: "{commondesktop}\Noise Reduction Tool"; Filename: "{app}\noise_reduction_tool.exe"; IconFilename: "{app}\noise_reduction_tool.ico"

Name: "{group}\Support Chat Link"; Filename: "explorer.exe"; Parameters: "https://www.perplexity.ai/search/i-have-an-mp4-video-file-howev-dzZBTQhnQ6i.ppfwfGHW1A"
Name: "{commondesktop}\Support Chat Link"; Filename: "explorer.exe"; Parameters: "https://www.perplexity.ai/search/i-have-an-mp4-video-file-howev-dzZBTQhnQ6i.ppfwfGHW1A"

[Run]
Filename: "{app}\noise_reduction_tool.exe"; Description: "Launch Noise Reduction Tool"; Flags: nowait postinstall skipifsilent
