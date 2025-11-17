"""
Lár: A "Define-by-Run" Agentic Framework.
This file makes the core classes available for easy import.
"""

# Import the core classes to the top level of the package
from .state import GraphState
from .node import (
    BaseNode, 
    AddValueNode, 
    LLMNode, 
    RouterNode,
    ToolNode,
    ClearErrorNode  
)
from .executor import GraphExecutor
from .utils import compute_state_diff, apply_diff

# Define what happens when a user types `from lar import *`
__all__ = [
    "GraphState",
    "BaseNode",
    "AddValueNode",
    "LLMNode",
    "RouterNode",
    "ToolNode",
    "ClearErrorNode",
    "GraphExecutor",
    "compute_state_diff",
    "apply_diff"  
]