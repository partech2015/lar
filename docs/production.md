# Go to Production

Lár is "Write Once, Run Anywhere." The same agent graph you build on your laptop can be deployed to the **Snath Cloud** or an **Air-Gapped Enterprise Server**.

> [!TIP]
> **Production Platforms**
> *   **[Snath Enterprise (Bunker)](https://snath.ai/enterprise)**: For GxP, HIPAA, and Air-Gapped workloads.
> *   **[Snath Cloud (The Hive)](https://snath.ai/cloud)**: For high-scale, managed agent orchestration.

---

## Path 1: Snath Enterprise ("The Bunker")
**Self-Hosted | Air-Gapped | GxP Ready**

Strictly for regulated industries (Pharma, Finance, Defense).

*   **Deployment**: Docker containers on your own infrastructure (AWS VPC, On-Prem, SCIF).
*   **Networking**: Zero egress. The worker blocks all external API calls by default (hardened offline mode).
*   **Compliance**:
    *   **21 CFR Part 11**: Generates PDF Validation Reports.
    *   **Digital Signatures**: Logs are HMAC-signed for tamper-proofing.
    *   **Audit Trail**: Immutable "Flight Log" JSONs stored on-disk.

[Contact Sales for Licensing](https://snath.ai/enterprise)

---

## Path 2: Snath Cloud ("The Hive")
**Managed Control Plane | Serverless | Scalable**

For startups and SaaS companies scaling to 1M+ agents.

*   **Deployment**: One-click upload (`executor.save_to_file("agent.json")` -> Upload).
*   **Features**:
    *   **Dashboard**: Live visualization of your agent graph execution.
    *   **Observability**: Token costs, latency tracking, and error heatmaps.
    *   **Managed Infrastructure**: Serverless workers that scale to zero.

[Sign Up for Beta](https://snath.ai/cloud)
