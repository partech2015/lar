[← Return to snath.ai](https://snath.ai)
# **Ready to build Auditable AI Agents**
 


**Lár** (Irish for "core" or "center") is the open source standard for **Deterministic, Auditable, and Air-Gap Capable** AI agents.

It is a **"define-by-run"** framework that acts as a **Flight Recorder** for your agent, creating a complete audit trail for every single step.

!!! info "Not a Wrapper"
    **Lár is NOT a wrapper.**
    It is a standalone, ground-up engine designed for reliability. It does not wrap LangChain, OpenAI Swarm, or any other library. It is pure, dependency-lite Python code optimized for "Code-as-Graph" execution.

## The "Black Box" Problem

You are a developer launching a **mission-critical AI agent**. It works on your machine, but in production, it fails.
You don't know **why**, **where**, or **how much** it cost. You just get a 100-line stack trace from a "magic" framework.

## The "Glass Box" Solution

**Lár removes the magic.**

It is a simple engine that runs **one node at a time**, logging every single step to a forensic **Flight Recorder**.

This means you get:
1.  **Instant Debugging**: See the exact node and error that caused the crash.
2.  **Free Auditing**: A complete history of every decision and token cost, built-in by default.
3.  **Total Control**: Build deterministic "assembly lines," not chaotic chat rooms.

> *"This demonstrates that for a graph without randomness or external model variability, Lár executes deterministically and produces identical state traces."*

*Stop guessing. Start building agents you can trust.*

## Demos & Examples

Learn by building with our ready-made demos:

*   **[RAG Agent Demo](https://github.com/axdithyaxo/rag-demo)**: A self-correcting RAG agent with local vector search.
*   **[Customer Support Swarm](https://github.com/axdithyaxo/customer-support-demo)**: A multi-agent orchestration pattern.

## Power Your IDE (Cursor / Windsurf)

Make your IDE an expert Lár Architect with this **2-Step Workflow**:

1.  **Reference The Rules**: In your chat, type `@lar/IDE_MASTER_PROMPT.md`. This loads the strict typing rules.
2.  **Use The Template**: Fill out `@lar/IDE_PROMPT_TEMPLATE.md` with your agent requirements.

[Read the Full Guide](ide_setup.md)

Get Started in 3 Minutes [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)

## Author
**[Lár](https://github.com/axdithyaxo/lar)** was created by **[Aadithya Vishnu Sajeev](https://github.com/axdithyaxo)**.