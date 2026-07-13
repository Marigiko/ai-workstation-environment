# Create Windows shortcuts for AI Workstation
# Run from PowerShell: .\create-shortcut.ps1
param(
    [string]$IconPath = "$PSScriptRoot\icon.ico"
)

$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = [Environment]::GetFolderPath("StartMenu")
$WshShell = New-Object -ComObject WScript.Shell

# Desktop shortcut - Invisible VBS launcher
$shortcut1 = $WshShell.CreateShortcut("$desktop\Terax AI Workstation.lnk")
$shortcut1.TargetPath = "wscript.exe"
$shortcut1.Arguments = "//nologo `"$PSScriptRoot\launch-terax.vbs`""
$shortcut1.WindowStyle = 7
$shortcut1.Description = "Launch Terax AI Workstation"
$shortcut1.WorkingDirectory = "%USERPROFILE%"
if (Test-Path $IconPath) {
    $shortcut1.IconLocation = "$IconPath,0"
}
$shortcut1.Save()

# Start Menu shortcut
$programsDir = "$startMenu\Programs\AI WorkStation"
if (-not (Test-Path $programsDir)) {
    New-Item -ItemType Directory -Path $programsDir -Force | Out-Null
}
$shortcut2 = $WshShell.CreateShortcut("$programsDir\Terax AI Workstation.lnk")
$shortcut2.TargetPath = "wscript.exe"
$shortcut2.Arguments = "//nologo `"$PSScriptRoot\launch-terax.vbs`""
$shortcut2.WindowStyle = 7
$shortcut2.Description = "Launch Terax AI Workstation"
$shortcut2.WorkingDirectory = "%USERPROFILE%"
if (Test-Path $IconPath) {
    $shortcut2.IconLocation = "$IconPath,0"
}
$shortcut2.Save()

Write-Host "Shortcuts created:" -ForegroundColor Green
Write-Host "  Desktop:    $desktop\Terax AI Workstation.lnk"
Write-Host "  Start Menu: $programsDir\Terax AI Workstation.lnk"
Write-Host ""
Write-Host "NOTE: Copy an icon.ico to $PSScriptRoot for the icon to work."
