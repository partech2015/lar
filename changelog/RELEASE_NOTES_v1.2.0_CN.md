# Lár v1.2.0 发布说明

**可观测性与调试更新**

此版本专注于“玻盒”（Glass Box）可见性，吸纳了需要精细化成本追踪和更整洁调试日志的高级用户反馈。

## 新特性

### 1. 按模型进行成本归因
执行摘要现在包含了 `tokens_by_model`（按模型区分的 Token 消耗）明细。这允许您审计不同供应商的成本（例如，将 Ollama 的使用量与 OpenAI 的使用量分开）。

**示例输出：**
```json
"summary": {
  "total_tokens": 1500,
  "tokens_by_model": {
    "ollama/phi4": 500,
    "gemini-pro": 1000
  }
}
```

### 2. 控制台噪音过滤
大型数据结构（如 50kb 的状态转储或超长提示词）现在会在**控制台输出**中自动截断，以保持终端的可读性。
*   **控制台**：显示 `... [已截断，总长度: 50000 字符]`
*   **JSON 日志**：保留完整的、未截断的数据用于审计。

### 3. 精细化节点日志
每一个 `LLMNode` 现在都会在步骤元数据中显式记录 `prompt_tokens`、`output_tokens` 和 `model`，从而实现精确的每步成本分析。

## 变更内容
*   **utils.py**：添加了 `truncate_for_log` 工具函数。
*   **executor.py**：更新了 `GraphExecutor` 以按模型汇总 Token 使用情况。
*   **node.py**：更新了 `ToolNode`、`LLMNode` 和 `AddValueNode` 以使用截断功能。

## 升级
```bash
pip install lar-engine==1.2.0
```
