python
import ollama
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from rich import print as r
from typing import Dict, Any
import asyncio

# Create FastAPI app
app = FastAPI(title="CHIMERA AUTARCH v4", version="4.0")

@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CHIMERA AUTARCH v4</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #1a1a1a; color: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; }
            .chat-container { border: 1px solid #444; border-radius: 5px; padding: 15px; margin: 10px 0; }
            .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .user { background-color: #2a2a2a; }
            .assistant { background-color: #3a3a3a; }
            input[type="text"] { width: 70%; padding: 8px; margin: 5px; border-radius: 3px; border: 1px solid
#444; }
            button { padding: 8px 15px; background-color: #4a4a4a; color: white; border: none; border-radius: 3px;
cursor: pointer; }
            button:hover { background-color: #5a5a5a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CHIMERA AUTARCH v4 ─ FULL CATHEDRAL MODE</h1>
            <div class="chat-container" id="chat">
                <div class="message assistant">Welcome to CHIMERA AUTARCH v4. Start chatting!</div>
            </div>
            <div>
                <input type="text" id="prompt" placeholder="Enter your prompt..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        <script>
            const ws = new WebSocket('ws://127.0.0.1:3000/ws');
            const chatContainer = document.getElementById('chat');
            const promptInput = document.getElementById('prompt');

            ws.onopen = function(event) {
                addMessage('assistant', 'Connected to CHIMERA AUTARCH v4');
            };

            ws.onmessage = function(event) {
                addMessage('assistant', event.data);
            };

            ws.onclose = function(event) {
                addMessage('assistant', 'Connection closed');
            };

            function addMessage(role, text) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function sendMessage() {
                const prompt = promptInput.value;
                if (prompt.trim()) {
                    addMessage('user', prompt);
                    ws.send(prompt);
                    promptInput.value = '';
                }
            }

            promptInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """WebSocket endpoint for chat interactions"""
    await ws.accept()

    # Send welcome message
    await ws.send_text("Connected to CHIMERA AUTARCH v4")

    try:
        while True:
            # Receive prompt from client
            prompt = await ws.receive_text()
            r(f"[bold magenta]>> {prompt}[/]")

            # Process with Ollama
            try:
                resp = ollama.chat(
                    model="mannix/llama3.1-8b-abliterated:q5_k_m",
                    messages=[{"role":"user","content":prompt}]
                )
                answer = resp["message"]["content"]
                await ws.send_text(answer)
                r(f"[bold green]>> {answer}[/]")
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                r(f"[bold red]>> {error_msg}[/]")
                await ws.send_text(f"Error: {error_msg}")

    except Exception as e:
        r(f"[bold red]>> WebSocket error: {str(e)}[/]")
        await ws.send_text(f"Connection error: {str(e)}")

if __name__ == "__main__":
    r("[bold red]CHIMERA AUTARCH v4 ─ FULL CATHEDRAL MODE[/]")
    uvicorn.run("chimera_autarch_v4_tuned:app", host="127.0.0.1", port=3000, reload=False)