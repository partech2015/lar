# API 参考：`RouterNode`

`RouterNode` 是智能体的“选择器”或 `if/else` 语句。它是一个**100% 确定性**的节点，使用纯 Python 逻辑来决定智能体接下来的去向。

它是构建复杂的、可审计的多智能体系统和循环的核心。

## 关键特性

- **确定性**：它只是一个 Python 函数。没有 AI，没有“魔法”。给定相同的状态，它每次都会执行相同的操作。

- **多路径**：它可以将智能体分流到许多不同的“流水线”上（例如，“账单处理” vs. “技术支持”）。

- **支持循环**：通过从“判定”节点路由回“测试”节点，您可以创建强大的自我修复循环。

## 使用示例

首先，定义您简单的、无状态的“逻辑”函数：

```python
def judge_function(state: GraphState) -> str:
    """读取状态并返回一个字符串键。"""
    if state.get("last_error"):
        return "failure_path" # 此键必须与 path_map 匹配
    else:
        return "success_path"
```

然后，将其接入您的 `RouterNode`：

```python
# RouterNode 读取从 judge_function 返回的字符串，
# 并根据该字符串选择下一个节点。
judge_node = RouterNode(
    decision_function=judge_function,
    path_map={
        "success_path": success_node,
        "failure_path": corrector_node
    },
    default_node=critical_fail_node # 可选：用于兜底安全
)
```

## 运行机制

当 `execute(state)` 被调用时：

1. 它运行 `route_key = self.decision_function(state)`。

2. 它在 `self.path_map` 中查找该 `route_key`。

3. 如果找到，它将返回对应的节点（例如 `corrector_node`）。

4. 如果未找到，它将返回 `default_node`。

5. 如果没有设置默认节点，它将返回 `None` 并停止运行图。

## `__init__` 参数

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----|---------------|
| `decision_function` | `Callable` | 是 | 一个 Python 函数，接受 `GraphState` 作为输入，并返回一个 `str`（路由键）。|
| `path_map` | `Dict` | 是 | 一个字典，将函数返回的字符串映射到要运行的 `BaseNode` 对象（例如 `{"success_path": ...}`）。|
| `default_node` | `BaseNode` | 否 | （可选）如果 `decision_function` 返回的键不在 `path_map` 中，则运行此兜底节点。|
