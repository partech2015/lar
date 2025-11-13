import streamlit as st
import graphviz
import os
import json
import datetime
from dotenv import load_dotenv

# --- NEW: Firestore Imports ---
import firebase_admin
from firebase_admin import credentials, firestore

# --- Import Your Lár Library ---
from lar import (
    GraphExecutor, 
    BaseNode,
    LLMNode, 
    ToolNode,
    RouterNode,
    AddValueNode,
    GraphState,
    ClearErrorNode
)
# We also import the new utility
from lar.utils import compute_state_diff 

# --- Load API Keys ---
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY not found in .env file. Please add it to run the agent.")

# --- Firestore Connection ---
SERVICE_ACCOUNT_FILE = "firestore-key.json"

@st.cache_resource
def get_db():
    """Initializes and returns the Firestore client."""
    try:
        if not firebase_admin._apps:
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                st.error(f"FATAL: '{SERVICE_ACCOUNT_FILE}' not found in project root.")
                st.error("Please download it from your Firebase project settings and place it in the root.")
                return None
                
            creds = credentials.Certificate(SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(creds)
        db = firestore.client()
        return db
    except Exception as e:
        st.error(f"Failed to connect to Firestore. Error: {e}")
        return None

db = get_db()

# === Agent Components (Tools & Logic) ===
# (Unchanged)
def run_generated_code(code_string: str) -> str:
    try:
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

def judge_code_function(state: GraphState) -> str:
    if state.get("last_error"):
        return "failure"
    else:
        return "success"

def plan_router_function(state: GraphState) -> str:
    plan = state.get("plan", "").strip().upper()
    if "CODE" in plan:
        return "CODE"
    else:
        return "TEXT"

def build_master_agent_graph() -> BaseNode:
    success_node = AddValueNode(key="final_status", value="SUCCESS", next_node=None)
    chatbot_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="You are a helpful assistant. Answer the user's task: {task}",
        output_key="final_response",
        next_node=success_node
    )
    critical_fail_node = AddValueNode(key="final_status", value="CRITICAL_FAILURE", next_node=None)
    tester_node = ToolNode(
        tool_function=run_generated_code,
        input_keys=["code_string"],
        output_key="test_result",
        next_node=None, error_node=None
    )
    clear_error_node = ClearErrorNode(next_node=tester_node)
    corrector_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        Your last attempt to write a Python function failed.
        CODE: {code_string}
        ERROR: {last_error}
        Please fix the code and ONLY output the complete, corrected Python function.
        """,
        output_key="code_string",
        next_node=clear_error_node
    )
    judge_node = RouterNode(
        decision_function=judge_code_function,
        path_map={ "success": success_node, "failure": corrector_node },
        default_node=critical_fail_node
    )
    tester_node.next_node = judge_node
    tester_node.error_node = judge_node
    writer_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        Write a Python function called `add_five(x)` that solves this task: {task}.
        This task requires code, so ONLY output the Python function.
        """,
        output_key="code_string",
        next_node=tester_node
    )
    master_router_node = RouterNode(
        decision_function=plan_router_function,
        path_map={ "CODE": writer_node, "TEXT": chatbot_node },
        default_node=chatbot_node
    )
    planner_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template="""
        You are a master agent. A user has given this task: "{task}"
        Analyze the task. Does it require writing Python code (like a math function) 
        or is it a simple question that needs a text answer (like 'hi' or 'what is AI?')?
        
        Respond with ONLY the word "CODE" or "TEXT".
        """,
        output_key="plan",
        next_node=master_router_node
    )
    return planner_node

# === UI Helper Functions ===

def apply_diff(state: dict, diff: dict) -> dict:
    """Applies a diff to a state dictionary to get the state_after."""
    new_state = state.copy()
    for key in diff.get("removed", {}):
        new_state.pop(key, None)
    for key, value in diff.get("added", {}).items():
        new_state[key] = value
    for key, values in diff.get("modified", {}).items():
        new_state[key] = values["new"]
    return new_state

def display_diff(diff_data: dict):
    """Renders the state diff in a clean, color-coded way."""
    if not any(diff_data.values()):
        st.info("No state changes in this step.")
        return
    diff_text = []
    for key, value in diff_data.get("added", {}).items():
        diff_text.append(f"+ ADDED: '{key}'")
        diff_text.extend([f"  {line}" for line in json.dumps(value, indent=2).splitlines()])
    for key, value in diff_data.get("removed", {}).items():
        diff_text.append(f"- REMOVED: '{key}'")
        diff_text.extend([f"  {line}" for line in json.dumps(value, indent=2).splitlines()])
    for key, values in diff_data.get("modified", {}).items():
        diff_text.append(f"~ MODIFIED: '{key}'")
        diff_text.append("  --- BEFORE ---")
        diff_text.extend([f"  - {line}" for line in json.dumps(values['old'], indent=2).splitlines()])
        diff_text.append("  --- AFTER ---")
        diff_text.extend([f"  + {line}" for line in json.dumps(values['new'], indent=2).splitlines()])
    st.code("\n".join(diff_text), language='diff')

def render_graph_history(history: list) -> str:
    """Takes the history log (with diffs) and builds a Graphviz DOT string."""
    dot = graphviz.Digraph(comment='Agent Execution Graph')
    dot.attr(bgcolor="transparent", rankdir="TB")
    dot.attr('node', shape='box', style='filled,rounded', 
             fontname='sans-serif', fontcolor='white', color='#4b5563')
    dot.attr('edge', fontname='sans-serif', fontcolor='white', color='white')
    dot.node("START", "START", shape="Mdiamond", fillcolor="#6366f1")
    if not history:
        dot.edge("START", "...")
        return dot

    last_step_id = "START"
    final_state = {}
    for i, step in enumerate(history):
        step_id = f"step_{i}"
        label = f"Step {i}: {step['node']}\n(Outcome: {step['outcome']})"
        color = '#22c55e' if step['outcome'] == 'success' else '#ef4444'
        dot.node(step_id, label, fillcolor=color)
        dot.edge(last_step_id, step_id)
        last_step_id = step_id
        
        # Reconstruct the final state as we go
        final_state = apply_diff(step["state_before"], step["state_diff"])
            
    is_finished = "final_status" in final_state or "final_response" in final_state
    if not is_finished:
        dot.node(last_step_id, label, fillcolor='#3b82f6')
    else:
        end_id = "END"
        dot.node(end_id, "END", shape="Mdiamond", fillcolor='#6b7280')
        dot.edge(last_step_id, end_id)
    return dot

@st.cache_data(ttl=60)
def get_past_runs(_db_client):
    """Fetches all past agent runs from Firestore."""
    if not _db_client:
        return {}
    try:
        runs_ref = _db_client.collection("agent_runs").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(20).stream()
        
        runs = {}
        for run in runs_ref:
            run_data = run.to_dict()
            timestamp = run_data.get("timestamp", datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")
            label = f"{timestamp} - {run_data.get('task_summary', run.id)}"
            runs[label] = run.id
        return runs
    except Exception as e:
        # This is where the index error happens
        st.sidebar.error(f"Error fetching past runs: {e}")
        st.sidebar.info("Trying a simpler, un-sorted query...")
        try:
            # --- FALLBACK QUERY ---
            # This query doesn't require a manual index.
            runs_ref = _db_client.collection("agent_runs").limit(20).stream()
            runs = {}
            for run in runs_ref:
                run_data = run.to_dict()
                timestamp = run_data.get("timestamp", datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")
                label = f"{timestamp} - {run_data.get('task_summary', run.id)}"
                runs[label] = run.id
            return runs
        except Exception as e2:
            st.sidebar.error(f"Fallback query failed: {e2}")
            return {}

# --- NEW: History Reconstruction (The core of v3.0) ---
def reconstruct_history(initial_state: dict, steps: list) -> list:
    """
    Takes the initial_state and a list of step_logs (diffs)
    and reconstructs the full history object for the UI.
    """
    history = []
    current_state = initial_state.copy()
    
    for step_log in steps:
        # The log from Firestore only has the diff.
        # We need to add the 'state_before' for the UI.
        full_step_log = step_log.copy()
        full_step_log["state_before"] = current_state
        
        # Calculate the next state
        current_state = apply_diff(current_state, step_log.get("state_diff", {}))
        
        history.append(full_step_log)
        
    return history

# === Streamlit App UI ===

st.set_page_config(layout="wide", page_title="Snath™ (powered by Lár)")

# Initialize session state
if "executor" not in st.session_state:
    st.session_state.executor = None
if "history" not in st.session_state:
    st.session_state.history = []
if "run_id" not in st.session_state:
    st.session_state.run_id = None
if "mode" not in st.session_state:
    st.session_state.mode = "idle"

with st.sidebar:
    st.markdown("<h1><span style='color: #60a5fa;'>Snath™</span>.ai</h1>", unsafe_allow_html=True)
    st.write("The visual platform for `lar` agents.")
    
    with st.expander("1. Run New Agent", expanded=True):
        task = st.text_area("Initial Task", 
                            "Write a Python function called `add_five(x)` that returns x + 5.",
                            height=100)

        if st.button("Start Agent", type="primary", use_container_width=True, disabled=(db is None)):
            with st.spinner("Building agent and saving to DB..."):
                start_node = build_master_agent_graph()
                initial_state_data = {"task": task}
                
                executor = GraphExecutor()
                st.session_state.executor = executor.run_step_by_step(start_node, initial_state_data)
                
                try:
                    # --- NEW: Create parent document ---
                    run_ref = db.collection("agent_runs").document()
                    st.session_state.run_id = run_ref.id
                    st.session_state.mode = "running"
                    
                    run_ref.set({
                        "task_summary": task[:50] + "...",
                        "timestamp": firestore.SERVER_TIMESTAMP,
                        "initial_state": initial_state_data,
                        "status": "running"
                        # The 'history' is now a sub-collection
                    })
                    
                    # Run the FIRST step (PlannerNode)
                    with st.spinner("Lár agent is planning... (Running Step 0: PlannerNode)"):
                        first_step_log = next(st.session_state.executor)
                    
                    # --- NEW: Save step in sub-collection ---
                    step_doc_id = f"step_{first_step_log['step']}"
                    step_data_to_save = {k: v for k, v in first_step_log.items() if k != 'state_before'}
                    run_ref.collection("steps").document(step_doc_id).set(step_data_to_save)

                    # We still build the local history for the UI
                    st.session_state.history = [first_step_log]
                    
                    st.success(f"Agent created! Run ID: {run_ref.id}.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Agent failed on first step: {e}")
                    st.session_state.executor = None

    st.subheader("2. Execution")
    is_running = st.session_state.mode == "running"
    
    if st.button("Next Step", use_container_width=True, disabled=not is_running):
        with st.spinner("Lár agent is thinking... (Running next step)"):
            try:
                step_log = next(st.session_state.executor)
                
                # --- NEW: Save step in sub-collection ---
                if db and st.session_state.run_id:
                    run_ref = db.collection("agent_runs").document(st.session_state.run_id)
                    step_doc_id = f"step_{step_log['step']}"
                    step_data_to_save = {k: v for k, v in step_log.items() if k != 'state_before'}
                    run_ref.collection("steps").document(step_doc_id).set(step_data_to_save)
                
                # We update the local history *after* saving, with the full data
                st.session_state.history.append(step_log)
                    
            except StopIteration:
                st.success("Agent has finished the run.")
                if db and st.session_state.run_id:
                    db.collection("agent_runs").document(st.session_state.run_id).update({"status": "completed"})
                st.session_state.mode = "readonly"
                st.session_state.executor = None
            except Exception as e:
                st.error(f"Agent failed with an unexpected error: {e}")
                if db and st.session_state.run_id:
                    db.collection("agent_runs").document(st.session_state.run_id).update({"status": "failed", "error": str(e)})
                st.session_state.executor = None
                st.session_state.mode = "readonly"
        st.rerun()

    if st.button("Reset", use_container_width=True):
        st.session_state.executor = None
        st.session_state.history = []
        st.session_state.run_id = None
        st.session_state.mode = "idle"
        st.rerun()

    st.subheader("3. Review Past Runs")
    if db:
        past_runs = get_past_runs(db)
        options = [""] + list(past_runs.keys())
        selected_run_label = st.selectbox("Load a past run:", options=options, index=0)

        if selected_run_label:
            selected_run_id = past_runs[selected_run_label]
            if st.session_state.run_id != selected_run_id:
                with st.spinner(f"Loading run {selected_run_id}..."):
                    
                    # --- NEW: Load from sub-collection ---
                    run_doc_ref = db.collection("agent_runs").document(selected_run_id)
                    run_doc = run_doc_ref.get()
                    
                    if run_doc.exists:
                        initial_state = run_doc.to_dict().get("initial_state", {})
                        
                        # Now, fetch all the steps
                        steps_ref = run_doc_ref.collection("steps").order_by("step").stream()
                        steps_logs = [step.to_dict() for step in steps_ref]
                        
                        # Reconstruct the full history object for the UI
                        st.session_state.history = reconstruct_history(initial_state, steps_logs)
                        
                        st.session_state.run_id = selected_run_id
                        st.session_state.executor = None
                        st.session_state.mode = "readonly"
                        st.rerun()
                    else:
                        st.error("Run not found.")
    else:
        st.warning("Firestore not connected. Past runs are unavailable.")

# --- Main Content Area (Graph & State) ---
col1, col2 = st.columns([3, 2])

with col1:
    st.header("Execution Graph")
    if st.session_state.run_id:
        st.caption(f"Current Run ID: `{st.session_state.run_id}` ({st.session_state.mode} mode)")
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
        last_step = st.session_state.history[-1]
        
        tab_changes, tab_full_state = inspector_container.tabs([
            "Changes in Last Step", 
            "Full State (After Step)"
        ])

        with tab_changes:
            st.subheader(f"Step {last_step['step']}: {last_step['node']}")
            # We just pass the diff directly!
            display_diff(last_step["state_diff"])

        with tab_full_state:
            st.subheader("Full State (After Step)")
            # We reconstruct the state after this step ran
            state_after = apply_diff(last_step["state_before"], last_step["state_diff"])
            st.json(state_after)
        
        with st.expander("Show Full Execution Log (Raw Diffs)"):
            # This is now the raw log from the DB (or in-memory)
            st.json(st.session_state.history)