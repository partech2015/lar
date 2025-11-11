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