# **Welcome to Lár: The Glass Box Agent Framework**

**Lár** (Irish for "core" or "center") by *SnathAI™*  is the open-source "PyTorch for Agents."

It is a "define-by-run" framework for building auditable, reliable, and production-ready AI agents.

Lár is engineered as a direct solution to the "black box" problem. While other frameworks hide their logic in complex, "magic" executors that are impossible to debug, `lar` is a simple, "dumb" engine. It runs one node at a time, logs exactly what happened, and then moves on.

This "glass box" philosophy gives you a complete, step-by-step "flight data recorder" for every agent run, allowing you to build systems you can actually trust.

## Why We Built Lár?

### The Problem: The "Black Box" Tax

You are a developer launching a **mission-critical AI agent**. It works flawlessly on your machine. You push it to production, and it instantly fails.

- Why did it fail? You don't know.

- Which node failed? You can't tell.

- What was the cost? You have to guess.

Instead of a solution, you get a **100-line stack trace** from deep inside a monolithic framework's core, pointing to an error you cannot debug. This is the **"Black Box Tax"**—the **price you pay** for using systems that **hide** their logic.

For too long, developers have been told that **auditing agents is a premium feature**. If you want to know *why* your agent spent $50, or *why* it got stuck in a loop, you had to integrate an external, complex, and **paid tracing tool** like LangSmith.

We got fed up. We believe that **auditing the reasoning flow of an AI agent should be easy, built-in, and free.**

### The Lár Solution: Your Agent's Flight Recorder

We built the **Lár Engine** as a direct antidote to the **"Black Box Tax."**

**Lár's core output is not just an answer; it is a full, immutable Flight Log.**

Lár's **"define-by-run" architecture** forces transparency: the `GraphExecutor` is designed as a simple generator that runs one node, **logs the exact state change**, and then pauses, producing a verifiable record for every step.

This means you can always:

- **Pinpoint Failure**: See the **exact node** (`ToolNode`) that failed, the **exact error** (e.g., `APIConnectionError`), and the full state of the agent at the moment of collapse.

- **Audit Costs**: Track token usage per node, ensuring you can justify and optimize every single API call.

- **Build Trust**: Move your agent from a chaotic chat loop to a predictable, testable assembly line that your team and your company can actually trust in production.

**We are not selling magic; we are selling trust.**

**Stop guessing. Start building agents you can trust!**

Get Started in 3 Minutes [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)