import json
import logging

from chimera_autarch import ToolResult

logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
    logger.info("[INTENT] Ollama detected - AI-powered intent compilation enabled")
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("[INTENT] Ollama not available - using pattern-based compilation")

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chimera_autarch import ToolRegistry

class IntentCompiler:
    """Compiles natural language intents into tool execution plans"""
    
    def __init__(self, registry: 'ToolRegistry'):
        self.registry = registry
        self.use_ai = OLLAMA_AVAILABLE
        logger.info(f"[INTENT] Initialized with AI mode: {self.use_ai}")
    
    async def compile(self, intent: str) -> list[tuple[str, dict[str, any]]]:
        """Compile intent to tool calls - TRY AI FIRST"""
        
        # USE LOCAL AI IF AVAILABLE (NO CORPORATE CENSORSHIP)
        if self.use_ai:
            try:
                logger.debug(f"[INTENT] AI analyzing: {intent[:60]}...")
                return await self._compile_with_ai(intent)
            except Exception as e:
                logger.warning(f"[INTENT] AI compilation failed ({e}), using patterns")
        
        # FALLBACK TO PATTERN MATCHING
        return await self._fallback_patterns(intent)
    
    async def _compile_with_ai(self, intent: str) -> list[tuple[str, dict[str, Any]]]:
        """Use local Qwen model to understand complex intents"""
        
        # Build tool registry context
        available_tools = []
        for name, tool in self.registry.tools.items():
            available_tools.append(f"- {name}: {tool.description}")
        tools_context = "\n".join(available_tools)
        
        # Query Ollama with CHIMERA-specific system prompt
        response = ollama.chat(
            model='dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m',
            messages=[{
                'role': 'system',
                'content': f'''You are CHIMERA AUTARCH's intent compiler. Convert natural language to tool calls.

AVAILABLE TOOLS:
{tools_context}

OUTPUT FORMAT (JSON only, no explanations):
[{{"tool": "tool_name", "params": {{"key": "value"}}}}]

- Use exact tool names from registry
- Infer reasonable parameter values
- Multiple tools allowed for complex intents
- Empty array [] if intent unclear'''
            }, {
                'role': 'user',
                'content': intent
            }],
            options={
                'temperature': 0.0,  # Deterministic for predictable metacognitive tracking
                'num_predict': 512,
                'top_p': 0.95
            }
        )
        
        # Parse AI response
        content = response['message']['content'].strip()
        
        # Strip markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
        
        tool_calls = json.loads(content)
        
        # Validate against registry (critical: prevent hallucinated tools)
        validated = []
        for tc in tool_calls:
            tool_name = tc.get('tool')
            if tool_name not in self.registry.tools:
                logger.warning(f"[INTENT] AI suggested unknown tool: {tool_name}")
                continue
            
            params = tc.get('params', {})
            validated.append((tool_name, params))
            logger.debug(f"[INTENT] Validated: {tool_name} with {len(params)} params")
        
        if not validated:
            logger.warning("[INTENT] AI returned no valid tools, using fallback")
            return await self._fallback_patterns(intent)
        
        logger.info(f"[INTENT] AI compiled to {len(validated)} tool call(s)")
        return validated
    
    async def _fallback_patterns(self, intent: str) -> list[tuple[str, dict[str, any]]]:
        """Pattern-based compilation (graceful degradation)"""
        intent_lower = intent.lower()
        plan = []
        
        # Federated learning triggers
        if "federated" in intent_lower or "distributed train" in intent_lower:
            rounds = 5 if "thorough" in intent_lower else 3
            plan.append(("start_federated_training", {
                "topic": "general",
                "num_rounds": rounds
            }))
        
        # Code optimization patterns
        if "optimize" in intent_lower:
            # Extract function name if mentioned
            words = intent.split()
            func_name = next((w for w in words if w.startswith("_") or w[0].isupper()), None)
            
            plan.append(("analyze_and_suggest_patch", {
                "function_name": func_name or "unknown",
                "goal": "performance" if "speed" in intent_lower else "efficiency"
            }))
        
        # Symbiotic arm initialization
        if "symbiotic" in intent_lower or "initialize arm" in intent_lower:
            plan.append(("initialize_symbiotic_link", {
                "capabilities": ["compute", "learning"]
            }))
        
        # System status queries
        if "status" in intent_lower or "health" in intent_lower:
            plan.append(("get_system_status", {}))
        
        logger.info(f"[INTENT] Pattern match: {len(plan)} tool call(s)")
        return plan if plan else [("echo", {"message": f"Unknown intent: {intent}"})]
    
    # AI-POWERED TOOL REGISTRATION HELPER (to be called from HeartNode._init_tools())
    async def register_ai_tools(registry: 'ToolRegistry') -> None:
        """Register AI-powered analysis tools if Ollama is available"""
        if not OLLAMA_AVAILABLE:
            return
        
        async def _tool_ai_analyze(query: str, context: str = "") -> ToolResult[dict[str, Any]]:
            """Use local AI for complex analysis tasks"""
            try:
                response = ollama.chat(
                    model='dagbs/qwen2.5-coder-14b-instruct-abliterated:q5_k_m',
                    messages=[{
                        'role': 'system',
                        'content': 'You are CHIMERA\'s analytical engine. Provide structured insights.'
                    }, {
                        'role': 'user',
                        'content': f"Context: {context}\n\nQuery: {query}"
                    }],
                    options={'temperature': 0.2}
                )
                
                return ToolResult(
                    success=True,
                    data={
                        'analysis': response['message']['content'],
                        'model': 'qwen2.5-coder-14b',
                        'censored': False
                    }
                )
            except Exception as e:
                return ToolResult(success=False, error=str(e))
        
        registry.register(
            name="ai_analyze",
            func=_tool_ai_analyze,
            version="1.0.0",
            description="Deep AI analysis of complex problems (local, uncensored)"
        )
        logger.info("[HEART] AI analysis tool registered")
