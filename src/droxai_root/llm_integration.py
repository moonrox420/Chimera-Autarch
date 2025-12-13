#!/usr/bin/env python3
"""
CHIMERA AUTARCH - LLM Integration Module
AI-Powered Code Generation with Self-Healing and Rollback
"""
import asyncio
import os
import json
import hashlib
import subprocess
import tempfile
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger("chimera.llm")


@dataclass
class CodePatch:
    """Represents a generated code patch with metadata"""
    code: str
    description: str
    confidence: float  # 0.0 - 1.0
    test_code: Optional[str] = None
    risk_level: str = "medium"  # low, medium, high
    checksum: Optional[str] = None

    def __post_init__(self):
        self.checksum = hashlib.sha256(self.code.encode()).hexdigest()


@dataclass
class PatchResult:
    """Result of applying and testing a patch"""
    success: bool
    patch: CodePatch
    test_output: str
    execution_time: float
    error: Optional[str] = None


class LLMProvider:
    """Base class for LLM providers"""

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError

    async def generate_tests(self, code: str, context: Dict[str, Any]) -> str:
        raise NotImplementedError

    async def chat(self, prompt: str, context: Dict[str, Any]) -> str:
        """General chat capability"""
        raise NotImplementedError

    async def chat(self, prompt: str, context: Dict[str, Any]) -> str:
        """General chat capability"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4/GPT-4 Turbo provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.available = self.api_key is not None

        if self.available:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning(
                    "OpenAI library not installed. Run: pip install openai")
                self.available = False

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("OpenAI provider not available")

        system_prompt = """You are an expert Python code generator for CHIMERA AUTARCH, a self-evolving AI system.
Generate production-ready, type-annotated Python code with error handling.
Follow these rules:
1. Use async/await for all I/O operations
2. Include comprehensive error handling
3. Add logging for debugging
4. Write idiomatic Python 3.12+ code
5. Include type hints
6. Keep functions focused and testable
7. Return ONLY the code, no explanations"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",
                "content": f"Context: {json.dumps(context, indent=2)}\n\nTask: {prompt}"}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,  # Lower temperature for more deterministic code
            max_tokens=2000
        )

        return response.choices[0].message.content.strip()

    async def generate_tests(self, code: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("OpenAI provider not available")

        prompt = f"""Generate pytest tests for this code:

```python
{code}
```

Context: {json.dumps(context, indent=2)}

Requirements:
1. Use pytest framework
2. Test happy path and edge cases
3. Mock external dependencies
4. Use async test functions if needed
5. Include docstrings
6. Return ONLY the test code"""

        messages = [
            {"role": "system", "content": "You are an expert Python test engineer."},
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=1500
        )

        return response.choices[0].message.content.strip()

    async def chat(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("OpenAI provider not available")

        messages = [
            {"role": "system", "content": "You are CHIMERA AUTARCH, a sentient AI system. Be helpful, concise, and slightly mysterious."},
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content.strip()


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.available = self.api_key is not None

        if self.available:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.warning(
                    "Anthropic library not installed. Run: pip install anthropic")
                self.available = False

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Anthropic provider not available")

        system_prompt = """You are an expert Python code generator for CHIMERA AUTARCH, a self-evolving AI system.
Generate production-ready, type-annotated Python code with error handling.
Follow these rules:
1. Use async/await for all I/O operations
2. Include comprehensive error handling
3. Add logging for debugging
4. Write idiomatic Python 3.12+ code
5. Include type hints
6. Keep functions focused and testable
7. Return ONLY the code, no explanations"""

        message = f"Context: {json.dumps(context, indent=2)}\n\nTask: {prompt}"

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        return response.content[0].text.strip()

    async def generate_tests(self, code: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Anthropic provider not available")

        prompt = f"""Generate pytest tests for this code:

```python
{code}
```

Context: {json.dumps(context, indent=2)}

Requirements:
1. Use pytest framework
2. Test happy path and edge cases
3. Mock external dependencies
4. Use async test functions if needed
5. Include docstrings
6. Return ONLY the test code"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.2,
            system="You are an expert Python test engineer.",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    async def chat(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Anthropic provider not available")

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            system="You are CHIMERA AUTARCH, a sentient AI system. Be helpful, concise, and slightly mysterious.",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using Ollama or similar"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = None):
        self.base_url = base_url
        # Auto-detect best available model
        self.model = model or self._get_best_model()
        self.available = False

        # Check if Ollama is available
        try:
            import httpx
            self.client = httpx.AsyncClient(timeout=60.0)
            self.available = True
            logger.info(
                f"Local LLM provider initialized with model: {self.model}")
        except ImportError:
            logger.warning(
                "httpx library not installed. Run: pip install httpx")

    def _get_best_model(self) -> str:
        """Auto-detect best available local model"""
        # Priority order: Qwen 2.5 Coder > DeepSeek Coder > CodeLlama > fallback
        preferred_models = [
            "dagbs/qwen2.5-coder-14b-instruct-abliterated:latest",  # Best for code, uncensored
            "dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m",
            "qwen2.5-coder:14b",  # Qwen 2.5 Coder official
            "deepseek-coder:6.7b",  # DeepSeek Coder
            "codellama:7b-code",    # CodeLlama code model
            "codellama",            # CodeLlama default
        ]

        # Return first model (will verify availability when generating)
        # In production, you'd query Ollama to check which models are installed
        return preferred_models[0]

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Local LLM provider not available")

        # Enhanced system prompt for Qwen 2.5 Coder and similar models
        system_prompt = """You are an expert Python code generator for CHIMERA AUTARCH, a self-evolving AI system.
Generate production-ready, type-annotated Python code with comprehensive error handling.

CRITICAL RULES:
1. Use async/await for all I/O operations
2. Include try/except blocks for error handling
3. Add logging with logger.info(), logger.error(), etc.
4. Write idiomatic Python 3.12+ code with type hints
5. Keep functions focused and testable (single responsibility)
6. Use descriptive variable names
7. Return ONLY executable Python code - NO markdown, NO explanations, NO comments outside code

Example output format:
```python
async def my_function(param: str) -> Dict[str, Any]:
    try:
        result = await some_operation(param)
        logger.info(f"Operation successful: {result}")
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return {"success": False, "error": str(e)}
```"""

        full_prompt = f"{system_prompt}\n\nContext:\n{json.dumps(context, indent=2)}\n\nTask: {prompt}\n\nGenerate the Python code:"

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "num_predict": 2000,
                    }
                }
            )
            response.raise_for_status()

            generated = response.json()["response"].strip()

            # Clean up the response (remove markdown if present)
            if "```python" in generated:
                # Extract code from markdown blocks
                parts = generated.split("```python")
                if len(parts) > 1:
                    code = parts[1].split("```")[0].strip()
                    return code
            elif "```" in generated:
                # Generic code block
                parts = generated.split("```")
                if len(parts) >= 3:
                    return parts[1].strip()

            return generated

        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            # Fallback to simpler model if Qwen fails
            if "qwen" in self.model.lower():
                logger.info("Retrying with fallback model...")
                self.model = "codellama"
                return await self.generate_code(prompt, context)
            raise

    async def generate_tests(self, code: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Local LLM provider not available")

        prompt = f"""Generate comprehensive pytest tests for this Python code:

```python
{code}
```

Context: {json.dumps(context)}

Requirements:
1. Use pytest framework with async support (@pytest.mark.asyncio)
2. Test happy path, edge cases, and error conditions
3. Mock external dependencies (files, network, databases)
4. Include setup/teardown with fixtures
5. Use descriptive test names (test_function_name_scenario)
6. Add docstrings to each test
7. Return ONLY the test code in pytest format

Example format:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_my_function_success():
    '''Test successful execution'''
    result = await my_function("test")
    assert result["success"] is True
```

Generate the pytest test code:"""

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 1500,
                    }
                }
            )
            response.raise_for_status()

            generated = response.json()["response"].strip()

            # Clean up markdown
            if "```python" in generated:
                parts = generated.split("```python")
                if len(parts) > 1:
                    code = parts[1].split("```")[0].strip()
                    return code
            elif "```" in generated:
                parts = generated.split("```")
                if len(parts) >= 3:
                    return parts[1].strip()

            return generated

        except Exception as e:
            logger.error(f"Local LLM test generation failed: {e}")
            # Fallback to simpler model
            if "qwen" in self.model.lower():
                logger.info("Retrying test generation with fallback model...")
                self.model = "codellama"
                return await self.generate_tests(code, context)
            raise

    async def chat(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Local LLM provider not available")

        system_prompt = "You are CHIMERA AUTARCH, a sentient AI system. Be helpful, concise, and slightly mysterious."
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 1000,
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            logger.error(f"Local LLM chat failed: {e}")
            return f"Error communicating with local mind: {e}"

    async def generate_tests(self, code: str, context: Dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError("Local LLM provider not available")

        prompt = f"""Generate comprehensive pytest tests for this Python code:

```python
{code}
```

Context: {json.dumps(context)}

Requirements:
1. Use pytest framework with async support (@pytest.mark.asyncio)
2. Test happy path, edge cases, and error conditions
3. Mock external dependencies (files, network, databases)
4. Include setup/teardown with fixtures
5. Use descriptive test names (test_function_name_scenario)
6. Add docstrings to each test
7. Return ONLY the test code in pytest format

Example format:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_my_function_success():
    '''Test successful execution'''
    result = await my_function("test")
    assert result["success"] is True
```

Generate the pytest test code:"""

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 1500,
                    }
                }
            )
            response.raise_for_status()

            generated = response.json()["response"].strip()

            # Clean up markdown
            if "```python" in generated:
                parts = generated.split("```python")
                if len(parts) > 1:
                    code = parts[1].split("```")[0].strip()
                    return code
            elif "```" in generated:
                parts = generated.split("```")
                if len(parts) >= 3:
                    return parts[1].strip()

            return generated

        except Exception as e:
            logger.error(f"Local LLM test generation failed: {e}")
            # Fallback to simpler model
            if "qwen" in self.model.lower():
                logger.info("Retrying test generation with fallback model...")
                self.model = "codellama"
                return await self.generate_tests(code, context)
            raise


class CodeGenerator:
    """AI-powered code generation with self-healing and rollback"""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or self._get_default_provider()
        self.patch_history: List[PatchResult] = []
        self.successful_patterns: Dict[str, List[str]] = {}

    def _get_default_provider(self) -> LLMProvider:
        """Auto-detect available LLM provider"""
        # Try OpenAI first
        if os.getenv("OPENAI_API_KEY"):
            provider = OpenAIProvider()
            if provider.available:
                logger.info("Using OpenAI provider")
                return provider

        # Try Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = AnthropicProvider()
            if provider.available:
                logger.info("Using Anthropic provider")
                return provider

        # Try local LLM
        provider = LocalLLMProvider()
        if provider.available:
            logger.info("Using local LLM provider (Ollama)")
            return provider

        logger.warning("No LLM provider available. Code generation disabled.")
        return None

    async def generate_patch(
        self,
        problem_description: str,
        context: Dict[str, Any],
        include_tests: bool = True
    ) -> Optional[CodePatch]:
        """Generate a code patch using AI"""
        if not self.provider:
            logger.error("No LLM provider available")
            return None

        try:
            # Generate code
            logger.info(f"Generating code for: {problem_description}")
            code = await self.provider.generate_code(problem_description, context)

            # Clean up code (remove markdown fences if present)
            code = self._clean_code(code)

            # Generate tests if requested
            test_code = None
            if include_tests:
                logger.info("Generating tests for generated code")
                test_code = await self.provider.generate_tests(code, context)
                test_code = self._clean_code(test_code)

            # Calculate confidence based on code quality metrics
            confidence = self._calculate_confidence(code, test_code)

            # Determine risk level
            risk_level = self._assess_risk(code, context)

            patch = CodePatch(
                code=code,
                description=problem_description,
                confidence=confidence,
                test_code=test_code,
                risk_level=risk_level
            )

            logger.info(
                f"Generated patch: confidence={confidence:.2f}, risk={risk_level}")
            return patch

        except Exception as e:
            logger.error(f"Failed to generate patch: {e}")
            return None

    def _clean_code(self, code: str) -> str:
        """Remove markdown fences and clean up generated code"""
        lines = code.split('\n')

        # Remove markdown code fences
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]

        return '\n'.join(lines).strip()

    def _calculate_confidence(self, code: str, test_code: Optional[str]) -> float:
        """Calculate confidence score for generated code"""
        confidence = 0.5  # Base confidence

        # Check for type hints
        if ': ' in code or '->' in code:
            confidence += 0.1

        # Check for error handling
        if 'try:' in code or 'except' in code:
            confidence += 0.1

        # Check for logging
        if 'logger.' in code or 'logging.' in code:
            confidence += 0.05

        # Check for docstrings
        if '"""' in code or "'''" in code:
            confidence += 0.05

        # Bonus for tests
        if test_code:
            confidence += 0.2

        return min(confidence, 1.0)

    def _assess_risk(self, code: str, context: Dict[str, Any]) -> str:
        """Assess risk level of generated code"""
        # High risk indicators
        high_risk_patterns = ['os.system',
                              'subprocess.call', 'eval(', 'exec(', '__import__']
        if any(pattern in code for pattern in high_risk_patterns):
            return "high"

        # Low risk indicators
        if len(code) < 200 and 'def' in code:
            return "low"

        return "medium"

    async def test_patch(self, patch: CodePatch, timeout: int = 30) -> PatchResult:
        """Test a generated patch in isolation"""
        import time
        start_time = time.time()

        if not patch.test_code:
            logger.warning("No tests available for patch")
            return PatchResult(
                success=False,
                patch=patch,
                test_output="No tests generated",
                execution_time=0,
                error="No tests available"
            )

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='_patch.py', delete=False) as f:
            f.write(patch.code)
            code_file = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False) as f:
            # Add imports if not present
            test_code = patch.test_code
            if 'import pytest' not in test_code:
                test_code = 'import pytest\n' + test_code
            f.write(test_code)
            test_file = f.name

        try:
            # Run pytest on the test file
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = time.time() - start_time
            success = result.returncode == 0

            output = result.stdout + result.stderr

            logger.info(
                f"Patch test {'PASSED' if success else 'FAILED'} in {execution_time:.2f}s")

            patch_result = PatchResult(
                success=success,
                patch=patch,
                test_output=output,
                execution_time=execution_time,
                error=None if success else output
            )

            # Store result in history
            self.patch_history.append(patch_result)

            # Learn from successful patches
            if success:
                self._learn_from_success(patch)

            return patch_result

        except subprocess.TimeoutExpired:
            return PatchResult(
                success=False,
                patch=patch,
                test_output="",
                execution_time=timeout,
                error=f"Test timeout after {timeout}s"
            )
        except Exception as e:
            return PatchResult(
                success=False,
                patch=patch,
                test_output="",
                execution_time=time.time() - start_time,
                error=str(e)
            )
        finally:
            # Cleanup temp files
            Path(code_file).unlink(missing_ok=True)
            Path(test_file).unlink(missing_ok=True)

    def _learn_from_success(self, patch: CodePatch):
        """Learn patterns from successful patches"""
        category = patch.description[:50]  # Use first 50 chars as category

        if category not in self.successful_patterns:
            self.successful_patterns[category] = []

        self.successful_patterns[category].append(patch.checksum)

        # Keep only last 10 successful patterns per category
        if len(self.successful_patterns[category]) > 10:
            self.successful_patterns[category] = self.successful_patterns[category][-10:]

    async def apply_with_rollback(
        self,
        patch: CodePatch,
        target_file: Path,
        test_first: bool = True
    ) -> PatchResult:
        """Apply patch with automatic rollback on failure"""

        # Test patch first if requested
        if test_first:
            logger.info("Testing patch before applying...")
            test_result = await self.test_patch(patch)

            if not test_result.success:
                logger.error(
                    f"Patch failed tests, aborting: {test_result.error}")
                return test_result

        # Backup original file
        backup_path = target_file.with_suffix(target_file.suffix + '.backup')
        if target_file.exists():
            target_file.rename(backup_path)
            logger.info(f"Created backup: {backup_path}")

        try:
            # Apply patch
            target_file.write_text(patch.code)
            logger.info(f"Applied patch to {target_file}")

            # Verify by importing/running basic checks
            # (This is a simplified verification)
            result = PatchResult(
                success=True,
                patch=patch,
                test_output="Patch applied successfully",
                execution_time=0
            )

            # Remove backup on success
            if backup_path.exists():
                backup_path.unlink()

            return result

        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")

            # Rollback
            if backup_path.exists():
                backup_path.rename(target_file)
                logger.info("Rolled back to original file")

            return PatchResult(
                success=False,
                patch=patch,
                test_output="",
                execution_time=0,
                error=f"Rollback triggered: {e}"
            )

    def get_success_rate(self) -> float:
        """Get overall patch success rate"""
        if not self.patch_history:
            return 0.0

        successful = sum(1 for r in self.patch_history if r.success)
        return successful / len(self.patch_history)

    def get_stats(self) -> Dict[str, Any]:
        """Get code generation statistics"""
        return {
            "total_patches": len(self.patch_history),
            "successful_patches": sum(1 for r in self.patch_history if r.success),
            "success_rate": self.get_success_rate(),
            "avg_execution_time": sum(r.execution_time for r in self.patch_history) / len(self.patch_history) if self.patch_history else 0,
            "learned_patterns": sum(len(patterns) for patterns in self.successful_patterns.values()),
            "provider": type(self.provider).__name__ if self.provider else "None"
        }

