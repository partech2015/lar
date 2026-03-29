# API 参考：`ToolNode`

`ToolNode` 是智能体的“双手”。它是一个强健的节点，用于运行任何纯 Python 函数（即“工具”）。

这是您的智能体与世界交互的方式：

- 运行代码 (`run_generated_code`)
- 搜索数据库 (`retrieve_relevant_chunks`)
- 调用外部 API (`Google Search`)
- 修改状态 (`increment_retry_count`)

## 关键特性

- **强健性**：默认情况下，它在 `try...except` 块中运行您的工具。

- **韧性**：它支持两条独立的路径：`next_node`（成功时）和 `error_node`（失败时）。

- **有状态**：它使用您提供的 `input_keys`，动态地从 `GraphState` 中收集工具所需的参数。

- **可审计**：如果您的工具失败，`ToolNode` 会自动捕获异常并将错误消息保存到 `state.set("last_error", ...)` 中，供其他节点读取。

## 使用示例

首先，定义您的“工具”。它只是一个简单的 Python 函数：

```python
def add_numbers(a: int, b: int) -> int:
    """一个简单的加法工具。"""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("输入必须是整数")
    return a + b
```

然后，通过 `ToolNode` 将其接入您的图中：

```python
# ToolNode 将会：
# 1. 获取 `state.get("num1")` 和 `state.get("num2")`
# 2. 调用 `add_numbers(num1, num2)`
# 3. 将结果保存到 `state.set("sum_result", ...)`
add_node = ToolNode(
    tool_function=add_numbers,
    input_keys=["num1", "num2"],
    output_key="sum_result",
    next_node=success_node,
    error_node=failure_node # 如果引发了 TypeError
)
```

## 运行机制

- 当 `execute(state)` 被调用时：

    1. 它通过从 `self.input_keys` 中获取每个键，构建一个输入列表。

    2. 它调用 `self.tool_function(*inputs)`。

- 如果成功：

    1. 它将返回值保存到 `state.set(self.output_key, ...)`。

    2. 它返回 `self.next_node`。

- 如果失败：

    1. 它将异常消息保存到 `state.set("last_error", ...)`。

    2. 它返回 `self.error_node`。

## `__init__` 参数

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----|---------------|
| `tool_function` | `Callable` | 是 | 您想要运行的 Python 函数。|
| `input_keys` | `List[str]` | 是 | 要从 'GraphState' 中读取的键列表。这些值将按顺序作为位置参数传递给您的工具。|
| `output_key` | `str` | 是 | 用于保存工具返回值的 `GraphState` 键。|
| `next_node` | `BaseNode` | 是 | 工具执行成功后要运行的节点。|
| `error_node` | `BaseNode` | 否 | 工具执行失败（引发异常）时要运行的节点。如果为 None，图将停止运行。|
