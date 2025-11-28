# DroxAI_Run.ps1
# Simple script to launch the DroxAI Autarch application and open the dashboard.
# Prerequisite: Dependencies must be installed via DroxAI_Setup_Sync.ps1 first.

# Get the directory where this script resides (assumes project root or build folder)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = (Get-Item $ScriptDir).Parent.FullName

# Determine the actual location of the launcher script
$LauncherPath = Join-Path $ProjectRoot "DroxAI_Launcher.py"
if (-not (Test-Path $LauncherPath)) {
    # Assume launcher might be in the current script directory if run from root
    $LauncherPath = Join-Path $ScriptDir "DroxAI_Launcher.py"
}

Write-Host "ðŸš€ Launching DroxAI Autarch..." -ForegroundColor Cyan

if (-not (Test-Path $LauncherPath)) {
    Write-Host "âŒ FATAL: DroxAI_Launcher.py not found. Run DroxAI_Setup_Sync.ps1 first." -ForegroundColor Red
    exit 1
}

# Execute the launcher. The DroxAI_Launcher.py script will:
# 1. Load configuration (getting host:3000 and ws:3000)
# 2. Start the Python backend (chimera_autarch_v4_tuned.py)
# 3. Automatically open the browser to http://127.0.0.1:3000
try {
    # Use the call operator to ensure the script runs and handles process correctly
    & python $LauncherPath
} catch {
    Write-Host "âŒ ERROR: DroxAI Launcher failed to start." -ForegroundColor Red
    Write-Host "Check your logs folder and ensure the .venv is active/installed." -ForegroundColor Yellow
    exit 1
}
