import os
import sys
import subprocess
import webbrowser
import time
import logging
from pathlib import Path

# Configure basic logging so logging.info() messages are displayed
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Assuming the script runs from C:\Drox_AI\docker\chimera_god_cli.py
# ROOT will be C:\Drox_AI\docker
# ROOT.parent (the current working directory for docker compose) will be C:\Drox_AI
ROOT = Path(__file__).parent.resolve()

def go(command: str):
    """
    Executes a command based on keywords, primarily managing the Docker environment.
    """
    cmd = command.strip().lower()

    if "deploy" in cmd or "up" in cmd or "launch" in cmd:
        logging.info("[GOD MODE] Fortress rising: building and deploying containers...")
        # Use subprocess.run with cwd=ROOT.parent to execute docker-compose 
        # from the project root (C:\Drox_AI)
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=ROOT.parent)
        time.sleep(5)
        webbrowser.open("http://127.0.0.1:3000")
        logging.info("[GOD MODE] Chimera Autarch LIVE — http://127.0.0.1:3000")

    elif "kill" in cmd or "down" in cmd:
        logging.info("[GOD MODE] Fortress nuked: shutting down containers and removing volumes.")
        subprocess.run(["docker", "compose", "down", "--remove-orphans", "-v"], cwd=ROOT.parent)

    elif "rebuild" in cmd:
        logging.info("[GOD MODE] Rebuilding fortress: cleaning and launching...")
        subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd=ROOT.parent)
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=ROOT.parent)

    elif "unify" in cmd:
        logging.info("[GOD MODE] Forcing total alignment: running unify_everything.py...")
        unify = ROOT.parent / "unify_everything.py"
        # Use sys.executable to ensure we run with the correct Python interpreter
        subprocess.run([sys.executable, str(unify)], cwd=ROOT.parent)
        logging.info("[GOD MODE] Project unified — one truth")

    elif "logs" in cmd:
        # Assuming your main container is named 'chimera-fortress' or similar
        subprocess.run(["docker", "logs", "-f", "chimera-fortress"])

    else:
        logging.info(f"[GOD MODE] Raw command executed: {command}")
        os.system(command)

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "go":
        logging.info("Usage: python chimera_god_cli.py go \"<your command>\"")
        sys.exit(1)

    go(" ".join(sys.argv[2:]))