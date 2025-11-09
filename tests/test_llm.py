# tests/test_llm.py

import pytest
import os
from dotenv import load_dotenv
from lar import GraphExecutor, LLMNode, PrintStateNode, GraphState

# --- Load .env file for testing ---
# This line reads your .env file and sets the GOOGLE_API_KEY
load_dotenv()

# Check if the API key is actually set
API_KEY_IS_PRESENT = os.getenv("GOOGLE_API_KEY") is not None

# --- Your New Test ---

# This marker tells pytest to skip this test if the API key isn't found.
# This prevents your tests from failing just because the key is missing.
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
    
    # Define the initial data for the graph
    initial_state = {"topic": "AI agents"}
    
    # Define the nodes in reverse order, from end to start
    # Node B: The end of the graph
    end_node = PrintStateNode()
    
    # Node A: The start of the graph (our new LLMNode)
    start_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="Explain the topic of {topic} in one short sentence.",
        output_key="llm_response",  # <-- The key to save the response to
        next_node=end_node
    )
    
    # Create the engine that will run the graph
    executor = GraphExecutor()

    # 2. Act: Run the graph
    result = executor.run(start_node, initial_state)
    final_state = result["state"]

    # 3. Assert: Check if the graph did its job
    
    # Check that the final state is what we expect
    assert final_state is not None
    
    # Check that the original 'topic' is still there
    assert final_state.get("topic") == "AI agents"
    
    # Check that the LLM response was added
    llm_response = final_state.get("llm_response")
    assert llm_response is not None
    assert isinstance(llm_response, str)
    assert len(llm_response) > 10  # Check that it's a real sentence
    
    print(f"\n  [Test Output] LLM Response: {llm_response}\n")