# CHIMERA AUTARCH - LLM Integration Guide

## Overview

CHIMERA AUTARCH now includes powerful LLM (Large Language Model) integration for AI-powered code generation, fixing, and optimization. The system supports multiple LLM providers with automatic fallback.

## Supported LLM Providers

### 1. **Local Ollama** (Recommended - Free & Private)
- **Model**: Qwen 2.5 Coder 14B (optimized for code)
- **Advantages**: Free, private, no API keys, GPU-accelerated
- **Setup**:
  ```powershell
  # Install Ollama from https://ollama.com
  # Pull the model
  ollama pull dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m
  
  # Start Ollama server
  ollama serve
  ```

### 2. **OpenAI** (GPT-4 Turbo)
- **Setup**: Set environment variable
  ```powershell
  $env:OPENAI_API_KEY = "sk-your-api-key-here"
  ```

### 3. **Anthropic** (Claude 3.5 Sonnet)
- **Setup**: Set environment variable
  ```powershell
  $env:ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
  ```

## Available Tools

### 1. `llm_generate_code`
Generate new code from natural language prompts.

**Usage via Intent**:
```python
# Natural language intents
"generate a function to calculate fibonacci numbers"
"write code to sort a list using quicksort"
"create a class for managing database connections"
```

**Direct API**:
```python
result = await heart.registry.execute(
    "llm_generate_code",
    prompt="Write a function that finds prime numbers up to n",
    context={"language": "python", "style": "functional"}
)
```

### 2. `llm_fix_code`
Automatically fix code errors and bugs.

**Usage via Intent**:
```python
"fix this code error: NameError"
"debug the function that's causing IndexError"
```

**Direct API**:
```python
result = await heart.registry.execute(
    "llm_fix_code",
    code=buggy_code,
    error="TypeError: unsupported operand type(s)",
    context={"framework": "asyncio"}
)
```

### 3. `llm_optimize_code`
Optimize code for performance, memory, or readability.

**Usage via Intent**:
```python
"optimize this code for performance"
"optimize code for memory usage"
"optimize code for readability"
```

**Direct API**:
```python
result = await heart.registry.execute(
    "llm_optimize_code",
    code=original_code,
    optimization_goal="performance",  # or "memory", "readability"
    context={"constraints": ["maintain API compatibility"]}
)
```

## Testing LLM Integration

### Quick Test
```powershell
python test_llm_integration.py
```

### Via WebSocket Client
```powershell
python ws_client.py
# Then send intents like:
> generate a function to reverse a string
> write code to read a CSV file
```

## Response Format

All LLM tools return a structured response:

```python
{
    "success": True,
    "code": "def fibonacci(n):\n    ...",  # Generated/fixed/optimized code
    "description": "Recursive fibonacci implementation",
    "confidence": 0.95,  # 0.0-1.0 confidence score
    "test_output": "All tests passed",  # or error message if failed
}
```

## Configuration

### Model Selection (Local)
Edit `chimera_autarch.py` to change the default model:

```python
# In HeartNode._init_llm_provider()
self.llm_provider = LocalLLMProvider(
    model="qwen2.5-coder:14b"  # or any Ollama model
)
```

### Temperature & Tokens
Adjust in `llm_integration.py`:

```python
# In provider's generate_code method
response = await self.client.chat.completions.create(
    model=self.model,
    temperature=0.2,  # Lower = more deterministic
    max_tokens=2000,  # Increase for longer code
    ...
)
```

## Advanced Features

### Self-Healing Code Generation
The LLM integration includes automatic testing and rollback:

1. Code is generated
2. Automatic tests are created
3. Code is validated in sandboxed environment
4. If tests fail, system automatically retries or rolls back
5. Confidence scores guide metacognitive learning

### Context-Aware Generation
Provide rich context for better results:

```python
context = {
    "project": "CHIMERA AUTARCH",
    "file_path": "src/tools/analysis.py",
    "imports": ["asyncio", "aiosqlite"],
    "style_guide": "Google Python Style Guide",
    "existing_functions": ["analyze_metrics", "record_event"],
    "requirements": ["async", "error handling", "logging"]
}

result = await heart.registry.execute(
    "llm_generate_code",
    prompt="Create a function to aggregate metrics over time windows",
    context=context
)
```

## Performance Tips

1. **Use Local Ollama for development** - Faster iteration, no API costs
2. **Cache generated code** - CHIMERA automatically stores successful patches
3. **Batch requests** - Group related code generation tasks
4. **Provide context** - More context = better results
5. **Iterate with feedback** - Use fix/optimize tools to refine output

## Troubleshooting

### "LLM not available"
- Check Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`
- Check API keys if using cloud providers

### "Model not found"
```powershell
# Pull the model
ollama pull dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m
```

### Slow generation
- Use local Ollama with GPU acceleration
- Reduce `max_tokens` parameter
- Use simpler models for faster responses

### Low quality output
- Increase temperature for creativity (0.3-0.5)
- Provide more detailed context
- Use more powerful models (GPT-4, Claude 3.5)
- Break complex tasks into smaller steps

## Integration with Metacognitive Engine

The LLM tools automatically integrate with CHIMERA's metacognitive learning:

- **Success tracking**: Code generation success rates are monitored
- **Confidence scoring**: Low-confidence outputs trigger human review
- **Failure patterns**: Repeated failures trigger federated learning
- **Self-improvement**: System learns which prompts produce best code

## Security Considerations

1. **Local models**: Keep data private, no external API calls
2. **Sandboxed execution**: Generated code runs in isolated environment
3. **Code review**: High-risk changes require confidence threshold
4. **Rollback**: Automatic rollback on test failures
5. **Audit trail**: All LLM operations logged to database

## Future Enhancements

- [ ] Multi-model ensemble (combine outputs from multiple LLMs)
- [ ] Fine-tuning on CHIMERA codebase
- [ ] Real-time collaborative coding
- [ ] Natural language → full project generation
- [ ] Automatic documentation generation
- [ ] Code review and security analysis

---

## Quick Start Example

```python
import asyncio
from chimera_autarch import HeartNode

async def demo():
    heart = HeartNode()
    await heart.init()
    
    # Generate code
    result = await heart.registry.execute(
        "llm_generate_code",
        prompt="Write an async function to fetch data from an API"
    )
    
    print(f"Success: {result.data['success']}")
    print(f"Code:\n{result.data['code']}")
    print(f"Confidence: {result.data['confidence']:.1%}")

asyncio.run(demo())
```

---

**Ready to harness AI-powered code generation in CHIMERA AUTARCH!** 🚀🤖
