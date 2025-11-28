#!/usr/bin/env python3
"""
CHIMERA v3.0 - LLM Integration Test
Tests AI code generation with auto-detected LLM provider (OpenAI/Claude/Ollama)
Supports: GPT-4, Claude 3.5, Qwen 2.5 Coder 14B, DeepSeek Coder, CodeLlama
"""
import os
import asyncio
from llm_integration import CodeGenerator, OpenAIProvider, AnthropicProvider, LocalLLMProvider


async def test_llm():
    print("=" * 60)
    print("CHIMERA v3.0 - LLM Integration Test")
    print("=" * 60)
    print()

    # Test 1: Auto-detect provider
    print("ðŸ” Test 1: Auto-detecting LLM provider...")
    generator = CodeGenerator()

    if generator.provider is None:
        print("âŒ No LLM provider available")
        print()
        print("ðŸ“‹ Setup instructions:")
        print()
        print("Option A - OpenAI GPT-4:")
        print("  1. Get API key: https://platform.openai.com/api-keys")
        print("  2. pip install openai")
        print("  3. export OPENAI_API_KEY='sk-proj-...'")
        print()
        print("Option B - Anthropic Claude:")
        print("  1. Get API key: https://console.anthropic.com/")
        print("  2. pip install anthropic")
        print("  3. export ANTHROPIC_API_KEY='sk-ant-...'")
        print()
        print("Option C - Local Ollama (FREE - RECOMMENDED):")
        print("  1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Download model:")
        print(
            "     ðŸ”¥ BEST: ollama pull dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m")
        print("     OR: ollama pull deepseek-coder:6.7b")
        print("     OR: ollama pull codellama")
        print("  3. pip install httpx")
        print()
        return

    provider_name = type(generator.provider).__name__
    print(f"âœ… Found: {provider_name}")

    # Show which model is being used for local LLM
    if isinstance(generator.provider, LocalLLMProvider):
        print(f"   Model: {generator.provider.model}")
        if "qwen" in generator.provider.model.lower():
            print("   ðŸ”¥ Using Qwen 2.5 Coder - Excellent choice!")
        elif "deepseek" in generator.provider.model.lower():
            print("   âš¡ Using DeepSeek Coder - Fast and capable!")
        elif "codellama" in generator.provider.model.lower():
            print("   âœ… Using CodeLlama - Reliable and tested!")
    print()

    # Test 2: Generate simple code
    print("ðŸ§ª Test 2: Generating simple Python function...")
    print("Task: Create a function to calculate fibonacci number")
    print()

    try:
        patch = await generator.generate_patch(
            problem_description="Create a function called fibonacci that takes an integer n and returns the nth fibonacci number. Use recursion with memoization for efficiency.",
            context={"language": "python", "style": "functional"},
            include_tests=True
        )

        if patch:
            print(f"âœ… Code generation successful!")
            print(f"   Confidence: {patch.confidence:.2f}")
            print(f"   Risk level: {patch.risk_level}")
            print(f"   Has tests: {'Yes' if patch.test_code else 'No'}")
            print(f"   Code lines: {len(patch.code.splitlines())}")
            if patch.test_code:
                print(f"   Test lines: {len(patch.test_code.splitlines())}")
            print()
            print("ðŸ“ Generated code:")
            print("-" * 60)
            print(patch.code)
            print("-" * 60)
            print()

            if patch.test_code:
                print("ðŸ§ª Generated tests:")
                print("-" * 60)
                print(patch.test_code)
                print("-" * 60)
                print()

            # Test 3: Run tests
            if patch.test_code:
                print("ðŸ”¬ Test 3: Running generated tests...")
                result = await generator.test_patch(patch)

                if result.success:
                    print(
                        f"âœ… All tests passed! ({result.execution_time:.2f}s)")
                    print()
                    print("ðŸŽ‰ Your LLM provider is working perfectly!")
                else:
                    print(f"âŒ Tests failed:")
                    print(result.error)
                print()
        else:
            print("âŒ Code generation failed")
            print()

    except Exception as e:
        print(f"âŒ Error during code generation: {e}")
        print()
        import traceback
        traceback.print_exc()
        return

    # Show stats
    print("ðŸ“Š Generator stats:")
    stats = generator.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    print("=" * 60)
    print("âœ… LLM Integration Test Complete!")
    print("=" * 60)
    print()
    print("ðŸš€ Next steps:")
    print("   1. Start CHIMERA: python chimera_autarch.py")
    print("   2. CHIMERA will auto-detect and use your LLM provider")
    print("   3. AI code generation will be ENABLED!")
    print()

    # Show provider-specific tips
    if isinstance(generator.provider, LocalLLMProvider):
        print("ðŸ’¡ Local LLM Tips:")
        if "qwen" in generator.provider.model.lower():
            print("   â€¢ Qwen 2.5 Coder excels at complex code generation")
            print("   â€¢ See QWEN_CODER_GUIDE.md for advanced usage")
            print("   â€¢ Hardware: 16GB RAM minimum, 32GB recommended")
        elif "deepseek" in generator.provider.model.lower():
            print("   â€¢ DeepSeek Coder is fast and efficient")
            print("   â€¢ Good for rapid prototyping")
        else:
            print("   â€¢ CodeLlama is lightweight and fast")
            print("   â€¢ Good for simple tasks")
        print("   â€¢ FREE forever - no API costs!")
        print("   â€¢ Complete privacy - code never leaves your machine")
        print()
    elif isinstance(generator.provider, OpenAIProvider):
        print("ðŸ’¡ OpenAI Tips:")
        print("   â€¢ Cost: ~$0.01-0.03 per code generation")
        print("   â€¢ Monitor usage at: https://platform.openai.com/usage")
        print()
    elif isinstance(generator.provider, AnthropicProvider):
        print("ðŸ’¡ Claude Tips:")
        print("   â€¢ Cost: ~$0.015 per code generation")
        print("   â€¢ Monitor usage at: https://console.anthropic.com/")
        print()


if __name__ == "__main__":
    asyncio.run(test_llm())

