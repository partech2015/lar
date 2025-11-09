# src/lar/node.py
from abc import ABC, abstractmethod
from .state import GraphState  # Import our new state class

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
    This node demonstrates:
    1. Taking arguments in __init__.
    2. Modifying the state.
    3. Returning the next node to continue the graph.
    """
    def __init__(self, key: str, value: any, next_node: BaseNode = None):
        self.key = key
        self.value = value
        self.next_node = next_node

    def execute(self, state: GraphState):
        print(f"  [AddValueNode]: Setting state['{self.key}'] = '{self.value}'")
        state.set(self.key, self.value)
        
        # This is the "define-by-run" magic: we return the next step
        return self.next_node

class PrintStateNode(BaseNode):
    """
    A simple node that prints the current state.
    This node demonstrates:
    1. Reading from the state.
    2. Returning `None` to end the graph execution.
    """
    def execute(self, state: GraphState):
        print(f"  [PrintStateNode]: Current state is {state.get_all()}")
        
        # Returning None signals to the GraphExecutor to stop
        return None

# src/lar/node.py (add this at the end)

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv() # This reads your .env file and sets the env variables
# ... (Keep your BaseNode, AddValueNode, and PrintStateNode classes) ...

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
        """
        Args:
            model_name (str): The name of the model to use (e.g., "gemini-1.5-flash").
            prompt_template (str): A f-string-like template for the prompt.
                                   Keys in braces {key} will be filled from state.
            output_key (str): The state key to save the LLM's text response to.
            next_node (BaseNode, optional): The next node to run.
        """
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.next_node = next_node

        # Initialize the model client once and cache it
        if LLMNode._model_client is None:
            print("  [LLMNode]: Initializing Gemini model client...")
            genai.configure() # Configures from GOOGLE_API_KEY env variable
            LLMNode._model_client = genai.GenerativeModel(self.model_name)
    
    def execute(self, state: GraphState):
        try:
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
            
        except Exception as e:
            print(f"  [LLMNode] ERROR: {e}")
            # You could also return a specific ErrorNode here
            return None # Stop the graph on error for now
# src/lar/node.py (add this at the end)

from typing import Callable, Dict

# ... (Keep your BaseNode, AddValueNode, PrintStateNode, LLMNode classes) ...

class RouterNode(BaseNode):
    """
    A node that provides conditional routing (branching).
    
    It uses a "decision function" to inspect the state and decide
    which node to execute next based on a simple string output.
    """
    def __init__(self,
                 decision_function: Callable[[GraphState], str],
                 path_map: Dict[str, BaseNode],
                 default_node: BaseNode = None):
        """
        Args:
            decision_function (Callable): A function that takes the `GraphState`
                and returns a string key (e.g., "search", "respond").
            path_map (Dict[str, BaseNode]): A dictionary mapping the string keys
                from the decision function to the actual node to run.
                Example: {"search": SearchNode(), "respond": LLMNode()}
            default_node (BaseNode, optional): A fallback node to run if the
                decision function returns a key that is not in the path_map.
        """
        self.decision_function = decision_function
        self.path_map = path_map
        self.default_node = default_node

    def execute(self, state: GraphState):
        # 1. Call the decision function to get the route key
        route_key = self.decision_function(state)
        print(f"  [RouterNode]: Decision function returned '{route_key}'")

        # 2. Find the next node in the path_map
        next_node = self.path_map.get(route_key)
        
        # 3. Handle cases where the route is not found
        if next_node is None:
            if self.default_node:
                print(f"  [RouterNode]: Route '{route_key}' not found. Using default path.")
                return self.default_node
            else:
                print(f"  [RouterNode] ERROR: Route '{route_key}' not found and no default path set.")
                return None # Stop the graph
        
        # 4. Return the chosen node
        print(f"  [RouterNode]: Routing to {next_node.__class__.__name__}")
        return next_node
    
# src/lar/node.py (add this at the end)

from typing import Callable, Dict, List

# ... (Keep your BaseNode, AddValueNode, PrintStateNode, LLMNode, RouterNode classes) ...

class ToolNode(BaseNode):
    """
    A node that executes a Python function (a "tool").
    
    It dynamically maps inputs from the GraphState to the
    function's arguments and saves the function's return
    value back to the state. It also supports error handling
    by routing to a different node on failure.
    """
    def __init__(self,
                 tool_function: Callable,
                 input_keys: List[str],
                 output_key: str,
                 next_node: BaseNode,
                 error_node: BaseNode = None):
        """
        Args:
            tool_function (Callable): The Python function to execute.
            input_keys (List[str]): A list of keys to read from the state.
                                    The values are passed to the tool_function
                                    as positional arguments in the same order.
            output_key (str): The state key to save the tool's return value to.
            next_node (BaseNode): The node to run if the tool executes successfully.
            error_node (BaseNode, optional): The node to run if the tool
                                            raises an exception. If None, the
                                            graph will stop on an error.
        """
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
                # Route to the error-handling node
                return self.error_node
            else:
                # Stop the graph
                return None