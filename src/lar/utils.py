import json

def compute_state_diff(before: dict, after: dict) -> dict:
    """
    Calculates the diff between two state dictionaries.
    Returns a dictionary with "added", "removed", and "modified" keys.
    """
    diff = {"added": {}, "removed": {}, "modified": {}}
    all_keys = set(before.keys()) | set(after.keys())
    
    for key in all_keys:
        if key not in before:
            diff["added"][key] = after[key]
        elif key not in after:
            diff["removed"][key] = before[key]
        elif before[key] != after[key]:
            # Use JSON dumps for a more robust comparison of complex types
            before_json = json.dumps(before[key], sort_keys=True)
            after_json = json.dumps(after[key], sort_keys=True)
            
            if before_json != after_json:
                diff["modified"][key] = {"old": before[key], "new": after[key]}
            
    return diff

# Diff Function
def apply_diff(state: dict, diff: dict) -> dict:
    """
    Applies a 'state_diff' object to a state dictionary
    to reconstruct the 'state_after'.
    """
    # Start with a copy of the old state
    new_state = state.copy()
    
    # Apply all changes from the diff
    for key in diff.get("removed", {}):
        new_state.pop(key, None)
    for key, value in diff.get("added", {}).items():
        new_state[key] = value
    for key, values in diff.get("modified", {}).items():
        new_state[key] = values["new"] # Set to the 'new' value
        
    return new_state
