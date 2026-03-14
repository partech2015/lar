# Fractal Agency (v1.5+)

While most agent frameworks operate in simple loops or static "chat rooms", Lár enables **Fractal Agency**: the ability for a graph execution to recursively spawn identical sub-graphs or entirely new graph topologies dynamically at runtime.

This allows you to scale complexity without scaling context windows.

## The Core Concept

Using a combination of the `DynamicNode` and `BatchNode` introduced in v1.5+, an agent can:

1. Analyze a highly complex problem.
2. Realize it is too complex for a single prompt or single linear reasoning path.
3. Automatically define a new, specialized graph (e.g., branching out to 5 parallel researchers).
4. Spawn that graph as an isolated sub-process.
5. Wait for the sub-graph to finish, collect its unified response, and resume the original top-level graph.

### Why this matters:

*   **Perfect Isolation**: The "Sub-Agent Graph" has its own `GraphState`. Its messy scratchpad reasoning, iterative tool calls, and bloated retrieval texts **never** pollute the Master Agent's state. It only returns the precise, distilled answer.
*   **Infinite Depth**: Because contexts are isolated, sub-agents can spawn sub-agents, creating recursive "deep research" trees that never trigger a Token Limit Crash.
*   **Deterministic Architecture**: Even though the graph is expanding infinitely over runtime, the architecture is still strictly node-to-node. Lár forces the LLM to output these topologies inside strict typed definitions.

## The `fractal_polymath.py` Architecture

The flagship example of this capability is the Fractal Polymath.
You can view the full source code in `examples/advanced/fractal_polymath.py`.

In this pattern, we want an AI to research a highly complex, multi-disciplinary question (e.g., "What are the socio-economic impacts of asteroid mining?").

1.  **The Master Orchestrator** defines the problem.
2.  It uses a `DynamicNode` to recursively spawn $N$ specialized `BatchNode` sub-graphs (e.g., an Economist, an Astrophysicist, a Lawyer).
3.  These agents run totally parallel in their own sandboxes.
4.  Once all sub-graphs execute and terminate, the Master Orchestrator merges their isolated outputs into one definitive summary.

## Enforcing Budgets on Fractals

Fractal Agency introduces the dangerous possibility of an infinite loop (an agent spawning an agent that spawns an agent forever). 

Lár completely mitigates this risk by forcing **Token Budget inheritance**.

*   If the Master Graph is initialized with a `token_budget=10_000`.
*   And it uses 2,000 tokens reasoning about how to split up the work.
*   It only has 8,000 tokens left. 
*   When it dynamically spawns 4 parallel sub-agents, Lár will distribute the remaining 8,000 tokens across them, granting them each a strict 2,000 token limit.
*   If *any* node across the fractal tree breaches the budget, the entire tree gracefully halts and raises a `TokenBudgetExceededEvent`.

This guarantees mathematical safety inside recursive AI architectures.
