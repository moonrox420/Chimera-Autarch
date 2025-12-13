# 🚀 START CHIMERA - SIMPLE INSTRUCTIONS

## Easiest Way (3 Steps)

### 1️⃣ Double-Click This File
```
START_CHIMERA.bat
```
Located in: `C:\Drox_AI\START_CHIMERA.bat`

### 2️⃣ Wait for This Message
```
Dashboard: http://localhost:3000
WebSocket: ws://localhost:3001
CHIMERA AUTARCH v3.0 — WICKEDLY BADASS EDITION — ONLINE
```

### 3️⃣ Open Your Browser
Go to: **http://localhost:3000**

**That's it!** ✅

---

## Alternative: PowerShell (Copy & Paste)

Open PowerShell and run:
```powershell
C:\Drox_AI\START_CHIMERA.ps1
```

Or this single command:
```powershell
cd C:\Drox_AI; .\droxai-env\Scripts\Activate.ps1; python src\chimera\chimera_main.py
```

---

## What You'll See

### In Terminal:
- Green text saying "ONLINE"
- Two URLs (Dashboard and WebSocket)

### In Browser (localhost:3000):
- Black background with green text
- "CHIMERA AUTARCH v3.0" title
- System Status showing "● ONLINE"
- Connect/Send/Disconnect buttons

---

## How to Stop

Press **Ctrl + C** in the terminal window

---

## Troubleshooting

### "Cannot run scripts"
Run PowerShell as **Administrator**, then:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Port already in use"
Something else is using port 3000. Find and kill it:
```powershell
netstat -ano | findstr ":3000"
taskkill /PID [NUMBER] /F
```
Replace `[NUMBER]` with the PID from first command.

### "Module not found"
Dependencies missing. Run:
```powershell
cd C:\Drox_AI
.\droxai-env\Scripts\Activate.ps1
pip install aiohttp websockets
```

---

## Testing the Dashboard

1. Click **"Connect"** button (turns green)
2. Type "hello" in the text box
3. Click **"Send"**
4. Look at console - you'll see your message echoed back

---

## Files You Need

All in `C:\Drox_AI\`:

- ✅ `START_CHIMERA.bat` ← **Double-click this!**
- ✅ `START_CHIMERA.ps1` ← PowerShell version
- ✅ `src\chimera\chimera_main.py` ← Main program
- ✅ `droxai-env\` ← Python environment folder

---

## Quick Reference

| What | Where |
|------|-------|
| Start Server | Double-click `START_CHIMERA.bat` |
| Dashboard | http://localhost:3000 |
| Stop Server | Press Ctrl+C |
| Check Status | Look for "● ONLINE" message |

---

## Emergency Reset

If everything breaks:
```powershell
cd C:\Drox_AI
Remove-Item droxai-env -Recurse -Force
python -m venv droxai-env
.\droxai-env\Scripts\Activate.ps1
pip install aiohttp websockets
```

Then try `START_CHIMERA.bat` again.

---

**Need more help?** Check `QUICK_START.md` for detailed instructions.
