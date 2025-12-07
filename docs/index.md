# **Lár: The PyTorch for Agents**
 
> [!TIP]
> **Production Ready?**
> *   **[Snath Enterprise](https://snath.ai/enterprise)**: Self-hosted, air-gapped, GxP-compliant platform (The Bunker).
> *   **[Snath Cloud](https://snath.ai/cloud)**: Managed control plane for 1M+ agents (The Hive).

**Lár** (Irish for "core" or "center") by *SnathAI™* is the open-source standard for **Deterministic, Auditable, and Air-Gap Capable** AI agents.

It is a "define-by-run" framework for building auditable, reliable, and production-ready AI agents.

Lár is engineered as a direct solution to the "black box" problem. While other frameworks hide their logic in complex, "magic" executors that are impossible to debug, `lar` is a simple, "dumb" engine. It runs one node at a time, logs exactly what happened, and then moves on.

This "glass box" philosophy gives you a complete, step-by-step "flight data recorder" for every agent run, allowing you to build systems you can actually trust.

## Why We Built Lár?

### The Problem: Compliance is Impossible with Black Boxes

You are a developer building an agent for **Clinical Trials** or **Government Intelligence**.
- **The FDA requires 21 CFR Part 11 audit trails.**
- **The SCIF has no internet.**

Traditional frameworks fail both tests. They are non-deterministic "chatbots" that require cloud connectivity for tracing.

### The Solution: The First GxP-Ready Flight Recorder

We built the **Lár Engine** to bring the **Scientific Method** to AI Agents. It is not just about answers; it is about providing a full, immutable **Flight Log**.

**Lár is:**
1.  **Deterministic**: Same seed + Same Graph = Identical Execution.
2.  **Auditable**: Generating a forensic flight log is the *default* behavior.
3.  **Air-Gap Capable**: Build on a laptop -> Serialize to JSON -> Run offline.

Lár's **"define-by-run" architecture** forces transparency. The `GraphExecutor` runs one node, **logs the exact state change**, and then calculates the diff, producing a verifiable record for every single step.

This means you can always:

- **Pinpoint Failure**: See the **exact node** (`ToolNode`) that failed, the **exact error** (e.g., `APIConnectionError`), and the full state of the agent at the moment of collapse.

- **Audit Costs**: Track token usage per node, ensuring you can justify and optimize every single API call.

- **Build Trust**: Move your agent from a chaotic chat loop to a predictable, testable assembly line that your team and your company can actually trust in production.

**We are not selling magic; we are selling trust.**

**Stop guessing. Start building agents you can trust!**

Get Started in 3 Minutes [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)