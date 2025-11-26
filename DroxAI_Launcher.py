#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
import psutil

# ──────────────────────────────────────────────────────────────
# 1. NUKE EVERY OLD FORTRESS — NO SURVIVORS
# ──────────────────────────────────────────────────────────────
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmd = proc.info['cmdline']
        if cmd and len(cmd) > 1:
            cmd_str = ' '.join(cmd).lower()
            if any(x in cmd_str for x in ['chimera_autarch', 'droxai_core', 'main.py', 'app.py']):
                logging.info(f"[LAUNCHER] ☠️  TERMINATING OLD PROCESS → PID {proc.pid}")
                proc.kill()
    except:
        pass

# ──────────────────────────────────────────────────────────────
# 2. THIS IS THE LAUNCHER — NO RECURSION ALLOWED
# ──────────────────────────────────────────────────────────────
if Path(sys.argv[0]).name != "DroxAI_Launcher.py":
    logging.info("[LAUNCHER] ERROR: You must name this file exactly 'DroxAI_Launcher.py'")
    sys.exit(1)

logging.info("[LAUNCHER] FINAL LAUNCH SEQUENCE INITIATED — ONE INSTANCE ONLY")

# ──────────────────────────────────────────────────────────────
# 3. PROJECT ROOT — BULLETPROOF
# ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ──────────────────────────────────────────────────────────────
# 4. CONFIG
# ──────────────────────────────────────────────────────────────
try:
    from DroxAI_ConfigManager import ConfigManager
    config = ConfigManager.load_config()
except Exception as e:
    logging.info(f"[FATAL] Config failed → {e}")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# 5. FIND AND LAUNCH YOUR LATEST CORE
# ──────────────────────────────────────────────────────────────
backend = PROJECT_ROOT / "chimera_autarch.py"
if not backend.exists():
    logging.info("[FATAL] chimera_autarch.py not found — did you delete it?")
    sys.exit(1)

logging.info(f"[DROXAI] EXECUTING → {backend.name}")
logging.info(f"[DROXAI] DASHBOARD → http://0.0.0.0:{config.server.http_port}")
logging.info(f"[DROXAI] WEBSOCKET → ws://0.0.0.0:{config.server.websocket_port}")

proc = subprocess.Popen(
    [sys.executable, str(backend)],
    cwd=str(PROJECT_ROOT),
    env=os.environ.copy()
)

time.sleep(8)

if proc.poll() is None:
    # THIS IS THE ONLY URL THAT WORKS — NO MORE 404s
    url = f"http://0.0.0.0:{config.server.http_port}/dashboard"
    logging.info(f"[DROXAI] FORTRESS IS LIVE → {url}")
    webbrowser.open(url)
else:
    logging.info(f"[DROXAI] CRASHED ON LAUNCH — CODE {proc.poll()}")
    sys.exit(1)

try:
    proc.wait()
except KeyboardInterrupt:
    logging.info("\n[DROXAI] Fortress shutdown by king command.")
    proc.terminate()

logging.info("[DROXAI] Empire secured. King has logged off.")