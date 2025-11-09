# tests/test_router.py

import pytest
from lar import GraphExecutor, AddValueNode, RouterNode, GraphState

# --- Define our "decision logic" ---
# This is the function the RouterNode will call.
def number_router(state: GraphState) -> str:
    """Checks a 'number' in the state and returns a route key."""
    number = state.get("number", 0)
    if number > 10:
        return "greater"
    else:
        return "less_or_equal"

# --- Tests ---

def test_router_path_greater():
    """Tests that the router correctly takes the 'greater' path."""
    
    # 1. Arrange
    
    # Define the destination nodes
    greater_node = AddValueNode(key="result", value="was_greater", next_node=None)
    less_node = AddValueNode(key="result", value="was_less", next_node=None)
    
    # Define the router's path map
    path_map = {
        "greater": greater_node,
        "less_or_equal": less_node
    }
    
    # Define the router node itself
    router = RouterNode(
        decision_function=number_router,
        path_map=path_map
    )
    
    executor = GraphExecutor()
    # We start the state with a number > 10
    initial_state = {"number": 20}

    # 2. Act
    # This test was already correct
    result = executor.run(router, initial_state)
    final_state = result["state"]

    # 3. Assert
    # We check that the 'greater_node' was run
    assert final_state.get("result") == "was_greater"


def test_router_path_less():
    """Tests that the router correctly takes the 'less_or_equal' path."""
    
    # 1. Arrange
    greater_node = AddValueNode(key="result", value="was_greater", next_node=None)
    less_node = AddValueNode(key="result", value="was_less", next_node=None)
    
    path_map = {
        "greater": greater_node,
        "less_or_equal": less_node
    }
    
    router = RouterNode(
        decision_function=number_router,
        path_map=path_map
    )
    
    executor = GraphExecutor()
    # We start the state with a number < 10
    initial_state = {"number": 5}

    # 2. Act
    # --- THIS IS THE FIX ---
    # We must unpack the result dictionary here as well.
    result = executor.run(router, initial_state)
    final_state = result["state"]
    # --- END FIX ---

    # 3. Assert
    # We check that the 'less_node' was run
    assert final_state.get("result") == "was_less"