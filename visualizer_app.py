import streamlit as st
import graphviz
import os
import json
from dotenv import load_dotenv

# --- Import Your Lár Library ---
# This import works because your app is in the root
# and your library is in src/
from lar import (
    GraphExecutor, 
    BaseNode,
    LLMNode, 
    ToolNode,
    RouterNode,
    AddValueNode,
    GraphState
)

# --- Load API Keys ---
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY not found in .env file. Please add it to run the agent.")

# === Agent Components (Tools & Logic) ===

def run_generated_code(code_string: str) -> str:
    """A 'tool' that executes LLM-generated code."""
    try:
        # Strip markdown fences
        if code_string.startswith("```python"):
            code_string = code_string.strip().split("\n", 1)[1]
            if code_string.endswith("```"):
                code_string = code_string.rsplit("\n", 1)[0]

        local_scope = {}
        exec(code_string, {}, local_scope)
        
        if 'add_five' not in local_scope:
            raise NameError("The function 'add_five' was not defined.")
            
        func = local_scope['add_five']
        result = func(10)
        
        if result != 15:
            raise ValueError(f"Logic error: Expected 15, but got {result}")
            
        return "Success!"
        
    except Exception as e:
        raise e

def judge_function(state: GraphState) -> str:
    """The 'choice' logic for the RouterNode."""
    if state.get("last_error"):
        # Clear the error before the next attempt
        state.set("last_error", None) 
        return "failure"
    else:
        return "success"

def build_agent_graph(writer_prompt: str) -> BaseNode:
    """Builds the complete self-correcting agent graph."""
    
    # Destination Nodes
    success_node = AddValueNode(key="final_status", value="SUCCESS", next_node=None)
    critical_fail_node = AddValueNode(key="final_status", value="CRITICAL_FAILURE", next_node=None)

    # Corrector Node (LLM)
    corrector_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        Your last attempt to write a Python function failed.
        CODE: {code_string}
        ERROR: {last_error}
        Please fix the code and ONLY output the complete, corrected Python function.
        """,
        output_key="code_string",
        next_node=None  # Will be set later to create the loop
    )

    # Judge Node (Router)
    judge_node = RouterNode(
        decision_function=judge_function,
        path_map={ "success": success_node, "failure": corrector_node },
        default_node=critical_fail_node
    )
    
    # Tester Node (Tool)
    tester_node = ToolNode(
        tool_function=run_generated_code,
        input_keys=["code_string"],
        output_key="test_result",
        next_node=judge_node,
        error_node=judge_node
    )
    
    # Writer Node (LLM) - The start of the graph
    writer_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template=writer_prompt, # Use the prompt from the UI
        output_key="code_string",
        next_node=tester_node
    )
    
    # Create the loop
    corrector_node.next_node = tester_node
    
    return writer_node

# === New "Killer" UI Helper Functions ===

def compute_state_diff(before: dict, after: dict) -> dict:
    """Calculates the diff between two state dictionaries."""
    diff = {"added": {}, "removed": {}, "modified": {}}
    all_keys = set(before.keys()) | set(after.keys())
    
    for key in all_keys:
        if key not in before:
            diff["added"][key] = after[key]
        elif key not in after:
            diff["removed"][key] = before[key]
        elif before[key] != after[key]:
            diff["modified"][key] = {"old": before[key], "new": after[key]}
            
    return diff

def display_diff(diff_data: dict):
    """Renders the state diff in a clean, color-coded way."""
    if not any(diff_data.values()):
        st.info("No state changes in this step.")
        return

    diff_text = []
    
    # Added (Green)
    for key, value in diff_data["added"].items():
        diff_text.append(f"+ ADDED: '{key}'")
        value_str = json.dumps(value, indent=2)
        diff_text.extend([f"  {line}" for line in value_str.splitlines()])

    # Removed (Red)
    for key, value in diff_data["removed"].items():
        diff_text.append(f"- REMOVED: '{key}'")
        value_str = json.dumps(value, indent=2)
        diff_text.extend([f"  {line}" for line in value_str.splitlines()])

    # Modified (Yellow/Blue)
    for key, values in diff_data["modified"].items():
        diff_text.append(f"~ MODIFIED: '{key}'")
        old_str = json.dumps(values['old'], indent=2)
        new_str = json.dumps(values['new'], indent=2)
        diff_text.append("  --- BEFORE ---")
        diff_text.extend([f"  - {line}" for line in old_str.splitlines()])
        diff_text.append("  --- AFTER ---")
        diff_text.extend([f"  + {line}" for line in new_str.splitlines()])
    
    st.code("\n".join(diff_text), language='diff')

def render_graph_history(history: list) -> str:
    """Takes the history log and builds a Graphviz DOT string."""
    dot = graphviz.Digraph(comment='Agent Execution Graph')
    dot.attr(bgcolor="transparent", rankdir="TB") # Top-to-Bottom
    dot.attr('node', shape='box', style='filled,rounded', 
             fontname='sans-serif', fontcolor='white', color='#4b5563')
    dot.attr('edge', fontname='sans-serif', fontcolor='white', color='white')

    dot.node("START", "START", shape="Mdiamond", fillcolor="#6366f1") # Start node

    if not history:
        dot.edge("START", "...")
        return dot

    last_step_id = "START"
    for i, step in enumerate(history):
        step_id = f"step_{i}"
        label = f"Step {i}: {step['node']}\n(Outcome: {step['outcome']})"
        
        # Color nodes
        if step['outcome'] == 'error':
            dot.node(step_id, label, fillcolor='#ef4444') # Red
        else:
            dot.node(step_id, label, fillcolor='#22c55e') # Green
        
        dot.edge(last_step_id, step_id)
        last_step_id = step_id
            
    # Highlight the last node run in blue
    dot.node(last_step_id, label, fillcolor='#3b82f6')
    
    # Add a final "END" node if the agent is finished
    if "final_status" in history[-1]["state_after"]:
        end_id = "END"
        dot.node(end_id, "END", shape="Mdiamond", fillcolor='#6b7280') # Gray
        dot.edge(last_step_id, end_id)
    
    return dot

# === Streamlit App UI ===

st.set_page_config(layout="wide", page_title="Lár.ai AgentScope")

# Initialize session state
if "executor" not in st.session_state:
    st.session_state.executor = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- Sidebar (Controls) ---
with st.sidebar:
    st.markdown("<h1><span style='color: #60a5fa;'>Lár.ai</span> AgentScope</h1>", unsafe_allow_html=True)
    st.write("A 'define-by-run' agent visualizer.")
    
    st.subheader("1. Agent Setup")
    task = st.text_area("Initial Task", 
                        "Write a Python function called `add_five(x)` that returns x + 5.",
                        height=100)
    
    writer_prompt = st.text_area("Writer Node Prompt",
        "Write a Python function called `add_five(x)` that solves this task: {task}. "
        "For this test, make a small syntax error on purpose (e.g., forget the colon). "
        "ONLY output the Python function.",
        height=150)

    if st.button("Start Agent", type="primary", use_container_width=True):
        with st.spinner("Building agent and running first step..."):
            # Build the graph
            full_prompt = writer_prompt.format(task=task)
            start_node = build_agent_graph(full_prompt)
            
            # Create the executor
            executor = GraphExecutor()
            st.session_state.executor = executor.run_step_by_step(start_node, {"task": task})
            
            # --- NEW: Run the *first step* automatically ---
            try:
                st.session_state.history = []
                first_step = next(st.session_state.executor)
                st.session_state.history.append(first_step)
                st.success("Agent started! Click 'Next Step' to continue.")
            except Exception as e:
                st.error(f"Agent failed on first step: {e}")
                st.session_state.executor = None

    # --- Step-by-Step Controls ---
    st.subheader("2. Execution")
    
    # Disable "Next Step" if the agent is not running
    is_disabled = st.session_state.executor is None
    
    if st.button("Next Step", use_container_width=True, disabled=is_disabled):
        try:
            # Run the next step
            step_log = next(st.session_state.executor)
            st.session_state.history.append(step_log)
        except StopIteration:
            st.success("Agent has finished the run.")
            st.session_state.executor = None # Clear the executor
        except Exception as e:
            st.error(f"Agent failed with an unexpected error: {e}")
            st.session_state.executor = None
        
        st.rerun() # Rerun the app to update the UI

    if st.button("Reset", use_container_width=True):
        st.session_state.executor = None
        st.session_state.history = []
        st.rerun()


# --- Main Content Area (Graph & State) ---
col1, col2 = st.columns([3, 2]) # Make graph wider

with col1:
    st.header("Execution Graph")
    graph_container = st.container(border=True)
    if not st.session_state.history:
        graph_container.info("Click 'Start Agent' in the sidebar to begin.")
    else:
        try:
            dot_graph = render_graph_history(st.session_state.history)
            graph_container.graphviz_chart(dot_graph)
        except Exception as e:
            graph_container.error(f"Failed to render graph: {e}")

with col2:
    st.header("State Inspector")
    inspector_container = st.container(border=True, height=600)
    
    if not st.session_state.history:
        inspector_container.info("State will appear here as the agent runs.")
    else:
        # Get the most recent step
        last_step = st.session_state.history[-1]
        
        # --- NEW "KILLER" UX ---
        tab_changes, tab_full_state = inspector_container.tabs([
            "Changes in Last Step", 
            "Full Current State"
        ])

        with tab_changes:
            st.subheader(f"Step {last_step['step']}: {last_step['node']}")
            # Calculate and display the diff
            diff = compute_state_diff(last_step["state_before"], last_step["state_after"])
            display_diff(diff)

        with tab_full_state:
            st.subheader("Full State (After Last Step)")
            st.json(last_step["state_after"])
        
        # --- Add a full history log at the bottom ---
        with st.expander("Show Full Execution Log"):
            st.json(st.session_state.history)