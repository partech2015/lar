# The 22 Core Patterns

Lár is built on the philosophy of "Code as Graph". We have created **21 robust engineering patterns** that strictly correspond to the examples in the repository.

Each pattern below includes a link to the source code.

---

## Standard Patterns

### 1. Simple Triage
**The "Hello World" of Agents.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/1_simple_triage.py)
*   **Mechanism**: `LLMNode` (Classifier) -> `RouterNode` -> `ToolNode` (Handler).
*   **Use Case**: Customer support routing (Billing vs Tech), Email sorting.
*   **Why**: Deterministic routing is safer than letting an LLM decide "what to do" implicitly.

### 2. RAG Researcher
**Retrieval Augmented Generation with State.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/2_rag_researcher.py)
*   **Mechanism**: `ToolNode` (Retriever) -> `LLMNode` (Answer Generator).
*   **Key Feature**: The `ToolNode` output merges into `state`, providing context for the `LLMNode`.

### 3. Self-Correction
**The "Unreliable Witness" fix.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/3_self_correction.py)
*   **Mechanism**: `Generator` -> `Validator` -> `Error?` -> `Refiner`.
*   **Use Case**: Code generation (run -> syntax error -> fix).
*   **Key Feature**: Uses `ClearErrorNode` to reset state after a fix before retrying.

### 4. Human-in-the-Loop
**Pausing for approval.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/4_human_in_the_loop.py)
*   **Mechanism**: `LLMNode` (Propose Plan) -> `Wait` (Stop Execution) -> User Input -> `ToolNode` (Execute).
*   **Use Case**: Deploying code, spending money, sending sensitive emails.

### 5. Parallel Execution (Basic)
**Fan-Out Aggregation.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/5_parallel_execution.py)
*   **Mechanism**: Running multiple logical branches that merge back.
*   **Note**: This is simulated parallelism. For true threading, see Pattern 14.

### 6. Structured Output
**Strict JSON Enforcement.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/6_structured_output.py)
*   **Mechanism**: `LLMNode` -> `JSONParser` -> `API`.
*   **Use Case**: Extracting data for APIs.
*   **Why**: Guarantees the output is machine-readable, preventing downstream crashes.

---

## Intermediate Patterns

### 7. Multi-Agent Handoff
**The Manager-Worker topology.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/7_multi_agent_handoff.py)
*   **Mechanism**: `Manager` (Router) -> `Worker A` / `Worker B` -> `Manager`.
*   **Use Case**: Complex projects (e.g., Writer <-> Editor).
*   **Why**: Specialization. A "Coder" prompt performs better than a "Generalist" prompt.

### 8. Meta-Prompt Optimizer
**Self-Modifying Agents.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/8_meta_prompt_optimizer.py)
*   **Mechanism**: An agent that rewrites its own system prompt based on results.
*   **Use Case**: Optimizing instructions for specific tasks.

### 9. Corporate Swarm
**Stress Testing.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/9_corporate_swarm.py)
*   **Mechanism**: Programmatically generating a graph with 60+ nodes.
*   **Why**: Proves Lár's graph engine scales `O(1)` with complexity, unlike chain-based frameworks.

### 10. Security Firewall
**Architecture-Level Safety.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/10_security_firewall.py)
*   **Mechanism**: `Input` -> `Guardrail Node` -> `Router` (Block/Allow) -> `Agent`.
*   **Why**: Blocks jailbreaks *before* they reach the expensive model.

### 11. Reward Code Agent
**Forward-Defined Logic.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/11_reward_code_agent.py)
*   **Mechanism**: Code-first logic design.

### 12. Support Helper
**Lightweight Assistant.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/12_support_helper_agent.py)
*   **Mechanism**: Specific tool usage for customer support data.

### 13. Mini Swarm Pruner
**Dynamic Graph management.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/13_mini_swarm_pruner.py)
*   **Mechanism**: Dynamically removing nodes from execution.

---

## Advanced & Ops Patterns

### 14. Parallel Newsroom
**True Threaded Parallelism.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/14_parallel_newsroom.py)
*   **Mechanism**: `BatchNode([Worker A, Worker B])`.
*   **Use Case**: Fetching 5 URLs at once using `ThreadPoolExecutor`.

### 15. Parallel Corporate Swarm
**Concurrent Branch Execution.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/15_parallel_corporate_swarm.py)
*   **Mechanism**: Scaling the Swarm (Pattern 9) with `BatchNode` for 50x speedup.

### 16. Integration Builder
**Just-in-Time Tools.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/16_integration_test.py)
*   **Mechanism**: User -> `@lar/IDE_INTEGRATION_PROMPT.md` -> New `ToolNode`.
*   **Use Case**: Wrappers for CoinCap, Stripe, Linear.

### 17. The A/B Tester
**Agentic Evaluation.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/17_ab_tester.py)
*   **Mechanism**: `BatchNode` (Model A, Model B) -> `JudgeNode` (Evaluator).
*   **Use Case**: Testing a new prompt against an old one.

### 18. The Time Traveller
**State Serialization.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/18_resumable_graph.py)
*   **Mechanism**: Save `state.json` -> Stop Process -> Load `state.json` -> Resume.
*   **Use Case**: Serverless deployments (stopping to save cost), Crash recovery.

### 19. FastAPI Server
**Deploy Anywhere.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/19_fastapi_server.py)
*   **Mechanism**: Wrapping `GraphExecutor` in a FastAPI route.
*   **Use Case**: Exposing your agent as a REST API for production deployment.

### 20. Juried Layer
**Architecture-Level Safety.**
[See Example](https://github.com/snath-ai/lar/blob/main/examples/20_juried_layer.py)
*   **Mechanism**: `Proposer (LLM)` -> `Jury (Code/Policy)` -> `Kernel (Execution)`.
*   **Why**: Separates the "Reasoning" (untrustworthy) from the "Authorization" (deterministic).

### 21. Access Control Agent
Combines Reasoning, Determinstic Policy, and Human-in-the-Loop.
**File**: [`21_access_control_agent.py`](../../examples/21_access_control_agent.py)
*   **Mechanism**: `Juried Layer` + `Human-in-the-Loop Interrupt` + `Strict JSON`.
*   **Use Case**: Enterprise Infrastructure Access Bot (e.g. "Grant admin access to DB").

### 22. Adversarial Stress Test (Red Teaming)
Demonstrates "Context Contamination". An attacker (LLM) tries to trick a Jury.
*   **Weak Jury (LLM)**: Falls for the lie.
*   **Strong Jury (Lár)**: Checks the state invaraint.
**File**: [`22_context_contamination_test.py`](../../examples/22_context_contamination_test.py)
