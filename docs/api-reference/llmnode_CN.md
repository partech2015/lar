# API 参考：`LLMNode`

`LLMNode` 是智能体的“大脑”。它是一个具有弹性（Resilient）且具备状态感知能力的节点，通过调用生成式 AI 模型（如 Google 的 Gemini）来执行推理任务。

它会自动使用 `GraphState` 中的数据对您的提示词进行格式化，并将模型的文本输出写回状态。

## 关键特性

- **弹性**：自动处理 `429`（速率限制）错误，并采用指数退避算法进行重试。

- **成本审计**：自动将 `prompt_tokens`、`output_tokens` 和 `total_tokens` 记录到历史日志的 `run_metadata` 中。

- **有状态**：采用 Python 的 `format()` 字符串方法，动态地将 `GraphState` 中的任何值填充到您的提示词中。

## 使用示例

```python
# LLMNode 从状态中读取 `task`
planner_node = LLMNode(
    model_name="gemini/gemini-2.0-flash",
    prompt_template="你是一个规划员。你的任务是：{task}",
    output_key="plan", # 将结果保存到 state["plan"] 中
    next_node=...
)
```

## `__init__` 参数

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----|---------------|
| `model_name` | `str` | 是 | 模型名称（例如 `"gemini-2.0-flash"`）。 |
| `prompt_template` | `str` | 是 | 兼容 f-string 的模板。`{大括号}` 中的键将从 GraphState 中填充。 |
| `output_key` | `str` | 是 | 在 `GraphState` 中用于保存 LLM 文本响应的键（例如 `"draft_answer"`）。 |
| `next_node` | `BaseNode`| 是 | 此节点执行成功后要运行的下一个节点。 |
| `max_retries` | `int` | 否 | 遇到 429 错误时的重试次数。默认值：3。 |
