"""
WebSocket client for connecting to CHIMERA AUTARCH server.
"""

import asyncio
import json
import sys
from typing import Optional

import websockets
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from config.settings import Settings
from core.logging import get_logger

logger = get_logger(__name__)
console = Console()


async def run_client(settings: Settings) -> None:
    """Run the WebSocket client."""
    uri = f"ws://{settings.server.http_host}:{settings.server.http_port}/ws"

    console.print(Panel.fit(
        f"[bold cyan]CHIMERA AUTARCH Client[/bold cyan]\n"
        f"[dim]Connecting to {uri}[/dim]",
        title="Client"
    ))

    try:
        async with websockets.connect(uri) as websocket:
            console.print("[green]Connected to server![/green]")

            # Start message receiver
            receive_task = asyncio.create_task(_receive_messages(websocket))

            # Main input loop
            while True:
                try:
                    message = await asyncio.get_event_loop().run_in_executor(
                        None, Prompt.ask, "message> "
                    )

                    if message.lower() in ('quit', 'exit', 'q'):
                        break

                    if message.strip():
                        await websocket.send(message)
                        logger.debug(f"Sent: {message}")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[red]Error sending message: {e}[/red]")
                    logger.error(f"Send error: {e}", exc_info=True)

            # Cancel receiver
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass

    except websockets.exceptions.ConnectionClosed:
        console.print("[yellow]Connection closed by server[/yellow]")
    except Exception as e:
        console.print(f"[red]Connection error: {e}[/red]")
        logger.error(f"Client error: {e}", exc_info=True)
        sys.exit(1)

    console.print("[yellow]Client disconnected[/yellow]")


async def _receive_messages(websocket) -> None:
    """Receive and display messages from server."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                console.print(f"[blue]Received:[/blue] {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                console.print(f"[blue]Received:[/blue] {message}")
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        console.print(f"[red]Receive error: {e}[/red]")
        logger.error(f"Receive error: {e}", exc_info=True)
