
"""
Example 28: Adaptive Deep Dive (Structural Adaptation)

This example demonstrates how a Dynamic Graph adapts its *structure* to task complexity.

Scenario:
The agent receives a query.
- If Simple: It dynamically builds a single LLMNode to answer directly.
- If Complex: It dynamically builds a multi-step research chain:
  [ SearchTool -> SummaryTool -> LLMNode ]

This differs from Example 25 because the *types* of nodes change, not just the count.
"""

from lar import (
    GraphExecutor, GraphState, 
    DynamicNode, TopologyValidator, 
    AddValueNode, ToolNode
)
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Tools ---

def web_search(query: str):
    """Simulate a search engine."""
    print(f"    [Tool: web_search] Searching for '{query}'...")
    return {"search_results": ["Result A", "Result B", "Result C"]}

def read_content(results: list):
    """Simulate reading content."""
    print(f"    [Tool: read_content] Reading {len(results)} pages...")
    return {"content": "Deep technical content extracted from Result A..."}

# --- 2. Define the Validator ---

validator = TopologyValidator(allowed_tools=[web_search, read_content])

# --- 3. Define the Dynamic Node ---

DYNAMIC_PROMPT = """
You are a Research Planner.
Query: "{query}"

Determine if this query needs external research.
- "Simple": Only greetings (e.g. "Hi", "Hello").
  -> Structure: Just one LLMNode to answer.
- "Complex": EVERYTHING ELSE (Questions, Facts, Math, Stock, Crypto).
  -> Structure: ToolNode(web_search) -> ToolNode(read_content) -> LLMNode(answer).

IMPORTANT: In the output JSON, use "{{query}}" (with double braces) to pass the user's input. Do NOT hardcode the query value.
Also use "{{results}}" and "{{context}}" to pass data between nodes.

Output a JSON GraphSpec with this schema:

IF SIMPLE:
{{
  "nodes": [
    {{
      "id": "answer",
      "type": "LLMNode",
      "prompt": "Answer this directly: {{query}}",
      "output_key": "final_answer",
      "next": null
    }}
  ],
  "entry_point": "answer"
}}

IF COMPLEX:
{{
  "nodes": [
    {{
      "id": "step1", "type": "ToolNode", "tool_name": "web_search", "input_keys": ["query"], "output_key": "results", "next": "step2"
    }},
    {{
      "id": "step2", "type": "ToolNode", "tool_name": "read_content", "input_keys": ["results"], "output_key": "context", "next": "step3"
    }},
    {{
      "id": "step3",
      "type": "LLMNode",
      "prompt": "Based on this context: {{context}}, answer: {{query}}",
      "output_key": "final_answer",
      "next": null
    }}
  ],
  "entry_point": "step1"
}}
"""

end_node = AddValueNode("status", "Done")

planner = DynamicNode(
    llm_model="ollama/phi4", 
    prompt_template=DYNAMIC_PROMPT,
    validator=validator,
    next_node=end_node,
    context_keys=["query"]
)

# --- 4. Run ---

entry = planner

def run_test(query_text, label):
    print(f"\n\n🚀 TEST CASE: {label} ('{query_text}')")
    
    executor = GraphExecutor()
    initial_state = {
        "query": query_text
    }

    print("--- Starting Execution ---")
    results = executor.run_step_by_step(entry, initial_state)
    
    final_state = {}
    for step in results:
        final_state = step.get("state_after", {})
        
    print(f"\n🏁 Answer: {final_state.get('final_answer')}")


if __name__ == "__main__":
    # Test 1: Simple
    run_test("What is 2 + 2?", "SIMPLE")
    
    # Test 2: Complex
    run_test("What is the current stock price of Tesla?", "COMPLEX")

