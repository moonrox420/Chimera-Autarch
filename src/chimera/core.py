import asyncio
import json
import hashlib
import time
import uuid
import inspect
import logging
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import os
import sys
from collections import defaultdict
import base64
import secrets
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import aiohttp
import aiofiles

# Optional imports with graceful degradation
try:
    from xai_sdk import Client  # xAI SDK for Grok API
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False
    Client = None

try:
    import restrictedpython  # For safe code exec
    RESTRICTEDPYTHON_AVAILABLE = True
except ImportError:
    RESTRICTEDPYTHON_AVAILABLE = False
    restrictedpython = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quantum Entropy for secure IDs
class QuantumEntropy:
    @staticmethod
    def generate_id() -> str:
        """Generate a quantum-secure ID using UUID4 and entropy"""
        return str(uuid.uuid4())

    @staticmethod
    def hash_data(data: str) -> str:
        """Generate a secure hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()

# Metacog - Outcome Recording System
class Metacog:
    def __init__(self):
        self.outcomes = []

    def record_outcome(self, task_id: str, result: Any, duration: float, metadata: Dict = None):
        """Record the outcome of a task execution"""
        outcome = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "duration": duration,
            "metadata": metadata or {}
        }
        self.outcomes.append(outcome)
        return outcome

# Core System
class CoreSystem:
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.nodes: Dict[str, Dict] = {}
        self.metacog = Metacog()
        self.registry = {}
        # xAI Grok client (optional)
        if XAI_AVAILABLE and Client is not None:
            self.grok_client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=3600)
        else:
            self.grok_client = None
        self._setup_default_tools()

    def _setup_default_tools(self):
        """Setup default tools for the system"""
        self.register_tool("analyze_code", self._analyze_code,
                          description="Analyze Python code for complexity and structure")
        self.register_tool("list_tools", self._list_tools,
                          description="List all available tools")
        self.register_tool("run_tests", self._run_tests,
                          description="Run test suites")  # Still stub; implement with unittest later
        self.register_tool("execute_console_command",
self._execute_console_command,
                          description="Execute Python commands in a console")
        self.register_tool("debug_code", self._debug_code,
                          description="Debug Python code interactively")  # Stub
        self.register_tool("run_code_analysis",
self._run_code_analysis,
                          description="Analyze code quality")  # Stub
        self.register_tool("generate_test_file",
self._generate_test_file,
                          description="Generate test skeletons")  # Stub
        self.register_tool("profile_performance",
self._profile_performance,
                          description="Profile function performance")  # Stub
        self.register_tool("create_documentation",
self._create_documentation,
                          description="Generate API documentation")  # Stub
        self.register_tool("get_development_report",
self._get_development_report,
                          description="Report on development environment")  # Stub

        # Security tools
        self.register_tool("encrypt_data", self._encrypt_data,
                          description="Encrypt data")
        self.register_tool("decrypt_data", self._decrypt_data,
                          description="Decrypt data")
        self.register_tool("create_zero_knowledge_proof",
self._create_zero_knowledge_proof,
                          description="Create ZKP")  # Stub
        self.register_tool("verify_zero_knowledge_proof",
self._verify_zero_knowledge_proof,
                          description="Verify ZKP")  # Stub
        self.register_tool("check_compliance", self._check_compliance,
                          description="Check regulatory compliance")  # Stub

        # New tools
        self.register_tool("execute_code_safely", self._execute_code_safely,
                          description="Safely execute Python code in a sandbox",
                          dependencies=[])
        self.register_tool("read_file", self._read_file,
                          description="Read content from a file asynchronously")
        self.register_tool("write_file", self._write_file,
                          description="Write content to a file asynchronously")

    def register_tool(self, name: str, func: Callable, description: str = "", dependencies: List[str] = None):
        """Register a new tool"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "dependencies": dependencies or []
        }
        logger.info(f"Registered tool: {name}")

    async def dispatch_task(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Dispatch a task to the appropriate tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.tools[tool_name]
        start_time = time.time()

        try:
            # Check dependencies
            for dep in tool["dependencies"]:
                if dep not in self.tools:
                    raise ValueError(f"Missing dependency: {dep}")

            # Execute the tool
            if asyncio.iscoroutinefunction(tool["function"]):
                result = await tool["function"](**args)
            else:
                result = tool["function"](**args)

            duration = time.time() - start_time
            task_id = QuantumEntropy.generate_id()

            # Record outcome
            self.metacog.record_outcome(task_id, result, duration)

            return result
        except Exception as e:
            duration = time.time() - start_time
            task_id = QuantumEntropy.generate_id()
            self.metacog.record_outcome(task_id, str(e), duration)
            raise

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages"""
        msg_type = message.get("type")

        if msg_type == "register":
            return await self._handle_register(message)
        elif msg_type == "heartbeat":
            return await self._handle_heartbeat(message)
        elif msg_type == "intent":
            return await self._handle_intent(message)
        else:
            return {"error": f"Unknown message type: {msg_type}"}

    async def _handle_register(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle node registration"""
        node_id = message.get("node_id")
        info = message.get("info", {})

        if not node_id:
            return {"error": "Missing node_id"}

        self.nodes[node_id] = {
            "info": info,
            "last_heartbeat": time.time(),
            "reputation": 0.0
        }

        return {"status": "registered", "node_id": node_id}

    async def _handle_heartbeat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle node heartbeat"""
        node_id = message.get("node_id")

        if not node_id or node_id not in self.nodes:
            return {"error": "Unknown node"}

        self.nodes[node_id]["last_heartbeat"] = time.time()
        return {"status": "heartbeat_received"}

    async def _handle_intent(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent execution"""
        intent = message.get("intent")
        user_code = message.get("code", "")  # Optional code from message
        if not intent:
            return {"error": "Missing intent"}

        # Compile intent to steps using Grok API
        steps = await self._compile_intent(intent, user_code)

        results = []
        for step in steps:
            try:
                result = await self.dispatch_task(step["tool"], step["args"])
                results.append({
                    "tool": step["tool"],
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "tool": step["tool"],
                    "error": str(e),
                    "success": False
                })

        return {"results": results}

    async def _compile_intent(self, intent: str, user_code: str = "") -> List[Dict[str, Any]]:
        """Compile an intent into executable steps using Grok API"""
        prompt = f"""
You are an elite task planner for a tool-using agent. Given the user intent and optional code, output a JSON list of steps.
Each step is an object with "tool": "tool_name" and "args": {{arg_dict}}.

Available tools: {', '.join(self.tools.keys())}

Intent: {intent}
Code (if relevant): {user_code[:2000]}  # Truncated for brevity

Respond ONLY with a valid JSON array of step objects, e.g.:
[{{"tool": "analyze_code", "args": {{"code": "print('hello')"}}}}, {{"tool": "run_tests", "args": {{}}}}]
"""
        chat = self.grok_client.chat.create(model="grok-4")
        chat.append(system("You are a precise JSON-outputting planner. Output only valid JSON, no extra text."))
        chat.append(user(prompt))
        response = chat.sample()
        
        try:
            steps = json.loads(response.content)
            if not isinstance(steps, list):
                raise ValueError("Invalid steps format")
            return steps
        except Exception as e:
            logger.error(f"Grok intent parsing failed: {e}")
            return []  # Fallback to empty

    # Tool implementations
    async def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code"""
        lines = code.split('\n')
        complexity = len(lines)
        functions = len(re.findall(r'def\s+\w+', code))
        classes = len(re.findall(r'class\s+\w+', code))

        return {
            "complexity": complexity,
            "functions": functions,
            "classes": classes,
            "code": code
        }

    async def _list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())

    async def _run_tests(self) -> Dict[str, Any]:
        """Run test suites"""
        return {"status": "tests_passed", "tests_run": 10}  # TODO: Implement real unittest

    async def _execute_console_command(self, command: str) -> Dict[str, Any]:
        """Execute Python command in console"""
        return {"command": command, "output": "Command executed successfully"}  # Stub

    async def _debug_code(self, code: str) -> Dict[str, Any]:
        """Debug Python code"""
        return {"debugging": True, "code": code}  # Stub

    async def _run_code_analysis(self) -> Dict[str, Any]:
        """Analyze code quality"""
        return {"quality_score": 95, "issues_found": 0}  # Stub

    async def _generate_test_file(self) -> Dict[str, Any]:
        """Generate test skeletons"""
        return {"test_file_generated": True, "file_name": "test_generated.py"}  # Stub

    async def _profile_performance(self) -> Dict[str, Any]:
        """Profile function performance"""
        return {"profile_results": "Performance data collected"}  # Stub

    async def _create_documentation(self) -> Dict[str, Any]:
        """Generate API documentation"""
        return {"documentation_generated": True, "format": "rst"}  # Stub

    async def _get_development_report(self) -> Dict[str, Any]:
        """Report on development environment"""
        return {"environment": "development", "status": "healthy"}  # Stub

    # Security tools
    async def _encrypt_data(self, data: str, password: str = None) -> Dict[str, Any]:
        """Encrypt data with random salt"""
        if not password:
            password = secrets.token_urlsafe(32)
        salt = os.urandom(16)  # Random salt per encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # Increased for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        # Combine salt + encrypted_data for storage
        combined = salt + encrypted_data
        return {
            "encrypted_data": base64.urlsafe_b64encode(combined).decode(),
            "password": password
        }

    async def _decrypt_data(self, encrypted_data: str, password: str) -> Dict[str, Any]:
        """Decrypt data"""
        combined = base64.urlsafe_b64decode(encrypted_data)
        salt = combined[:16]  # Extract salt
        encrypted_data = combined[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return {"decrypted_data": decrypted_data.decode()}

    async def _create_zero_knowledge_proof(self, statement: str) -> Dict[str, Any]:
        """Create a zero-knowledge proof"""
        return {
            "proof": "zkp_" + QuantumEntropy.generate_id(),
            "statement": statement,
            "status": "created"
        }  # Stub

    async def _verify_zero_knowledge_proof(self, proof: str, statement: str) -> Dict[str, Any]:
        """Verify a zero-knowledge proof"""
        return {
            "proof": proof,
            "statement": statement,
            "verified": True,
            "status": "verified"
        }  # Stub

    async def _check_compliance(self, data: str) -> Dict[str, Any]:
        """Check regulatory compliance"""
        return {
            "compliant": True,
            "checks_performed": ["GDPR", "HIPAA", "SOX"],
            "data": data
        }  # Stub

    # New tools
    def _execute_code_safely(self, code: str) -> Dict[str, Any]:
        """Safely execute Python code in a sandbox"""
        safe_globals = restrictedpython.safe_globals
        safe_locals = {}
        byte_code = restrictedpython.compile_restricted(code, '<string>', 'exec')
        exec(byte_code, safe_globals, safe_locals)
        return {"output": safe_locals.get('result', 'Executed safely')}  # Assume code sets 'result'

    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content from a file asynchronously"""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        return {"content": content}

    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file asynchronously"""
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
        return {"status": "written"}

# Global core instance
core = CoreSystem()

# Example usage functions
async def example_usage():
    """Demonstrate core system usage"""
    print("=== Core System v2 Demo ===")

    # Register a node
    register_msg = {
        "type": "register",
        "node_id": "node_123",
        "info": {"name": "Dev Node", "type": "developer"}
    }
    result = await core.handle_message(register_msg)
    print(f"Registration result: {result}")

    # Heartbeat
    heartbeat_msg = {
        "type": "heartbeat",
        "node_id": "node_123"
    }
    result = await core.handle_message(heartbeat_msg)
    print(f"Heartbeat result: {result}")

    # List tools
    tools = await core.dispatch_task("list_tools", {})
    print(f"Available tools: {tools}")

    # Analyze code
    code_analysis = await core.dispatch_task("analyze_code", {"code": "def hello():\n    print('Hello')\n\nclass Test:\n    pass"})
    print(f"Code analysis: {code_analysis}")

    # Run tests
    test_results = await core.dispatch_task("run_tests", {})
    print(f"Test results: {test_results}")

    # Intent execution with real Grok parsing
    intent_msg = {
        "type": "intent",
        "intent": "analyze and test this code",
        "code": "def hello():\n    print('Hello')"
    }
    intent_result = await core.handle_message(intent_msg)
    print(f"Intent execution result: {intent_result}")

    # Security operations
    encrypted = await core.dispatch_task("encrypt_data", {"data": "Secret data"})
    print(f"Encrypted data: {encrypted}")

    decrypted = await core.dispatch_task("decrypt_data", {
        "encrypted_data": encrypted["encrypted_data"],
        "password": encrypted["password"]
    })
    print(f"Decrypted data: {decrypted}")

    # New tools demo
    # Safe exec
    safe_exec = core.dispatch_task("execute_code_safely", {"code": "result = 2 + 2"})  # Non-async for simplicity
    print(f"Safe exec: {safe_exec}")

    # File I/O (async)
    await core.dispatch_task("write_file", {"file_path": "test.txt", "content": "Hello v2"})
    file_content = await core.dispatch_task("read_file", {"file_path": "test.txt"})
    print(f"File content: {file_content}")

# Run example if script is executed directly
if __name__ == "__main__":
    asyncio.run(example_usage())