# API 参考：工具组件

## 图组件

这些是维持框架运行的“脚手架”组件：`GraphExecutor`（图执行器）、`GraphState`（图状态）以及我们的简单辅助节点。

### **`1. GraphExecutor`**

这是运行图的“引擎”。您通常只需要在开始运行之前与之交互。

```python
from lar import GraphExecutor

executor = GraphExecutor()

# run_step_by_step 是一个生成器
result_log = list(executor.run_step_by_step(
    start_node=my_start_node, 
    initial_state={"task": "我的任务"}
))
```

**方法**

`run_step_by_step(start_node, initial_state)`

- 这是 `lar` 的核心方法，是一个 Python ` generator`（生成器）。
- 它运行一个节点，`yield`（产出）该步骤的“飞行记录”（`step_log`），然后暂停。
- 它还包含主 `try...except` 块，用于捕获节点中出现的关键未处理错误（例如 `LLMNode` 在所有重试后仍然失败）。

### **`2. GraphState`**

这是智能体的“内存”或“剪贴板”。它是一个简单的 Python 对象，会自动传递给每个节点的 `execute` 方法。

```python
from lar import GraphState

state = GraphState({"task": "我的任务"})

# 写入状态
state.set("plan", "TEXT")

# 从状态中读取
my_plan = state.get("plan") 
```

**方法**

- `set(key, value)`：在状态中设置一个值。
- `get(key, default=None)`：从状态中获取一个值。
- `get_all()`：返回整个状态字典的副本。

## 工具节点

### **`3. AddValueNode`**

一个简单的用于写入或复制数据的节点。它具备“状态感知”能力。

```python
# 将 state["final_status"] 设置为字面量字符串 "SUCCESS"
success_node = AddValueNode(
    key="final_status", 
    value="SUCCESS", 
    next_node=None
)

# 从 state["draft_answer"] *复制*值
# 到 state["final_response"]
copy_answer_node = AddValueNode(
    key="final_response", 
    value="{draft_answer}", 
    next_node=success_node
)
```

### **`4. ClearErrorNode`**

一个“清理”节点。其唯一工作是清理 `last_error` 键，这对实现自我修复循环至关重要。

```python
# 在修正器 (Corrector) 运行后，此节点进行清理，
# 然后循环回测试器 (Tester)。
clear_error_node = ClearErrorNode(
    next_node=tester_node
)
```
