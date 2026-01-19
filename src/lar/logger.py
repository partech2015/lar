import json
import os
import datetime
from typing import List, Dict, Any, Optional


class AuditLogger:
    """
    Handles audit trail logging and persistence for Lár graph executions.
    
    This class is responsible for recording execution history and saving
    it to JSON files for compliance and debugging purposes.
    """
    
    def __init__(self, log_dir: str = "lar_logs"):
        """
        Initialize the AuditLogger.
        
        Args:
            log_dir (str): Directory where audit logs will be saved.
        """
        self.log_dir = log_dir
        self.history: List[Dict[str, Any]] = []
        
        # Create log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_step(self, step_data: dict) -> None:
        """
        Record a single step execution.
        
        Args:
            step_data (dict): The execution data for this step, including:
                - step (int): Step index
                - timestamp (str): ISO format timestamp
                - node (str): Node class name
                - state_before (dict): State snapshot before execution
                - state_diff (dict): What changed in this step
                - run_metadata (dict): Token usage and model info
                - outcome (str): "success" or "error"
        """
        self.history.append(step_data)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete execution history.
        
        Returns:
            List[Dict[str, Any]]: All logged steps
        """
        return self.history.copy()
    
    def save_to_file(self, run_id: str, user_id: Optional[str] = None, 
                     summary: Optional[Dict[str, Any]] = None) -> None:
        """
        Persist the audit log to a JSON file.
        
        Args:
            run_id (str): Unique identifier for this run (UUIDv4)
            user_id (str, optional): User identifier for multi-tenant systems
            summary (dict, optional): Aggregated summary data (tokens, steps, etc.)
        """
        filename = f"{self.log_dir}/run_{run_id}.json"
        
        log_data = {
            "run_id": run_id,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": self.history,
            "summary": summary or {}
        }

        try:
            with open(filename, "w") as f:
                json.dump(log_data, f, indent=2)
            print(f"\n✅ [AuditLogger] Log saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️ [AuditLogger] Failed to save log: {e}")
    
    def clear_history(self) -> None:
        """Clear the current execution history (useful for reusing the logger)."""
        self.history = []
