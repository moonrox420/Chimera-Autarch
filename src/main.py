#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Unified Entry Point

A self-evolving AI orchestration system with federated learning capabilities.

Usage:
    python -m src.main server    # Start the server
    python -m src.main client    # Start the client
    python -m src.main cli       # Start CLI interface
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from core.logging import setup_logging
from cli.interface import run_cli
from api.server import run_server
from cli.client import run_client


def main():
    """Main entry point with mode selection."""
    parser = argparse.ArgumentParser(
        description="CHIMERA AUTARCH - Self-evolving AI orchestration system"
    )
    parser.add_argument(
        "mode",
        choices=["server", "client", "cli"],
        help="Run mode: server (start API server), client (WebSocket client), cli (command-line interface)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )

    args = parser.parse_args()

    # Load configuration
    settings = get_settings(config_path=args.config)

    # Setup logging
    setup_logging(
        level=getattr(logging, args.log_level),
        settings=settings.logging
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting CHIMERA AUTARCH in {args.mode} mode")

    try:
        if args.mode == "server":
            asyncio.run(run_server(settings))
        elif args.mode == "client":
            asyncio.run(run_client(settings))
        elif args.mode == "cli":
            run_cli(settings)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()