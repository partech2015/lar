
"""
Example 25: Dynamic Fan-Out (Metacognitive Primitive)

This example demonstrates the new `DynamicNode` primitive.
The agent analyzes a query's complexity at runtime and decides how many parallel
workers (`BatchNode`) are needed to solve it.

"Simple" query -> 1 worker.
"Complex" query -> 5 workers in parallel.
"""

import os
import json
from lar import (
    GraphExecutor, GraphState, 
    DynamicNode, TopologyValidator, 
    LLMNode, AddValueNode, ToolNode
)
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Tools ---

def scrape_url(url: str, depth: int = 1):
    """Simulate scraping."""
    print(f"    [Tool: scrape_url] Scraping {url} (Depth {depth})...")
    return {"content": f"Scraped content from {url}"}

def summarize_results(*results):
    """Simulate summarization."""
    print(f"    [Tool: summarize] Summarizing {len(results)} items...")
    return f"Summary of {len(results)} sources."

# --- 2. Define the Validator ---

# We only allow the dynamic graph to use specific tools
validator = TopologyValidator(allowed_tools=[scrape_url, summarize_results])

# --- 3. Define the Dynamic Node ---


# This prompt teaches the LLM how to build the graph.
# It requests a JSON spec that uses "BatchNode" if high intensity is needed.
# Note: Since the simple DynamicNode primitive in `src/lar/dynamic.py` 
# currently only factory-instantiates LLMNode/ToolNode, we will demonstrate
# a dynamic chain of ToolNodes for simplicity, or we'd need to extend the factory.
#
# For this Proof of Concept, we will ask it to generate N separate ToolNodes
# wired in a chain (Sequential) or a specific branching structure supported by the basic factory.
# 
# LIMITATION CHECK: `src/lar/dynamic.py` currently only supports LLMNode and ToolNode factories.
# It does NOT support BatchNode factory yet.
# So we will demonstrate "Dynamic Depth" -> "Chain of N Researchers".

DYNAMIC_PROMPT = """
You are a Research Architect.
Analyze the user's request: "{request}"

If it is simple (e.g., "Fact check"), use 1 researcher node.
If it is complex (e.g., "Deep dive"), use 3 researcher nodes in a sequence.

You have access to these tools ONLY:
- scrape_url
- summarize_results

Output a JSON GraphSpec with this schema:
{{
  "nodes": [
    {{
        "id": "r1", 
        "type": "ToolNode", 
        "tool_name": "scrape_url", 
        "input_keys": ["url"], 
        "output_key": "res1", 
        "next": "r2" (or "final")
    }},
    ...
    {{
        "id": "final",
        "type": "ToolNode",
        "tool_name": "summarize_results",
        "input_keys": ["res1", "res2"...], # Pass available keys
        "output_key": "summary",
        "next": null # End of subgraph
    }}
  ],
  "entry_point": "r1"
}}
"""

# The exit node of the main graph (where we land after dynamic subgraph)
end_node = AddValueNode("status", "Done")

dynamic_architect = DynamicNode(
    llm_model="ollama/phi4", 
    prompt_template=DYNAMIC_PROMPT,
    validator=validator,
    next_node=end_node,
    context_keys=["request", "url"]
)


# --- 4. Wire the Main Graph ---

entry = dynamic_architect # Start directly with the dynamic node

# --- 5. Run ---

def run_simulation(request_text, complexity_label):
    print(f"\n\n🚀 TEST CASE: {complexity_label} ('{request_text}')")
    
    executor = GraphExecutor()
    initial_state = {
        "request": request_text, 
        "url": "http://example.com"
    }

    print("--- Starting Execution ---")
    results = executor.run_step_by_step(entry, initial_state)
    
    for step in results:
        # print(f"Step {step['step']}: {step['node']}")
        pass

if __name__ == "__main__":
    # Test 1: Simple
    run_simulation("What is the capital of France?", "SIMPLE")
    
    # Test 2: Complex
    # run_simulation("Analyze the geopolitical impact of quantum computing on crypto.", "COMPLEX")
