# Lár v1.7.0 发布说明

## 新特性

### 1. 企业级流式传输与结构化 JSON 能力 (`LLMNode`)
`LLMNode` 迎来了重大升级，将企业级功能无缝集成到了 LiteLLM 后端中。

* **流式传输支持**：具备了直接的终端流式传输能力。当以 `stream=True` 实例化时，输出会逐块流式传输到 `sys.stdout`，同时在底层生成凝聚的 `total_tokens` 使用指标。
* **结构化输出支持**：通过传递 `response_format=<PydanticModel>`，可以轻松确保输出符合 Pydantic 模型定义的模式（Schema）。
* **Snath Cloud 挂钩**：添加了新参数 `fallbacks`（降级策略）、`caching`（缓存）和 `success_callbacks`（成功回调），为深度的基础设施可观测性挂钩和集成做好准备。

### 2. 精确的 Token 预算合并 (`BatchNode`)
* **线程安全的预算扣除**：在 `BatchNode` 线程中并行执行的状态修改现在会严格计算 Delta Token 成本，以避免竞态条件下的覆盖。父图会从数学上正确地合并所有工作节点产生的总预算。

### 3. 合规性与审计跟踪（面向审计师）
* 我们引入了一个正式的校验脚本（`examples/compliance/11_verify_audit_log.py`），专门供合规官和审计师通过 `HMAC-SHA256` 签名对 JSON 审计日志文件进行离线鉴权，以证明其防篡改性（这对于遵守 FDA/欧盟 AI 法案至关重要）。使用文档也已同步到了 `README.md` 中。

## Bug 修复与重构
* 更新了标准单元测试，以正确地为流式分支模拟 API 生成，并确保分支对齐时预算的准确性。
