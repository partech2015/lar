import random
import time
from typing import Dict, List
from lar import *

# ==============================================================================
# 9. THE CORPORATE SWARM (Programmatic Graph Generation)
# ==============================================================================
# This example demonstrates Lár's "Power User" feature:
# Since Graphs are just Python Objects, you can generate massive, complex
# agents using loops and recursive functions.
#
# We will build a "Corporate Hierarchy" of ~63 nodes:
# CEO -> 2 Presidents -> 4 VPs -> 8 Directors -> 16 Managers -> 32 Workers
# ==============================================================================

print("🏗️  Building Massive Graph (Corporate Swarm)...")

class HierarchyBuilder:
    def __init__(self):
        self.node_count = 0
        self.nodes = []

    def create_worker(self, id: str, next_node: BaseNode) -> BaseNode:
        """Creates a leaf node (Worker) that does actual work."""
        self.node_count += 1
        
        # A simple tool that "does work"
        def worker_task(work_load: int) -> dict:
            # Simulate work
            return {"completed_units": work_load + 1}

        return ToolNode(
            tool_function=worker_task,
            input_keys=["work_load"],
            output_key=f"worker_{id}_result",
            next_node=next_node
        )

    def create_manager(self, id: str, level: int, max_depth: int, next_node_success: BaseNode) -> BaseNode:
        """
        Recursively creates a manager and their subordinates.
        Returns the 'Head' node of this branch.
        """
        self.node_count += 1
        
        # Base Case: If we are at the bottom, become a worker
        if level >= max_depth:
            return self.create_worker(id, next_node_success)

        # Recursive Step: Create 2 subordinates (Left and Right branches)
        # Note: In a linear execution flow, 'Left' must point to 'Right', 
        # and 'Right' must point to 'Next Node' (Parent's successor).
        # We are linearizing a tree traversal (Pre-order traversal).
        
        # 3. Create Right Branch (Executes second) -> Points to Manager's Successor
        right_branch_head = self.create_manager(f"{id}_R", level + 1, max_depth, next_node_success)
        
        # 2. Create Left Branch (Executes first) -> Points to Right Branch Head
        left_branch_head = self.create_manager(f"{id}_L", level + 1, max_depth, right_branch_head)

        # 1. Create This Manager (Router/Logic) -> Points to Left Branch Head
        # The Manager decides if work is needed.
        def manager_logic(state: GraphState) -> str:
            # Randomly decide to skip work? (For variety)
            # return "DELEGATE" if random.random() > 0.1 else "SKIP"
            return "DELEGATE"

        manager_node = RouterNode(
            decision_function=manager_logic,
            path_map={
                "DELEGATE": left_branch_head,
                "SKIP": next_node_success # Short-circuit this entire branch
            },
            default_node=next_node_success
        )
        return manager_node

# --- Build the Graph ---

# 1. Define End Node
end_node = AddValueNode(key="final_status", value="PROJECT_COMPLETE", next_node=None)

# 2. Generate the Swarm (Depth 5 = 1 + 2 + 4 + 8 + 16 + 32 nodes)
builder = HierarchyBuilder()
ceo_node = builder.create_manager("CEO", level=1, max_depth=6, next_node_success=end_node)

print(f"✅ Graph Built! Total Nodes: {builder.node_count}")
print("   - This is structurally a Binary Tree.")
print("   - Execution is flattened into a linear traversal.")

# --- Run the Swarm ---

executor = GraphExecutor()
initial_state = {"work_load": 0}

print("\n🚀 Starting Execution (This might take a moment)...")
start_time = time.time()

step_count = 0
for step in executor.run_step_by_step(ceo_node, initial_state):
    step_count += 1
    node_type = type(step['node']).__name__
    node_name = getattr(step['node'], 'output_key', 'Router/Manager')
    
    # Print a minimal log for speed, full log for "Worker" nodes
    if "ToolNode" in node_type:
        print(f"  [Step {step_count}] 👷 Worker Finished")
    elif "RouterNode" in node_type:
        print(f"  [Step {step_count}] 👔 Manager Delegating...")
    elif "AddValueNode" in node_type:
        print(f"  [Step {step_count}] 🏁 {step['node'].value}")

duration = time.time() - start_time
print(f"\n✨ DONE in {duration:.2f}s!")
print(f"📊 Total Steps Executed: {step_count}")
print(f"📈 Complexity: {builder.node_count} nodes in memory.")
