"""
Unit tests for CHIMERA AUTARCH core components
"""
import unittest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chimera import (
    QuantumEntropy, ToolResult, Tool, ToolRegistry,
    EvolutionRecord, FailurePattern, IntentCompiler
)


class TestQuantumEntropy(unittest.TestCase):
    """Test cryptographic utilities"""
    
    def test_secure_id_generation(self):
        """Test secure ID generation"""
        id1 = QuantumEntropy.secure_id()
        id2 = QuantumEntropy.secure_id()
        
        # IDs should be unique
        self.assertNotEqual(id1, id2)
        
        # IDs should be non-empty strings
        self.assertIsInstance(id1, str)
        self.assertGreater(len(id1), 0)
    
    def test_message_signing(self):
        """Test message signing with HMAC"""
        message = "test message"
        secret = "test_secret"
        
        signature1 = QuantumEntropy.sign_message(message, secret)
        signature2 = QuantumEntropy.sign_message(message, secret)
        
        # Same message and secret should produce same signature
        self.assertEqual(signature1, signature2)
        
        # Different secret should produce different signature
        signature3 = QuantumEntropy.sign_message(message, "different_secret")
        self.assertNotEqual(signature1, signature3)


class TestToolRegistry(unittest.TestCase):
    """Test tool registration and execution"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = ToolRegistry()
    
    def test_tool_registration(self):
        """Test registering a tool"""
        async def test_func():
            return "test result"
        
        tool = Tool(
            name="test_tool",
            func=test_func,
            description="Test tool",
            version="1.0.0"
        )
        
        self.registry.register(tool)
        self.assertIn("test_tool", self.registry.tools)
        self.assertEqual(self.registry.tools["test_tool"].name, "test_tool")
    
    def test_tool_execution(self):
        """Test executing a registered tool"""
        async def echo_func(message: str):
            return f"Echo: {message}"
        
        tool = Tool(name="echo", func=echo_func)
        self.registry.register(tool)
        
        # Execute tool
        async def run_test():
            result = await self.registry.execute("echo", message="Hello")
            self.assertTrue(result.success)
            self.assertEqual(result.data, "Echo: Hello")
        
        asyncio.run(run_test())
    
    def test_tool_not_found(self):
        """Test executing non-existent tool"""
        async def run_test():
            result = await self.registry.execute("nonexistent")
            self.assertFalse(result.success)
            self.assertIn("not found", result.data)
        
        asyncio.run(run_test())


class TestFailurePattern(unittest.TestCase):
    """Test failure pattern tracking"""
    
    def test_failure_pattern_initialization(self):
        """Test FailurePattern initialization"""
        pattern = FailurePattern("test_topic")
        
        self.assertEqual(pattern.topic, "test_topic")
        self.assertEqual(pattern.count, 0)
        self.assertEqual(pattern.confidence, 1.0)
        self.assertFalse(pattern.learning_triggered)
    
    def test_record_success(self):
        """Test recording successful attempts"""
        pattern = FailurePattern("test_topic")
        
        # Record successes
        for _ in range(10):
            pattern.record_attempt(True)
        
        self.assertEqual(pattern.count, 10)
        self.assertEqual(pattern.confidence, 1.0)
    
    def test_record_failure(self):
        """Test recording failed attempts"""
        pattern = FailurePattern("test_topic")
        
        # Record failures
        for _ in range(5):
            pattern.record_attempt(False)
        
        self.assertEqual(pattern.count, 5)
        self.assertEqual(pattern.confidence, 0.0)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        pattern = FailurePattern("test_topic")
        
        # 7 successes, 3 failures = 70% confidence
        for _ in range(7):
            pattern.record_attempt(True)
        for _ in range(3):
            pattern.record_attempt(False)
        
        self.assertEqual(pattern.count, 10)
        self.assertEqual(pattern.confidence, 0.7)


class TestIntentCompiler(unittest.TestCase):
    """Test intent compilation to tool calls"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = ToolRegistry()
        
        # Register mock tools for testing
        async def mock_tool(**kwargs):
            return ToolResult(success=True, data={"result": "mock"})
        
        self.registry.register(Tool(
            name="start_federated_training",
            func=mock_tool,
            description="Start federated learning training"
        ))
        self.registry.register(Tool(
            name="initialize_symbiotic_link",
            func=mock_tool,
            description="Initialize symbiotic link"
        ))
        self.registry.register(Tool(
            name="analyze_and_suggest_patch",
            func=mock_tool,
            description="Analyze and suggest code patches"
        ))
        self.registry.register(Tool(
            name="echo",
            func=mock_tool,
            description="Echo tool"
        ))
        
        self.compiler = IntentCompiler(self.registry)
    
    def test_federated_learning_intent(self):
        """Test compiling federated learning intent"""
        plan = self.compiler.compile("start federated learning")
        
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool"], "start_federated_training")
        self.assertIn("model_type", plan[0]["args"])
    
    def test_symbiotic_link_intent(self):
        """Test compiling symbiotic link intent"""
        plan = self.compiler.compile("initialize symbiotic arm")
        
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool"], "initialize_symbiotic_link")
        self.assertIn("arm_type", plan[0]["args"])
    
    def test_code_optimization_intent(self):
        """Test compiling code optimization intent"""
        plan = self.compiler.compile("optimize function test_func for performance")
        
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool"], "analyze_and_suggest_patch")
        self.assertIn("bottleneck_func", plan[0]["args"])
        self.assertIn("goal", plan[0]["args"])
    
    def test_default_echo_intent(self):
        """Test default echo for unknown intents"""
        plan = self.compiler.compile("unknown command")
        
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool"], "echo")


class TestEvolutionRecord(unittest.TestCase):
    """Test evolution tracking"""
    
    def test_evolution_record_creation(self):
        """Test creating an evolution record"""
        record = EvolutionRecord(
            topic="test_topic",
            failure_reason="Test failure",
            applied_fix="Test fix",
            observed_improvement=0.15
        )
        
        self.assertEqual(record.topic, "test_topic")
        self.assertEqual(record.failure_reason, "Test failure")
        self.assertEqual(record.applied_fix, "Test fix")
        self.assertEqual(record.observed_improvement, 0.15)
        self.assertIsNotNone(record.id)
        self.assertGreater(record.timestamp, 0)


if __name__ == "__main__":
    unittest.main()

