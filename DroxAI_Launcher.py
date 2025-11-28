#!/usr/bin/env python3
import os, sys, time, subprocess, webbrowser
from pathlib import Path
if getattr(sys, "frozen", False): LAUNCHER_HOME = Path(sys.executable).parent
else: LAUNCHER_HOME = Path(__file__).parent
PROJECT_ROOT = LAUNCHER_HOME.parent if LAUNCHER_HOME.name == "build" else LAUNCHER_HOME
sys.path.insert(0, str(PROJECT_ROOT))
os.environ['PYTHONPATH'] = str(PROJECT_ROOT) + os.pathsep + os.environ.get('PYTHONPATH', '')
try: from DroxAI_ConfigManager import ConfigManager
except Exception as e: print(f"FATAL: DroxAI_ConfigManager.py missing → {e}"); sys.exit(1)
config = ConfigManager.load_config()
os.environ["HTTP_HOST"] = config.server.http_host
os.environ["HTTP_PORT"] = str(config.server.http_port)
os.environ["WS_HOST"] = config.server.websocket_host
os.environ["WS_PORT"] = str(config.server.websocket_port)
BACKENDS = ["chimera_autarch_v4_tuned.py","main.py"]
backend = next((PROJECT_ROOT / f for f in BACKENDS if (PROJECT_ROOT / f).exists()), None)
if not backend: print("FATAL: No backend"); sys.exit(1)
print(f"[{config.app.name}] Launching → {backend.name}")
proc = subprocess.Popen([sys.executable, str(backend)], cwd=str(PROJECT_ROOT), env=os.environ.copy())
time.sleep(5)
if proc.poll() is None:
    url = f"http://localhost:{config.server.http_port}/"
    print(f"[{config.app.name}] CATHEDRAL LIVE → {url}")
    webbrowser.open(url)
try: proc.wait()
except KeyboardInterrupt: proc.terminate()

