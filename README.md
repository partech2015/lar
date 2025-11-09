🍀 Lár: A "Define-by-Run" Agentic Framework

Lár (Irish for "core" or "center") is a "define-by-run" agentic framework built in Python, inspired by the dynamic graphs of PyTorch.

It is designed to solve the "black box" problem in AI agent development. Instead of building rigid, static chains, Lár allows you to build dynamic, stateful agents as a graph of simple Python nodes.

The core philosophy is "Glass Box, not Black Box." You can see and debug every thought, action, and choice your agent makes.

⭐️ Key Features

Define-by-Run: Your agent's "thought process" isn't a static plan. It's a dynamic graph that builds itself as it executes, allowing for loops, self-correction, and complex branching.

Simple, Powerful Primitives: Build any agent with just four core node types:

LLMNode: To Think.

ToolNode: To Act.

RouterNode: To Choose.

GraphExecutor: The engine that Runs it all.

Stateful & Debuggable: State is an explicit object, not a hidden variable. You can inspect the full state of your agent after every single step.

Lár.ai AgentScope: A built-in Streamlit visualizer (visualizer_app.py) that lets you run your agents step-by-step and inspect the graph and state changes in real-time.

🚀 Quick Start: The "Self-Correcting" Agent

This example shows an agent that writes Python code, tests it, and loops back to correct itself if it finds an error.

1. Install Dependencies

This project uses Poetry.

# Install project dependencies (lar, streamlit, pytest, etc.)
poetry install


2. Set Your API Key

Create a .env file in the root of the project:

# .env
GOOGLE_API_KEY='YOUR_API_KEY_HERE'


3. Run the AgentScope Visualizer

The best way to experience lar is with the interactive AgentScope debugger.

poetry run streamlit run visualizer_app.py


Your browser will open. Click "Start Agent" and then "Next Step" to watch the agent think, fail, loop, and correct itself, step-by-step.

4. Running the pytest Demos

You can also run the full suite of tests, including the self-correcting agent test, from your terminal:

poetry run pytest


📦 Core Concepts: The 4 Primitives

Lár is built on four simple classes that you combine to create complex behavior.

1. The GraphState

A simple Python class that holds the "memory" of the agent in a dictionary.

state = GraphState(initial_state={"user_query": "Hello"})
state.set("new_data", 123)
data = state.get("user_query")


2. The BaseNode

The "contract" for all nodes. The execute method must return the next node to run, or None to stop.

class MyNode(BaseNode):
    def execute(self, state: GraphState):
        # ... do logic ...
        return SomeOtherNode()


3. The GraphExecutor

The "engine" that runs the graph. It's a simple generator that runs one node at a time.

# The executor is a generator
agent_executor = GraphExecutor().run_step_by_step(start_node, state)

# Run the first step
step_1_log = next(agent_executor)

# Run the second step
step_2_log = next(agent_executor)


4. The "Lego Bricks"

LLMNode(model_name, prompt_template, output_key, next_node):
Calls the Gemini API. It formats the prompt_template with data from the state and saves the result to the output_key.

ToolNode(tool_function, input_keys, output_key, next_node, error_node):
Runs any Python function. It gathers arguments from the input_keys in the state, runs the function, and saves the result to the output_key. If the function fails, it routes to the error_node.

RouterNode(decision_function, path_map, default_node):
The "if" statement. It runs the decision_function, which inspects the state and returns a string (e.g., "success"). The RouterNode then uses this string to find the next node to run from the path_map.

🗺️ The Roadmap: lar vs. Lár.ai

This project follows the "Open Core" model (like Git/GitHub).

lar (The Core): This repository. The powerful, free, and open-source library for building and running agents locally.

Lár.ai (The Cloud): The future commercial product. A web platform for deploying, hosting, managing, and collaborating on lar agents at scale. The AgentScope app is the prototype for this "killer feature."