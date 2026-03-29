# Lár v1.5.1 发布说明

## 加密审计日志

Lár v1.5.1 引入了**加密审计日志 (Cryptographic Audit Logs)**，这是企业合规（欧盟 AI 法案、SOC2、HIPAA）的一项关键特性。

虽然 Lár 始终通过 `AuditLogger` 提供“玻盒”执行轨迹，但 v1.5.1 允许您使用 HMAC-SHA256 签名对这些 JSON 日志进行加密签名。

### 为什么这很重要：
如果智能体执行了一项高风险操作（如金融交易或医疗数据路由），您不仅需要了解发生了什么的日志，还需要数学证明该日志在事后未被篡改。

### 如何使用：
在初始化 `GraphExecutor` 时传入 `hmac_secret` 字符串。

```python
from lar import GraphExecutor

# 引擎将自动对最终的 AuditLog 输出进行签名
executor = GraphExecutor(log_dir="compliance_logs", hmac_secret="super_secret_key")
```

生成的 `JSON` 日志文件将包含一个 `signature`（签名）载荷。如果 JSON 文件中的任何值（如 Token 成本、访问的节点或 LLM 的推理轨迹）被更改，签名验证将失败。

### 示例
我们添加了三个新的合规模式来演示此特性：
*   [8_hmac_audit_log.py](examples/compliance/8_hmac_audit_log.py)：演示如何运行智能体、生成带签名的日志，并编写手动验证钩子以证明载荷未被篡改。
*   [9_high_risk_trading_hmac.py](examples/compliance/9_high_risk_trading_hmac.py)：一个更复杂的模拟算法交易示例，展示如何使用 KMS 密钥保护高风险的 LLM 执行路径。
*   [10_pharma_clinical_trials_hmac.py](examples/compliance/10_pharma_clinical_trials_hmac.py)：演示如何使用安全签名的账本保护患者数据路由（符合 GxP / FDA 21 CFR Part 11 标准）。

## 微小修复
*   修复了 `FunctionalNode` 在实例化期间需要 `name` 关键字参数的错误。
