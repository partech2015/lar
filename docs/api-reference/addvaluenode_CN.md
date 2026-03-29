[← 返回 API 参考](../api-reference/utilities.md)

# AddValueNode

一个用于在状态（State）中注入数据或复制值的工具节点。它在设置标志、默认值或设置键别名时非常有用。

## 导入

```python
from lar.node import AddValueNode
```

## 构造函数

```python
AddValueNode(
    key: str, 
    value: Any, 
    next_node: BaseNode = None
)
```

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `key` | `str` | 状态字典中要设置或覆盖的键。 |
| `value` | `Any` | 要分配的值。支持使用 `{key_name}` 语法的动态状态引用。 |
| `next_node` | `BaseNode` | 图中要执行的下一个节点。 |

## 使用示例

### 1. 设置静态标志
```python
mark_success = AddValueNode(
    key="status",
    value="SUCCESS",
    next_node=None
)
```

### 2. 复制状态变量（设置别名）
你可以使用 `{}` 语法将一个状态键复制到另一个键中。这在将数据传递给工具前对其进行重塑时非常有用。

```python
# 将 state["llm_output"] 复制到 state["final_answer"]
alias_node = AddValueNode(
    key="final_answer",
    value="{llm_output}",
    next_node=next_step
)
```
