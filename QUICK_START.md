# CHIMERA AUTARCH - Quick Start Guide

## 🚀 Launch Commands (Copy & Paste)

### Option 1: Standard Launch (Recommended)
```powershell
cd C:\Drox_AI
.\droxai-env\Scripts\Activate.ps1
python src\chimera\chimera_main.py
```

### Option 2: One-Line Launch
```powershell
cd C:\Drox_AI && .\droxai-env\Scripts\Activate.ps1 && python src\chimera\chimera_main.py
```

### Option 3: Background Launch (keeps running)
```powershell
cd C:\Drox_AI
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\droxai-env\Scripts\Activate.ps1; python src\chimera\chimera_main.py"
```

---

## 📋 Step-by-Step Instructions

### 1. Open PowerShell
- Press `Win + X`
- Click "Windows PowerShell" or "Terminal"

### 2. Navigate to Project
```powershell
cd C:\Drox_AI
```

### 3. Activate Virtual Environment
```powershell
.\droxai-env\Scripts\Activate.ps1
```
✅ You should see `(droxai-env)` appear before your prompt

### 4. Start CHIMERA
```powershell
python src\chimera\chimera_main.py
```

### 5. Access Dashboard
Open your browser and go to:
```
http://localhost:3000
```

---

## ⚡ Quick Actions

### Stop the Server
Press `Ctrl + C` in the terminal

### Restart the Server
1. Stop with `Ctrl + C`
2. Press `↑` (up arrow) to recall last command
3. Press `Enter`

### Check if Running
```powershell
netstat -ano | findstr ":3000"
```

---

## 🎯 What You Should See

### Terminal Output:
```
[NOTE] Signal handlers unavailable on Windows (use Ctrl+C for shutdown)
Dashboard → http://0.0.0.0:3000
WebSocket → ws://0.0.0.0:3001
CHIMERA AUTARCH v3.0 — WICKEDLY BADASS EDITION — ONLINE
Press Ctrl+C for graceful shutdown
```

### Browser Dashboard:
- Green cyberpunk theme
- System Status card showing "● ONLINE"
- WebSocket test buttons
- Live metrics and console

---

## 🐛 Troubleshooting

### "Port already in use"
```powershell
# Find process using port 3000
netstat -ano | findstr ":3000"
# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

### "Cannot find path"
Make sure you're in the right directory:
```powershell
cd C:\Drox_AI
dir src\chimera\chimera_main.py
```

### "Module not found"
Reinstall dependencies:
```powershell
.\droxai-env\Scripts\Activate.ps1
pip install aiohttp websockets
```

### Virtual Environment Not Activating
```powershell
# Allow script execution (run as Admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎮 Testing the Dashboard

1. Open `http://localhost:3000`
2. Click **"Connect"** button
3. Type a message in the input box
4. Click **"Send"**
5. Watch the console show your message echo

---

## 📦 Create Desktop Shortcut

### Windows Shortcut
1. Right-click Desktop → New → Shortcut
2. Target:
```
powershell.exe -ExecutionPolicy Bypass -File "C:\Drox_AI\launch.ps1"
```
3. Name it "Start CHIMERA"

### Create launch.ps1
```powershell
# Save this as C:\Drox_AI\launch.ps1
Set-Location C:\Drox_AI
.\droxai-env\Scripts\Activate.ps1
python src\chimera\chimera_main.py
pause
```

---

## ⚙️ Advanced Options

### Run on Different Port
```powershell
$env:CHIMERA_HTTP_PORT="8080"
python src\chimera\chimera_main.py
```

### Enable Debug Logging
```powershell
$env:PYTHONVERBOSE="1"
python src\chimera\chimera_main.py
```

### Run as Background Service
```powershell
Start-Job -ScriptBlock {
    cd C:\Drox_AI
    .\droxai-env\Scripts\Activate.ps1
    python src\chimera\chimera_main.py
}
```

---

## 🆘 Emergency Commands

### Kill All Python Processes
```powershell
Get-Process python | Stop-Process -Force
```

### Reset Everything
```powershell
cd C:\Drox_AI
Remove-Item droxai-env -Recurse -Force
python -m venv droxai-env
.\droxai-env\Scripts\Activate.ps1
pip install aiohttp websockets
```

---

## ✅ Quick Health Check

Run this to verify everything is working:
```powershell
# 1. Check Python
python --version

# 2. Check virtual environment
.\droxai-env\Scripts\Activate.ps1

# 3. Check imports
python -c "import aiohttp, websockets; print('✓ Dependencies OK')"

# 4. Check file exists
Test-Path src\chimera\chimera_main.py
```

All should return OK/True!

---

## 🔗 URLs Reference

- **Dashboard**: http://localhost:3000
- **Metrics API**: http://localhost:3000/metrics
- **WebSocket**: ws://localhost:3001

---

## 💡 Tips

1. **Keep terminal open** while server runs
2. **Use Ctrl+C** to stop gracefully (not X button)
3. **Refresh browser** if dashboard doesn't update
4. **Check terminal** for error messages
5. **Use Option 3** to run in separate window

---

Need help? Check the terminal output for error messages!
