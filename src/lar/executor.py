import copy
import json
import os
import datetime
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

    NEW in v6.0: Now includes automatic logging to a file.
    """
    def __init__(self, log_dir: str = "lar_logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _save_log(self, history: list, run_id: str):
        """Saves the execution history to a JSON file."""
        filename = f"{self.log_dir}/run_{run_id}.json"
        try:
            with open(filename, "w") as f:
                json.dump(history, f, indent=2)
            print(f"\n✅ [GraphExecutor] Audit log saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️ [GraphExecutor] Failed to save log: {e}")


    def run_step_by_step(self, start_node: BaseNode, initial_state: dict):
        """
        Executes a graph step-by-step, yielding the history
        of each step as it completes.
        """
        state = GraphState(initial_state)
        current_node = start_node

        # Generate a unique ID for this run
        run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        history = [] # We keep a local copy to save at the end
        
        step_index = 0
        while current_node is not None:
            node_name = current_node.__class__.__name__
            state_before = copy.deepcopy(state.get_all())
            
            log_entry = {
                "step": step_index,
                "node": node_name,
                "state_before": state_before,
                "state_diff": {},
                "run_metadata": {}, 
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
            
             # Extract metadata
            if "__last_run_metadata" in state_after:
                log_entry["run_metadata"] = state_after.pop("__last_run_metadata")


            # 6. Compute the diff (now on the *cleaned* state_after)
            state_diff = compute_state_diff(state_before, state_after)
            log_entry["state_diff"] = state_diff

            # Add to history and yield
            history.append(log_entry)
            yield log_entry
            
            
            '''# 7. Yield the log of this step and pause
            yield log_entry '''
            
            # 8. Resume on the next call
            current_node = next_node
            step_index += 1
            # --- AUTO-SAVE LOG ON FINISH ---  
        self._save_log(history, run_id)