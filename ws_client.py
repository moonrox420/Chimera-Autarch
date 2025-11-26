import asyncio
import websockets
import json
import sys
import time
import ssl

# Try SSL first, fallback to non-SSL
WS_URL = "wss://localhost:8765"  # SSL enabled
WS_URL_FALLBACK = "ws://localhost:8765"  # Non-SSL fallback


async def send_commands(ws):
    while True:
        try:
            cmd = input(
                "Enter CHIMERA command (or type `exit` to quit): ").strip()
            if cmd.lower() == "exit":
                print("Exiting...")
                await ws.close()
                break
            if cmd:
                msg = json.dumps({"type": "intent", "intent": cmd})
                await ws.send(msg)
        except EOFError:
            break


async def receive_events(ws):
    async for msg in ws:
        try:
            data = json.loads(msg)
        except Exception:
            data = msg
        print(f"[SERVER] {data}")


async def chimera_client():
    # Try SSL first, then fallback to non-SSL
    urls_to_try = [WS_URL, WS_URL_FALLBACK]

    for url in urls_to_try:
        print(f"Connecting to {url} ...")
        try:
            # Create SSL context that doesn't verify certificates (for self-signed certs)
            ssl_context = None
            if url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(url, ssl=ssl_context) as ws:
                print("[CLIENT] Connected to CHIMERA core.")
                sender = asyncio.create_task(send_commands(ws))
                receiver = asyncio.create_task(receive_events(ws))
                done, pending = await asyncio.wait(
                    [sender, receiver],
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
                print("[CLIENT] Disconnected from server.")
                return  # Exit if successful
        except (ConnectionRefusedError, OSError):
            print(f"[CLIENT] Connection to {url} failed...")
            continue
        except websockets.ConnectionClosed as e:
            print(f"[CLIENT] Server closed connection ({e.code}): {e.reason}.")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"[CLIENT] Error with {url}: {e}")
            continue

    print("[CLIENT] All connection attempts failed. Retrying in 3s...")
    await asyncio.sleep(3)
    await chimera_client()  # Retry

if __name__ == "__main__":
    try:
        asyncio.run(chimera_client())
    except KeyboardInterrupt:
        print("Exiting client.")
