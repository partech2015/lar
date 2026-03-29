# 防御性约束 (v1.6.0)

随着智能体变得越来越自主（如 v1.5 中引入的 `DynamicNode`），它们面临着两个主要风险：
1. **上下文膨胀**：并行工作节点返回的海量文档会淹没下游的上下文窗口（产生“黑洞”效应）。
2. **死循环**：智能体陷入自我修复循环，迅速耗尽 API 额度。

Lár v1.6.0 引入了架构层面的解决方案，使您的智能体在生产环境中更加稳健且在数学上是安全的。

---

## 1. 内存压缩 (`ReduceNode`)

在 v1.6.0 之前，运行一个 `BatchNode` 并行收集 10 篇文章，会将这 10 篇文章同时直接塞回 `GraphState`。这将立即产生一个“黑洞”，瞬间撑爆任何读取该状态的下游模型的上下文窗口。

我们通过引入 `ReduceNode`（`LLMNode` 的子类）解决了这个问题。

`ReduceNode` 设计用于紧随 `BatchNode`（即“Map”阶段）之后。它读取状态中膨胀的键，要求一个快速且廉价的 LLM 将关键见解总结或提取到一个新键中，然后**显式地对上游的海量报告调用 `state.delete(key)`**。

这保证了在节点间传递的状态“接力棒”始终保持轻量和聚焦。

### 实现示例

```python
from lar import BatchNode, ReduceNode, LLMNode

# 1. Map 阶段：三个智能体并行进行研究
researcher_1 = LLMNode(model_name="ollama/phi4", prompt_template="研究 AI 在医疗领域的应用。", output_key="healthcare")
researcher_2 = LLMNode(model_name="ollama/phi4", prompt_template="研究 AI 在金融领域的应用。", output_key="finance")
researcher_3 = LLMNode(model_name="ollama/phi4", prompt_template="研究 AI 在机器人领域的应用。", output_key="robotics")

# 2. Reduce 阶段：读取 3 份厚重的报告，提取见解，并删除原始文本
reducer = ReduceNode(
    model_name="ollama/phi4",
    prompt_template="总结核心主题：1. {healthcare} 2. {finance} 3. {robotics}",
    input_keys=["healthcare", "finance", "robotics"], # 这些键在执行后将被删除
    output_key="executive_summary"
)

# 将它们批处理在一起，并直接路由到 reducer
map_phase = BatchNode(
    nodes=[researcher_1, researcher_2, researcher_3],
    next_node=reducer
)
```

---

## 2. 经济约束（Token 预算）

Lár 现在支持通过 `token_budget`（Token 预算）设定数学上的美元金额上限，而不是依赖于粗放的“最大步数”或猜测智能体的成本。

您可以在初始图状态中设置一个整数类型的 `token_budget`。每当 `LLMNode` 执行时，它都会从 LiteLLM 读取确切的 Token 使用量，并在路由到下一个节点之前从 `token_budget` 状态变量中扣除。

如果模型尝试执行时 `token_budget` 为 `0` 或负数，引擎将拦截此调用，抛出错误并优雅地终止工作流，从而保护您的 API 额度。

### 实现示例

```python
from lar import GraphExecutor, LLMNode

executor = GraphExecutor()

# 给智能体设定 2500 个 Token 的严格最大预算
initial_state = {
    "task": "写一本关于罗马帝国的 50 页的书。",
    "token_budget": 2500 
}

book_writer = LLMNode(
    model_name="openai/gpt-4o",
    prompt_template="{task}",
    output_key="book_draft"
)

# 执行器将运行该节点。
# 如果生成内容超过 2500 个 Token，状态中的预算将降至零以下。
# 链条中的下一个 LLMNode 将立即拒绝运行并产出错误日志。
for log in executor.run_step_by_step(book_writer, initial_state):
    print(log["outcome"])
```

---

## 3. 节点疲劳（死循环保护）

为了防止真正的死循环（例如 `RouterNode` 在 `FixCodeNode` 修正代码节点和 `TestCodeNode` 测试代码节点之间无休止地跳转，虽然技术上没有瞬间消耗海量 Token），`GraphExecutor` 会安全地追踪访问特定节点类的次数。

每当一个节点运行时，执行器都会增加其计数器。如果单个节点被访问的次数超过了全局的 `max_node_fatigue`（最大节点疲劳）限制，引擎将强制触发断路器并停止运行，确保没有任何 `RouterNode` 能在没有人工干预的情况下无限循环图的一个子集。

### 实现示例

```python
from lar import GraphExecutor

# 设置在一次图运行中，任何单个节点的最大执行次数为 5 次
executor = GraphExecutor(max_node_fatigue=5)

# 如果一个智能体陷入自我修复循环，经过同一个 LLMNode 达 6 次，
# 执行器将拦截它并抛出 FATIGUE（疲劳）错误。
```

要查看这三个特性协同工作的顶级演示，请参考开源仓库中的 [`examples/advanced/11_map_reduce_budget.py`](https://github.com/snath-ai/lar/blob/main/examples/advanced/11_map_reduce_budget.py)。
