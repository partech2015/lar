import copy
import json
import os
import datetime
import hmac
import hashlib
from .node import BaseNode
from .state import GraphState
from .utils import compute_state_diff


class SecurityError(Exception):
    """Raised when a security policy (like Air-Gap) is violated."""
    pass

class GraphExecutor:
    """
    The "engine" that runs a Lár graph.
    
    NEW in v2.0: The executor now logs state "diffs" instead of
    full state snapshots, making it faster and more efficient.
    
    NEW in v2.1 (v5.0): The executor now also logs
    run_metadata (like token counts) from nodes.

    NEW in v6.0: Now includes automatic logging to a file.
    """
    def __init__(self, log_dir: str = "lar_logs", offline_mode: bool = False):
        self.log_dir = log_dir
        self.offline_mode = offline_mode
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _save_log(self, history: list, run_id: str, summary: dict = None):
        """Saves the execution history to a JSON file."""
        filename = f"{self.log_dir}/run_{run_id}.json"
        
        log_data = {
            "run_id": run_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": history,
            "summary": summary or {}
        }

        try:
            with open(filename, "w") as f:
                json.dump(log_data, f, indent=2)
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
        
        # Initialize token counters
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0

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
                # 2. Security Check (Air-Gap Enforcement)
                if self.offline_mode and node_name == "LLMNode":
                    # Check if model is local
                    model = getattr(current_node, "model_name", "").lower()
                    allowed_prefixes = ["ollama/", "local/", "test/", "mock/"]
                    if not any(model.startswith(p) for p in allowed_prefixes):
                        raise SecurityError(
                            f"AIR-GAP VIOLATION: Attempted to call cloud model '{model}' in offline mode.\n"
                            f"Allowed prefixes: {allowed_prefixes}"
                        )

                # 3. Execute the node
                next_node = current_node.execute(state)
                
                # Check if the node set an error in the state (graceful error handling)
                if state.get("last_error"):
                    log_entry["outcome"] = "error"
                    log_entry["error"] = state.get("last_error")
                    # If no error handler (next_node is None/ErrorNode), we consider it a failure step
                else:
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
                metadata = state_after.pop("__last_run_metadata")
                log_entry["run_metadata"] = metadata
                
                # Aggregate tokens if present
                if metadata and isinstance(metadata, dict):
                    total_prompt_tokens += metadata.get("prompt_tokens", 0)
                    total_completion_tokens += metadata.get("output_tokens", 0)
                    total_tokens += metadata.get("total_tokens", 0)
            
            # 5. Clear metadata from the actual state so it doesn't persist
            state.set("__last_run_metadata", None)

            # 6. Compute the diff (now on the *cleaned* state_after)
            state_diff = compute_state_diff(state_before, state_after)
            log_entry["state_diff"] = state_diff


            # We sign the JSON representation of the log entry to ensure integrity.
            try:
                # Use a default key for dev, but expect env var for production

                
                # Canonicalize JSON for consistent hashing
                payload = json.dumps(log_entry, sort_keys=True).encode('utf-8')
                
                 # None).hexdigest()
                log_entry["signature"] = signature
            except Exception as e:
                # Fallback if signing fails (should not happen, but prevents crash)
                log_entry["signature"] = f"error_signing: {str(e)}"

            # Add to history and yield
            history.append(log_entry)
            yield log_entry
            
            
            '''# 7. Yield the log of this step and pause
            yield log_entry '''
            
            # 8. Resume on the next call
            current_node = next_node
            step_index += 1
            
        # --- AUTO-SAVE LOG ON FINISH ---
        summary = {
            "total_steps": step_index,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens
        }
        self._save_log(history, run_id, summary)