Getting Started

Let's build a "smart" agent in 3 minutes. This agent is a "Master Planner" that can decide what kind of work to do.

1. Installation

This project is managed with Poetry.

pip install lar-engine


(This installs the core lar engine from PyPI.)

2. Set Your API Key

Lár reads your Google API key from an environment variable. Create a .env file in your project's root:

# .env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"


3. Build Your First "Glass Box" Agent

This agent will take a user's task and plan its response, deciding whether to route to a "Coder" agent or a simple "Chatbot."

import os
from lar import *
from lar.utils import compute_state_diff
from dotenv import load_dotenv
```python
# Load your .env file
load_dotenv()
os.environ["GOOGLE_API_KEY"] # (This line is for Colab/Jupyter)

# 1. Define the "choice" logic for our Router
def plan_router_function(state: GraphState) -> str:
    """Reads the 'plan' from the state and returns a route key."""
    plan = state.get("plan", "").strip().upper()
    
    if "CODE" in plan:
        return "CODE_PATH"
    else:
        return "TEXT_PATH"

# 2. Define the agent's nodes (the "bricks")
# We build from the end to the start.

# --- The End Nodes (the destinations) ---
success_node = AddValueNode(
    key="final_status", 
    value="SUCCESS", 
    next_node=None # 'None' means the graph stops
)

chatbot_node = LLMNode(
    model_name="gemini-2.5-pro",
    prompt_template="You are a helpful assistant. Answer the user's task: {task}",
    output_key="final_response",
    next_node=success_node # After answering, go to success
)

code_writer_node = LLMNode(
    model_name="gemini-2.5-pro",
    prompt_template="Write a Python function for this task: {task}",
    output_key="code_string",
    next_node=success_node 
)

# --- 2. Define the "Choice" (The Router) ---
master_router_node = RouterNode(
    decision_function=plan_router_function,
    path_map={
        "CODE_PATH": code_writer_node,
        "TEXT_PATH": chatbot_node
    },
    default_node=chatbot_node # Default to just chatting
)

# --- 3. Define the "Start" (The Planner) ---
planner_node = LLMNode(
    model_name="gemini-2.5-pro",
    prompt_template="""
    Analyze this task: "{task}"
    Does it require writing code or just a text answer?
    Respond with ONLY the word "CODE" or "TEXT".
    """,
    output_key="plan",
    next_node=master_router_node # After planning, go to the router
)

# --- 4. Run the Agent ---
executor = GraphExecutor()
initial_state = {"task": "What is the capital of France?"}

# The executor runs the graph and returns the full log
result_log = list(executor.run_step_by_step(
    start_node=planner_node, 
    initial_state=initial_state
))

# --- 5. Inspect the "Glass Box" ---

print("--- AGENT FINISHED! ---")

# Reconstruct the final state
final_state = initial_state
for step in result_log:
    final_state = apply_diff(final_state, step["state_diff"])

print(f"\nFinal Answer: {final_state.get('final_response')}")
print("\n--- FULL AUDIT LOG (The 'Glass Box') ---")
print(json.dumps(result_log, indent=2))
```



The Output (Your Audit Log)

When you run this, you'll get the final answer, and you'll get this **"flight data recorder"** log. This is the `lar` difference.

```json
[
  {
    "step": 0,
    "node": "LLMNode",
    "state_before": {
      "task": "What is the capital of France?"
    },
    "state_diff": {
      "added": {
        "plan": "TEXT"
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {
      "prompt_tokens": 42,
      "output_tokens": 1,
      "total_tokens": 43
    },
    "outcome": "success"
  },
  {
    "step": 1,
    "node": "RouterNode",
    "state_before": {
      "task": "What is the capital of France?",
      "plan": "TEXT"
    },
    "state_diff": {
      "added": {},
      "removed": {},
      "modified": {}
    },
    "run_metadata": {},
    "outcome": "success"
  },
  {
    "step": 2,
    "node": "LLMNode",
    "state_before": {
      "task": "What is the capital of France?",
      "plan": "TEXT"
    },
    "state_diff": {
      "added": {
        "final_response": "The capital of France is Paris."
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {
      "prompt_tokens": 30,
      "output_tokens": 6,
      "total_tokens": 36
    },
    "outcome": "success"
  },
  {
    "step": 3,
    "node": "AddValueNode",
    "state_before": {
      "task": "What is the capital of France?",
      "plan": "TEXT",
      "final_response": "The capital of France is Paris."
    },
    "state_diff": {
      "added": {
        "final_status": "SUCCESS"
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {},
    "outcome": "success"
  }
]
```