import time
import google.generativeai as genai
from abc import ABC, abstractmethod
from .state import GraphState
from typing import Callable, Dict, List
from google.api_core import exceptions as google_exceptions

# --- The Core API "Contract" ---
class BaseNode(ABC):
    """
    This is the "master blueprint" or "contract" for all other nodes.
    It forces all other node classes to have an `execute` method.
    """
    
    @abstractmethod
    def execute(self, state: GraphState):
        """
        Executes the node's logic.
        Returns:
            BaseNode | None: The next node to execute, or None to stop.
        """
        pass

# --- Node Implementations (The "Lego Bricks") ---

# --- THIS IS THE FIX (v1.2) ---
# The AddValueNode is now "state-aware"
class AddValueNode(BaseNode):
    """
    A utility node for adding or *copying* data into the state.
    
    If the value is a string like "{key_name}", it will
    copy the value from state.get("key_name").
    """
    
    def __init__(self, key: str, value: any, next_node: BaseNode = None):
        """
        Args:
            key (str): The key to write to in the state (e.g., "final_status").
            value (any): The value to write. Can be a literal (like "SUCCESS")
                         or a state key (like "{draft_answer}").
            next_node (BaseNode, optional): The next node to run. Defaults to None.
        """
        self.key = key
        self.value = value
        self.next_node = next_node

    def execute(self, state: GraphState):
        value_to_set = self.value
        
        # Check if the value is a state reference (like "{draft_answer}")
        if isinstance(self.value, str) and self.value.startswith("{") and self.value.endswith("}"):
            # It's a reference. Let's try to copy the value.
            key_to_copy = self.value.strip("{}")
            if state.get(key_to_copy) is not None:
                value_to_set = state.get(key_to_copy)
                print(f"  [AddValueNode]: Copying state['{key_to_copy}'] to state['{self.key}']")
            else:
                # Key not found, just set the literal string "{draft_answer}"
                print(f"  [AddValueNode] WARN: Key '{key_to_copy}' not in state. Setting literal value.")
        else:
             # It's a literal value, not a state reference
             print(f"  [AddValueNode]: Setting state['{self.key}'] = '{str(value_to_set)[:50]}...'")

        # Set the final value in the state
        state.set(self.key, value_to_set)
        
        # Return the next node (which is often None, to end the graph)
        return self.next_node
# --- END FIX ---

class LLMNode(BaseNode):
    """
    This is the agent's "brain." It calls the Gemini LLM.
    It is "resilient" and will retry on rate-limit errors.
    """
    _model_client = None

    def __init__(self, 
                 model_name: str, 
                 prompt_template: str, 
                 output_key: str, 
                 next_node: BaseNode = None,
                 max_retries: int = 3):
        
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.next_node = next_node
        self.max_retries = max_retries

        if LLMNode._model_client is None:
            print("  [LLMNode]: Initializing Gemini model client...")
            genai.configure() 
            LLMNode._model_client = genai.GenerativeModel(self.model_name)
    
    def execute(self, state: GraphState):
        prompt = self.prompt_template.format(**state.get_all())
        print(f"  [LLMNode]: Sending prompt: '{prompt[:50]}...'")
        
        retries = 0
        base_delay = 1
        
        while retries <= self.max_retries:
            try:
                response = self._model_client.generate_content(prompt)
                state.set(self.output_key, response.text)
                print(f"  [LLMNode]: Saved response to state['{self.output_key}']")
                return self.next_node
            except google_exceptions.ResourceExhausted as e:
                print(f"  [LLMNode] WARN: Rate limit hit. Retrying in {base_delay}s... (Attempt {retries + 1}/{self.max_retries})")
                time.sleep(base_delay)
                retries += 1
                base_delay *= 2
            except Exception as e:
                print(f"  [LLMNode] CRITICAL ERROR: {e}")
                raise e
        print(f"  [LLMNode] FATAL: Failed after {self.max_retries} retries.")
        raise google_exceptions.ResourceExhausted(f"LLMNode failed after {self.max_retries} retries.")

class RouterNode(BaseNode):
    """
    This is the agent's "if/else" statement or "choice" logic.
    """
    def __init__(self,
                 decision_function: Callable[[GraphState], str],
                 path_map: Dict[str, BaseNode],
                 default_node: BaseNode = None):
        self.decision_function = decision_function
        self.path_map = path_map
        self.default_node = default_node

    def execute(self, state: GraphState):
        route_key = self.decision_function(state)
        print(f"  [RouterNode]: Decision function returned '{route_key}'")
        next_node = self.path_map.get(route_key)
        if next_node:
            print(f"  [RouterNode]: Routing to {next_node.__class__.__name__}")
            return next_node
        elif self.default_node:
            print(f"  [RouterNode]: Route '{route_key}' not found. Using default path.")
            return self.default_node
        else:
            print(f"  [RouterNode] ERROR: Route '{route_key}' not found and no default path set.")
            return None

class ToolNode(BaseNode):
    """
    This is the agent's "hands." It runs any Python function.
    """
    def __init__(self,
                 tool_function: Callable,
                 input_keys: List[str],
                 output_key: str,
                 next_node: BaseNode,
                 error_node: BaseNode = None):
        
        self.tool_function = tool_function
        self.input_keys = input_keys
        self.output_key = output_key
        self.next_node = next_node
        self.error_node = error_node

    def execute(self, state: GraphState):
        try:
            inputs = [state.get(key) for key in self.input_keys]
            print(f"  [ToolNode]: Running {self.tool_function.__name__} with inputs: {inputs}")
            result = self.tool_function(*inputs)
            state.set(self.output_key, result)
            print(f"  [ToolNode]: Saved result to state['{self.output_key}']")
            return self.next_node
        except Exception as e:
            print(f"  [ToolNode] ERROR: {self.tool_function.__name__} failed: {e}")
            state.set("last_error", str(e))
            if self.error_node:
                return self.error_node
            else:
                return None

class ClearErrorNode(BaseNode):
    """
    A simple "janitor" node. Its only job is to clean up
    the 'last_error' key from the state.
    """
    def __init__(self, next_node: BaseNode):
        self.next_node = next_node

    def execute(self, state: GraphState):
        if state.get("last_error") is not None:
            print("  [ClearErrorNode]: Clearing 'last_error' from state.")
            state.set("last_error", None)
        return self.next_node

