
"""
Example 26: The Tool Inventor (Self-Programming)

This example demonstrates how a Dynamic Graph can implement "Code Generation + Execution".
The user asks for a calculation that requires code (e.g., "7th Fibonacci number").
The DynamicNode builds a subgraph:
1. LLMNode: Writes the Python function to a state key 'code'.
2. ToolNode: Executes the 'code' using a safe wrapper tool.

Note: In a real "Glass Box" system, the 'execute_python' tool would be heavily sandboxed (e.g., e2b or docker).
Here we use a constrained local exec for demonstration.
"""

import ast
from lar import (
    GraphExecutor, GraphState, 
    DynamicNode, TopologyValidator, 
    AddValueNode
)
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Execution Tool ---

def safe_python_exec(code_str: str):
    """
    Executes a Python function string and calls it.
    Assumes the code defines a function named 'solution'.
    """
    print(f"\n    [Tool: python_exec] Executing code:\n{code_str[:50]}...")
    
    # Strip markdown
    cleaned = code_str.replace("```python", "").replace("```", "").strip()

    try:
        # Constrained execution environment (Allowed builtins for demo)
        local_scope = {}
        exec(cleaned, {"__builtins__": __builtins__}, local_scope)


        
        if "solution" not in local_scope:
            return "Error: Code did not define 'solution()'."
        
        result = local_scope["solution"]()
        return result
    except Exception as e:
        return f"Execution Error: {e}"

# --- 2. Define the Validator ---

validator = TopologyValidator(allowed_tools=[safe_python_exec])

# --- 3. Define the Dynamic Node ---

# The Architect Prompt
# We teach it to build a "Coder -> Executor" chain.
# Note: The output_key for the Coder becomes the input_key for the Executor.

DYNAMIC_PROMPT = """
You are a Software Architect.
User Request: "{request}"

Design a subgraph to solve this using Python code.
1. Create an LLMNode ("coder") to write the defined Python function.
   - Prompt: "Write a python function named 'solution' that {request}. Return ONLY the code."
   - Output Key: "generated_code"
   
2. Create a ToolNode ("executor") to run the code.
   - Tool Name: "safe_python_exec"
   - Input Keys: ["generated_code"]
   - Output Key: "result"

You have access to these tools ONLY:
- safe_python_exec

Output a JSON GraphSpec with this schema:
{{
  "nodes": [
    {{
      "id": "coder",
      "type": "LLMNode",
      "prompt": "Write a python function named 'solution' (no arguments) that returns the answer to: {{request}}. Return ONLY the code, no markdown.",
      "output_key": "generated_code",
      "next": "executor"
    }},
    {{
      "id": "executor",
      "type": "ToolNode",
      "tool_name": "safe_python_exec",
      "input_keys": ["generated_code"],
      "output_key": "result",
      "next": null
    }}
  ],
  "entry_point": "coder"
}}
"""

end_node = AddValueNode("status", "Done")

dynamic_architect = DynamicNode(
    llm_model="ollama/phi4", 
    prompt_template=DYNAMIC_PROMPT,
    validator=validator,
    next_node=end_node,
    context_keys=["request"]
)

# --- 4. Run ---

entry = dynamic_architect

if __name__ == "__main__":
    print("\n🚀 TEST CASE: Self-Programming ('Calculate 12th Fibonacci number')")
    
    executor = GraphExecutor()
    initial_state = {
        "request": "Calculate the 12th Fibonacci number"
    }

    print("--- Starting Execution ---")
    results = executor.run_step_by_step(entry, initial_state)
    
    final_state = {}
    for step in results:
        final_state = step.get("state_after", {})
        
    print(f"\n🏁 Final Result: {final_state.get('result')}")
