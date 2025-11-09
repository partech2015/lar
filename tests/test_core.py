# tests/test_core.py

import pytest
from lar import GraphExecutor, AddValueNode, PrintStateNode, GraphState

def test_simple_graph_execution():
    """
    Tests a simple, linear A -> B graph.
    - Node A (AddValueNode) adds a value to the state.
    - Node B (PrintStateNode) prints the state and ends the graph.
    We will then assert that the final state contains the value from Node A.
    """
    
    # 1. Arrange: Set up the graph and executor
    
    # Define the initial data for the graph
    initial_state = {"user": "Solo Developer"}
    
    # Define the nodes in reverse order, from end to start
    # Node B: The end of the graph
    end_node = PrintStateNode()
    
    # Node A: The start of the graph
    # This node will run, then return `end_node` as the next step
    start_node = AddValueNode(
        key="message", 
        value="Hello Lár!", 
        next_node=end_node
    )
    
    # Create the engine that will run the graph
    executor = GraphExecutor()

    # 2. Act: Run the graph
    
    # The executor will run start_node, which modifies the state,
    # then returns end_node. The executor then runs end_node,
    # which returns None, ending the loop.
    result = executor.run(start_node, initial_state)
    final_state = result["state"]

    # 3. Assert: Check if the graph did its job
    
    # Check that the final state is what we expect
    assert final_state is not None
    
    # Check that the value from the initial state is still there
    assert final_state.get("user") == "Solo Developer"
    
    # Check that the value from AddValueNode was added correctly
    assert final_state.get("message") == "Hello Lár!"