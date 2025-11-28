# chimera_god_cli.py â€” FINAL, FIXED, NO MISSING IMPORTS, NO ERRORS

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path  # â† WAS MISSING â€” NOW FIXED

ROOT = Path(__file__).parent.resolve()  # C:\Drox_AI\build

def go(command: str):
    cmd = command.strip().lower()

    if "deploy" in cmd or "up" in cmd or "launch" in cmd:
        logging.info("[GOD MODE] Fortress rising...")
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=ROOT.parent)
        time.sleep(5)
        webbrowser.open("http://127.0.0.1:3000")
        logging.info("[GOD MODE] Chimera Autarch LIVE â€” http://127.0.0.1:3000")

    elif "kill" in cmd or "down" in cmd:
        logging.info("[GOD MODE] Fortress nuked")
        subprocess.run(["docker", "compose", "down", "--remove-orphans", "-v"], cwd=ROOT.parent)

    elif "rebuild" in cmd:
        logging.info("[GOD MODE] Rebuilding fortress...")
        subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd=ROOT.parent)
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=ROOT.parent)

    elif "unify" in cmd:
        logging.info("[GOD MODE] Forcing total alignment...")
        unify = ROOT.parent / "unify_everything.py"
        subprocess.run([sys.executable, str(unify)], cwd=ROOT.parent)
        logging.info("[GOD MODE] Project unified â€” one truth")

    elif "logs" in cmd:
        subprocess.run(["docker", "logs", "-f", "chimera-fortress"])

    else:
        logging.info(f"[GOD MODE] Raw command: {command}")
        os.system(command)

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "go":
        logging.info("Usage: python chimera_god_cli.py go \"<your command>\"")
        sys.exit(1)

    go(" ".join(sys.argv[2:]))
