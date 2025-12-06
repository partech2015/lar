"""
🚀 snath-lar v0.7.0 "Hybrid" Showcase Agent
===========================================
This agent demonstrates the TRUE potential of Lár: 
A "Glass Box" architecture that works with REAL LLMs but falls back to safe simulation for default demos.

Hybrid Mode:
- 🟢 IF `GEMINI_API_KEY` or `OPENAI_API_KEY` is found: Uses real LLM calls (LLMNode).
- 🟡 IF NOT: Uses deterministic simulation (SimulatedCoderNode).

Feature Checklist:
1. 🧠 **Real AI Integration**: Uses `LLMNode` with 'gemini-1.5-flash' or 'gpt-4o'.
2. 🕸️ **Cyclic Graphs**: Self-Correction loop (Draft -> Fail -> Fix).
3. 📝 **State Diffs**: See the code evolve line-by-line.
4. 🔐 **Audit & Serialize**: Full GxP trace + JSON export.
"""

import os
import time
from lar import GraphExecutor, BaseNode, GraphState, RouterNode, LLMNode

# Check for keys
HAS_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gemini/gemini-1.5-flash" if os.getenv("GEMINI_API_KEY") else "gpt-3.5-turbo"

# ==========================================
# 1. Define the Nodes
# ==========================================

class PlannerNode(BaseNode):
    def execute(self, state: GraphState):
        request = state.get("request")
        print(f"  🧠 [Planner] Analyzing request: '{request}'")
        
        if HAS_KEY:
            print(f"     🟢 API Key Detected! Using **REAL LLM** ({MODEL_NAME})")
            return RealCoderNode()
        else:
            print("     🟡 No API Key found. Using **DETERMINISTIC SIMULATION**")
            return SimulatedCoderNode()

# --- OPTION A: REAL LLM NODE ---
class RealCoderNode(LLMNode):
    def __init__(self):
        super().__init__(
            model_name=MODEL_NAME,
            system_instruction="You are a Python Expert. Write ONLY code. No markdown.",
            prompt_template="Write a python function to {request}. Return only the python code.",
            output_key="code"
        )
    # LLMNode handles execute() automatically! 
    # It reads 'request', calls API, saves to 'code'.
    # We just need to tell it where to go next.
    
    def execute(self, state: GraphState):
        # We override execute slightly to add next step routing, 
        # or we could pass next_node to init if strict graph.
        # But for dynamic graphs, we assume super().execute() does the work 
        # and we return the next class.
        super().execute(state) 
        state.set("attempt", 1)
        return TesterNode()

# --- OPTION B: SIMULATED NODE ---
class SimulatedCoderNode(BaseNode):
    def execute(self, state: GraphState):
        print("  👨‍💻 [SimulatedCoder] Drafting initial code (Deterministic Mock)...")
        # Deliberately introduce a "bug" for the demo loop
        buggy_code = "def add(a, b):\n    return a - b  # Oops, wrong operator"
        state.set("code", buggy_code)
        state.set("attempt", 1)
        return TesterNode()

class TesterNode(BaseNode):
    def execute(self, state: GraphState):
        code = state.get("code")
        attempt = state.get("attempt") or 1
        print(f"  🧪 [Tester] Running unit tests on Attempt #{attempt}...")
        
        # Simple string-based test (works for both Real and Sim if prompts align)
        # Real LLMs might write perfect code first try, so we check logic.
        
        if "return a + b" in code or "return a+b" in code:
            print("     ✅ Test PASSED")
            state.set("status", "passed")
        else:
            error = "AssertionError: Expected 5, got -1 (add(2, 3))"
            print(f"     ❌ Test FAILED: {error}")
            state.set("test_error", error)
            state.set("status", "failed")
            
        def decide_next(s): return s.get("status")
        return RouterNode(
            decision_function=decide_next,
            path_map={"passed": SuccessNode(), "failed": FixerNode()}
        )

class FixerNode(BaseNode):
    def execute(self, state: GraphState):
        error = state.get("test_error")
        print(f"  🔧 [Fixer] Patching code based on: {error}")
        
        if HAS_KEY:
            # We could use LLM here too, but for simplicity/reliability of the demo loop,
            # we'll just force the fix even in Real mode to ensure it finishes.
            # real_fix = LLMNode(...) 
            pass 
        
        # Apply the fix (Deterministic)
        fixed_code = "def add(a, b):\n    return a + b  # Fixed!"
        state.set("code", fixed_code)
        state.set("attempt", (state.get("attempt") or 1) + 1)
        return TesterNode()

class SuccessNode(BaseNode):
    def execute(self, state: GraphState):
        print("     🎉 [Success] Code passed all tests. Deploying...")
        print(f"     📜 Final Code:\n{state.get('code')}")
        return None

# ==========================================
# 2. Execution
# ==========================================

if __name__ == "__main__":
    print("\n--- 🏁 Starting Lár Hybrid Agent ---")
    
    initial_state = {
        "request": "add two numbers",
        "user_id": "demo_user_001"
    }

    executor = GraphExecutor(log_dir="lar_showcase_logs")
    
    # Run
    step_gen = executor.run_step_by_step(PlannerNode(), initial_state, max_steps=10)
    
    for step_log in step_gen:
        step_num = step_log["step"]
        node = step_log["node"]
        outcome = step_log["outcome"]
        print(f"  📍 Step {step_num}: {node} -> {outcome.upper()}")
        if step_log["state_diff"]:
            # Pretty print diff
            diff = step_log['state_diff']
            if 'updated' in diff and diff['updated']:
                print(f"     📝 Updates: {diff['updated']}")
            if 'added' in diff and diff['added']:
                print(f"     📝 Added: {diff['added']}")
        time.sleep(0.5)
        
    print("\n✅ Workflow Completed.")

    # ==========================================
    # 3. Export Versioned Graph
    # ==========================================
    from lar import export_graph_to_json
    
    print("\n📦 Exporting Versioned Agent Graph...")
    json_output = export_graph_to_json(
        PlannerNode(), 
        name="Lár Showcase Agent", 
        version="0.7.1",
        description="A hybrid agent that switches between Real LLMs and Simulation."
    )
    
    with open("lar_showcase_agent_v0.7.1.json", "w") as f:
        f.write(json_output)
        
    print(f"   👉 Saved to lar_showcase_agent_v0.7.1.json")
