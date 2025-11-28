import pytest

from chimera_autarch import IntentCompiler


def test_compile_default_includes_choices():
    compiler = IntentCompiler()
    plan = compiler.compile("this is not a recognized intent")
    assert isinstance(plan, list)
    assert len(plan) == 1
    step = plan[0]
    assert step["tool"] == "echo"
    assert "choices" in step
    # Validate choices structure
    choices = step["choices"]
    assert isinstance(choices, list)
    assert any(c["tool"] == "echo" for c in choices)
    assert any(c["tool"] == "analyze_and_suggest_patch" for c in choices)
    assert any(c["tool"] == "start_federated_training" for c in choices)


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

