import time
import google.generativeai as genai
from abc import ABC, abstractmethod  # ABC stands for Abstract Base Class
from .state import GraphState
from typing import Callable, Dict, List
from google.api_core import exceptions as google_exceptions

# --- The Core API "Contract" ---

class BaseNode(ABC):
    """
    This is the "master blueprint" or "contract" for all other nodes.
    
    It's an Abstract Base Class (ABC), which means you can't use it directly.
    Instead, it forces all other node classes (like LLMNode, ToolNode, etc.)
    to follow the same rule: they *must* have an `execute` method.
    
    This "contract" is what allows your GraphExecutor to run any node
    without knowing what it does.
    """
    
    @abstractmethod
    def execute(self, state: GraphState):
        """
        This is the one required function for every node. The GraphExecutor
        will call this function when it's this node's turn to run.

        Args:
            state (GraphState): The agent's "clipboard" or memory. The node
                                can read from this (`state.get(...)`) and
                                write to it (`state.set(...)`).

        Returns:
            BaseNode | None: This is the "define-by-run" magic.
                             - If it returns *another node object*, the
                               GraphExecutor will run that node next.
                             - If it returns *None*, the GraphExecutor will
                               stop, and the agent's run will end.
        """
        pass

# --- Node Implementations (The "Lego Bricks") ---

class AddValueNode(BaseNode):
    """
    This is a simple utility node for adding or copying data into the state.
    
    It's the "Success" or "Failure" node at the end of a graph, 
    but it can also be used to set up initial values.
    
    It is "state-aware": if you give it a value like "{draft_answer}",
    it will intelligently copy the value of `state.get("draft_answer")`
    instead of just saving the literal string.
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

class LLMNode(BaseNode):
    """
    This is the agent's "brain." It calls the Gemini LLM.
    
    It's a "resilient" node: if it gets a rate-limit error (429)
    from the API, it will automatically wait and retry with
    "exponential backoff" (1s, 2s, 4s...) before failing.
    """
    
    # A "class variable" to hold the Gemini client.
    # This way, we only initialize it *once* for all LLMNodes,
    # not every single time a node is created.
    _model_client = None

    def __init__(self, 
                 model_name: str, 
                 prompt_template: str, 
                 output_key: str, 
                 next_node: BaseNode = None,
                 max_retries: int = 3): # How many times to retry on a 429
        
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.next_node = next_node
        self.max_retries = max_retries

        # Initialize the client only if it hasn't been done yet
        if LLMNode._model_client is None:
            print("  [LLMNode]: Initializing Gemini model client...")
            genai.configure() # Reads GOOGLE_API_KEY from your .env
            LLMNode._model_client = genai.GenerativeModel(self.model_name)
    
    def execute(self, state: GraphState):
        # 1. Read from state to build the prompt
        prompt = self.prompt_template.format(**state.get_all())
        print(f"  [LLMNode]: Sending prompt: '{prompt[:50]}...'")
        
        retries = 0
        base_delay = 1  # Start with a 1-second delay
        
        while retries <= self.max_retries:
            try:
                # 2. Try to call the API
                response = self._model_client.generate_content(prompt)
                
                # 3. If successful, save to state and return
                state.set(self.output_key, response.text)
                print(f"  [LLMNode]: Saved response to state['{self.output_key}']")
                return self.next_node

            except google_exceptions.ResourceExhausted as e:
                # 4. If rate limited (429), wait and retry
                print(f"  [LLMNode] WARN: Rate limit hit. Retrying in {base_delay}s... (Attempt {retries + 1}/{self.max_retries})")
                time.sleep(base_delay)
                retries += 1
                base_delay *= 2  # This is the "exponential backoff"
            
            except Exception as e:
                # 5. If it's a *different* error (e.g., a 404 model not found),
                # fail immediately. We don't want to retry.
                print(f"  [LLMNode] CRITICAL ERROR: {e}")
                raise e # This will be caught by the GraphExecutor

        # 6. If we've used all our retries and still failed
        print(f"  [LLMNode] FATAL: Failed after {self.max_retries} retries.")
        raise google_exceptions.ResourceExhausted(f"LLMNode failed after {self.max_retries} retries.")

class RouterNode(BaseNode):
    """
    This is the agent's "if/else" statement or "choice" logic.
    
    It runs a simple Python function (the "decision_function")
    which inspects the state and returns a simple string (a "key").
    
    It then uses that key to look up the *next node to run*
    in a dictionary (the "path_map").
    """
    
    def __init__(self,
                 decision_function: Callable[[GraphState], str],
                 path_map: Dict[str, BaseNode],
                 default_node: BaseNode = None):
        """
        Args:
            decision_function: The Python function to run (e.g., `judge_function`)
            path_map: A dict mapping string keys to nodes (e.g., 
                      {"success": success_node, "failure": corrector_node})
            default_node: (Optional) A node to run if the key isn't in the map.
        """
        self.decision_function = decision_function
        self.path_map = path_map
        self.default_node = default_node

    def execute(self, state: GraphState):
        # 1. Run the simple logic function
        route_key = self.decision_function(state)
        print(f"  [RouterNode]: Decision function returned '{route_key}'")

        # 2. Look up the next node in the dictionary
        next_node = self.path_map.get(route_key)
        
        # 3. Decide where to go
        if next_node:
            print(f"  [RouterNode]: Routing to {next_node.__class__.__name__}")
            return next_node
        elif self.default_node:
            print(f"  [RouterNode]: Route '{route_key}' not found. Using default path.")
            return self.default_node
        else:
            print(f"  [RouterNode] ERROR: Route '{route_key}' not found and no default path set.")
            return None # Stop the graph

class ToolNode(BaseNode):
    """
    This is the agent's "hands." It runs any Python function.
    
    This node is the "test" in your self-correcting loops. It's
    the "search" in your RAG agent. It's the most versatile node.
    
    It's robust: it runs the function in a `try...except` block
    and can route to a *different* node if an error occurs.
    """
    
    def __init__(self,
                 tool_function: Callable,
                 input_keys: List[str],
                 output_key: str,
                 next_node: BaseNode,
                 error_node: BaseNode = None):
        """
        Args:
            tool_function: The Python function to run (e.g., `run_generated_code`)
            input_keys: A list of keys to read from state. These are
                        passed as arguments to the tool (e.g., ["code_string"])
            output_key: The state key to save the tool's return value to.
            next_node: The node to run if the tool *succeeds*.
            error_node: The node to run if the tool *fails* (raises an Exception).
        """
        self.tool_function = tool_function
        self.input_keys = input_keys
        self.output_key = output_key
        self.next_node = next_node
        self.error_node = error_node

    def execute(self, state: GraphState):
        try:
            # 1. Gather all inputs for the tool from the state
            inputs = [state.get(key) for key in self.input_keys]
            print(f"  [ToolNode]: Running {self.tool_function.__name__} with inputs: {inputs}")

            # 2. Execute the tool (e.g., run_generated_code("..."))
            result = self.tool_function(*inputs)

            # 3. Save the output
            state.set(self.output_key, result)
            print(f"  [ToolNode]: Saved result to state['{self.output_key}']")

            # 4. On success, return the 'next_node'
            return self.next_node

        except Exception as e:
            # 5. On failure, log the error...
            print(f"  [ToolNode] ERROR: {self.tool_function.__name__} failed: {e}")
            state.set("last_error", str(e)) # Save the error for the Corrector
            
            # ...and return the 'error_node' (e.g., the Router)
            if self.error_node:
                return self.error_node
            else:
                return None # Or just stop

class ClearErrorNode(BaseNode):
    """
    A simple "janitor" node. Its only job is to clean up
    the 'last_error' key from the state.
    
    This is critical for self-correcting loops. You run this
    *after* the CorrectorNode has used the error, so that when
    the agent tries again, the 'last_error' is gone.
    """
    
    def __init__(self, next_node: BaseNode):
        self.next_node = next_node

    def execute(self, state: GraphState):
        if state.get("last_error") is not None:
            print("  [ClearErrorNode]: Clearing 'last_error' from state.")
            state.set("last_error", None)
        return self.next_node