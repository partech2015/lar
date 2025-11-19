# The "Glass Box" Philosophy

The primary challenge in production-grade AI is a lack of traceability. When a multi-step agent fails, it's often impossible to determine why.

## The **"Black Box" (Other Frameworks)**

Traditional agent frameworks rely on "magic" `AgentExecutor` objects that try to do everything at once. They are complex, monolithic, and hide their internal logic.

- When this "magic" fails, you get a 100-line stack trace from deep inside the framework's code.

- You have to guess what went wrong. Was it a bad prompt? A failed tool? A malformed JSON response?

- Debugging becomes a frustrating, time-consuming nightmare. To get any visibility, you are forced to use external, often paid, tracing platforms.

## **The "Glass Box" (The `Lár` Way)**

`Lár` is built on the opposite philosophy. We believe that **reliability comes from simplicity and transparency.**

Our "engine" (`GraphExecutor`) is simple, "dumb," and predictable. It only knows how to do one thing:

1. Run **one node** at a time.

2. Log the exact change to the agent's memory (`state_diff`).

3. Move to the next node.

This "glass box" approach is not an "add-on"; it is the **core, default, open-source output of the engine.**

**This means you get:**

- **Instant Debugging**: You can see the exact node that failed, the exact data it received, and the exact error it produced.

- **Total Auditability**: Your "history log" is a complete, immutable "flight data recorder" for every agent run. This is essential for compliance and security.

- **Deterministic Control**: You are not in a "chaotic chat room." You are building a deterministic "assembly line," where you have 100% control over the agent's path.

`Lár` is the framework for developers who are tired of "magic" and are ready to build production-grade agents they can actually trust.