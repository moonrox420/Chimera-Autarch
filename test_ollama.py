#!/usr/bin/env python3
"""Quick Ollama connection test"""
import asyncio
import httpx


async def test_ollama():
    print("Testing Ollama connection...")

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Test 1: Check if server is responding
        try:
            response = await client.get("http://localhost:11434/api/tags")
            print(f"âœ… Server responding: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"âœ… Found {len(models)} models:")
                for m in models:
                    print(f"   - {m.get('name')}")
        except Exception as e:
            print(f"âŒ Connection failed: {e}")
            return

        # Test 2: Try generation
        try:
            print("\nðŸ§ª Testing code generation...")
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m",
                    "prompt": "Write a Python function to add two numbers",
                    "stream": False
                },
                timeout=30.0
            )
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"âœ… Generation successful!")
                print(f"Response: {result.get('response', '')[:200]}...")
            else:
                print(f"âŒ Generation failed: {response.text}")
        except Exception as e:
            print(f"âŒ Generation error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())

