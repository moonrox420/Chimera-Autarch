# CHIMERA NEXUS - Windows Installation Script
# Installs ALL real dependencies for production-grade AI system

Write-Host "ðŸš€ CHIMERA NEXUS v3.0 - Windows Installation" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "âœ“ Python version: $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "droxai-env")) {
  Write-Host "ðŸ“¦ Creating virtual environment..." -ForegroundColor Yellow
  python -m venv droxai-env
}

Write-Host "ðŸ”§ Activating virtual environment..." -ForegroundColor Yellow
& .\droxai-env\Scripts\Activate.ps1

Write-Host "ðŸ“¥ Upgrading pip and setuptools..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "ðŸ“¥ Installing core dependencies..." -ForegroundColor Yellow
Write-Host "Using Windows-optimized requirements (pre-built wheels only)..." -ForegroundColor Cyan

# Use Windows-specific requirements file
if (Test-Path "requirements_windows.txt") {
  pip install -r requirements_windows.txt
}
else {
  # Fallback: Install critical packages manually with version constraints
  Write-Host "Installing packages individually (safe mode)..." -ForegroundColor Yellow
    
  # Core packages
  pip install websockets aiosqlite numpy pyyaml pycryptodome
    
  # ML packages - use versions with pre-built wheels
  pip install "tensorflow>=2.16.0,<2.17.0" "scikit-learn>=1.4.0"
    
  # Cloud SDKs (optional)
  pip install boto3
    
  # Voice (optional)
  pip install openai-whisper pyttsx3 sounddevice
    
  # Federated learning
  pip install flwr grpcio
    
  # Utilities
  pip install psutil httpx watchdog
}

Write-Host ""
Write-Host "Note: Skipping Azure/GCP SDKs by default (uncomment in requirements_windows.txt if needed)" -ForegroundColor Cyan

Write-Host ""
Write-Host "ðŸ“¦ PyAudio Installation (for voice interface):" -ForegroundColor Cyan
Write-Host "  PyAudio requires manual installation on Windows." -ForegroundColor White
Write-Host ""
Write-Host "  Option 1 - Download precompiled wheel:" -ForegroundColor Yellow
Write-Host "    1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor White
Write-Host "    2. Download: PyAudio-0.2.14-cp312-cp312-win_amd64.whl" -ForegroundColor White
Write-Host "    3. Run: python -m pip install <path-to-wheel>.whl" -ForegroundColor White
Write-Host ""
Write-Host "  Option 2 - Install Microsoft C++ Build Tools:" -ForegroundColor Yellow
Write-Host "    https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor White
Write-Host ""
Write-Host "  Then run: python -m pip install pyaudio sounddevice" -ForegroundColor White
Write-Host ""

Write-Host ""
Write-Host "âœ… Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸ“Š System Status:" -ForegroundColor Cyan

python -c @"
import sys
print(f'  Python: {sys.version.split()[0]}')

try:
    import tensorflow as tf
    print(f'  TensorFlow: {tf.__version__} âœ…')
except:
    print('  TensorFlow: Not installed âŒ')

try:
    import sklearn
    print(f'  scikit-learn: {sklearn.__version__} âœ…')
except:
    print('  scikit-learn: Not installed âŒ')

try:
    import whisper
    print('  Whisper: Installed âœ…')
except:
    print('  Whisper: Not installed âŒ')

try:
    import pyttsx3
    print('  pyttsx3: Installed âœ…')
except:
    print('  pyttsx3: Not installed âŒ')

try:
    import boto3
    print(f'  boto3: {boto3.__version__} âœ…')
except:
    print('  boto3: Not installed âŒ')

try:
    import azure.mgmt.compute
    print('  Azure SDK: Installed âœ…')
except:
    print('  Azure SDK: Not installed âŒ')

try:
    import google.cloud.compute_v1
    print('  GCP SDK: Installed âœ…')
except:
    print('  GCP SDK: Not installed âŒ')
"@

Write-Host ""
Write-Host "ðŸŽ¯ Next Steps:" -ForegroundColor Cyan
Write-Host "1. For audio support, install PyAudio wheel manually" -ForegroundColor White
Write-Host "2. Configure cloud credentials (see INTEGRATION_GUIDE.md)" -ForegroundColor White
Write-Host "3. Test individual systems: python predictive_monitor.py" -ForegroundColor White
Write-Host "4. Start CHIMERA: python chimera_autarch.py" -ForegroundColor White
Write-Host "5. Access 3D dashboard: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "ðŸ“– Full guide: Get-Content INTEGRATION_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "ðŸ”¥ Ready to change the world!" -ForegroundColor Green

