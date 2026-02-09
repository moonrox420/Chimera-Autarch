#!/usr/bin/env python3
import os, sys, time, subprocess, webbrowser
from pathlib import Path

# Determine project root
if getattr(sys, "frozen", False): 
    LAUNCHER_HOME = Path(sys.executable).parent
else: 
    LAUNCHER_HOME = Path(__file__).parent

PROJECT_ROOT = LAUNCHER_HOME.parent if LAUNCHER_HOME.name == "build" else LAUNCHER_HOME

# Setup Python path
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.environ['PYTHONPATH'] = str(PROJECT_ROOT / "src") + os.pathsep + str(PROJECT_ROOT) + os.pathsep + os.environ.get('PYTHONPATH', '')

# Default configuration (can be overridden via environment variables or config.yaml)
http_port = int(os.environ.get("APP_SERVER_HTTP_PORT", "3000"))
http_host = os.environ.get("APP_SERVER_HTTP_HOST", "localhost")
ws_port = int(os.environ.get("APP_SERVER_WEBSOCKET_PORT", "3001"))
ws_host = os.environ.get("APP_SERVER_WEBSOCKET_HOST", "localhost")

# Launch the unified entry point
print(f"[CHIMERA AUTARCH] Launching unified server")
print(f"[CHIMERA AUTARCH] HTTP: {http_host}:{http_port} | WebSocket: {ws_host}:{ws_port}")

proc = subprocess.Popen([sys.executable, "-m", "src.main", "server"], cwd=str(PROJECT_ROOT), env=os.environ.copy())
time.sleep(5)

if proc.poll() is None:
    url = f"http://{http_host}:{http_port}"
    print(f"[CHIMERA AUTARCH] Server running → {url}")
    webbrowser.open(url)

try: 
    proc.wait()
except KeyboardInterrupt: 
    proc.terminate()
