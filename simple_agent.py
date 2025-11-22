"""
This script is a complete, runnable example of the `lar` framework.
It builds and runs a 2-step agent:
1. "Writer" (LLMNode): Writes a story.
2. "Packager" (AddValueNode): Saves the story as the final answer.

It then saves a beautiful, table-formatted "glass box" audit log
to a text file for you to review.
"""

# === Block 1: Imports ===
# --- Standard Python Libraries ---
import os
import json
import datetime
from dotenv import load_dotenv
from rich.console import Console

# --- Lár "Lego Bricks" ---
# We import the core components from our engine
from lar import (
    GraphExecutor, 
    BaseNode,
    LLMNode, 
    AddValueNode,
    GraphState,
    build_log_table  
)
from lar.utils import compute_state_diff, apply_diff


"""
- `lar` imports: These are your "Lego Bricks" from the `lar-engine`.
  - `GraphExecutor`: The "Conveyor Belt" that runs the agent.
  - `LLMNode`: The "Brain" that calls Gemini.
  - `AddValueNode`: The "Utility" node that copies data.
  - `GraphState`: The "Clipboard" or "Memory" object.
- `lar.utils`: These are our helper functions for reading and writing
  to the "glass box" log.

"""

# === Block 2: Setup ===
print("--- Lár 'StoryBot' Initializing... ---")
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()

"""
This block loads your `.env` file and checks for the 
GOOGLE_API_KEY. The agent will stop if it's not found.
"""

# === Block 3: Building the Agent Graph ===
"""
This is the "assembly line" blueprint. 
We define the nodes (stations) backwards, from the end to the start, 
so we can "plug" them into each other.
"""

# --- Station 2: The "Packager" (The End) ---
finish_node = AddValueNode(
    key="final_response",
    value="{story_text}",
    next_node=None
)
"""
We create our *last* node, the "Packager."
- key="final_response": It will save its data to a new key called 'final_response'.
- value="{story_text}": This is the "smart" part. The {} tell our "state-aware" 
  AddValueNode to *copy* the value from `state.get("story_text")`.
- next_node=None: This is critical. It tells the GraphExecutor that
  the assembly line is **finished** after this node.
"""

# --- Station 1: The "Writer" (The Start) ---
story_writer_node = LLMNode(
    model_name="gemini/gemini-2.5-pro",
    prompt_template="Write a short, one-paragraph story about: {topic}",
    output_key="story_text",
    next_node=finish_node,
    
    #generation_config={
    #    "temperature": 1.0,  
    #    "top_p": 0.95,
    #    "max_output_tokens": 250,
    #}
)

"""
We create our *first* node, the "Writer."
- prompt_template="...{topic}": This is the prompt. The `LLMNode` will
  automatically pull the `topic` from the GraphState.
- output_key="story_text": It will save Gemini's story to a new
  key called 'story_text'.
- next_node=finish_node: This is the "wiring." It tells the "Conveyor Belt"
  that after this node runs, the next station is `finish_node`.
"""

# === Block 4: Running the Agent ===

print("--- Lár Agent 'StoryBot' is running... ---")

# 1. Create the "Conveyor Belt" object
executor = GraphExecutor()

# 2. Create the "Clipboard" and write the first task on it
initial_state = {
    "task": "Write a story about Open Source Agentic Frameworks",
    "topic": "Open Source Frameworks"
}

# 3. Run the agent and get the full "flight log"
result_log = list(executor.run_step_by_step(
    start_node=story_writer_node, 
    initial_state=initial_state
))

"""
This is the "Go" button.
- `executor = GraphExecutor()`: We create the "Conveyor Belt."
- `initial_state = {...}`: We create the "Clipboard" and give it the `topic`.
- `result_log = list(...)`: We tell the executor to start at our `story_writer_node`
  and run from start to finish (`list()`) and give us the full log.
"""

# === Block 5: Saving the "Glass Box" Log ===
"""
This happens *after* the agent is done.
`result_log` is now a list of all the steps.
"""

print("\n--- AGENT RUN COMPLETE. ---")

# 1. Reconstruct the final state to find the answer
final_state_data = initial_state
for step in result_log:
    final_state_data = apply_diff(final_state_data, step["state_diff"])


"""
This is the "Log Replay." We loop through the `result_log` (which has the
`state_diff`s) and use our imported `apply_diff` function to
re-build the final state, step-by-step.
"""

# 2. Create a "virtual" console that we can record
console = Console(record=True)

# 3. Print the final answer *to the recording*
console.print("\n[bold]--- FINAL ANSWER ---[/bold]")
console.print(f"[italic green]{final_state_data.get('final_response')}[/italic green]")

# 4. Print the beautiful table *to the recording*
console.print("\n[bold]--- FULL HISTORY (TABLE) ---[/bold]")
# This one line now does all the work, using the imported function
log_table = build_log_table(result_log) 
console.print(log_table)

# 5. (Optional) Print the raw JSON *to the recording*
console.print("\n[bold]--- FULL HISTORY (RAW JSON) ---[/bold]")
console.print_json(data=result_log)

