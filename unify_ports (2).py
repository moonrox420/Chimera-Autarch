import os
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PYTHON_PATTERN = re.compile(r"\.py[iw]?$", re.IGNORECASE)
DOCKERFILE_NAMES = {"Dockerfile", "dockerfile"}
COMPOSE_NAMES = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}

def replace_in_file(path: Path):
    content = path.read_text(encoding="utf-8")
    original = content

    # 1. Python files â€“ smash any port numbers
    if path.suffix.lower() == ".py":
        # Hardcoded ports â†’ env vars
        content = re.sub(
            r"(\bport\s*[:=])\s*[\'\"]?(\d+)[\'\"]?",
            lambda m: f"{m.group(1)} os.getenv('HTTP_PORT' if {m.group(2)} in ('3000','3000','3000') else 'WS_PORT', '{m.group(2)}')",
            content,
        )
        # Specific common patterns
        content = re.sub(r"port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000')|port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000')|port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000')|port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000'), "port=int(os.getenv('WS_PORT', 3000))", content)
        content = re.sub(r"port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000')|port= os.getenv('HTTP_PORT' if 3000 in ('3000','3000','3000') else 'WS_PORT', '3000')|port= os.getenv('HTTP_PORT' if 80 in ('3000','3000','3000') else 'WS_PORT', '80')|port= os.getenv('HTTP_PORT' if 443 in ('3000','3000','3000') else 'WS_PORT', '443'), "port=int(os.getenv('HTTP_PORT', 3000))", content)
        # Add import if missing
        if "os.getenv" in content and "import os" not in content:
            content = "import os\n" + content

    # 2. Dockerfile â€“ force EXPOSE
    if path.name.lower() in [n.lower() for n in DOCKERFILE_NAMES]:
        content = re.sub(
            r"EXPOSE\s+.*",
            "EXPOSE 3000 3000",
            content,
            flags=re.IGNORECASE
        )
        if "EXPOSE" not in content:
            content += "\nEXPOSE 3000 3000\n"

    # 3. docker-compose.yml â€“ force ports mapping + env
    if path.name.lower() in [n.lower() for n in COMPOSE_NAMES]:
        # Ports mapping
        content = re.sub(
            r"-\s*[\"']?\d+:(\d+)[\"']?",
            lambda m: f"- \"3000:3000\"  # was {m.group(0)}\n      - \"3000:3000\"",
            content
        )
        # Environment section
        env_block = """
    environment:
      HTTP_PORT: 3000
      WS_PORT: 3000
"""
        if "environment:" not in content:
            content = re.sub(
                r"(services:\s+\w+:\s+)",
                f"\\1{env_block}    ",
                content,
                count=1
            )

    # 4. entrypoint.sh or any shell script
    if path.suffix == ".sh" or "entrypoint" in path.name.lower():
        content = re.sub(
            r"export\s+\w*_PORT=.*",
            "export HTTP_PORT=3000\nexport WS_PORT=3000",
            content
        )
        if "HTTP_PORT" not in content:
            content = "export HTTP_PORT=3000\nexport WS_PORT=3000\n\n" + content

    if content != original:
        path.write_text(content, encoding="utf-8")
        logging.info(f"Unified â†’ {path}")

def main():
    logging.info("CHIMERA PORT UNIFIER â€“ FORCING 3000/3000 EVERYWHERE")
    for path in ROOT.rglob("*"):
        if path.is_file():
            if PYTHON_PATTERN.search(path.name) or \
               path.name.lower() in [n.lower() for n in DOCKERFILE_NAMES] or \
               path.name.lower() in [n.lower() for n in COMPOSE_NAMES] or \
               path.suffix == ".sh":
                replace_in_file(path)
    logging.info("DONE. All ports smashed to HTTP_PORT=3000 and WS_PORT=3000. Total consistency achieved.")

if __name__ == "__main__":
    main()
