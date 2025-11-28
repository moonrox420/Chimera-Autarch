#!/usr/bin/env python3
"""Quick test script for Qwen 2.5 Coder integration with CHIMERA"""

import asyncio
import sys
from pathlib import Path


async def test_qwen_model():
    """Test if Qwen 2.5 Coder is available and working"""

    print("=" * 60)
    print("QWEN 2.5 CODER - Quick Test")
    print("=" * 60)

    # Test 1: Check if llm_integration module exists
    print("\nðŸ“¦ Test 1: Checking llm_integration module...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from llm_integration import CodeGenerator
        print("âœ… llm_integration module loaded")
    except Exception as e:
        print(f"âŒ Failed to load module: {e}")
        return False

    # Test 2: Initialize generator
    print("\nðŸ”§ Test 2: Initializing Code Generator...")
    try:
        generator = CodeGenerator()
        print(f"âœ… Generator initialized")
        print(f"   Provider: {generator.provider.__class__.__name__}")
        if hasattr(generator.provider, 'model'):
            print(f"   Model: {generator.provider.model}")
    except Exception as e:
        print(f"âŒ Failed to initialize: {e}")
        return False

    # Test 3: Check Ollama availability
    print("\nðŸ¤– Test 3: Checking Ollama models...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"âœ… Ollama server running")
                print(f"   Available models: {len(models)}")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) / (1024**3)  # Convert to GB
                    print(f"   - {name} ({size:.1f} GB)")

                # Check for Qwen specifically
                qwen_found = any("qwen" in m.get("name", "").lower()
                                 for m in models)
                if qwen_found:
                    print("\nâœ… Qwen 2.5 Coder is ready!")
                else:
                    print("\nâš ï¸  Qwen 2.5 Coder not found yet")
                    print("   Model may still be downloading...")
                    print("   Check with: ollama list")
            else:
                print(
                    f"âŒ Ollama server returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"âŒ Failed to connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

    # Test 4: Simple code generation (only if model ready)
    if qwen_found:
        print("\nðŸš€ Test 4: Testing code generation...")
        try:
            code = await generator.generate_code(
                "Create a Python function that calculates fibonacci numbers",
                context="Simple utility function"
            )
            print("âœ… Code generation successful!")
            print(f"\nGenerated code preview (first 200 chars):")
            print("-" * 60)
            print(code[:200] + "..." if len(code) > 200 else code)
            print("-" * 60)
        except Exception as e:
            print(f"âŒ Code generation failed: {e}")
            return False

    print("\n" + "=" * 60)
    if qwen_found:
        print("âœ… ALL TESTS PASSED - Qwen 2.5 Coder is ready!")
        print("\nðŸš€ Next steps:")
        print("   1. Run: python test_llm.py")
        print("   2. Run: python chimera_autarch.py")
        print("   3. Visit: http://localhost:3000")
    else:
        print("â³ Setup incomplete - waiting for model download")
        print("\nðŸ“ To check download progress:")
        print("   Run: ollama list")
        print("\nðŸ“ Once complete, run this test again:")
        print("   python quick_test.py")
    print("=" * 60)

    return qwen_found


if __name__ == "__main__":
    success = asyncio.run(test_qwen_model())
    sys.exit(0 if success else 1)

