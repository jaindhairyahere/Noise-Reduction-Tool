# Specify your script and filenames
$scriptName = "noise_reduction_tool.py"
$distDir = ".\dist"
$packageDir = ".\package"
$exeName = "noise_reduction_tool.exe"
$iconFile = "noise_reduction_tool.ico"

# Clean old build and dist folders
if (Test-Path $distDir) { Remove-Item -Recurse -Force $distDir }
if (Test-Path $packageDir) { Remove-Item -Recurse -Force $packageDir }
if (Test-Path ".\build") { Remove-Item -Recurse -Force ".\build" }

# Build executable with icon embedded
Write-Host "Building executable with PyInstaller and icon..."
python -m PyInstaller --onefile --windowed --icon=$iconFile $scriptName

# Prepare package folder and copy all necessary files
Write-Host "Preparing package files..."
New-Item -ItemType Directory -Force -Path $packageDir
Copy-Item -Path "$distDir\$exeName" -Destination $packageDir
Copy-Item -Path $scriptName -Destination $packageDir
Copy-Item -Path ".\README.txt" -Destination $packageDir
Copy-Item -Path ".\$iconFile" -Destination $packageDir

# Build installer with Inno Setup
Write-Host "Building installer executable with Inno Setup..."
$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-Not (Test-Path $isccPath)) {
    Write-Warning "Inno Setup Compiler not found at $isccPath. Please install or update path in script."
    exit 1
}
& "$isccPath" ".\install.iss"

Write-Host "Installer build finished. Check 'install.exe' in project folder."
