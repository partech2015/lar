# Air-Gap Security Mode

Lár is designed for environments where data exfiltration is not just a risk—it's illegal.
For high-security deployments (SCIFs, Clinical Trials, Financial Data), Lár provides a software-enforced **Air-Gap Mode**.

!!! warning "Enterprise Feature"
    The Open Source engine provides software-level hooks. For **Kernel-Level Enforcement** (blocking network drivers, syscall auditing) and **Offline Key Generation**, you need **[Snath Enterprise](https://snath.ai/enterprise)**.

## Enabling Offline Mode

To prevent accidental calls to cloud providers (OpenAI, Anthropic, Google Vertx), initialize the executor with `offline_mode=True`:

```python
from lar import GraphExecutor

# SECURE MODE: ON
executor = GraphExecutor(offline_mode=True)
```

## How it Works

When `offline_mode` is enabled, the `GraphExecutor` installs an application-level firewall before every node execution.

1.  **Inspection**: Before running an `LLMNode`, the engine inspects the `model_name`.
2.  **Allowlist**: Only models starting with the following prefixes are allowed:
    *   `ollama/` (Local Ollama instance)
    *   `local/` (Custom local models)
    *   `test/` (Test mocks)
    *   `mock/` (Test mocks)
3.  **Blocking**: Any attempt to use a cloud model (e.g., `gemini/`, `gpt-4`) will immediately raise a `SecurityError` and halt the agent.

## Example: Blocking Cloud Access

```python
from lar import GraphExecutor, LLMNode, GraphState

# This agent tries to use Gemini
agent = LLMNode(model_name="gemini/gemini-1.5-pro", ...)

executor = GraphExecutor(offline_mode=True)

try:
    executor.run(agent, input_data)
except Exception as e:
    print(e)
    # Output: 
    # AIR-GAP VIOLATION: Attempted to call cloud model 'gemini/gemini-1.5-pro' in offline mode.
```

## Snath Cloud (Enterprise)

If you are using the Snath Cloud platform (self-hosted), you can enforce this globally for all workers by setting the environment variable:

```bash
SNATH_OFFLINE_MODE=true
```

This will force all Agents to run in Air-Gap mode, regardless of their individual configuration, and display a **"SECURE MODE"** badge in the Admin Dashboard.
