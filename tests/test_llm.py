# tests/test_llm.py

import pytest
import os
from dotenv import load_dotenv
# Removed PrintStateNode import
from lar import GraphExecutor, LLMNode, AddValueNode, GraphState, apply_diff

# --- Load .env file for testing ---
load_dotenv()

# Check if the API key is actually set
API_KEY_IS_PRESENT = os.getenv("GOOGLE_API_KEY") is not None

# --- Your Existing Test ---

@pytest.mark.skipif(not API_KEY_IS_PRESENT, reason="GOOGLE_API_KEY not found in .env file")
def test_llm_node_integration():
    """
    Tests that the LLMNode can:
    1. Be initialized.
    2. Format a prompt from the state.
    3. Call the Gemini API.
    4. Save the response back to the state.
    """
    
    # 1. Arrange: Set up the graph and executor
    initial_state = {"topic": "AI agents"}
    
    # Node B: The end of the graph (replaces PrintStateNode)
    end_node = AddValueNode(key="completion_marker", value=True, next_node=None)
    
    # Node A: The start of the graph (our new LLMNode)
    start_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="Explain the topic of {topic} in one short sentence.",
        output_key="llm_response",  
        next_node=end_node # Wires to the new end_node
    )
    
    executor = GraphExecutor()

    # 2. Act: Run the graph
    audit_log = list(executor.run_step_by_step(start_node=start_node, initial_state=initial_state))
    
    # Reconstruct the final state (optional, but good practice)
    final_state_data = initial_state
    for step in audit_log:
        final_state_data = apply_diff(final_state_data, step["state_diff"])


    # 3. Assert: Check if the graph did its job
    
    # Check that the final state is what we expect
    assert final_state_data is not None
    
    # Check that the LLM response was added
    llm_response = final_state_data.get("llm_response")
    assert llm_response is not None
    assert isinstance(llm_response, str)
    assert len(llm_response) > 10  # Check that it's a real sentence
    
    print(f"\n  [Test Output] LLM Response: {llm_response}\n")

