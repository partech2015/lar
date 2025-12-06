import json
from .node import BaseNode, LLMNode, ToolNode, RouterNode, AddValueNode, ClearErrorNode

def serialize_node(node: BaseNode, visited: set, nodes_dict: dict):
    if not node or node in visited:
        return
    
    visited.add(node)
    node_id = f"node_{id(node)}"
    
    # Base structure
    node_data = {
        "type": node.__class__.__name__,
        "id": node_id
    }
    
    # Inspect attributes based on type
    if isinstance(node, LLMNode):
        node_data["model_name"] = node.model_name
        node_data["prompt_template"] = node.prompt_template
        node_data["output_key"] = node.output_key
        if node.next_node:
            node_data["next_node"] = f"node_{id(node.next_node)}"
            serialize_node(node.next_node, visited, nodes_dict)
            
    elif isinstance(node, ToolNode):
        node_data["function_name"] = node.tool_function.__name__
        node_data["input_keys"] = node.input_keys
        node_data["output_key"] = node.output_key
        if node.next_node:
            node_data["next_node"] = f"node_{id(node.next_node)}"
            serialize_node(node.next_node, visited, nodes_dict)
        if node.error_node:
            node_data["error_node"] = f"node_{id(node.error_node)}"
            serialize_node(node.error_node, visited, nodes_dict)

    elif isinstance(node, RouterNode):
        node_data["function_name"] = node.decision_function.__name__
        # Route map
        routes = {}
        for key, target in node.path_map.items():
             routes[key] = f"node_{id(target)}"
             serialize_node(target, visited, nodes_dict)
        node_data["routes"] = routes
        
        if node.default_node:
             node_data["default_node"] = f"node_{id(node.default_node)}"
             serialize_node(node.default_node, visited, nodes_dict)
             
    elif isinstance(node, AddValueNode):
        node_data["key"] = node.key
        node_data["value"] = node.value
        if node.next_node:
            node_data["next_node"] = f"node_{id(node.next_node)}"
            serialize_node(node.next_node, visited, nodes_dict)

    elif isinstance(node, ClearErrorNode):
        if node.next_node:
            node_data["next_node"] = f"node_{id(node.next_node)}"
            serialize_node(node.next_node, visited, nodes_dict)

    nodes_dict[node_id] = node_data

def save_agent_to_file(start_node: BaseNode, filename: str, name: str = "Untitled Agent"):
    visited = set()
    nodes_dict = {}
    
    serialize_node(start_node, visited, nodes_dict)
    
    # Find entry point ID
    entry_point = f"node_{id(start_node)}"
    
    manifest = {
        "metadata": {
             "name": name,
             "version": "1.0.0",
             "description": "Exported from Lar Python SDK"
        },
        "graph": {
            "entry_point": entry_point,
            "nodes": nodes_dict
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Agent saved to {filename}")
