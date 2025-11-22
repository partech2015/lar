# **Welcome to Lár: The Glass Box Agent Framework**

**Lár** (Irish for "core" or "center") by *SnathAI™*  is the open-source "PyTorch for Agents."

It is a "define-by-run" framework for building auditable, reliable, and production-ready AI agents.

Lár is engineered as a direct solution to the "black box" problem. While other frameworks hide their logic in complex, "magic" executors that are impossible to debug, `lar` is a simple, "dumb" engine. It runs one node at a time, logs exactly what happened, and then moves on.

This "glass box" philosophy gives you a complete, step-by-step "flight data recorder" for every agent run, allowing you to build systems you can actually trust.

## **Why Lár?**

### The Problem: The "Black Box"

You're a solo developer or a team lead. You've built an agent using a "magic" framework. It works in your notebook, but in production, it fails.

- Why did it fail? You don't know.

- Which step failed? You can't tell.

- What data was it processing? You have to guess.

You get a 100-line stack trace from deep inside the framework's code. You are completely blind. Debugging is a nightmare. This is the "black box" problem, and it's what stops 99% of agent projects from ever reaching production.

### The Solution: The "Glass Box"

`Lár` is built on a simple premise: **the "magic" is the enemy of reliability.**

Our `GraphExecutor` is a simple `generator` that `yields` the execution log after every single step. The audit trail isn't a paid add-on; it's the **core output of the engine.**

This means you can:

1. **Instantly Find Failures**: Your log shows you the exact node, the exact error (`429 Rate Limit`), and the exact data that caused it.

2. **Audit Costs**: Our `LLMNode` logs token usage per step. You can see exactly which node is costing you money.

3. **Build Deterministic Systems** : You are not in a "chaotic chat room." You are building a "deterministic assembly line." You have 100% control over the flow.

**Stop guessing. Start building agents you can trust!**

Get Started in 3 Minutes [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)