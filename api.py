import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
import os
import datetime
from typing import Dict, Any, List
import time

# --- Firestore Imports ---
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
from lar.utils import compute_state_diff

# --- Load API Keys (from .env) ---
from dotenv import load_dotenv
load_dotenv()
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
    db_client = None

# === Agent "Tool" & "Logic" Registries ===

def run_generated_code(code_string: str) -> str:
    try:
        if code_string.startswith("```python"):
            code_string = code_string.strip().split("\n", 1)[1]
            if code_string.endswith("```"):
                code_string = code_string.rsplit("\n", 1)[0]
        local_scope = {}
        exec(code_string, {}, local_scope)
        if 'add_five' not in local_scope: raise NameError("func 'add_five' not defined")
        func = local_scope['add_five']
        result = func(10)
        if result != 15: raise ValueError(f"Logic error: Expected 15, got {result}")
        return "Success!"
    except Exception as e:
        raise e

def judge_code_function(state: GraphState) -> str:
    return "failure" if state.get("last_error") else "success"

def plan_router_function(state: GraphState) -> str:
    plan = state.get("plan", "").strip().upper()
    return "CODE" if "CODE" in plan else "TEXT"

TOOL_REGISTRY = { "run_generated_code": run_generated_code }
LOGIC_REGISTRY = {
    "judge_code_function": judge_code_function,
    "plan_router_function": plan_router_function,
}

# === THIS IS THE FIX (v2.1) ===
def build_graph_from_json(graph_definition: dict) -> BaseNode:
    """
    Parses a JSON-defined graph and constructs the Lár node objects.
    """
    nodes = {}
    
    # We get the 'nodes' dictionary *from* the graph definition
    nodes_config = graph_definition.get("nodes", {})
    
    # First pass: create all the node objects
    for node_id, config in nodes_config.items(): # <-- FIX: Iterate over nodes_config
        node_type = config["type"]
        
        if node_type == "LLMNode":
            nodes[node_id] = LLMNode(
                model_name=config["model_name"],
                prompt_template=config["prompt_template"],
                output_key=config["output_key"],
                next_node=None
            )
        elif node_type == "ToolNode":
            tool_func = TOOL_REGISTRY.get(config["tool_function_name"])
            if not tool_func: raise ValueError(f"Tool '{config['tool_function_name']}' not found.")
            
            nodes[node_id] = ToolNode(
                tool_function=tool_func,
                input_keys=config["input_keys"],
                output_key=config["output_key"],
                next_node=None,
                error_node=None
            )
        elif node_type == "RouterNode":
            logic_func = LOGIC_REGISTRY.get(config["decision_function_name"])
            if not logic_func: raise ValueError(f"Logic func '{config['decision_function_name']}' not found.")
            
            nodes[node_id] = RouterNode(
                decision_function=logic_func,
                path_map={},
                default_node=None
            )
        elif node_type == "ClearErrorNode":
            nodes[node_id] = ClearErrorNode(next_node=None)
        elif node_type == "AddValueNode":
            nodes[node_id] = AddValueNode(
                key=config["key"],
                value=config["value"],
                next_node=None
            )
    
    # Second pass: link all the nodes together
    for node_id, config in nodes_config.items(): # <-- FIX: Iterate over nodes_config
        current_node = nodes.get(node_id)
        if not current_node: continue
            
        # We need to check the type of `current_node` before accessing `type`
        current_node_type = config.get("type")

        if config.get("next_node"):
            current_node.next_node = nodes.get(config["next_node"])
            
        if current_node_type == "ToolNode" and config.get("error_node"):
            current_node.error_node = nodes.get(config["error_node"])
            
        if current_node_type == "RouterNode":
            if config.get("default_node"):
                current_node.default_node = nodes.get(config["default_node"])
            for key, target_node_id in config.get("path_map", {}).items():
                current_node.path_map[key] = nodes.get(target_node_id)

    # The graph must have an "entry_point" defined
    entry_point_id = graph_definition.get("entry_point")
    if not entry_point_id:
        raise ValueError("Graph definition is missing 'entry_point'.")
    
    start_node = nodes.get(entry_point_id)
    if not start_node:
        raise ValueError(f"Entry point '{entry_point_id}' not found in nodes.")

    return start_node
# === END FIX ===

# === Headless Executor (Unchanged) ===
def run_agent_in_background(run_id: str, agent_id: str, initial_state: dict):
    if not db_client:
        print(f"Error: Firestore not connected. Cannot run agent for {run_id}.")
        return

    run_ref = db_client.collection("agent_runs").document(run_id)
    
    try:
        agent_doc = db_client.collection("agents").document(agent_id).get()
        if not agent_doc.exists:
            raise ValueError(f"Agent blueprint '{agent_id}' not found.")
        
        graph_definition = agent_doc.to_dict().get("graph")
        
        start_node = build_graph_from_json(graph_definition)
        executor = GraphExecutor()
        
        for step_log in executor.run_step_by_step(start_node, initial_state):
            print(f"  [Run {run_id}] Step {step_log['step']}: {step_log['node']}...")
            step_doc_id = f"step_{step_log['step']}"
            step_data_to_save = {k: v for k, v in step_log.items() if k != 'state_before'}
            run_ref.collection("steps").document(step_doc_id).set(step_data_to_save)
        
        print(f"[Run {run_id}] ...Finished.")
        run_ref.update({"status": "completed"})

    except Exception as e:
        print(f"[Run {run_id}] ...CRITICAL FAILURE: {e}")
        run_ref.update({"status": "failed", "final_error": str(e)})

# === API Endpoints (Unchanged) ===
app = FastAPI(title="Snath.ai API (v2.1)", version="2.1")

class CreateAgentRequest(BaseModel):
    agent_name: str
    graph: Dict[str, Any]
    
class AgentRunRequest(BaseModel):
    user_id: str = Field(..., example="user_aadithya")
    initial_data: Dict[str, Any] = Field(..., example={"task": "Fix this code..."})

@app.post("/agents")
def create_agent(request: CreateAgentRequest):
    if not db_client:
        raise HTTPException(status_code=500, detail="Firestore not connected")
    try:
        agent_ref = db_client.collection("agents").document(request.agent_name)
        agent_ref.set({
            "agent_name": request.agent_name,
            "graph": request.graph,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return {"message": "Agent blueprint saved", "agent_id": agent_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/run")
def start_agent_run(agent_id: str, request: AgentRunRequest, background_tasks: BackgroundTasks):
    if not db_client:
        raise HTTPException(status_code=500, detail="Firestore not connected")
    
    run_ref = db_client.collection("agent_runs").document()
    run_id = run_ref.id
    
    initial_state = request.initial_data
    initial_state["run_id"] = run_id
    initial_state["user_id"] = request.user_id
    
    run_ref.set({
        "task_summary": initial_state.get("task", "No task")[:50] + "...",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "pending",
        "agent_id": agent_id,
        "user_id": request.user_id,
        "initial_state": initial_state
    })
    
    background_tasks.add_task(
        run_agent_in_background,
        run_id=run_id,
        agent_id=agent_id,
        initial_state=initial_state
    )
    
    return {"message": "Agent run queued", "run_id": run_id}

@app.get("/agents/run/{run_id}")
def get_agent_run(run_id: str):
    if not db_client:
        raise HTTPException(status_code=500, detail="Firestore not connected")
    try:
        run_doc_ref = db_client.collection("agent_runs").document(run_id)
        run_doc = run_doc_ref.get()
        if not run_doc.exists:
            raise HTTPException(status_code=404, detail="Run not found")
        
        run_data = run_doc.to_dict()
        
        steps_ref = run_doc_ref.collection("steps").order_by("step").stream()
        run_data["steps"] = [step.to_dict() for step in steps_ref]
        
        return run_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)