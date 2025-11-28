# DroxAI_Setup_Sync.ps1
# Runs a comprehensive synchronization and setup process:
# 1. Finds the project root directory.
# 2. Creates the .venv if it doesn't exist.
# 3. Activates the virtual environment.
# 4. Installs/updates all dependencies from requirements.txt.

# --- 1. Find Project Root ---
# Determines the script directory, then assumes the project root is one level up
# if executed from a subdirectory (like 'build'). 
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = (Get-Item $ScriptDir).Parent.FullName

# If running directly from the root, adjust.
if ((Get-ChildItem -Path "$ScriptDir\requirements.txt" -ErrorAction SilentlyContinue) -ne $null) {
    $ProjectRoot = $ScriptDir
}

$VenvPath = "$ProjectRoot\.venv"
$RequirementsPath = "$ProjectRoot\requirements.txt"

Write-Host "--- DroxAI Setup Synchronization ---" -ForegroundColor Yellow
Write-Host "Project Root Detected: $ProjectRoot" -ForegroundColor Cyan

# --- 2. Create Venv if missing ---
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating fresh .venv in $VenvPath" -ForegroundColor Magenta
    try {
        python -m venv $VenvPath
    } catch {
        Write-Host "âŒ ERROR: Failed to create Virtual Environment. Ensure Python 3.8+ is installed and in your PATH." -ForegroundColor Red
        exit 1
    }
}

# --- 3. Activate Venv ---
Write-Host "Activating .venv..." -ForegroundColor DarkGreen
# Note: Activation must be done using the call operator (&) to execute in the current scope
# We do this before installing dependencies so pip runs inside the venv.
. "$VenvPath\Scripts\Activate.ps1"

# --- 4. Install/Update Dependencies ---
if (-not (Test-Path $RequirementsPath)) {
    Write-Host "âŒ FATAL: requirements.txt not found at $RequirementsPath. Cannot install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "Installing/Updating dependencies from requirements.txt..." -ForegroundColor Blue
try {
    pip install --upgrade pip
    # Using 'install -r' handles new installs, updates, and synchronization.
    pip install -r $RequirementsPath
    Write-Host "âœ… Dependencies successfully synchronized." -ForegroundColor Green
} catch {
    Write-Host "âŒ ERROR: Failed to install Python dependencies. See error above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "DroxAI .venv ACTIVATED and Dependencies Synchronized" -ForegroundColor Green
Write-Host "Run 'python DroxAI_Launcher.py' to start the Autarch." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Note: The script exits here. The venv remains active in the current terminal session.
