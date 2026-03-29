[← 返回 API 参考](../api-reference/utilities.md)

# ClearErrorNode

一个用于自我修复循环的“清理”节点。它的唯一职责是从状态中移除 `last_error` 键，从而允许重试循环干净地继续进行。

## 导入

```python
from lar.node import ClearErrorNode
```

## 构造函数

```python
ClearErrorNode(
    next_node: BaseNode = None
)
```

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `next_node` | `BaseNode` | 清除错误后转换到的节点（通常是您想要重试的节点）。 |

## 使用模式：重试循环

该节点通常放置在路由器检测到错误*之后*以及智能体重试任务*之前*。

```python
# 1. 重试目标
generator = LLMNode(...)

# 2. 清理节点
cleaner = ClearErrorNode(next_node=generator)

# 3. 路由器逻辑
def check_error(state):
    if state.get("last_error"):
        return "RETRY"
    return "SUCCESS"

router = RouterNode(
    decision_function=check_error,
    path_map={
        "RETRY": cleaner, # 转到清理节点，然后返回生成器
        "SUCCESS": end_node
    }
)
```
