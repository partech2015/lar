from abc import ABC, abstractmethod
from .state import GraphState
from typing import Callable, Dict, List
import google.generativeai as genai

# --- The Core API ---

class BaseNode(ABC):
    """
    Abstract base class for all nodes in a Lár graph.
    Each node represents a single unit of work.
    """
    
    @abstractmethod
    def execute(self, state: GraphState):
        """
        Executes the node's logic.

        Args:
            state (GraphState): The current state of the graph. 
                                This object can be read from and written to.

        Returns:
            BaseNode | None: The next node to execute. Return None to 
                             signal the end of the graph's execution.
        """
        pass

# --- v0.1 Example Nodes ---

class AddValueNode(BaseNode):
    """
    A simple node that adds a specific key-value pair to the state.
    """
    def __init__(self, key: str, value: any, next_node: BaseNode = None):
        self.key = key
        self.value = value
        self.next_node = next_node

    def execute(self, state: GraphState):
        print(f"  [AddValueNode]: Setting state['{self.key}'] = '{self.value}'")
        state.set(self.key, self.value)
        return self.next_node

class PrintStateNode(BaseNode):
    """
    A simple node that prints the current state.
    """
    def execute(self, state: GraphState):
        print(f"  [PrintStateNode]: Current state is {state.get_all()}")
        return None

# --- v0.2 Thinking Node ---

class LLMNode(BaseNode):
    """
    A node that calls the Gemini LLM.
    
    It formats a prompt string with values from the state,
    sends the prompt to the Gemini API, and saves the
    text response back into the state.
    """
    _model_client = None

    def __init__(self, 
                 model_name: str, 
                 prompt_template: str, 
                 output_key: str, 
                 next_node: BaseNode = None):
        
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.next_node = next_node

        if LLMNode._model_client is None:
            print("  [LLMNode]: Initializing Gemini model client...")
            genai.configure() 
            LLMNode._model_client = genai.GenerativeModel(self.model_name)
    
    # --- THIS IS THE FIX ---
    # We have REMOVED the try...except block.
    # If the API call fails, it will now raise an exception
    # which the GraphExecutor will catch and log correctly.
    def execute(self, state: GraphState):
        
        # 1. Format the prompt with data from the state
        prompt = self.prompt_template.format(**state.get_all())
        print(f"  [LLMNode]: Sending prompt: '{prompt[:50]}...'")
        
        # 2. Send the prompt to the Gemini API
        response = self._model_client.generate_content(prompt)
        
        # 3. Save the response text to the state
        state.set(self.output_key, response.text)
        print(f"  [LLMNode]: Saved response to state['{self.output_key}']")
        
        # 4. Return the next node
        return self.next_node
    # --- END FIX ---

# --- v0.3 Decision Node ---

class RouterNode(BaseNode):
    """
    A node that provides conditional routing (branching).
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
        
        if next_node is None:
            if self.default_node:
                print(f"  [RouterNode]: Route '{route_key}' not found. Using default path.")
                return self.default_node
            else:
                print(f"  [RouterNode] ERROR: Route '{route_key}' not found and no default path set.")
                return None
        
        print(f"  [RouterNode]: Routing to {next_node.__class__.__name__}")
        return next_node

# --- v0.4 Action Node ---

class ToolNode(BaseNode):
    """
    A node that executes a Python function (a "tool").
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
            # 1. Gather inputs from the state
            inputs = [state.get(key) for key in self.input_keys]
            print(f"  [ToolNode]: Running {self.tool_function.__name__} with inputs: {inputs}")

            # 2. Execute the tool function
            result = self.tool_function(*inputs)

            # 3. Save the output to the state
            state.set(self.output_key, result)
            print(f"  [ToolNode]: Saved result to state['{self.output_key}']")

            # 4. Return the success node
            return self.next_node

        except Exception as e:
            # 5. Handle errors
            print(f"  [ToolNode] ERROR: {self.tool_function.__name__} failed: {e}")
            state.set("last_error", str(e)) # Save the error message
            
            if self.error_node:
                return self.error_node
            else:
                return None

# --- v0.5 Utility Node ---

class ClearErrorNode(BaseNode):
    """
    A simple utility node that clears the 'last_error' key
    from the state. This is crucial for preventing
    infinite loops in self-correcting graphs.
    """
    def __init__(self, next_node: BaseNode):
        self.next_node = next_node

    def execute(self, state: GraphState):
        if state.get("last_error") is not None:
            print("  [ClearErrorNode]: Clearing 'last_error' from state.")
            state.set("last_error", None)
        return self.next_node