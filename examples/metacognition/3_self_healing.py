
"""
Example 27: Self-Healing Pipeline (Runtime Recovery)

This example demonstrates how a Dynamic Graph can implement "Self-Healing".
Scenario:
1. Agent tries to connect to a 'database'.
2. It fails (Simulated Error).
3. Router detects error -> Routes to "Doctor" (DynamicNode).
4. Doctor analyzes error -> Generates a recovery subgraph:
   [ Diagnose -> Rotate Creds -> Retry Connect ]
5. Graph hot-swaps and the connection succeeds.
"""

import json
from lar import (
    GraphExecutor, GraphState, 
    DynamicNode, TopologyValidator, 
    AddValueNode, ToolNode, RouterNode, BaseNode
)
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Tools ---

# Mock DB State
DB_CREDS = {"user": "admin", "pass": "wrong_password"}

def connect_to_db(creds_key: str):
    """Simulate a DB connection that fails if password is wrong."""
    creds = globals()["DB_CREDS"] # simplistic mock
    print(f"    [Tool: connect_db] Connecting with {creds}...")
    
    if creds["pass"] != "correct_password":
         raise ValueError("AuthFailed: Invalid Password")
    
    return "Connected to DB!"

def rotate_credentials():
    """Simulate fixing the issue."""
    print("    [Tool: rotate_creds] Rotating password to 'correct_password'...")
    globals()["DB_CREDS"]["pass"] = "correct_password" # Fix the global state
    return "Credentials Rotated"

# --- 2. Define the Validator ---

validator = TopologyValidator(allowed_tools=[connect_to_db, rotate_credentials])

# --- 3. Define the Static Graph (The "Happy Path" that fails) ---

# Node 3: Success State
success_node = AddValueNode("status", "Success")

# Node 1: Try Check
# We wrap it in a ToolNode
# IF it fails, ToolNode sets 'last_error'.
connect_node = ToolNode(
    tool_function=connect_to_db,
    input_keys=["creds"], # We'll just pass a dummy key, the tool uses globals
    output_key="db_conn",
    next_node=success_node,
    # No error_node defined here because we handle it via Router
)

# --- 4. Define the Doctor (Dynamic Node) ---

DOCTOR_PROMPT = """
You are a Self-Healing Runtime.
Error: "{last_error}"

Design a recovery subgraph to fix this error.
The error is "AuthFailed".
Recipe:
1. Call 'rotate_credentials'.
2. Call 'connect_to_db' again.

Output a JSON GraphSpec with this schema:
{{
  "nodes": [
    {{
      "id": "fix",
      "type": "ToolNode",
      "tool_name": "rotate_credentials",
      "input_keys": [],
      "output_key": "fix_status",
      "next": "retry"
    }},
    {{
      "id": "retry",
      "type": "ToolNode",
      "tool_name": "connect_to_db",
      "input_keys": ["creds"], 
      "output_key": "db_conn",
      "next": null
    }}
  ],
  "entry_point": "fix"
}}
"""

doctor = DynamicNode(
    llm_model="ollama/phi4",
    prompt_template=DOCTOR_PROMPT,
    validator=validator,
    next_node=success_node, # If recovery succeeds, go to success
    context_keys=["last_error"]
)

# --- 5. The Routing Logic ---

def check_error(state: GraphState):
    err = state.get("last_error")
    if err:
        return "error"
    return "ok"

# We start with the connect node.
# But ToolNode doesn't have a "on_error" router built-in easily in the basic class
# except via 'next_node' or 'error_node'.
# So we modify the graph structure:
# Entry -> ConnectNode (fails) -> (if error) -> Doctor -> Success
#                              -> (if ok)    -> Success

# To implement this "If Error" check, we actually need ConnectNode to NOT crash hard,
# but set 'last_error'. Our ToolNode does this.
# But ToolNode only has one 'next_node'.
# So we need ConnectNode -> RouterNode -> (Doctor or Success).

router = RouterNode(
    decision_function=check_error,
    path_map={
        "error": doctor,
        "ok": success_node
    }
)

# Re-wire connect_node to go to router regardless of outcome
# (In reality, ToolNode goes to next_node on success, error_node on failure)
# Let's use the explicit error_node feature of ToolNode primitive
connect_node.next_node = success_node
connect_node.error_node = doctor # Make ToolNode jump directly to Doctor on error

# --- 6. Run ---

if __name__ == "__main__":
    print("\n🚀 TEST CASE: Self-Healing Pipeline")
    
    executor = GraphExecutor()
    initial_state = {
        "creds": "dummy" 
    }

    print("--- Starting Execution ---")
    # We must reset the global for the test
    globals()["DB_CREDS"]["pass"] = "wrong_password"
    
    results = executor.run_step_by_step(connect_node, initial_state)
    
    final_state = {}
    for step in results:
        final_state = step.get("state_after", {})
        
    print(f"\n🏁 Final DB Connection: {final_state.get('db_conn')}")
