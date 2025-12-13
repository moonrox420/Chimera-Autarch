Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = "C:\Drox_AI"
$Venv = "$Root\AUTARCH\Scripts\python.exe"
$Log = "$Root\RESTORE_LOG.txt"

"=== CHIMERA AUTARCH v3 RESTORE $(Get-Date) ===" | Out-File $Log -Encoding utf8 -Force
function Log { param([string]$m); "[$(Get-Date -f 'HH:mm:ss')] $m" | Out-File $Log -Encoding utf8 -Append }

try {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Drox_AI*"} | Stop-Process -Force
    Log "Old processes killed"

    & $Venv -m pip uninstall -y fastapi uvicorn websockets pydantic python-dotenv rich 2>&1 | Out-Host
    & $Venv -m pip install --no-cache-dir --force-reinstall fastapi uvicorn[standard] websockets pydantic python-dotenv rich ollama --quiet
    Log "Dependencies nuked & rebuilt"

    Get-ChildItem $Root -Recurse -Include *.py | Where-Object {$_.FullName -notlike "*\AUTARCH\*"} | ForEach-Object {
        (Get-Content $_.FullName -Raw) -replace "`r`n","`n" | Set-Content $_.FullName -Encoding utf8
    }
    Log "Line endings fixed"

    $files = @{
        "$Root\chimera_autarch.py" = @'
from fastapi import APIRouter
from personality_engine import PersonalityEngine
router = APIRouter()
engine = PersonalityEngine()
@router.get("/core")
async def core_status():
    return {"heart":"online","personality":engine.current_profile(),"status":"operational"}
'@
        "$Root\personality_engine.py" = @'
class PersonalityEngine:
    def __init__(self): self.profile = "chimera-autarch-default"
    def current_profile(self): return self.profile
'@
    }
    foreach ($path in $files.Keys) {
        $files[$path] | Set-Content $path -Encoding utf8
        Log "Restored $path"
    }

    if (-not (Test-Path "$Root\main.py")) { throw "main.py missing" }
    $main = Get-Content "$Root\main.py" -Raw
    if ($main -notmatch "FastAPI") { "from fastapi import FastAPI`napp = FastAPI()" | Set-Content "$Root\main.py" }
    if ($main -notmatch "chimera_router") {
        Add-Content "$Root\main.py" "`nfrom chimera_autarch import router as chimera_router`napp.include_router(chimera_router, prefix='/chimera')"
    }
    Log "main.py validated & linked"

    Log "Launching Chimera Autarch..."
    Start-Process "http://localhost:3000"
    & $
