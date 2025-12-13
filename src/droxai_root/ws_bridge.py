from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import ollama

app = FastAPI()

with open("chimera_god_cli.html", "r", encoding="utf-8") as f:
    html = f.read()

@app.get("/", response_class=HTMLResponse)
async def root():
    return html

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        try:
            resp = ollama.chat(
                model="mannix/llama3.1-8b-abliterated:q5_k_m",
                messages=[{"role": "user", "content": msg}],
            )
            await ws.send_text(resp["message"]["content"])
        except Exception:
            await ws.send_text(" Error - but I'm alive. Retrying...")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="critical")
