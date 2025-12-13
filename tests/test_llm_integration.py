#!/usr/bin/env python3
"""
Test script for LLM integration in CHIMERA AUTARCH
"""
import asyncio
import sys

async def test_llm():
    # Import after path setup
    from chimera_autarch import HeartNode
    
    print("🧠 Initializing CHIMERA with LLM integration...")
    heart = HeartNode()
    await heart.init()
    
    # Test 1: Check if LLM tools are registered
    print("\n📋 Registered Tools:")
    for tool_name in heart.registry.tools.keys():
        print(f"  ✓ {tool_name}")
    
    llm_tools = [t for t in heart.registry.tools.keys() if t.startswith("llm_")]
    if llm_tools:
        print(f"\n✅ LLM tools registered: {', '.join(llm_tools)}")
    else:
        print("\n⚠️  No LLM tools registered")
        print("   Make sure Ollama is running: ollama serve")
        print("   Or set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    # Test 2: Generate simple code
    print("\n🔧 Testing code generation...")
    prompt = "Write a Python function that calculates fibonacci numbers recursively"
    result = await heart.registry.execute("llm_generate_code", prompt=prompt)
    
    if result.success:
        print(f"✅ Code generated successfully!")
        print(f"   Confidence: {result.data.get('confidence', 0):.2%}")
        print("\n📝 Generated Code:")
        print("=" * 60)
        print(result.data.get('code', 'No code returned'))
        print("=" * 60)
    else:
        print(f"❌ Code generation failed: {result.data}")
    
    print("\n✅ LLM integration test complete!")

if __name__ == "__main__":
    try:
        asyncio.run(test_llm())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
