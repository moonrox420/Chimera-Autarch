"""Lightweight Ollama client for local LLM chat/inference.

This keeps dependencies minimal (aiohttp already used by the server).
Defaults:
  OLLAMA_HOST=http://127.0.0.1:11434
  OLLAMA_MODEL=dagbs/qwen2.5-coder-14b-instruct-abliterated
  OLLAMA_TIMEOUT=60 (seconds)
"""

import os
import asyncio
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger("chimera.llm")


class OllamaClient:
    """Async client for the local Ollama REST API."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "dagbs/qwen2.5-coder-14b-instruct-abliterated")
        self.timeout = int(timeout or os.getenv("OLLAMA_TIMEOUT", "60"))

    async def chat(self, prompt: str, system: Optional[str] = None) -> str:
        """Send a prompt to Ollama /api/generate with stream disabled."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt if not system else f"{system}\n\n{prompt}",
            "stream": False,
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise RuntimeError(f"Ollama error {resp.status}: {text}")
                    data = await resp.json()
                    # generate endpoint returns `response`
                    return data.get("response", "").strip()
            except Exception as exc:  # network errors, JSON errors, timeouts
                logger.error("Ollama request failed: %s", exc)
                raise

    async def is_available(self) -> bool:
        """Lightweight availability check using /api/tags (best-effort)."""
        url = f"{self.base_url}/api/tags"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            try:
                async with session.get(url) as resp:
                    return resp.status == 200
            except Exception:
                return False


# Convenience singleton for modules that prefer a ready client
OLLAMA_CLIENT = OllamaClient()


if __name__ == "__main__":
    async def _smoke():
        client = OllamaClient()
        ok = await client.is_available()
        if not ok:
            print("Ollama not reachable at", client.base_url)
            return
        try:
            reply = await client.chat("Say hello in one sentence.")
            print("Response:", reply)
        except Exception as exc:  # pragma: no cover
            print("Error:", exc)

    asyncio.run(_smoke())
