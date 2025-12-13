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
sys.path.insert(0, str(PROJECT_ROOT / "src" / "droxai_root"))
os.environ['PYTHONPATH'] = str(PROJECT_ROOT / "src" / "droxai_root") + os.pathsep + str(PROJECT_ROOT) + os.pathsep + os.environ.get('PYTHONPATH', '')

# Load config
try: 
    from DroxAI_ConfigManager import ConfigManager
except Exception as e: 
    print(f"FATAL: DroxAI_ConfigManager.py missing → {e}")
    sys.exit(1)

config = ConfigManager.load_config()

# Set environment variables
os.environ["HTTP_HOST"] = config.server.http_host
os.environ["HTTP_PORT"] = str(config.server.http_port)
os.environ["WS_HOST"] = config.server.web_socket_host
os.environ["WS_PORT"] = str(config.server.web_socket_port)

# Launch the backend
backend = PROJECT_ROOT / "src" / "droxai_root" / "chimera_autarch.py"

if not backend.exists():
    print(f"FATAL: Backend not found at {backend}")
    sys.exit(1)

print(f"[{config.app.name}] Launching → {backend.name}")
print(f"[{config.app.name}] Binding {config.server.http_host}:{config.server.http_port} (HTTP) / {config.server.web_socket_host}:{config.server.web_socket_port} (WS)")

proc = subprocess.Popen([sys.executable, str(backend)], cwd=str(PROJECT_ROOT), env=os.environ.copy())
time.sleep(5)

if proc.poll() is None:
    url = f"http://localhost:{config.server.http_port}/chimera_god_cli.html"
    print(f"[{config.app.name}] CATHEDRAL LIVE → {url}")
    webbrowser.open(url)

try: 
    proc.wait()
except KeyboardInterrupt: 
    proc.terminate()
