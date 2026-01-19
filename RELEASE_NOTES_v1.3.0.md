# Lár v1.3.0 Release Notes

**Production Architecture Quality Update**

This release focuses on architectural excellence, refactoring core components for better separation of concerns, adding comprehensive validation, and completing API documentation.

## New Features

### 1. **Modular Architecture** - Separation of Concerns

The `GraphExecutor` has been refactored to delegate responsibilities to specialized classes:

#### **New: `AuditLogger` Class**
Handles all logging and file persistence logic.

```python
from lar import AuditLogger

# Use custom logger
logger = AuditLogger(log_dir="custom_logs")
executor = GraphExecutor(logger=logger)
```

**Benefits**:
- Swap logging backends (JSON, database, remote logging)
- Test logging independently
- Customize audit trail format

####**New: `TokenTracker` Class**
Tracks token usage across models with granular statistics.

```python
from lar import TokenTracker

# Use custom tracker
tracker = TokenTracker()
executor = GraphExecutor(tracker=tracker)

# Access token summary
summary = tracker.get_summary()
print(summary["tokens_by_model"])
```

**Benefits**:
- Independent cost tracking
- Per-model token breakdown
- Reusable across multiple graph runs

### 2. **Construction-Time Validation**

All nodes now validate their configuration at construction time, catching errors early with helpful messages.

**Before v1.3.0** (Runtime Error):
```python
router = RouterNode(
    decision_function="not a function",  # Wrong type
    path_map={}
)
# Cryptic error during execution: 'str' object is not callable
```

**After v1.3.0** (Construction Error):
```python
router = RouterNode(
    decision_function="not a function",
    path_map={}
)
# ValueError: decision_function must be callable
```

**Validation Coverage**:
- ✅ `AddValueNode`: Validates `key` is non-empty string
- ✅ `LLMNode`: Validates model_name, prompt_template, max_retries
- ✅ `RouterNode`: Validates `decision_function` is callable, `path_map` has BaseNode values
- ✅ `ToolNode`: Validates `tool_function` is callable, `input_keys` are strings
- ✅ `BatchNode`: Validates `nodes` list contains only BaseNode instances
- ✅ `HumanJuryNode`: Validates `choices` list is non-empty
- ✅ All nodes: Validate `next_node` is BaseNode or None

### 3. **Complete API Documentation**

Added comprehensive developer documentation:

- **[`BatchNode` API Reference](docs/api-reference/batchnode.md)** - Parallel execution patterns, performance tips, examples
- **[`DynamicNode` API Reference](docs/api-reference/dynamicnode.md)** - Metacognition capabilities, safety concerns, compliance
- **[`TopologyValidator` API Reference](docs/api-reference/topologyvalidator.md)** - Security guarantees, cycle detection, tool allowlisting

Each doc includes:
- Full parameter descriptions
- Behavior explanations
- Working code examples
- Best practices & anti-patterns
- Performance considerations

### 4. **Enhanced Module Exports**

New classes are now part of the public API:

```python
from lar import AuditLogger, TokenTracker

__all__ = [
    # ... existing exports
    "AuditLogger",  # NEW in v1.3.0
    "TokenTracker",  # NEW in v1.3.0
]
```

## Changes

### Backward Compatibility

**100% Backward Compatible** - No breaking changes.

Existing code works unchanged:
```python
# This still works exactly as before
executor = GraphExecutor()
result = list(executor.run_step_by_step(start_node, initial_state))
```

### Internal Refactoring

| Component | Change | Impact |
|-----------|--------|--------|
| `executor.py` | Extracted logger logic to `logger.py` | Cleaner, testable code |
| `executor.py` | Extracted token tracking to `tracker.py` | Independent cost analysis |
| `node.py` | Added `_validate_next_node()` helper | Early error detection |
| `__init__.py` | Updated exports and version | New public APIs |

## Upgrading

```bash
# Update via Poetry
poetry update lar-engine

# Or via pip
pip install --upgrade lar-engine==1.3.0
```

**No code changes required** - Your existing graphs will work immediately.

## New Capabilities Unlocked

### 1. **Custom Logging Backends**

```python
class DatabaseLogger(AuditLogger):
    def save_to_file(self, run_id, user_id, summary):
        # Save to PostgreSQL instead of JSON
        db.execute("INSERT INTO audit_logs ...")

executor = GraphExecutor(logger=DatabaseLogger())
```

### 2. **Cost Estimation**

```python
tracker = TokenTracker()
executor = GraphExecutor(tracker=tracker)

# Run graph
list(executor.run_step_by_step(start_node, state))

# Calculate cost
summary = tracker.get_summary()
gpt4_tokens = summary["tokens_by_model"].get("gpt-4", 0)
cost = gpt4_tokens * 0.00003  # $0.03 per 1K tokens
print(f"Estimated cost: ${cost:.4f}")
```

### 3. **Early Error Detection**

```python
# This now fails immediately with clear error
try:
    node = LLMNode(
        model_name="",  # Empty string
        prompt_template="test",
        output_key="result"
    )
except ValueError as e:
    print(e)  # "model_name must be a non-empty string"
```

## Bug Fixes

- Fixed: Duplicate `GraphExecutor` entry in `__all__` exports
- Fixed: TODO comment in `IDE_INTEGRATION_PROMPT.md` (line 34)
- Fixed: Missing `ClearErrorNode` in `__all__` exports

## Documentation Improvements

- Added complete API documentation for `BatchNode`
- Added complete API documentation for `DynamicNode`
- Added complete API documentation for `TopologyValidator`
- Updated IDE integration template with installation instructions

## For Contributors

### New Test Files Needed

If you're contributing tests, focus on:
- `tests/test_logger.py` - AuditLogger behavior
- `tests/test_tracker.py` - TokenTracker accuracy
- `tests/test_validation.py` - Node construction validation

### Architecture Philosophy

The v1.3.0 refactoring follows these principles:
1. **Single Responsibility** - Each class has one job
2. **Dependency Injection** - Components are injectable for testing
3. **Early Validation** - Fail fast with clear errors
4. **Backward Compatibility** - Never break existing code

## Next Steps

Planned for v1.4.0:
- Streaming LLM support (`LLMNode.execute_stream()`)
- Async execution (`async def execute_async()`)
- Graph visualization utilities (`GraphVisualizer.to_mermaid()`)

## Changelog

- **[NEW]** `AuditLogger` class for logging abstraction (executor.py → logger.py)
- **[NEW]** `TokenTracker` class for token aggregation (executor.py → tracker.py)
- **[NEW]** Construction validation for all node types (node.py)
- **[NEW]** API documentation for BatchNode, DynamicNode, TopologyValidator
- **[FIXED]** TODO in IDE_INTEGRATION_PROMPT.md
- **[IMPROVED]** Module exports (__init__.py)
- **[IMPROVED]** Error messages for invalid node configurations
- **[UPDATED]** Version to 1.3.0 (pyproject.toml, __init__.py)

---

**Full Diff**: https://github.com/snath-ai/lar/compare/v1.2.0...v1.3.0

**Questions?** Open an issue on [GitHub](https://github.com/snath-ai/lar/issues)
