API Reference: Utilities

These are the "scaffolding" components that hold the framework together: the GraphExecutor, the GraphState, and our simple helper nodes.

GraphExecutor

This is the "engine" that runs your graph. You only interact with this at the beginning of a run.

from lar import GraphExecutor

executor = GraphExecutor()

# run_step_by_step is a generator
result_log = list(executor.run_step_by_step(
    start_node=my_start_node, 
    initial_state={"task": "My task"}
))


Methods

run_step_by_step(start_node, initial_state)

This is the core method of lar. It's a Python generator.

It runs one node, yields the "flight log" (step_log) for that step, and then pauses.

This "pause" is what allows your Snath app to be interactive.

It also contains the master try...except block that catches critical, unhandled errors from nodes (like the LLMNode failing after all its retries).

GraphState

This is the "memory" or "clipboard" of your agent. It's a simple Python object that is automatically passed to every node's execute method.

from lar import GraphState

state = GraphState({"task": "My task"})

# Write to the state
state.set("plan", "TEXT")

# Read from the state
my_plan = state.get("plan") 


Methods

set(key, value): Sets a value in the state.

get(key, default=None): Gets a value from the state.

get_all(): Returns a copy of the entire state dictionary.

Utility Nodes

AddValueNode

A simple node to write or copy data. It's "state-aware."

# Sets state["status"] to the literal string "SUCCESS"
success_node = AddValueNode(
    key="final_status", 
    value="SUCCESS", 
    next_node=None
)

# *Copies* the value from state["draft_answer"] 
# into state["final_response"]
copy_answer_node = AddValueNode(
    key="final_response", 
    value="{draft_answer}", 
    next_node=success_node
)


ClearErrorNode

A "janitor" node. Its only job is to clean up the last_error key, which is critical for self-correcting loops.

# After the Corrector runs, this node cleans up
# before looping back to the Tester.
clear_error_node = ClearErrorNode(
    next_node=tester_node
)
