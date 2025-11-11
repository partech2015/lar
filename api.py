import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import datetime
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

# --- Load API Keys (from .env) ---
# (FastAPI doesn't load .env automatically, but uvicorn can.
# For simplicity, we'll assume they are set in the environment)
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in .env file.")

# --- Firestore Connection ---
SERVICE_ACCOUNT_FILE = "firestore-key.json"
db_client = None
try:
    if not firebase_admin._apps:
        creds = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(creds)
    db_client = firestore.client()
    print("Successfully connected to Firestore.")
except Exception as e:
    print(f"FATAL: Failed to connect to Firestore: {e}")

# === Agent Components (Copied from snath_app.py) ===
# All your "lar" logic is re-used here

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

def judge_function(state: GraphState) -> str:
    if state.get("last_error"):
        return "failure"
    else:
        return "success"

def build_agent_graph(writer_prompt: str) -> BaseNode:
    success_node = AddValueNode(key="final_status", value="SUCCESS", next_node=None)
    critical_fail_node = AddValueNode(key="final_status", value="CRITICAL_FAILURE", next_node=None)
    tester_node = ToolNode(
        tool_function=run_generated_code,
        input_keys=["code_string"], output_key="test_result",
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
        decision_function=judge_function,
        path_map={ "success": success_node, "failure": corrector_node },
        default_node=critical_fail_node
    )
    tester_node.next_node = judge_node
    tester_node.error_node = judge_node
    writer_node = LLMNode(
        model_name="gemini-2.5-pro",
        prompt_template=writer_prompt,
        output_key="code_string",
        next_node=tester_node
    )
    return writer_node

# === The "Headless" Agent Executor ===
# This is what runs in the background

def run_agent_in_background(run_id: str, task: str, writer_prompt: str):
    """
    This is the function that does the actual work.
    It will run the agent and save every step to Firestore.
    """
    if not db_client:
        print(f"Error: Firestore not connected. Cannot run agent for {run_id}.")
        return

    run_ref = db_client.collection("agent_runs").document(run_id)
    
    try:
        # 1. Build the graph
        full_prompt = writer_prompt.format(task=task)
        start_node = build_agent_graph(full_prompt)
        executor = GraphExecutor()
        
        # 2. Run the generator step-by-step
        for step_log in executor.run_step_by_step(start_node, {"task": task}):
            print(f"  [Run {run_id}] Step {step_log['step']}: {step_log['node']}...")
            # Save each step to the database as it happens
            run_ref.update({"history": firestore.ArrayUnion([step_log])})
        
        print(f"[Run {run_id}] ...Finished.")
        run_ref.update({"status": "completed"})

    except Exception as e:
        print(f"[Run {run_id}] ...CRITICAL FAILURE: {e}")
        run_ref.update({"status": "failed", "error": str(e)})


# === The API Endpoints ===

# This creates our FastAPI app
app = FastAPI(title="Snath.ai API", version="1.0")

class AgentRunRequest(BaseModel):
    task: str
    writer_prompt: str

@app.post("/agents/run")
def start_agent_run(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """
    Starts a new agent run in the background.
    """
    if not db_client:
        raise HTTPException(status_code=500, detail="Firestore not connected")
    
    # 1. Create a new document in Firestore to get a Run ID
    run_ref = db_client.collection("agent_runs").document()
    run_id = run_ref.id
    
    run_ref.set({
        "task_summary": request.task[:50] + "...",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "running",
        "history": []
    })
    
    # 2. Add the *actual* agent run as a background task
    # This lets the API return a response *immediately*
    background_tasks.add_task(
        run_agent_in_background,
        run_id=run_id,
        task=request.task,
        writer_prompt=request.writer_prompt
    )
    
    # 3. Return the Run ID to the user instantly
    return {"message": "Agent run started", "run_id": run_id}

@app.get("/agents/run/{run_id}")
def get_agent_run(run_id: str):
    """
    Gets the status and history of a specific agent run.
    """
    if not db_client:
        raise HTTPException(status_code=500, detail="Firestore not connected")
        
    try:
        run_doc = db_client.collection("agent_runs").document(run_id).get()
        if not run_doc.exists:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return run_doc.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This is the command to run the server
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

