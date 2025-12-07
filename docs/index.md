# **Lár: The PyTorch for Agents**
 
!!! tip "Production Ready?"
    *   **[Snath Enterprise](https://snath.ai/enterprise)**: Self-hosted, air-gapped, GxP-compliant platform (The Bunker).
    *   **[Snath Cloud](https://snath.ai/cloud)**: Managed control plane for 1M+ agents (The Hive).

**Lár** (Irish for "core" or "center") by *SnathAI™* is the open-source standard for **Deterministic, Auditable, and Air-Gap Capable** AI agents.

It is a "define-by-run" framework for building auditable, reliable, and production-ready AI agents.

Lár is engineered as a direct solution to the "black box" problem. While other frameworks hide their logic in complex, "magic" executors that are impossible to debug, `lar` is a simple, "dumb" engine. It runs one node at a time, logs exactly what happened, and then moves on.

This "glass box" philosophy gives you a complete, step-by-step "flight data recorder" for every agent run, allowing you to build systems you can actually trust.

## Why We Built Lár?

### The Problem: The "Black Box Tax"

You are a developer launching a **mission-critical AI agent**. It works flawlessly on your machine. You push it to production, and it instantly fails.

-   **Why did it fail?** You don't know.
-   **Which step failed?** You can't tell.
-   **Which node failed?** You can't tell.
-   **What data was it processing?** You have to guess.
-   **What was the cost?** You have to guess.

Instead of a solution, you get a **100-line stack trace** from deep inside a monolithic framework's core, pointing to an error you cannot debug. This is the **"Black Box Tax"**—the **price you pay** for using systems that **hide** their logic.

### The Solution: The "Glass Box"

For too long, developers have been told that **auditing agents is a premium feature**. If you want to know *why* your agent spent $50, or *why* it got stuck in a loop, you had to integrate an external, complex, and **paid tracing tool** like LangSmith.

`Lár` is built on a simple premise: **the "magic" is the enemy of reliability.**

We believed that **auditing the reasoning flow of an AI agent should be easy, built-in, and free.**

Our `GraphExecutor` is a simple `generator` that `yields` the execution log after every single step. The audit trail isn't a paid add-on; it's the **core output of the engine.**

### The Lár Solution: Your Agent's Flight Recorder

We built the **Lár Engine** as a direct antidote to the **"Black Box Tax."**

**Lár's core output is not just an answer; it is a full, immutable Flight Log.**

Lár's **"define-by-run" architecture** forces transparency: the `GraphExecutor` is designed as a simple generator that runs one node, **logs the exact state change**, and then pauses, producing a verifiable record for every step.

This means you can always:

1.  **Instantly Find Failures**: Your log shows you the exact node, the exact error (`429 Rate Limit`), and the exact data that caused it.
2.  **Audit Costs**: Our `LLMNode` logs token usage per step. You can see exactly which node is costing you money.
3.  **Build Deterministic Systems**: You are not in a "chaotic chat room." You are building a "deterministic assembly line." You have 100% control over the flow.

**We are not selling magic; we are selling trust.**

*Stop guessing. Start building agents you can trust!*

> **Need Certified Validation?**
> For **FDA 21 CFR Part 11 Audit Trails**, **Air-Gap environments**, and **GxP Validation**, see **[Snath Enterprise](https://snath.ai/enterprise)**.

Get Started in 3 Minutes [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)