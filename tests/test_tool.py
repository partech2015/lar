# tests/test_tool.py

import pytest
from lar import GraphExecutor, ToolNode, AddValueNode, GraphState

# --- Define some "tools" to test ---

def add_numbers(a: int, b: int) -> int:
    """A simple tool that succeeds."""
    return a + b

def failing_tool():
    """A simple tool that always fails."""
    raise ValueError("This tool was designed to fail")

# --- Tests ---

def test_tool_success_path():
    """Tests that the ToolNode runs a function and saves the output."""
    
    # 1. Arrange
    
    # Define the destination node
    success_node = AddValueNode(key="status", value="success", next_node=None)
    
    # Define the tool node
    tool = ToolNode(
        tool_function=add_numbers,
        input_keys=["num1", "num2"],  # Will read state.get("num1") and state.get("num2")
        output_key="sum_result",     # Will write to state.set("sum_result", ...)
        next_node=success_node,
        error_node=None              # We don't expect an error
    )
    
    executor = GraphExecutor()
    initial_state = {"num1": 10, "num2": 5}

    # 2. Act
    
    # --- THIS IS THE FIX ---
    # The variable is `tool`, not `start_node`
    result = executor.run(tool, initial_state)
    final_state = result["state"]
    # --- END FIX ---

    # 3. Assert
    # Check that the tool's output was saved
    assert final_state.get("sum_result") == 15
    # Check that the success_node was run
    assert final_state.get("status") == "success"


def test_tool_failure_path():
    """Tests that the ToolNode routes to the error_node on failure."""
    
    # 1. Arrange
    
    # Define the destination nodes
    success_node = AddValueNode(key="status", value="success", next_node=None)
    error_node = AddValueNode(key="status", value="failed", next_node=None)
    
    # Define the tool node
    tool = ToolNode(
        tool_function=failing_tool,
        input_keys=[],              # No inputs
        output_key="never_set",     # This key should not be set
        next_node=success_node,     # This node should not be run
        error_node=error_node       # This node *should* be run
    )
    
    executor = GraphExecutor()
    initial_state = {}

    # 2. Act
    
    # --- THIS IS THE FIX ---
    # We must unpack the `result` dictionary to get the `state`
    result = executor.run(tool, initial_state)
    final_state = result["state"]
    # --- END FIX ---

    # 3. Assert
    # Check that the error_node was run
    assert final_state.get("status") == "failed"
    # Check that the success output was never set
    assert final_state.get("never_set") is None
    # Check that the error message was saved to the state
    assert "This tool was designed to fail" in final_state.get("last_error")