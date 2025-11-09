import copy
from .node import BaseNode
from .state import GraphState

class GraphExecutor:
    """
    The "engine" that runs a Lár graph.
    
    NEW in v0.6: The executor is now a generator, yielding
    one step at a time for interactive debugging.
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
            
            log_entry = {
                "step": step_index,
                "node": node_name,
                "state_before": copy.deepcopy(state.get_all())
            }
            
            try:
                next_node = current_node.execute(state)
                
                log_entry["state_after"] = copy.deepcopy(state.get_all())
                log_entry["outcome"] = "success"
                
            except Exception as e:
                print(f"  [GraphExecutor] CRITICAL ERROR in {node_name}: {e}")
                log_entry["state_after"] = copy.deepcopy(state.get_all())
                log_entry["outcome"] = "error"
                log_entry["error"] = str(e)
                next_node = None # Stop the graph
            
            # Yield the log of this step and pause
            yield log_entry
            
            # Resume on the next call
            current_node = next_node
            step_index += 1