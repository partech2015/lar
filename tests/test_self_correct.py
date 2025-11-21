# tests/test_self_correct.py

import pytest
import os
from dotenv import load_dotenv
from lar import (
    GraphExecutor, 
    BaseNode,
    LLMNode, 
    ToolNode,
    RouterNode,
    AddValueNode,
    GraphState,
    apply_diff # <--- CRITICAL FIX: Imported apply_diff
)

# --- Load .env file for testing ---
load_dotenv()
API_KEY_IS_PRESENT = os.getenv("GOOGLE_API_KEY") is not None

# --- The "Tool" (Code Sandbox) ---
# This is the "hand" our agent will use.
# It's a sandbox to safely execute and test the LLM's code.

def run_generated_code(code_string: str) -> str:
    """
    A 'tool' that attempts to execute LLM-generated code.
    It executes the code, finds the 'add_five' function,
    and runs a test case (10 + 5 = 15).
    """
    try:
        # --- NEW FIX: Strip markdown fences ---
        if code_string.startswith("```python"):
            code_string = code_string.strip().split("\n", 1)[1]
            if code_string.endswith("```"):
                code_string = code_string.rsplit("\n", 1)[0]
        # --- END FIX ---

        # 1. Execute the code string in a local scope
        local_scope = {}
        exec(code_string, {}, local_scope)
        
        # 2. Try to find the function
        if 'add_five' not in local_scope:
            raise NameError("The function 'add_five' was not defined.")
            
        func = local_scope['add_five']
        
        # 3. Run the test case
        result = func(10)
        
        # 4. Check the logic
        if result != 15:
            raise ValueError(f"Logic error: Expected 15, but got {result}")
            
        print("  [Tool-run_generated_code]: Test PASSED!")
        return "Success!"
        
    except Exception as e:
        raise e
    
# --- The "Logic" for the Router ---
# This is the "choice" our agent will make.

def judge_function(state: GraphState) -> str:
    """
    Checks the state for 'last_error'.
    If an error exists, it routes to the 'failure' path (to correct).
    If no error, it routes to the 'success' path (to end).
    """
    # NOTE: The RouterNode's execute method should clear the metadata, 
    # but the judge function still needs the last_error check.
    
    if state.get("last_error"):
        state.set("last_error", None)
        return "failure"
    else:
        return "success"

# --- The Main Test ---

@pytest.mark.skipif(not API_KEY_IS_PRESENT, reason="GOOGLE_API_KEY not found in .env file")
def test_self_correcting_agent_loop():
    """
    Tests the full "Think -> Act -> Choose -> Loop" cycle.
    """
    
    # 1. ARRANGE: Define all the nodes (our "agent's brain")
    
    # --- Destination Nodes ---
    success_node = AddValueNode(key="final_status", value="SUCCESS", next_node=None)
    critical_fail_node = AddValueNode(key="final_status", value="CRITICAL_FAILURE", next_node=None)

    # --- The "Corrector" Node (LLM) ---
    corrector_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        Your last attempt to write a Python function failed.
        CODE:
        {code_string}
        
        ERROR:
        {last_error}
        
        Please fix the code and ONLY output the complete, corrected Python function.
        """,
        output_key="code_string",  # <-- Overwrites the bad code
        next_node=None  
    )

    # --- The "Judge" Node (Router) ---
    judge_node = RouterNode(
        decision_function=judge_function,
        path_map={
            "success": success_node,
            "failure": corrector_node 
        },
        default_node=critical_fail_node
    )
    
    # --- The "Tester" Node (Tool) ---
    tester_node = ToolNode(
        tool_function=run_generated_code,
        input_keys=["code_string"],     
        output_key="test_result",     
        next_node=judge_node,         
        error_node=judge_node         
    )
    
    # --- The "Writer" Node (LLM) ---
    writer_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        Write a Python function called `add_five(x)` that returns x + 5.
        But for this test, make a small syntax error on purpose.
        For example, write 'def add_five(x)' but forget the colon.
        ONLY output the Python function.
        """,
        output_key="code_string",
        next_node=tester_node  
    )
    
    # --- Create the Loop ---
    corrector_node.next_node = tester_node

    # 2. ACT: Run the agent
    
    executor = GraphExecutor()
    initial_state = {"task": "Create a function to add 5"}
    
    # FIX: Use run_step_by_step to get the full audit log
    audit_log = list(executor.run_step_by_step(
        start_node=writer_node, 
        initial_state=initial_state
    ))
    
    # FIX: Reconstruct the final state from the audit log
    final_state_data = initial_state
    for step in audit_log:
        final_state_data = apply_diff(final_state_data, step["state_diff"])

    # 3. ASSERT: Check if the agent *eventually* succeeded
    
    # The final result from the tool ("Success!") should be in the state
    assert final_state_data.get("test_result") == "Success!"
    
    # The "Judge" should have routed to the "success_node" in the end
    assert final_state_data.get("final_status") == "SUCCESS"
    
    # The audit log length should be at least 4 (Write, Test, Judge, Correct, Test, Judge)
    assert len(audit_log) >= 6 
    
    print(f"\n  [Test Output] Final Code: {final_state_data.get('code_string')}\n")