# CHIMERA Core Package
# Self-evolving AI orchestration system

from .core import (
    HeartNode,
    ToolRegistry,
    MetacognitiveEngine,
    Tool,
    ToolResult,
    QuantumEntropy,
    FailurePattern,
    EvolutionRecord,
    PersistenceLayer,
    IntentCompiler,
)
from .llm import (
    LLMIntegration,
    CodeGenerator,
    CodePatch,
    PatchResult,
    OpenAIProvider,
    AnthropicProvider,
    LocalLLMProvider,
)
from .web import (
    WebInterface,
    DashboardHandler,
    create_dashboard_handler,
    DASHBOARD_HTML,
)
from .devex import (
    DeveloperExperienceIntegration,
    InteractiveDebugger,
    TestRunner,
    CodeQualityAnalyzer,
    PerformanceProfiler,
    DocumentationGenerator,
    DevelopmentConsole,
)

__version__ = "3.0.0"
__all__ = [
    # Core components
    'HeartNode',
    'ToolRegistry',
    'MetacognitiveEngine',
    'Tool',
    'ToolResult',
    'QuantumEntropy',
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