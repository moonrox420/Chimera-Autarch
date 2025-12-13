"""
Command-line interface for CHIMERA AUTARCH.
"""

import asyncio
import json
import sys
from typing import Optional

import websockets
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from config.settings import Settings
from core.logging import get_logger

logger = get_logger(__name__)
console = Console()


def run_cli(settings: Settings) -> None:
    """Run the command-line interface."""
    console.print(Panel.fit(
        "[bold cyan]CHIMERA AUTARCH CLI[/bold cyan]\n"
        "[dim]Type 'help' for commands, 'quit' to exit[/dim]",
        title="Welcome"
    ))

    while True:
        try:
            command = Prompt.ask("chimera> ").strip()

            if not command:
                continue

            if command.lower() in ('quit', 'exit', 'q'):
                console.print("[yellow]Goodbye![/yellow]")
                break

            if command.lower() == 'help':
                _show_help()
                continue

            # For now, just echo the command
            # TODO: Implement actual command processing
            console.print(f"[dim]Command: {command}[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logger.error(f"CLI error: {e}", exc_info=True)


def _show_help() -> None:
    """Show help information."""
    help_text = """
[bold]Available Commands:[/bold]

[cyan]help[/cyan]          Show this help message
[cyan]quit[/cyan]          Exit the CLI
[cyan]status[/cyan]        Show system status
[cyan]connect[/cyan]       Connect to WebSocket server
[cyan]send <message>[/cyan] Send message to server

[dim]More commands coming soon...[/dim]
    """
    console.print(Panel(help_text, title="Help"))