# Lár v1.3.0 Release Notes

**"The Compliance & Architecture Update"**

This release focuses on hardening the framework for enterprise and regulatory compliance (EU AI Act), while refactoring the core execution engine for better separation of concerns.

## Key Features

### 1. "Human-in-the-Loop" Primitive (`HumanJuryNode`)
A new node type that pauses execution to request explicit human feedback via the CLI.
- **Why**: Directly satisfies EU AI Act Article 14 ("Human Oversight") requirements.
- **How**:
  ```python
  jury = HumanJuryNode(
      prompt="Approve sensitive action?",
      choices=["approve", "reject"],
      output_key="approval_status"
  )
  ```

### 2. Static Safety Analysis (`TopologyValidator`)
We've added a `TopologyValidator` (backed by NetworkX) that runs comprehensive checks on **Dynamic Graphs** *before* they execute.
- **Cycle Detection**: Catches infinite loops in generated subgraphs.
- **Structural Integrity**: Validates `next_node` references.
- **Tool Allowlisting**: Enforces strict boundaries on what tools a dynamic agent can access.

### 3. Core Refactor: Modular Observability
The `GraphExecutor` has been refactored to delegate responsibilities to dedicated components, keeping the engine lightweight.
- **`AuditLogger`**: Centralizes audit trail logging and file persistence.
- **`TokenTracker`**: Aggregates token usage across multiple providers and models with precision.

## Usage Updates

### Breaking Changes
- `GraphExecutor` constructor now accepts optional `logger` and `tracker` instances for dependency injection.
- **Compliance**: The "Glass Box" is now even more transparent with improved metadata fidelity in logs.

## Chains to State Machines
With `v1.3`, the debate is settled. Lár's state machine architecture now offers native compliance features (Breakpoints, Static Analysis) that Chain-based frameworks struggle to implement.

## Changelog
- **[NEW]** `HumanJuryNode` in `src/lar/node.py`
- **[NEW]** `TopologyValidator` in `src/lar/dynamic.py`
- **[NEW]** `AuditLogger` in `src/lar/logger.py`
- **[NEW]** `TokenTracker` in `src/lar/tracker.py`
- **[REFACTOR]** `GraphExecutor` to use new helper classes.
