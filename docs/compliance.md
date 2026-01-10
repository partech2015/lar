# Compliance & Safety (EU AI Act Ready - Aug 2026)

> **Legal Disclaimer**: The Lár framework provides architectural patterns to *assist* with compliance. It does not guarantee compliance on its own. You are responsible for the final validation of your system.

Lár is engineered to meet the stringent requirements of the **EU AI Act (2026)** and **FDA 21 CFR Part 11** for High-Risk AI Systems.

Unlike "Black Box" frameworks that obfuscate decision paths, Lár is a "Glass Box" engine designed for forensic auditability.

---

## EU AI Act Alignment

The EU AI Act (fully enforceable August 2026) imposes strict obligations on "High-Risk" systems (e.g., Medical Devices, Employment, Credit Scoring, Critical Infrastructure).

### 1. Article 12: Record-Keeping (Logging)
**Requirement**: Systems must enable "automatic recording of events ('logs') over their lifetime" to ensure traceability.

**Lár Solution**: `State-Diff Ledger`

Every Lár agent automatically produces a `flight_recorder.json` log. This is not a simple debugging print stream; it is a **forensic ledger** containing:

*   **Timestamp**: UTC-aligned execution time.
*   **Input/Output**: The exact prompt sent and the raw completion received.
*   **Model ID**: The specific version of the model used (e.g., `gpt-4-0613`).
*   **State Diff**: The exact variables changed in memory.

```json
// Example Lár Ledger Entry
{
  "step": 4,
  "node": "TriageNode",
  "timestamp": "2026-08-12T10:00:01Z",
  "state_diff": {
    "risk_score": {"old": 0.1, "new": 0.95},
    "routing": {"old": null, "new": "HUMAN_REVIEW"}
  }
}
```

### 2. Article 13: Transparency & Interpretability
**Requirement**: High-risk AI systems must be designed "in such a way that their operation is sufficiently transparent to enable users to interpret the system's output."

**Lár Solution**: "Glass Box" Architecture

*   **No Hidden Prompts**: Lár does not inject "system prompts" behind your back. You own 100% of the prompt.
*   **Explicit Routing**: The logic flow is defined in standard Python code (Nodes and Edges), not in a hidden neural network or a complex "Agent Executor" loop.
*   **Interpretability**: Any Python developer can read `graph.add_edge("Triage", "Human")` and understand the decision path without needing to understand the LLM's internal weights.

### 3. Article 14: Human Oversight
**Requirement**: Systems must be designed so that they can be "effectively overseen by natural persons," including the ability to "interrupt the system" or "override" decisions.

**Lár Solution**: Native `Interrupt` Pattern

Lár treats "Human Intervention" as a first-class citizen in the graph.

*   **Pause & Resume**: You can execute the graph up to a checkpoint (e.g., `before="ExecuteTool"`), inspect the state, and resume.
*   **State Modification**: A human supervisor can manually edit the memory (e.g., correcting a hallucinated argument) before approving the next step.

---

## FDA 21 CFR Part 11 (Electronic Records)

For healthcare and pharmaceutical applications (e.g., Drug Discovery pipelines), Lár supports the key requirements of **Part 11**:

1.  **Validation**: The deterministic nature of the graph means you can run regression tests. Given Input X and Fixed Seed Y, the graph traverses effectively the same path.
2.  **Audit Trails**: The `GraphExecutor` logs are immutable and time-stamped.
3.  **Authority Checks**: Lár's `SecurityNode` pattern allows you to implement permissions (e.g., "Only User A can approve Tool B") directly in the graph logic.

---

## Summary for Auditors

| Feature | Lár Implementation | Compliance Value |
| :--- | :--- | :--- |
| **Determinism** | State Machines vs. Loops | Eliminates "Runaway Agent" risk. |
| **Observability** | JSON Flight Recorder | Meets Art. 12 (Recording). |
| **Control** | Standard HIL Patterns | Meets Art. 14 (Oversight). |
| **Privacy** | Local/Air-Gapped Capable | Meets GDPR / Data Sovereignty. |
