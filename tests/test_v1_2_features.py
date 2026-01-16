import pytest
from lar.utils import truncate_for_log
from lar.executor import GraphExecutor
from lar.node import BaseNode
from lar.state import GraphState

# --- Mock Node for Testing Token Aggregation ---
class MockLLMNode(BaseNode):
    def __init__(self, model_name, tokens):
        self.model_name = model_name
        self.tokens = tokens
        self.next_node = None

    def execute(self, state: GraphState):
        usage = {
            "prompt_tokens": self.tokens,
            "output_tokens": self.tokens,
            "total_tokens": self.tokens * 2,
            "model": self.model_name
        }
        state.set("__last_run_metadata", usage)
        return self.next_node

# --- Unit Test for Truncation ---
def test_truncate_for_log():
    # Test short string
    assert truncate_for_log("hello", 10) == "hello"
    
    # Test dictionary
    d = {"a": 1, "b": 2}
    assert "{\n  \"a\": 1" in truncate_for_log(d)
    
    # Test truncation
    long_str = "x" * 100
    truncated = truncate_for_log(long_str, max_length=60)
    assert "truncated" in truncated
    assert len(truncated) <= 60

# --- Integration Test for Token Aggregation ---
def test_token_aggregation():
    # Setup
    node1 = MockLLMNode(model_name="ollama/phi4", tokens=100)
    node2 = MockLLMNode(model_name="gemini-pro", tokens=500)
    node3 = MockLLMNode(model_name="ollama/phi4", tokens=50) # Same model as node1
    
    # Link them
    node1.next_node = node2
    node2.next_node = node3
    
    executor = GraphExecutor(log_dir="test_logs")
    
    # Monkeypatch _save_log to capture summary without IO
    captured_summary = {}
    
    def mock_save(history, run_id, summary):
        captured_summary.update(summary)
    
    executor._save_log = mock_save
    
    # Run
    list(executor.run_step_by_step(node1, {}))
    
    # Assertions
    breakdown = captured_summary.get("tokens_by_model", {})
    
    # Node 1: 200 total (100+100)
    # Node 3: 100 total (50+50)
    # Total Ollama: 300
    assert breakdown["ollama/phi4"] == 300
    
    # Node 2: 1000 total (500+500)
    # Total Gemini: 1000
    assert breakdown["gemini-pro"] == 1000
    
    assert captured_summary["total_tokens"] == 1300
