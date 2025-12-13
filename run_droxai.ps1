# Launch Drox AI
Set-Location "C:\Drox_AI"
& ".\.venv\Scripts\Activate.ps1"

Write-Host "🚀 Starting Drox AI..." -ForegroundColor Cyan
Write-Host "🔗 Backend: Qwen3 Coder 30B on http://localhost:8080" -ForegroundColor Green

python -m src.droxai_root.chimera_autarch
