
"""
Example 29: The Expert Summoner (Modular Agency)

This example demonstrates "Sub-Agent Loading".
Instead of the LLM generating the graph structure, it selects a pre-defined
"Expert Agent" file (JSON) to load and inject.

Scenario:
User asks a legal question.
1. Router detects "Legal" topic.
2. DynamicNode loads `legal_expert.json`.
3. The Legal Expert subgraph runs.
"""

import json
import os
from lar import (
    GraphExecutor, GraphState, 
    DynamicNode, TopologyValidator, 
    AddValueNode, ToolNode, LLMNode
)
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define the Expert Tools ---

def cite_law(code_section: str):
    print(f"    [LegalExpert] Citing Law: {code_section}")
    return "According to Section 230..."

# --- 2. Define the Validator ---

validator = TopologyValidator(allowed_tools=[cite_law])

# --- 3. Create the serialized "Expert Agent" (Simulated File) ---

EXPERT_FILE = "legal_expert.json"
expert_agent = {
  "nodes": [
    {
      "id": "research",
      "type": "ToolNode",
      "tool_name": "cite_law",
      "input_keys": ["query"], 
      "output_key": "law_context",
      "next": "advice"
    },
    {
      "id": "advice",
      "type": "LLMNode",
      "prompt": "Based on {{law_context}}, answer: {{query}}",
      "output_key": "final_advice",
      "next": None # Flows to next_node of DynamicNode
    }
  ],
  "entry_point": "research"
}

with open(EXPERT_FILE, "w") as f:
    json.dump(expert_agent, f, indent=2)

# --- 4. Define the Summoner (Dynamic Node) ---

# This DynamicNode doesn't ask the LLM to *generate* the graph.
# It asks the LLM to *return the JSON content* of the file (conceptually).
# 
# BUT: The standard `DynamicNode` expects the LLM to output the JSON spec.
# We can just inject the JSON directly into the prompt context if we want "Loading".
# Or better: We subclass DynamicNode to be a `LoaderNode`.
#
# For this example using the *existing* primitive:
# We will use a Tool that "reads" the file, and the LLM just outputs the content.
# Actually, that's inefficient.
#
# Workaround for POC: The LLM "Summons" the expert by outputting the specific JSON structure
# it "knows" (or we put in context).
#
# A true "LoaderNode" would be a different primitive.
# Let's simulate "Summoning" by putting the JSON in the prompt as a "Skill".

SUMMONER_PROMPT = """
You are a Staffing Manager.
Query: "{query}"

If the query is about Law, output NOT the answer, but the LEGAL AGENT SPEC.
LEGAL AGENT SPEC:
""" + json.dumps(expert_agent) + """

If the query is about Math, output a simple math node spec.

Output valid JSON matching the spec.
"""

end_node = AddValueNode("status", "Done")

summoner = DynamicNode(
    llm_model="ollama/phi4",
    prompt_template=SUMMONER_PROMPT,
    validator=validator,
    next_node=end_node,
    context_keys=["query"]
)

# --- 5. Run ---

entry = summoner

if __name__ == "__main__":
    print("\n🚀 TEST CASE: Expert Summoner ('My landlord evicted me...')")
    
    executor = GraphExecutor()
    initial_state = {
        "query": "My landlord evicted me without notice."
    }

    print("--- Starting Execution ---")
    results = executor.run_step_by_step(entry, initial_state)
    
    final_state = {}
    for step in results:
        final_state = step.get("state_after", {})
        
    print(f"\n🏁 Advice: {final_state.get('final_advice')}")
    
    # Cleanup
    if os.path.exists(EXPERT_FILE):
        os.remove(EXPERT_FILE)
