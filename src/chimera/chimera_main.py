import asyncio
import json
import time
import sqlite3
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import httpx
import websockets

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()

WS_HOST = "0.0.0.0"
WS_PORT = 3001

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.1-8b-abliterated:tools-q8_0"

RATE_LIMIT = 20
RATE_WINDOW = 60
RETENTION_DAYS = 30

# Token auth:
# - UI sends {"type":"auth","token":"..."} as first message
# - then sends {"type":"ask","prompt":"..."}
VALID_TOKENS = {"dev-token-9001", "admin-token-9001"}

DB_PATH = BASE_DIR / "chimera_memory.db"

# ──────────────────────────────────────────────────────────────
# DB
# ──────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            client_ip TEXT,
            token TEXT,
            role TEXT,
            content TEXT
        )
    """)
    if RETENTION_DAYS > 0:
        conn.execute(
            "DELETE FROM chat WHERE timestamp < datetime('now', ?)",
            (f"-{RETENTION_DAYS} days",)
        )
    conn.commit()
    conn.close()

def log_chat(ip: str, token: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO chat (client_ip, token, role, content) VALUES (?, ?, ?, ?)",
        (ip, token, role, content)
    )
    conn.commit()
    conn.close()

init_db()

# ──────────────────────────────────────────────────────────────
# RATE LIMIT
# ──────────────────────────────────────────────────────────────
@dataclass
class ClientState:
    count: int = 0
    reset_time: float = 0.0

clients = defaultdict(ClientState)

def check_auth(token: str) -> bool:
    return token in VALID_TOKENS

def ip_from_ws(ws) -> str:
    ra = getattr(ws, "remote_address", None)
    if not ra:
        return "unknown"
    # websockets remote_address is usually (ip, port)
    return ra[0] if isinstance(ra, (tuple, list)) and ra else "unknown"

async def authenticate_and_rate_limit(ws) -> Optional[str]:
    ip = ip_from_ws(ws)
    state = clients[ip]
    now = time.time()

    if now - state.reset_time > RATE_WINDOW:
        state.count = 0
        state.reset_time = now

    # Count this connection attempt (or message)
    state.count += 1
    if state.count > RATE_LIMIT:
        await ws.send(json.dumps({"type": "error", "message": "Rate limit exceeded"}))
        await ws.close(code=1013, reason="Rate limited")
        return None

    # Expect first message to be auth JSON
    try:
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(msg)
        token = data.get("token") if isinstance(data, dict) else None
        if not token or not check_auth(token):
            await ws.send(json.dumps({"type": "error", "message": "Invalid token"}))
            await ws.close(code=1008, reason="Unauthorized")
            return None

        await ws.send(json.dumps({"type": "welcome", "status": "authorized"}))
        return token
    except Exception:
        await ws.close(code=1008, reason="Auth timeout")
        return None

# ──────────────────────────────────────────────────────────────
# OLLAMA STREAM
# ──────────────────────────────────────────────────────────────
async def stream_ollama(ws, token: str, ip: str, prompt: str):
    log_chat(ip, token, "user", prompt)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=300) as client:
        try:
            async with client.stream("POST", OLLAMA_URL, json=payload) as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)

                    # streamed token chunk
                    if "response" in data:
                        chunk = data["response"]
                        if chunk:
                            await ws.send(json.dumps({"type": "chunk", "content": chunk}))
                            log_chat(ip, token, "assistant", chunk)

                    # done
                    if data.get("done"):
                        await ws.send(json.dumps({"type": "done"}))
                        break

        except Exception as e:
            await ws.send(json.dumps({"type": "error", "message": str(e)}))

# ──────────────────────────────────────────────────────────────
# WS HANDLER
# ──────────────────────────────────────────────────────────────
async def ws_handler(ws):
    token = await authenticate_and_rate_limit(ws)
    if not token:
        return

    ip = ip_from_ws(ws)

    try:
        async for message in ws:
            try:
                data = json.loads(message)

                # expected format: {"type":"ask","prompt":"..."}
                if isinstance(data, dict) and data.get("type") == "ask":
                    prompt = (data.get("prompt") or "").strip()
                    if not prompt:
                        await ws.send(json.dumps({"type": "error", "message": "Empty prompt"}))
                        continue
                    await stream_ollama(ws, token, ip, prompt)

                else:
                    await ws.send(json.dumps({"type": "error", "message": "Unknown message type"}))

            except json.JSONDecodeError:
                await ws.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
    except websockets.ConnectionClosed:
        pass

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
async def main():
    ws_server = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    print(f"✓ WebSocket: ws://localhost:{WS_PORT}")
    print("✓ Chimera WS Core - Online")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
