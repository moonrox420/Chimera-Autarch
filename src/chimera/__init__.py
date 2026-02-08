# CHIMERA Core Package
# Self-evolving AI orchestration system

# Import stubs and available classes from core
from .core import (
    QuantumEntropy,
    Metacog,
    CoreSystem,
)

# Try to import from droxai_root if available (legacy compatibility)
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "droxai_root"))
    from chimera_autarch import (
        HeartNode,
        ToolRegistry,
        MetacognitiveEngine,
        Tool,
        ToolResult,
        FailurePattern,
        EvolutionRecord,
        PersistenceLayer,
        IntentCompiler,
    )
    LEGACY_AVAILABLE = True
except ImportError:
    # Create stub classes for compatibility
    LEGACY_AVAILABLE = False
    class HeartNode:
        pass
    class ToolRegistry:
        pass
    class MetacognitiveEngine:
        pass
    class Tool:
        pass
    class ToolResult:
        pass
    class FailurePattern:
        pass
    class EvolutionRecord:
        pass
    class PersistenceLayer:
        pass
    class IntentCompiler:
        pass

# Try to import LLM components (may not exist)
try:
    from .llm import (
        OllamaClient,
        OLLAMA_CLIENT,
    )
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    class OllamaClient:
        pass
    OLLAMA_CLIENT = None

# Create stub classes for components that don't exist yet
class LLMIntegration:
    pass
class CodeGenerator:
    pass
class CodePatch:
    pass
class PatchResult:
    pass
class OpenAIProvider:
    pass
class AnthropicProvider:
    pass
class LocalLLMProvider:
    pass

# Web components stubs
class WebInterface:
    pass
class DashboardHandler:
    pass
def create_dashboard_handler():
    pass
DASHBOARD_HTML = ""

# DevEx stubs
class DeveloperExperienceIntegration:
    pass
class InteractiveDebugger:
    pass
class TestRunner:
    pass
class CodeQualityAnalyzer:
    pass
class PerformanceProfiler:
    pass
class DocumentationGenerator:
    pass
class DevelopmentConsole:
    pass

__version__ = "3.0.0"
__all__ = [
    # Core components
    'HeartNode',
    'ToolRegistry',
    'MetacognitiveEngine',
    'Tool',
    'ToolResult',
    'QuantumEntropy',
    'Metacog',
    'CoreSystem',
    'FailurePattern',
    'EvolutionRecord',
    'PersistenceLayer',
    'IntentCompiler',
    # LLM components
    'LLMIntegration',
    'CodeGenerator',
    'CodePatch',
    'PatchResult',
    'OpenAIProvider',
    'AnthropicProvider',
    'LocalLLMProvider',
    'OllamaClient',
    'OLLAMA_CLIENT',
    # Web components
    'WebInterface',
    'DashboardHandler',
    'create_dashboard_handler',
    'DASHBOARD_HTML',
    # Developer Experience components
    'DeveloperExperienceIntegration',
    'InteractiveDebugger',
    'TestRunner',
    'CodeQualityAnalyzer',
    'PerformanceProfiler',
    'DocumentationGenerator',
    'DevelopmentConsole',
]