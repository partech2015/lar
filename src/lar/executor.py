import copy
from .node import BaseNode
from .state import GraphState
from .utils import compute_state_diff  # <-- IMPORT THE NEW UTILITY

class GraphExecutor:
    """
    The "engine" that runs a Lár graph.
    
    NEW in v2.0: The executor now logs state "diffs" instead of
    full state snapshots, making it faster and more efficient.
    """
    
    def run_step_by_step(self, start_node: BaseNode, initial_state: dict):
        """
        Executes a graph step-by-step, yielding the history
        of each step as it completes.

        Args:
            start_node (BaseNode): The entry point of the graph.
            initial_state (dict): The initial data to populate the state with.

        Yields:
            dict: A log entry for the completed step.
        """
        state = GraphState(initial_state)
        current_node = start_node
        
        step_index = 0
        while current_node is not None:
            node_name = current_node.__class__.__name__
            
            # 1. Capture the state *before* the node runs
            state_before = copy.deepcopy(state.get_all())
            
            log_entry = {
                "step": step_index,
                "node": node_name,
                "state_before": state_before,
                "state_diff": {}, # Will be populated below
                "outcome": "pending"
            }
            
            try:
                # 2. Execute the node
                next_node = current_node.execute(state)
                log_entry["outcome"] = "success"
                
            except Exception as e:
                # 3. Handle a critical error in the node itself
                print(f"  [GraphExecutor] CRITICAL ERROR in {node_name}: {e}")
                log_entry["outcome"] = "error"
                log_entry["error"] = str(e)
                next_node = None # Stop the graph
            
            # 4. Capture the state *after* the node runs
            state_after = copy.deepcopy(state.get_all())
            
            # 5. Compute the diff and add it to the log
            state_diff = compute_state_diff(state_before, state_after)
            log_entry["state_diff"] = state_diff
            
            # 6. Yield the log of this step and pause
            yield log_entry
            
            # 7. Resume on the next call
            current_node = next_node
            step_index += 1