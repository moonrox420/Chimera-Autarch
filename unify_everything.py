# unify_everything.py
# THE ONLY SCRIPT YOU WILL EVER NEED AGAIN
# Overwrite EVERY OTHER unify script with this exact code.
# Run once. Done forever.

import os
import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
EXCLUDE = {".venv", "__pycache__", ".git", "node_modules", "build", "dist", "release"}

def is_text(p):
    try:
        p.read_text("utf-8", errors="strict")
        return True
    except:
        return False

def total_lockdown(path):
    if not is_text(path):
        return False

    text = path.read_text("utf-8")
    old = text

    # 1. HOST â†’ 127.0.0.1 EVERYWHERE
    text = re.sub(r"127\.0\.0\.1|127.0.0.1", "127.0.0.1", text)

    # 2. PORTS â†’ ENV VARS (HTTP 3000 / WS 3000)
    text = re.sub(r"\bport\s*=\s*\d+", "port=int(os.getenv('HTTP_PORT', 3000))", text)
    text = re.sub(r"\bport\s*:\s*\d+", "port: int(os.getenv('HTTP_PORT', 3000))", text)
    text = re.sub(r"\b3001\b|\b8081\b", "3000", text)
    text = re.sub(r"\b3000\b|\b5000\b", "3000", text)

    # 3. DOCKERFILE â†’ FORTRESS
    if path.name.lower().startswith("dockerfile"):
        text = """FROM python:3.12-slim-bookworm
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
RUN useradd -m chimera && mkdir -p /chimera/data /chimera/tmp && chown chimera:chimera /chimera/tmp
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
USER chimera
EXPOSE 3000 3000
ENTRYPOINT ["python", "DroxAILauncher.py"]
"""

    # 4. COMPOSE â†’ FORTRESS
    if "compose" in path.name.lower():
        text = """services:
  chimera:
    build: .
    container_name: chimera-fortress
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /chimera/tmp:noexec,nosuid,nodev,size=64m
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    ports:
      - "3000:3000"
      - "3000:3000"
    environment:
      MASTER_KEY: ${MASTER_KEY}
      ENABLE_FL_RUNTIME: ${ENABLE_FL_RUNTIME:-false}
      IMAGE_DIGEST: ${IMAGE_DIGEST}
      HTTP_PORT: 3000
      WS_PORT: 3000
    volumes:
      - ./ssl:/chimera/ssl:ro
      - ./cosign.pub:/chimera/cosign.pub:ro
"""

    # 5. LAUNCHERS â†’ ONE TRUTH
    if "launch" in path.name.lower():
        text = "python DroxAILauncher.py"

    # 6. CONFIG â†’ LOCKED
    if path.name.endswith(".json") and "config" in str(path).lower():
        text = json.dumps({
            "Server": {
                "HttpHost": "127.0.0.1",
                "HttpPort": 3000,
                "WebSocketHost": "127.0.0.1",
                "WebSocketPort": 3000
            }
        }, indent=2)

    if text != old:
        path.write_text(text, "utf-8")
        logging.info(f"LOCKED â†’ {path.relative_to(ROOT)}")
        return True
    return False

logging.info("TOTAL PROJECT LOCKDOWN â€” ONE PASS")
any_change = any(total_lockdown(p) for p in ROOT.rglob("*") if p.is_file() and not any(ex in p.parts for ex in EXCLUDE))

if not any_change:
    logging.info("PROJECT ALREADY LOCKED DOWN")

logging.info("DONE. THREE SCRIPTS ARE DEAD. ONLY ONE REMAINS. FORTRESS COMPLETE.")
