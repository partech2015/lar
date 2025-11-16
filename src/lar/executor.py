import copy
from .node import BaseNode
from .state import GraphState
from .utils import compute_state_diff

class GraphExecutor:
    """
    The "engine" that runs a Lár graph.
    
    NEW in v2.0: The executor now logs state "diffs" instead of
    full state snapshots, making it faster and more efficient.
    
    NEW in v2.1 (v5.0): The executor now also logs
    run_metadata (like token counts) from nodes.
    """
    
    def run_step_by_step(self, start_node: BaseNode, initial_state: dict):
        """
        Executes a graph step-by-step, yielding the history
        of each step as it completes.
        """
        state = GraphState(initial_state)
        current_node = start_node
        
        step_index = 0
        while current_node is not None:
            node_name = current_node.__class__.__name__
            state_before = copy.deepcopy(state.get_all())
            
            log_entry = {
                "step": step_index,
                "node": node_name,
                "state_before": state_before,
                "state_diff": {},
                "run_metadata": {}, # <-- NEW: Prepare to log metadata
                "outcome": "pending"
            }
            
            try:
                # 2. Execute the node
                next_node = current_node.execute(state)
                log_entry["outcome"] = "success"
                
            except Exception as e:
                # 3. Handle a critical error
                print(f"  [GraphExecutor] CRITICAL ERROR in {node_name}: {e}")
                log_entry["outcome"] = "error"
                log_entry["error"] = str(e)
                next_node = None 
            
            # 4. Capture the state *after* the node runs
            state_after = copy.deepcopy(state.get_all())
            
            # --- THIS IS THE v5.0 FIX ---
            # 5. Check for and extract run metadata
            if "__last_run_metadata" in state_after:
                # Add it to the log
                log_entry["run_metadata"] = state_after.pop("__last_run_metadata")
                # And remove it from the *real* state so it doesn't pollute
                state.set("__last_run_metadata", None) 
            # --- END FIX ---

            # 6. Compute the diff (now on the *cleaned* state_after)
            state_diff = compute_state_diff(state_before, state_after)
            log_entry["state_diff"] = state_diff
            
            # 7. Yield the log of this step and pause
            yield log_entry
            
            # 8. Resume on the next call
            current_node = next_node
            step_index += 1