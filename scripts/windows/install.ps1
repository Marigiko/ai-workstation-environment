#Requires -RunAsAdministrator
<#
.SYNOPSIS
    AI Workstation - Windows Installer
.DESCRIPTION
    Installs the complete AI Workstation environment on Windows via WSL2.
    - Verifies WSL2 and Docker
    - Runs the Linux bootstrap inside WSL
    - Creates desktop shortcut
    - Configures auto-start gateway service
.NOTES
    Run by right-clicking and selecting "Run with PowerShell" or from admin PowerShell:
    PS> .\install.ps1
#>

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

$GITHUB_TOKEN = $env:AIWSL_GITHUB_TOKEN
$Distro = $env:WSL_DISTRO -or "Ubuntu-24.04"

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Get-WSLStatus {
    try {
        $wslOutput = wsl --status 2>&1
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# ============================================================
# 1. Check Prerequisites
# ============================================================
Write-Step "Checking prerequisites"

if (-not (Test-Command "wsl")) {
    Write-Host "WSL not found. Installing..." -ForegroundColor Yellow
    wsl --install --no-distribution
    Write-Host "WSL installed. Please restart your computer and run this installer again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$wslOk = Get-WSLStatus
if (-not $wslOk) {
    Write-Host "WSL is installed but not initialized. Starting WSL..." -ForegroundColor Yellow
    wsl --set-default-version 2
}

# ============================================================
# 2. Ensure distro exists
# ============================================================
Write-Step "Checking WSL distribution"

$distros = wsl --list --quiet 2>&1
if ($distros -notcontains $Distro) {
    Write-Host "Distro '$Distro' not found. Installing from Microsoft Store..." -ForegroundColor Yellow
    wsl --install -d $Distro --no-launch
    Write-Host "Please complete WSL setup (create username/password), then re-run this installer." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# ============================================================
# 3. Check Docker
# ============================================================
Write-Step "Checking Docker"

$dockerInWSL = wsl -d $Distro -- bash -c "command -v docker && docker info" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker not found in WSL. Installing Docker Desktop with WSL2 backend is recommended." -ForegroundColor Yellow
    Write-Host "Download from: https://docs.docker.com/desktop/windows-install/" -ForegroundColor Yellow
    $installDocker = Read-Host "Press 'Y' to open Docker download page, or any other key to continue without Docker"
    if ($installDocker -eq "Y" -or $installDocker -eq "y") {
        Start-Process "https://docs.docker.com/desktop/windows-install/"
    }
}

# ============================================================
# 4. Configure git credentials
# ============================================================
Write-Step "Configuring Git"

if ($GITHUB_TOKEN) {
    wsl -d $Distro -- bash -c @"
        git config --global credential.helper store
        git config --global init.defaultBranch main
        git config --global pull.rebase false
        echo 'https://oauth2:${GITHUB_TOKEN}@github.com' >> ~/.git-credentials
        echo 'Git credentials configured.'
"@
} else {
    Write-Host "Skipping git config (set AIWSL_GITHUB_TOKEN env var to auto-configure)" -ForegroundColor DarkGray
}

# ============================================================
# 5. Clone and bootstrap ai-workstation-environment
# ============================================================
Write-Step "Installing AI Workstation Environment"

wsl -d $Distro -- bash -c @"
    set -euo pipefail

    # Clone environment repo if missing
    if [ ! -d ~/ai-workstation-environment ]; then
        git clone https://github.com/keyz/ai-workstation-environment.git ~/ai-workstation-environment
    fi

    cd ~/ai-workstation-environment

    # Bootstrap with desktop profile
    echo 'Running bootstrap...'
    ./bootstrap bootstrap --profile desktop
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "Bootstrap failed. Check output above for errors." -ForegroundColor Red
    exit 1
}

# ============================================================
# 6. Create desktop shortcut
# ============================================================
Write-Step "Creating desktop shortcut"

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Terax AI Workstation.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wsl.exe"
$shortcut.Arguments = "-d $Distro -- bash -c 'cd ~/ai-workstation && docker compose -f infrastructure/compose/docker-compose.prod.yml up -d && terax'"
$shortcut.WindowStyle = 7
$shortcut.Description = "Launch Terax AI Workstation"
$shortcut.WorkingDirectory = "%USERPROFILE%"
# $shortcut.IconLocation = "$PSScriptRoot\icon.ico,0"
$shortcut.Save()

Write-Host "Shortcut created: $shortcutPath" -ForegroundColor Green

# ============================================================
# 7. Create Task Scheduler entry for auto-start
# ============================================================
Write-Step "Configuring auto-start gateway"

$taskName = "AI WorkStation Gateway"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action = New-ScheduledTaskAction `
    -Execute "wsl.exe" `
    -Argument "-d $Distro -- bash -c 'cd ~/ai-workstation && docker compose -f infrastructure/compose/docker-compose.prod.yml up -d'"

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Auto-start AI Workstation Gateway on login"

Write-Host "Auto-start configured: Gateway starts on Windows login." -ForegroundColor Green

# ============================================================
# Done
# ============================================================
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Desktop:  Terax AI Workstation shortcut"
Write-Host "  Gateway:  http://localhost:8000"
Write-Host "  Grafana:  http://localhost:3000"
Write-Host ""
Write-Host "  Double-click the shortcut to launch Terax."
Write-Host ""

$launchNow = Read-Host "Launch Terax now? (Y/N)"
if ($launchNow -eq "Y" -or $launchNow -eq "y") {
    Write-Host "Launching Terax..." -ForegroundColor Cyan
    Set-Location $PSScriptRoot
    cscript //nologo launch-terax.vbs
}
