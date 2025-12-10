import random
import time
import os
from typing import Dict, List
from lar import *

# Fix for LiteLLM + Gemini (Maps GOOGLE_API_KEY to GEMINI_API_KEY)
if os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# ==============================================================================
# 9. THE CORPORATE SWARM (Dynamic Graph Pruning)
# ==============================================================================
# "THE TRUE POTENTIAL OF LÁR": HYBRID COGNITIVE ARCHITECTURE
#
# Most frameworks are "All LLM" (slow, expensive, hallucination-prone).
# Lár allows you to mix 1% Intelligence (LLM) with 99% Structure (Code).
#
# In this example:
# 1. The CEO (LLMNode) thinks ONCE. It sets a global "Strategic Directive".
# 2. The Swarm (60+ Nodes) matches that strategy deterministically.
#    - If Strategy is "BLITZSCALING": Every manager hires/works (Full Graph Execution).
#    - If Strategy is "AUSTERITY": Managers aggressively prune branches (Dynamic Graph Pruning).
#
# Result: One expensive call controls a massive, cheap, reliable fleet.
# ==============================================================================

print("🏗️  Building Massive Graph (Corporate Swarm)...")

class HierarchyBuilder:
    def __init__(self):
        self.node_count = 0

    def create_worker(self, id: str, next_node: BaseNode) -> BaseNode:
        """Leaf node: Actually does the work (if reached)."""
        self.node_count += 1
        
        def worker_task(total_completed: int) -> dict:
            return {"total_completed": total_completed + 1}

        return ToolNode(
            tool_function=worker_task,
            input_keys=["total_completed"],
            output_key=f"res_{id}", # Dummy key
            next_node=next_node
        )

    def create_manager(self, id: str, level: int, max_depth: int, next_node_success: BaseNode) -> BaseNode:
        """
        Recursively creates a manager.
        The Manager reads the CEO's 'strategy' to decide whether to run this branch or PRUNE it.
        """
        self.node_count += 1
        
        # Base Case
        if level >= max_depth:
            return self.create_worker(id, next_node_success)

        # Recursive Step: Build Children (Pre-order traversal linearization)
        right_branch = self.create_manager(f"{id}_R", level + 1, max_depth, next_node_success)
        left_branch  = self.create_manager(f"{id}_L", level + 1, max_depth, right_branch)

        # --- THE "INTELLIGENCE" LINK ---
        # The Manager (Code) obeys the CEO (LLM)
        def manager_logic(state: GraphState) -> str:
            strategy = state.get("strategy", "NORMAL")
            
            if strategy == "BLITZSCALING":
                return "EXECUTE" # Always run everything
            elif strategy == "AUSTERITY":
                # In austerity, we prune 50% of branches to save costs
                return "EXECUTE" if random.random() > 0.5 else "PRUNE" 
            else:
                return "EXECUTE"

        return RouterNode(
            decision_function=manager_logic,
            path_map={
                "EXECUTE": left_branch,    # Run the sub-tree
                "PRUNE": next_node_success # Skip the sub-tree entirely (Optimization)
            },
            default_node=next_node_success
        )

# --- Build the Graph ---

# 1. End Node
end_node = AddValueNode(key="final_status", value="MISSION_ACCOMPLISHED", next_node=None)

# 2. Build the Swarm (The deterministic army)
builder = HierarchyBuilder()
head_manager = builder.create_manager("VP", level=1, max_depth=6, next_node_success=end_node)

# 3. The CEO (The Strategic Brain)
# This is the ONLY LLM node. It effectively programming the rest of the graph.
ceo_node = LLMNode(
    model_name="gemini/gemini-1.5-pro", # Explicit provider prefix to avoid Vertex AI
    prompt_template=(
        "You are the CEO of a tech giant. The market is: {market_condition}.\n"
        "Set the corporate strategy directives.\n"
        "Respond ONLY with one word:\n"
        "- BLITZSCALING (If market is favorable/booming)\n"
        "- AUSTERITY (If market is crash/recession)"
    ),
    output_key="strategy",
    next_node=head_manager
)

print(f"✅ Organization Built! Total Capacity: {builder.node_count} nodes.")

# --- Run the Swarm ---

executor = GraphExecutor()

def run_scenario(name, market_condition, description):
    print(f"\n{name}")
    initial_state = {"market_condition": market_condition, "total_completed": 0}

    start_time = time.time()
    steps = []
    
    # Graceful Fallback: If CEO (LLM) fails, we simulate the strategy
    try:
        # Run CEO Step Step-by-Step
        gen = executor.run_step_by_step(ceo_node, initial_state)
        
        # Step 1: CEO Thinks
        ceo_step = next(gen) 
        steps.append(ceo_step)
        
        # Check if CEO failed
        if ceo_step['node'].output_key == "strategy" and "error" in ceo_step.get('outcome', ''):
             raise Exception("LLM Error")
             
    except Exception as e:
        print(f"   ⚠️  CEO (LLM) Unavailable ({e}). Switching to **SIMULATION MODE**.")
        # Simulate the decision based on the input
        simulated_strategy = "AUSTERITY" if "crash" in market_condition else "BLITZSCALING"
        print(f"   🤖 [SIMULATION] CEO Decided: {simulated_strategy}")
        
        # Manually inject strategy and continue from Head Manager
        initial_state["strategy"] = simulated_strategy
        gen = executor.run_step_by_step(head_manager, initial_state)

    # Run the rest of the swarm
    for step in gen:
        steps.append(step)
        
    duration = time.time() - start_time
    
    # Analysis
    # Depending on fallback, strategy might differ where it's stored
    strategy = steps[0].get('state_diff', {}).get('added', {}).get('strategy', initial_state.get('strategy'))
    final_state = steps[-1].get('final_state', {})
    work_done = final_state.get('total_completed', 0)
    
    print(f"   ⚡ Execution Time: {duration:.2f}s")
    print(f"   💼 Work Units Completed: {work_done} ({description})")

# Scenario 1: Recession
run_scenario(
    name="📉 SCENARIO 1: The Market Crashes...",
    market_condition="Competitors are folding, stock market is down 20%, crash is coming.",
    description="Graph Pruned!"
)

print("-" * 40)

# Scenario 2: Boom
run_scenario(
    name="📈 SCENARIO 2: The AI Boom...",
    market_condition="AI is eating the world. VC money is free. Capture market share.",
    description="Full Utilization!"
)

print(f"\n✨ This demonstrates DYNAMIC COMPUTATION GRAPHS controlled by AI.")
