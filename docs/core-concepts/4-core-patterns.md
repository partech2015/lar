# The 18 Core Patterns

Lár is built on the philosophy of "Code as Graph". We have identified **18 robust engineering patterns** that cover 99% of agentic use cases.

From simple routing to complex self-correcting swarms, these patterns are your building blocks.

---

## 🟢 Standard Patterns (Foundational)

### 1. Simple Triage
**The "Hello World" of Agents.**
*   **Mechanism**: `LLMNode` (Classifier) -> `RouterNode` -> `ToolNode` (Handler).
*   **Use Case**: Customer support routing (Billing vs Tech), Email sorting.
*   **Why**: Deterministic routing is safer than letting an LLM decide "what to do" implicitly.

### 2. RAG Chain
**Retrieval Augmented Generation.**
*   **Mechanism**: `ToolNode` (Retriever) -> `LLMNode` (Answer Generator).
*   **Use Case**: answering questions based on internal docs.
*   **Key Feature**: The `ToolNode` output merges into `state`, providing context for the `LLMNode`.

---

## 🟡 Intermediate Patterns (Loops & Logic)

### 3. Cyclic Agent (The Loop)
**Basic feedback loop.**
*   **Mechanism**: `Think` -> `Act` -> `Observe` -> `Think`.
*   **Use Case**: Solving math problems, multi-step research.
*   **Why**: Allows the agent to react to new information (tool outputs) iteratively.

### 4. Human-in-the-Loop
**Pausing for approval.**
*   **Mechanism**: `LLMNode` (Propose Plan) -> `Wait` (Stop Execution) -> User Input -> `ToolNode` (Execute).
*   **Use Case**: Deploying code, spending money, sending sensitive emails.
*   **Details**: Lár's state persistence allows you to stop execution and resume days later.

### 5. Memory Agent
**Long-term contextual awareness.**
*   **Mechanism**: `HistoryFetcher` -> `LLMNode` -> `HistorySaver`.
*   **Use Case**: Personal assistants, learning user preferences over time.
*   **Why**: Separates "Context Window" (Ram) from "Database" (Hard Drive).

### 6. Self-Correction
**The "Unreliable Witness" fix.**
*   **Mechanism**: `Generator` -> `Validator` (Tool/LLM) -> `Error?` -> `Refiner`.
*   **Use Case**: Code generation (run -> syntax error -> fix), structured data extraction.
*   **Key Feature**: Uses `ClearErrorNode` to reset state after a fix before retrying.

### 7. Multi-Agent Orchestration
**The Manager-Worker topology.**
*   **Mechanism**: `Manager` (Router) -> `Worker A` / `Worker B` -> `Manager`.
*   **Use Case**: Complex projects (e.g., writing a software feature: Product Manager -> Dev -> QA).
*   **Why**: Specialization. A "Coder" prompt performs better than a "Generalist" prompt.

### 8. Streaming
**Real-time UX.**
*   **Mechanism**: Utilizing `executor.run_step_by_step()` or `node.stream()` (if supported).
*   **Use Case**: Chat interfaces where latency matters.

### 9. JSON Mode
**Strict Object Generation.**
*   **Mechanism**: `LLMNode` with `pydantic_schema` or strict instruction -> `JSONParser`.
*   **Use Case**: Extracting data for APIs.
*   **Why**: Guarantees the output is machine-readable, preventing downstream crashes.

### 10. Sub-Graphs
**Fractal Architecture.**
*   **Mechanism**: A `ToolNode` that calls *another* `GraphExecutor`.
*   **Use Case**: Isolating complexity. A "Research Agent" can be a single node in a "Writer Agent" graph.

---

## 🔴 Advanced Patterns (Architecture)

### 11. Dynamic Routing
**Runtime decision making.**
*   **Mechanism**: LLM decides the *next step* during execution, rather than a hardcoded Router.
*   **Use Case**: Open-ended exploration/research.

### 12. Parallel Execution (Fan-Out / Fan-In)
**Speed & Concurrency.**
*   **Mechanism**: `BatchNode([Node A, Node B])` -> `AggregatorNode`.
*   **Use Case**: Searching 5 websites at once, generating 3 draft options.
*   **Why**: Linear execution is slow. Agents should multitask.

### 13. Map-Reduce
**Summarizing massive data.**
*   **Mechanism**: Split data -> Parallel Process (`BatchNode`) -> Merge Results (`LLMNode`).
*   **Use Case**: Summarizing a whole book, analyzing log files.

### 14. Branching
**Complex Decision Trees.**
*   **Mechanism**: `RouterNode` leading to distinct sub-graphs that never merge.
*   **Use Case**: A "Signup Flow" vs "Login Flow" processing pipeline.

### 15. Wait-for-User (Interrupts)
**Asynchronous Human Input.**
*   **Mechanism**: Similar to Human-in-the-Loop, but designed for non-blocking flows (webhooks).
*   **Use Case**: "Email me when done, I'll click a link to continue."

### 16. Integration Builder (Just-in-Time)
**AI-Generated Tools.**
*   **Mechanism**: User -> `@lar/IDE_INTEGRATION_PROMPT.md` -> New `ToolNode`.
*   **Use Case**: Wrapping a niche API (e.g., custom CRM) in seconds.
*   **Why**: "Glass Box" philosophy—you own the integration code.

---

## 🟣 Experimental / Agentic Ops

### 17. The A/B Tester
**Iterative Improvement.**
*   **Mechanism**: `BatchNode` (Model A, Model B) -> `JudgeNode` (Evaluator).
*   **Use Case**: Testing a new prompt against an old one.
*   **Why**: Agents should evaluate themselves.

### 18. The Time Traveller
**State Serialization.**
*   **Mechanism**: Save `state.json` -> Stop Process -> Load `state.json` -> Resume.
*   **Use Case**: Serverless deployments (stopping to save cost), Crash recovery.
*   **Why**: Since State is just JSON, Lár agents are trivially resumable.
