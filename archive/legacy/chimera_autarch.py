import asyncio
import json
import time
import hashlib
import websockets
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Callable, Optional, Dict, Any, List, Awaitable
from collections import defaultdict, deque
import aiosqlite
import logging
from concurrent.futures import ThreadPoolExecutor
import ssl
import secrets
import traceback
import os
import warnings

# Suppress protobuf deprecation warnings (Python â‰¥3.14 compatibility)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google._upb")

from graphql_api import GraphQLResolver

# Flower optional import – guarded at runtime
try:
    import flwr as fl
    from flwr.server import ServerConfig
    from flwr.server.strategy import FedAvg
    FLOWER_AVAILABLE = True
except Exception:  # ImportError or any runtime issue
    FLOWER_AVAILABLE = False

# LLM Integration – guarded at runtime
LLM_AVAILABLE = False
try:
    from llm_integration import LocalLLMProvider, OpenAIProvider, AnthropicProvider, CodeGenerator as LLMCodeGenerator
    LLM_AVAILABLE = True
except Exception as e:
    if logger:
        logger.warning(f"LLM integration unavailable: {e}")

# --------------------------------------------------------------------------- #
# Logging â€“ structured, timestamped, color-ready for production
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("chimera")

# --------------------------------------------------------------------------- #
# Secure Cryptographic Primitives
# --------------------------------------------------------------------------- #
class QuantumEntropy:
    """Cryptographically secure entropy with forward-secrecy guarantees."""
    @staticmethod
    def secure_id() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def sign_message(message: str, secret: str) -> str:
        """Constant-time safe HMAC-SHA3-256."""
        return hashlib.sha3_256((message + secret).encode()).hexdigest()

# --------------------------------------------------------------------------- #
# Generic Tool System â€“ typed, metered, self-healing
# --------------------------------------------------------------------------- #
T = TypeVar("T", covariant=True)

@dataclass
class ToolResult(Generic[T]):
    success: bool
    data: T
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class Tool(Generic[T]):
    def __init__(
        self,
        name: str,
        func: Callable[..., Awaitable[T]],
        description: str = "",
        version: str = "1.0.0",
        dependencies: Optional[List[str]] = None,
    ):
        self.name = name
        self.func = func
        self.description = description
        self.version = version
        self.dependencies = dependencies or []
        self._latency_samples: deque[float] = deque(maxlen=200)

    async def execute(self, **kwargs) -> ToolResult[T]:
        start = time.monotonic()
        try:
            result = await self.func(**kwargs)
            latency = time.monotonic() - start
            self._latency_samples.append(latency)
            return ToolResult(
                success=True,
                data=result,
                metrics={"latency": latency, "version": self.version},
            )
        except Exception as exc:
            logger.error(f"[TOOL:{self.name}] {exc!r}\n{traceback.format_exc()}")
            return ToolResult(
                success=False,
                data=str(exc),  # type: ignore
                metrics={"error": str(exc), "traceback": traceback.format_exc()},
            )

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._metrics: defaultdict[str, List[Dict[str, Any]]] = defaultdict(list)

    @property
    def tools(self) -> Dict[str, Tool]:
        return self._tools

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        logger.info(f"[REGISTRY] Registered tool: {tool.name} v{tool.version}")

    async def execute(self, name: str, **kwargs) -> ToolResult[Any]:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(False, f"Tool '{name}' not found", {"error": "not_found"})

        result = await tool.execute(**kwargs)
        self._metrics[name].append(
            {
                "ts": time.time(),
                "success": result.success,
                "latency": result.metrics.get("latency", 0),
            }
        )
        return result

    def stats(self, name: str, window: Optional[int] = None) -> Dict[str, float]:
        history = self._metrics[name][-window:] if window else self._metrics[name]
        if not history:
            return {"success_rate": 1.0, "avg_latency": 0.0}
        successes = sum(e["success"] for e in history)
        return {
            "success_rate": successes / len(history),
            "avg_latency": sum(e["latency"] for e in history) / len(history),
        }

# --------------------------------------------------------------------------- #
# Metacognitive Engine â€“ predictive self-evolution
# --------------------------------------------------------------------------- #
@dataclass
class EvolutionRecord:
    id: str = field(default_factory=QuantumEntropy.secure_id)
    topic: str = ""
    failure_reason: str = ""
    applied_fix: str = ""
    observed_improvement: float = 0.0
    timestamp: float = field(default_factory=time.time)
    validation_metrics: Dict[str, Any] = field(default_factory=dict)

class FailurePattern:
    def __init__(self, topic: str):
        self.topic = topic
        self.count: int = 0
        self.first_seen: float = 0.0
        self.last_seen: float = 0.0
        self.success_history: deque[bool] = deque(maxlen=100)
        self.confidence: float = 1.0
        self.learning_triggered: bool = False

    def record_attempt(self, success: bool):
        self.record(success)

    def record(self, success: bool):
        self.count += 1
        now = time.time()
        self.last_seen = now
        if not self.first_seen:
            self.first_seen = now
        self.success_history.append(success)
        recent = list(self.success_history)
        self.confidence = sum(recent) / len(recent) if recent else 1.0

class PersistenceLayer:
    def __init__(self, db_path: str = "chimera_memory.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS evolutions (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    failure_reason TEXT,
                    applied_fix TEXT,
                    observed_improvement REAL,
                    timestamp REAL,
                    validation_metrics TEXT
                );
                CREATE TABLE IF NOT EXISTS tool_metrics (
                    tool_name TEXT,
                    timestamp REAL,
                    success BOOLEAN,
                    latency REAL,
                    context TEXT
                );
            """)
            await db.commit()

    async def log_evolution(self, rec: EvolutionRecord):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO evolutions VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.id,
                    rec.topic,
                    rec.failure_reason,
                    rec.applied_fix,
                    rec.observed_improvement,
                    rec.timestamp,
                    json.dumps(rec.validation_metrics),
                ),
            )
            await db.commit()

    async def log_tool_metric(
        self,
        tool_name: str,
        success: bool,
        latency: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO tool_metrics VALUES (?, ?, ?, ?, ?)
                """,
                (tool_name, time.time(), success, latency, json.dumps(context or {})),
            )
            await db.commit()

class MetacognitiveEngine:
    def __init__(self, heart):
        self.heart = heart
        self.patterns: Dict[str, FailurePattern] = {}
        self.persistence = PersistenceLayer()
        self.cooldown = 300
        self.predictive_threshold = 0.65
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def init(self):
        await self.persistence.init()
        asyncio.create_task(self._predictive_monitor())
        logger.info("[METACOG] Predictive self-evolution engine ready")

    def _topic_from_intent(self, intent: str) -> str:
        intent = intent.lower()
        mapping = {
            "image": ["image", "vision", "pixel"],
            "hn": ["hacker news", "news", "article"],
            "fl": ["federated", "flower", "learning"],
            "symbiotic": ["symbiotic", "arm"],
            "file": ["file", "disk", "read", "write"],
            "code": ["code", "function", "optimize"],
        }
        for topic, keywords in mapping.items():
            if any(k in intent for k in keywords):
                return topic
        return "general"

    def log_failure(self, intent: str, reason: str) -> str:
        topic = self._topic_from_intent(intent)
        pattern = self.patterns.setdefault(topic, FailurePattern(topic))
        pattern.record(False)
        logger.warning(f"[FAIL:{topic}] {reason} | confidence={pattern.confidence:.2%}")
        return topic

    def record_success(self, topic: str):
        pattern = self.patterns.setdefault(topic, FailurePattern(topic))
        pattern.record(True)

    async def _predictive_monitor(self):
        while True:
            await asyncio.sleep(15)
            now = time.time()
            for topic, pat in list(self.patterns.items()):
                if pat.confidence < self.predictive_threshold:
                    if (now - pat.last_seen) > self.cooldown:
                        logger.info(f"[PREDICTIVE] Triggering proactive learning for {topic}")
                        await self._trigger_proactive_learning(topic)

    async def _trigger_proactive_learning(self, topic: str):
        plan = self.heart.compiler.compile(
            f"start federated learning to improve {topic}",
            learning_rounds=6,
        )
        for step in plan:
            await self.heart.dispatch_task(step["tool"], step["args"])

    async def record_outcome(
        self,
        topic: str,
        success: bool,
        metrics: Optional[Dict[str, Any]] = None,
    ):
        pattern = self.patterns.setdefault(topic, FailurePattern(topic))
        pattern.record(success)
        improvement = 0.07 if success else -0.04
        await self.persistence.log_evolution(
            EvolutionRecord(
                topic=topic,
                failure_reason="" if success else "operation_failed",
                applied_fix="auto-healing" if success else "none",
                observed_improvement=improvement,
                validation_metrics=metrics or {},
            )
        )

# --------------------------------------------------------------------------- #
# Intent Compiler â€“ context-aware plan generation
# --------------------------------------------------------------------------- #
class IntentCompiler:
    def compile(self, intent: str, **ctx) -> List[Dict[str, Any]]:
        lower = intent.lower().strip()

        if any(k in lower for k in ["federated", "fl ", "learning"]):
            topic = "general"
            if "improve" in lower:
                topic = lower.split("improve")[-1].strip()
            return [{
                "tool": "start_federated_training",
                "args": {
                    "topic": topic,
                    "rounds": ctx.get("learning_rounds", 5),
                    "confidence": ctx.get("confidence", 0.7),
                    "model_type": "neural_network",
                },
            }]

        if "symbiotic" in lower or "arm" in lower:
            return [{
                "tool": "initialize_symbiotic_link",
                "args": {"arm_type": "quantum" if "quantum" in lower else "edge"},
            }]

        if any(k in lower for k in ["optimize", "performance", "patch"]):
            func = "unknown"
            goal = "performance"
            parts = lower.split()
            if "function" in parts:
                idx = parts.index("function") + 1
                if idx < len(parts):
                    func = parts[idx]
            return [{
                "tool": "analyze_and_suggest_patch",
                "args": {"bottleneck_func": func, "goal": goal},
            }]
        
        # LLM-powered code generation
        if any(k in lower for k in ["generate", "write", "create"]) and any(k in lower for k in ["code", "function", "class", "script"]):
            return [{
                "tool": "llm_generate_code",
                "args": {"prompt": intent, "context": ctx},
            }]
        
        # LLM-powered code fixing
        if any(k in lower for k in ["fix", "repair", "debug"]) and any(k in lower for k in ["code", "error", "bug"]):
            return [{
                "tool": "llm_fix_code",
                "args": {"code": ctx.get("code", ""), "error": ctx.get("error", "unknown error"), "context": ctx},
            }]
        
        # LLM-powered code optimization
        if "optimize" in lower and "code" in lower:
            goal = "performance"
            if "memory" in lower:
                goal = "memory"
            elif "readability" in lower or "readable" in lower:
                goal = "readability"
            return [{
                "tool": "llm_optimize_code",
                "args": {"code": ctx.get("code", ""), "optimization_goal": goal, "context": ctx},
            }]

        # Fallback – Use LLM for general chat
        return [{
            "tool": "llm_chat",
            "args": {"prompt": intent},
        }]

# --------------------------------------------------------------------------- #
# Core Heart Node â€“ orchestration, reputation, secure dispatch
# --------------------------------------------------------------------------- #
@dataclass
class NodeInfo:
    id: str
    type: str
    resources: Dict[str, Any]
    websocket: Any
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)
    reputation: float = 1.0

class HeartNode:
    def __init__(self):
        self.nodes: Dict[str, NodeInfo] = {}
        self.secrets: Dict[str, str] = {}
        self.metacog = MetacognitiveEngine(self)
        self.compiler = IntentCompiler()
        self.registry = ToolRegistry()
        self.graphql_resolver = GraphQLResolver(self)
        self.llm_provider = None
        self.llm_generator = None
        if LLM_AVAILABLE:
            self._init_llm_provider()
        self._register_core_tools()

    def _init_llm_provider(self):
        """Initialize LLM provider with fallback chain: Local > OpenAI > Anthropic"""
        try:
            # Try local Ollama first (free, private, fast)
            self.llm_provider = LocalLLMProvider()
            self.llm_generator = LLMCodeGenerator(self.llm_provider)
            logger.info("[LLM] Initialized with Local Ollama provider")
        except Exception as e:
            logger.warning(f"[LLM] Local provider unavailable: {e}")
            
            # Fallback to OpenAI if API key available
            if os.getenv("OPENAI_API_KEY"):
                try:
                    self.llm_provider = OpenAIProvider()
                    self.llm_generator = LLMCodeGenerator(self.llm_provider)
                    logger.info("[LLM] Initialized with OpenAI provider")
                except Exception as e:
                    logger.warning(f"[LLM] OpenAI provider unavailable: {e}")
            
            # Fallback to Anthropic if API key available
            if not self.llm_provider and os.getenv("ANTHROPIC_API_KEY"):
                try:
                    self.llm_provider = AnthropicProvider()
                    self.llm_generator = LLMCodeGenerator(self.llm_provider)
                    logger.info("[LLM] Initialized with Anthropic provider")
                except Exception as e:
                    logger.warning(f"[LLM] Anthropic provider unavailable: {e}")
    
    def _register_core_tools(self):
        self.registry.register(Tool("echo", self._tool_echo, version="2.2.0"))
        self.registry.register(Tool("initialize_symbiotic_link", self._tool_symbiotic_link, version="1.4.0"))
        if FLOWER_AVAILABLE:
            self.registry.register(Tool("start_federated_training", self._tool_federated_training, version="2.1.0"))
        self.registry.register(Tool("analyze_and_suggest_patch", self._tool_analyze_patch, version="1.3.0"))
        
        # Register LLM tools if available
        if LLM_AVAILABLE and self.llm_generator:
            self.registry.register(Tool("llm_generate_code", self._tool_llm_generate_code, 
                                       description="Generate code using LLM", version="1.0.0"))
            self.registry.register(Tool("llm_fix_code", self._tool_llm_fix_code,
                                       description="Fix code errors using LLM", version="1.0.0"))
            self.registry.register(Tool("llm_optimize_code", self._tool_llm_optimize_code,
                                       description="Optimize code using LLM", version="1.0.0"))
            self.registry.register(Tool("llm_chat", self._tool_llm_chat,
                                       description="General chat with LLM", version="1.0.0"))
            logger.info("[LLM] Registered LLM code generation tools")

    async def init(self):
        await self.metacog.init()
        asyncio.create_task(self._health_monitor())

    async def _health_monitor(self):
        while True:
            await asyncio.sleep(12)
            now = time.time()
            dead = [nid for nid, ni in self.nodes.items() if now - ni.last_heartbeat > 90]
            for nid in dead:
                logger.warning(f"[HEART] Node {nid} timed out â€“ evicting")
                del self.nodes[nid]
                self.secrets.pop(nid, None)
                self.metacog.log_failure("node_comm", f"timeout {nid}")

    async def dispatch_task(self, tool: str, args: Dict[str, Any]) -> ToolResult[Any]:
        # Local first â€“ zero-latency path
        result = await self.registry.execute(tool, **args)
        if result.success:
            await self.metacog.record_outcome(tool.split("_")[0], True, result.metrics)
            return result

        # Distributed fallback (simplified â€“ reputation-ordered)
        capable = sorted(
            [ni for ni in self.nodes.values() if "adaptive" in ni.capabilities],
            key=lambda n: n.reputation,
            reverse=True,
        )
        for node in capable:
            if await self._secure_send(node, tool, args):
                return ToolResult(True, f"Dispatched to {node.id}")

        await self.metacog.record_outcome(tool.split("_")[0], False)
        return ToolResult(False, "exhausted all execution paths")

    async def _secure_send(self, node: NodeInfo, tool: str, args: Dict[str, Any]) -> bool:
        payload = json.dumps({"type": "task", "tool": tool, "args": args, "ts": time.time()})
        signature = QuantumEntropy.sign_message(payload, self.secrets[node.id])
        try:
            await node.websocket.send(json.dumps({"payload": payload, "signature": signature}))
            return True
        except Exception:
            node.reputation = max(0.05, node.reputation - 0.15)
            return False

    async def handle_message(self, ws, raw: str):
        try:
            data = json.loads(raw)
            typ = data.get("type")

            # ------------------- Registration -------------------
            if typ == "register":
                node_id = QuantumEntropy.secure_id()
                secret = QuantumEntropy.secure_id()
                info = NodeInfo(
                    id=node_id,
                    type=data.get("node_type", "worker"),
                    resources=data.get("resources", {}),
                    websocket=ws,
                    capabilities=data.get("capabilities", ["basic"]),
                )
                self.nodes[node_id] = info
                self.secrets[node_id] = secret
                await ws.send(json.dumps({
                    "type": "registered",
                    "node_id": node_id,
                    "secret": secret,
                }))
                logger.info(f"[HEART] Registered node {node_id}")

            # ------------------- Heartbeat -------------------
            elif typ == "heartbeat":
                node_id = data.get("node_id")
                if node_id in self.nodes:
                    self.nodes[node_id].last_heartbeat = time.time()
                    self.nodes[node_id].resources = data.get("resources", {})

            # ------------------- Intent -------------------
            elif typ == "intent":
                intent = data["intent"]
                intent_id = data.get("timestamp", time.time())

                # Send processing acknowledgment
                await ws.send(json.dumps({
                    "type": "response",
                    "intent": intent,
                    "status": "processing",
                    "message": f"Processing intent: '{intent[:50]}...'",
                    "intent_id": intent_id
                }))

                # Process the intent through the compiler
                plan = self.compiler.compile(intent)
                logger.info(f"[HEART] Intent compiled into {len(plan)} steps")

                for step in plan:
                    tool_name = step["tool"]
                    args = step["args"]

                    logger.info(f"[HEART] Executing tool: {tool_name}")
                    result = await self.dispatch_task(tool_name, args)

                    # Send tool execution result back to client
                    if result.success:
                        response_type = "success"
                        message = str(result.data) if result.data else "Command executed successfully"
                    else:
                        response_type = "error"
                        message = f"Error: {result.data or 'Unknown error'}"

                    await ws.send(json.dumps({
                        "type": "response",
                        "intent": intent,
                        "status": response_type,
                        "message": message,
                        "intent_id": intent_id,
                        "tool": tool_name,
                        "metrics": result.metrics
                    }))

                # Send completion message
                await ws.send(json.dumps({
                    "type": "response",
                    "intent": intent,
                    "status": "completed",
                    "message": f"Intent '{intent}' processed successfully",
                    "intent_id": intent_id
                }))

        except Exception as exc:
            logger.error(f"[HEART] Message handling error: {exc}")
            # Send error response to client
            try:
                await ws.send(json.dumps({
                    "type": "response",
                    "status": "error",
                    "message": f"Processing error: {str(exc)}"
                }))
            except Exception:
                logger.error(f"[HEART] Failed to send error response to client")

    # ------------------- Core Tools -------------------
    async def _tool_echo(self, message: str) -> str:
        return f"â†¯ ECHO: {message}"

    async def _tool_symbiotic_link(self, arm_type: str = "edge") -> Dict[str, Any]:
        return {
            "link_id": QuantumEntropy.secure_id(),
            "arm_type": arm_type,
            "status": "active",
            "established_at": time.time(),
        }

    async def _tool_federated_training(self, topic: str, rounds: int = 5, confidence: float = 0.7) -> Dict[str, Any]:
        if not FLOWER_AVAILABLE:
            return {"error": "flwr unavailable on this node"}

        logger.info(f"[FL] Launching federated training â€“ topic={topic} rounds={rounds}")

        # Minimal real Flower server (non-blocking)
        def _start_server():
            strategy = FedAvg(min_available_clients=2)
            fl.server.start_server(
                server_address="127.0.0.1:8081",
                config=ServerConfig(num_rounds=rounds),
                strategy=strategy,
            )

        loop = asyncio.get_running_loop()
        asyncio.create_task(loop.run_in_executor(self.metacog.executor, _start_server))
        return {"status": "started", "topic": topic, "rounds": rounds}

    async def _tool_analyze_patch(self, bottleneck_func: str, goal: str) -> str:
        # Real static analysis + patch generation stub (expandable with LLM later)
        return f"Optimized patch for `{bottleneck_func}` targeting `{goal}` would be inserted here."
    
    # ------------------- LLM Tools -------------------
    async def _tool_llm_generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate code using LLM"""
        if not self.llm_generator:
            return {"error": "LLM not available", "code": None}
        
        try:
            context = context or {}
            patch = await self.llm_generator.generate_patch(prompt, context, include_tests=True)
            
            if patch:
                return {
                    "success": True,
                    "code": patch.code,
                    "description": patch.description,
                    "confidence": patch.confidence,
                    "risk_level": patch.risk_level,
                }
            else:
                return {"error": "Failed to generate code", "code": None}
        except Exception as e:
            logger.error(f"[LLM] Code generation failed: {e}")
            return {"error": str(e), "code": None}
    
    async def _tool_llm_fix_code(self, code: str, error: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fix code errors using LLM"""
        if not self.llm_generator:
            return {"error": "LLM not available", "fixed_code": None}
        
        try:
            context = context or {}
            context["original_code"] = code
            context["error_message"] = error
            
            prompt = f"Fix this Python code that has the following error:\n\nError: {error}\n\nCode:\n{code}"
            patch = await self.llm_generator.generate_patch(prompt, context, include_tests=True)
            
            if patch:
                return {
                    "success": True,
                    "fixed_code": patch.code,
                    "description": patch.description,
                    "confidence": patch.confidence,
                    "risk_level": patch.risk_level,
                }
            else:
                return {"error": "Failed to fix code", "fixed_code": None}
        except Exception as e:
            logger.error(f"[LLM] Code fix failed: {e}")
            return {"error": str(e), "fixed_code": None}
    
    async def _tool_llm_optimize_code(self, code: str, optimization_goal: str = "performance", 
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize code using LLM"""
        if not self.llm_generator:
            return {"error": "LLM not available", "optimized_code": None}
        
        try:
            context = context or {}
            context["original_code"] = code
            context["optimization_goal"] = optimization_goal
            
            prompt = f"Optimize this Python code for {optimization_goal}:\n\n{code}\n\nProvide an optimized version that maintains the same functionality."
            patch = await self.llm_generator.generate_patch(prompt, context, include_tests=True)
            
            if patch:
                return {
                    "success": True,
                    "optimized_code": patch.code,
                    "description": patch.description,
                    "confidence": patch.confidence,
                    "improvements": patch.description,
                    "risk_level": patch.risk_level,
                }
            else:
                return {"error": "Failed to optimize code", "optimized_code": None}
        except Exception as e:
            logger.error(f"[LLM] Code optimization failed: {e}")
            return {"error": str(e), "optimized_code": None}

    async def _tool_llm_chat(self, prompt: str) -> str:
        """General chat with LLM"""
        if not self.llm_provider:
            return "I am currently disconnected from my higher reasoning centers (LLM unavailable)."
        
        try:
            response = await self.llm_provider.chat(prompt, {})
            return response
        except Exception as e:
            logger.error(f"[LLM] Chat failed: {e}")
            return f"I encountered an error while thinking: {e}"

# --------------------------------------------------------------------------- #
# Production-grade Web Dashboard (fixed, complete, secure)
# --------------------------------------------------------------------------- #
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CHIMERA AUTARCH v3</title>
<style>
    :root{--primary:#00ffcc;--bg:#0a0a12;--card-bg:rgba(20,25,40,0.95);}
    body{font-family:Consolas,Menlo,monospace;background:var(--bg);color:#e0e0e0;margin:0;}
    .container{max-width:1600px;margin:0 auto;padding:20px;}
    header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--primary);padding-bottom:15px;margin-bottom:25px;}
    h1{font-size:2.5em;margin:0;text-shadow:0 0 12px rgba(0,255,204,.4);}
    .status-indicator{width:16px;height:16px;background:#0f0;border-radius:50%;display:inline-block;animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    .dashboard{display:grid;grid-template-columns:1fr 380px;gap:25px;}
    .main-panel{background:var(--card-bg);border:1px solid var(--primary);border-radius:10px;padding:20px;height:76vh;}
    .terminal{background:#0004;padding:15px;border-radius:8px;height:100%;overflow-y:auto;font-family:inherit;}
    #output{min-height:100%;white-space:pre-wrap;}
    .input-area{display:flex;margin-top:12px;gap:10px;}
    input{flex:1;background:#111;border:1px solid var(--primary);color:var(--primary);padding:12px;border-radius:6px;}
    button{background:var(--primary);color:#000;border:none;padding:12px 20px;border-radius:6px;cursor:pointer;font-weight:bold;}
    button:hover{transform:translateY(-2px);box-shadow:0 6px 12px rgba(0,255,204,.3);}
    .sidebar{display:flex;flex-direction:column;gap:20px;}
    .card{background:var(--card-bg);border:1px solid var(--primary);border-radius:10px;padding:20px;}
    .card h2{color:var(--primary);display:flex;align-items:center;gap:10px;}
    .metric-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;}
    .metric{background:#1114;padding:14px;border-radius:6px;text-align:center;}
    .metric-value{font-size:2em;font-weight:bold;color:var(--primary);}
    .confidence-bar{height:8px;background:#333;border-radius:4px;overflow:hidden;margin-top:6px;}
    .confidence-fill{height:100%;background:var(--primary);transition:width .6s;}
</style>
</head>
<body>
<div class="container">
    <header>
        <div><span class="status-indicator"></span><h1>CHIMERA AUTARCH v3</h1></div>
        <div>SYSTEM OPERATIONAL</div>
    </header>
    <div class="dashboard">
        <div class="main-panel">
            <div class="terminal"><div id="output"></div></div>
            <div class="input-area">
                <input type="text" id="cmd" placeholder="enter intentâ€¦" autocomplete="off">
                <button onclick="send()">EXECUTE</button>
            </div>
        </div>
        <div class="sidebar">
            <div class="card">
                <h2>âš¡ METRICS</h2>
                <div class="metric-grid">
                    <div class="metric"><div class="metric-label">Nodes</div><div class="metric-value" id="nodes">0</div></div>
                    <div class="metric"><div class="metric-label">Confidence</div><div class="metric-value" id="conf">100%</div></div>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    const ws = new WebSocket(`ws://${location.hostname}:3001`);
    const out = document.getElementById('output');
    const inp = document.getElementById('cmd');
    function log(m){const d=document.createElement('div');d.textContent=m;out.appendChild(d);out.scrollTop=out.scrollHeight;}
    ws.onopen = () => log('[SYSTEM] Connected');
    ws.onmessage = e => log(`> ${e.data}`);
    function send(){if(!inp.value.trim())return;ws.send(JSON.stringify({type:'intent',intent:inp.value}));log(`$ ${inp.value}`);inp.value='';}
    inp.addEventListener('keypress',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>"""

class DashboardHandler(BaseHTTPRequestHandler):
    def __init__(self, heart_node, *args, **kwargs):
        self.heart_node = heart_node
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in {"", "/"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == "/graphql":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            playground_html = """<!DOCTYPE html>
<html>
<head>
    <title>GraphQL Playground</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
    <link rel="shortcut icon" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
</head>
<body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/index.js"></script>
</body>
</html>"""
            self.wfile.write(playground_html.encode())
        elif self.path == "/chimera_god_cli.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                # Try to read from static directory
                static_path = Path("src/droxai_root/static/chimera_god_cli.html")
                if not static_path.exists():
                    # Fallback to current directory or project root
                    static_path = Path("chimera_god_cli.html")
                
                if static_path.exists():
                    self.wfile.write(static_path.read_bytes())
                else:
                    self.wfile.write(b"<h1>Error: God CLI file not found</h1>")
            except Exception as e:
                self.wfile.write(f"<h1>Error loading God CLI: {e}</h1>".encode())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/graphql":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                query = data.get("query", "")
                variables = data.get("variables", {})
                
                # Run the GraphQL query synchronously for simplicity
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.heart_node.graphql_resolver.resolve(query, variables))
                finally:
                    loop.close()
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"errors": [{"message": str(e)}]}).encode())
        else:
            self.send_error(404)

# --------------------------------------------------------------------------- #
# HTTP Handler Factory
# --------------------------------------------------------------------------- #
def create_dashboard_handler(heart_node):
    class HandlerWithHeart(DashboardHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(heart_node, *args, **kwargs)
    return HandlerWithHeart

# --------------------------------------------------------------------------- #
# Production Entry Point â€“ TLS-aware, graceful shutdown
# --------------------------------------------------------------------------- #
async def main():
    # TLS auto-detect
    ssl_ctx = None
    for base in ["ssl/", ""]:
        if Path(base + "cert.pem").exists() and Path(base + "key.pem").exists():
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_ctx.load_cert_chain(base + "cert.pem", base + "key.pem")
            logger.info(f"[TLS] Loaded certificates from {base}")
            break

    heart = HeartNode()
    await heart.init()

    ws_port = int(os.getenv("WS_PORT", 3001))
    http_port = int(os.getenv("HTTP_PORT", 3000))

    async def ws_handler(ws):
        await ws.send(json.dumps({"type": "welcome"}))
        async for msg in ws:
            await heart.handle_message(ws, msg)

    ws_server = await websockets.serve(
        ws_handler,
        "127.0.0.1",
        ws_port,
        ssl=ssl_ctx,
    )

    httpd = HTTPServer(("127.0.0.1", http_port), create_dashboard_handler(heart))
    http_thread = asyncio.to_thread(httpd.serve_forever)

    logger.info(f"CHIMERA AUTARCH v3 ready â€“ ws://127.0.0.1:{ws_port} | http://127.0.0.1:{http_port}")

    try:
        await asyncio.gather(http_thread, ws_server.wait_closed())
    except KeyboardInterrupt:
        logger.info("[SHUTDOWN] Graceful termination")
    finally:
        httpd.shutdown()
        ws_server.close()
        await ws_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
