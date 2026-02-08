import pytest

from chimera_autarch import IntentCompiler


def test_compile_default_includes_choices():
    compiler = IntentCompiler()
    plan = compiler.compile("this is not a recognized intent")
    assert isinstance(plan, list)
    assert len(plan) == 1
    step = plan[0]
    # Default fallback is llm_chat
    assert step["tool"] == "llm_chat"


def test_compile_federated_learning_and_optimize():
    compiler = IntentCompiler()
    # Federated learning intent
    plan = compiler.compile("start federated learning to improve our understanding of image detection")
    assert isinstance(plan, list)
    assert plan[0]["tool"] == "start_federated_training"

    # Code optimization intent
    plan = compiler.compile("optimize function process_image for performance")
    assert isinstance(plan, list)
    assert plan[0]["tool"] == "analyze_and_suggest_patch"

