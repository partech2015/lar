# 基于事件溯源的审计日志

**`GraphExecutor` 的“杀手锏”是它生成的结构化历史日志。这不仅仅是一个简单的 `print` 语句，而是一条取证轨迹。**

对于复杂的智能体工作流，你需要详细的出处（Provenance）。

**Lár 提供了：**
1.  **不可变性**：每一步都是一个离散的事件。
2.  **因果关系**：我们记录了导致新现实的*确切状态变化* (`state_diff`)。
3.  **可复现性**：使用相同的种子重放这些事件保证能得到相同的结果。

## “事件溯源”模型

为了实现无限的可扩展性，`lar`（自 v2.0 起）不再在每一步记录整个状态，因为那样既慢又昂贵。

相反，它记录的是**“事件”（状态差异）**。

`GraphExecutor` 为每一步 `yield` 一个 `step_log` 对象。该日志是一个小型、高效的 JSON 对象：
```json
{
  "step": 0,
  "node": "LLMNode",
  "outcome": "success",
  
  "state_before": {
    "task": "法国的首都是哪里？"
  },
  
  "state_diff": {
    "added": {
      "plan": "TEXT"
    },
    "removed": {},
    "modified": {}
  },

  "run_metadata": {
    "prompt_tokens": 42,
    "output_tokens": 1,
    "total_tokens": 43
  }
}
```

**这份日志能告诉你什么**

- `step` **与** `node`：您在图中的位置。

- `outcome`：发生了什么（“success” 成功或 “error” 错误）。

- `state_before`：在该节点运行前智能体整个内存的“快照”。

- `state_diff`：这就是**“杀手锏”**。这是该节点对状态所做的确切更改。你可以看到它 `added`（添加）了 `"plan": "TEXT"` 这个键值对。

- `run_metadata`：**成本审计**。你可以看到这单一的 `LLMNode` 步骤花费了 43 个 Token。

当你的智能体失败时，“玻盒”会为你提供完美的记录：
```json
{
  "step": 3,
  "node": "LLMNode",
  "outcome": "error",
  "error": "429 LLMNode 在 3 次重试后失败。",
  "state_before": { ... },
  "state_diff": { ... },
  "run_metadata": {}
}
```

这就是 `lar` 的不同之处。你不需要再去猜测它为什么失败。日志会告诉你确切的节点、确切的错误以及失败时确切的状态。

---

## v1.3.0 新特性：模块化可观测性

**Lár 现在将日志记录和追踪功能分离到了专用的、可注入的组件中：**

### AuditLogger（审计日志器）

管理审计轨迹，并支持符合 GxP 标准的 JSON 持久化。

**默认用法：**
```python
executor = GraphExecutor(log_dir="my_logs")
# AuditLogger 会自动创建
history = executor.logger.get_history()
```

**高级用法（自定义注入）：**
```python
from lar import AuditLogger

custom_logger = AuditLogger(log_dir="compliance_logs")
executor = GraphExecutor(logger=custom_logger)

# 直接访问审计历史
for step in custom_logger.get_history():
    print(f"步骤 {step['step']}: {step['node']} - {step['outcome']}")
```

### TokenTracker（Token 追踪器）

跨模型和工作流汇总 Token 使用情况。

**默认用法：**
```python
executor = GraphExecutor()
summary = executor.tracker.get_summary()
print(f"总 Token 数: {summary['total_tokens']}")
print(f"按模型区分: {summary['tokens_by_model']}")
```

**高级用法（共享追踪器以进行成本汇总）：**
```python
from lar import TokenTracker

# 在多个执行器之间共享同一个追踪器
shared_tracker = TokenTracker()

executor1 = GraphExecutor(log_dir="workflow1", tracker=shared_tracker)
executor2 = GraphExecutor(log_dir="workflow2", tracker=shared_tracker)

# 运行两个工作流
executor1.run(agent1, state1)
executor2.run(agent2, state2)

# 获取汇总成本
total = shared_tracker.get_summary()
print(f"两个工作流的总成本: {total['total_tokens']} tokens")
```

**查看完整示例：** `examples/patterns/16_custom_logger_tracker.py`
