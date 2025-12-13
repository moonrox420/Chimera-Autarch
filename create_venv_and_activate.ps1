# create_venv_and_activate.ps1
# Run this in C:\Drox_AI\build or C:\Drox_AI â€” it will create .venv in the project root and activate it immediately

# Determine the project root directory.
# $PSScriptRoot is the directory containing this script.
# If running from 'build', .Parent.FullName moves up to the project root.
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName

# 1. Check if the virtual environment directory exists
if (-not (Test-Path "$ProjectRoot\.venv")) {
    Write-Host "Creating fresh .venv in $ProjectRoot" -ForegroundColor Cyan
    # Create the virtual environment
    python -m venv "$ProjectRoot\.venv"
}

# 2. Activate the virtual environment
# '&' is the call operator, necessary to execute the Activation script directly.
& "$ProjectRoot\.venv\Scripts\Activate.ps1"
Write-Host "DroxAI .venv ACTIVATED â€” ready to install or run" -ForegroundColor Green
