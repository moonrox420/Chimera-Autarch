import asyncio
import websockets
import json
import os

WS_HOST = os.environ.get("WS_HOST", "localhost")
WS_PORT = os.environ.get("WS_PORT", "3000")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

async def client():
    async with websockets.connect(WS_URL) as ws:
        print("Connected to Chimera Autarch")
        while True:
            msg = input("> ")
            if msg.lower() in ["quit", "exit"]: break
            await ws.send(json.dumps({"type": "user", "content": msg}))
            resp = await ws.recv()
            print(resp)

if __name__ == "__main__":
    asyncio.run(client())

