# BatchNode API 参考

## 概述

`BatchNode` 利用 Python 的 `ThreadPoolExecutor` 实现多个节点的**真正并行执行**。这对于独立分支可以并发运行的“扇出/扇入”(Fan-Out/Fan-In) 模式至关重要。

## 类签名

```python
class BatchNode(BaseNode):
    def __init__(self, nodes: List[BaseNode], next_node: BaseNode = None)
```

## 参数

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----------|-------------|
| `nodes` | `List[BaseNode]` | 是 | 要并行执行的节点列表。必须非空，且所有元素必须是 `BaseNode` 实例。 |
| `next_node` | `BaseNode` | 否 | 所有并行节点运行结束后要执行的单个节点。默认为 `None`（图终止）。 |

## 行为

### 1. **执行流程**
1. 创建当前状态的快照。
2. 为每个并行节点创建状态的深度副本。
3. 在独立线程中并发执行所有节点。
4. 将非冲突的更新合并回主状态。
5. 继续执行 `next_node`。

### 2. **状态隔离**
每个节点都运行在自己独立的状态**深度副本**中，从而防止竞态条件。线程之间在执行过程中互不干扰。

### 3. **状态合并策略**
所有线程完成后，`BatchNode` 会合并结果：
- **新增键**：自动添加到主状态。
- **更新键**：最后写入者胜出（存在竞态条件 - 请避免重叠的 `output_key` 值）。
- **未更改键**：忽略。

> [!WARNING]
> **键重叠风险**：如果多个节点写入同一个状态键，由于线程调度的原因，结果是不可预测的（非确定性）。请设计您的图以确保每个并行节点写入唯一的键。

### 4. **错误处理**
- 如果任何线程引发异常，该异常会被记录，并在主状态中设置 `last_error`。
- 其他线程会继续执行。
- `BatchNode` 总是会继续执行 `next_node`（它不会执行“快速失败”策略）。

## 使用示例

### 简单并行执行

```python
from lar import BatchNode, LLMNode, GraphExecutor

# 定义三个独立的分析任务
analyst_1 = LLMNode(
    model_name="gpt-4",
    prompt_template="分析该文本的情感：{text}",
    output_key="sentiment_analysis"
)

analyst_2 = LLMNode(
    model_name="gpt-4",
    prompt_template="从该文本中提取关键词：{text}",
    output_key="entity_extraction"
)

analyst_3 = LLMNode(
    model_name="gpt-4",
    prompt_template="总结该文本：{text}",
    output_key="summary"
)

# 并行运行这三个任务
parallel_batch = BatchNode(
    nodes=[analyst_1, analyst_2, analyst_3],
    next_node=None  # 合并结果后结束
)

# 执行
executor = GraphExecutor()
initial_state = {"text": "Apple 宣布了创纪录的第四季度营收..."}

for step in executor.run_step_by_step(parallel_batch, initial_state):
    print(f"步骤 {step['step']}: {step['node']}")

# 最终状态将包含所有三项分析结果
print(final_state.get("sentiment_analysis"))
print(final_state.get("entity_extraction"))
print(final_state.get("summary"))
```

### 新闻编辑室模式（真实场景示例）

参见 [`examples/scale/3_parallel_newsroom.py`](https://github.com/snath-ai/lar/blob/main/examples/scale/3_parallel_newsroom.py) 查看生产环境模式：

1. **规划节点 (Planner Node)**：LLM 生成报道角度。
2. **批处理节点 (BatchNode)**：3 个记者智能体并行进行研究。
3. **聚合节点 (Aggregator Node)**：将发现的研究成果合并成最终文章。

## 性能考量

### 何时使用 BatchNode

✅ **适用场景**：
- 具有独立输入的多个 LLM 调用（例如，翻译成 5 种语言）。
- 并行 API 请求（例如，从 3 个来源获取数据）。
- 独立的数据处理任务。

❌ **不适用场景**：
- 存在顺序依赖关系（请使用线性链）。
- 共享可变资源（线程会发生冲突）。
- CPython 中的 CPU 密集型任务（由于 GIL 限制了并行性 - 请改为使用 `ProcessPoolExecutor`）。

### 提速计算

对于 I/O 密集型任务（LLM 调用、API 请求）：
```
顺序执行时间: N × T
并行执行时间: T + 开销

提速倍数 = N (理想情况下)
实际提速 ≈ 0.8N (考虑线程开销)
```

对于 3 次持续 2 秒的 LLM 调用：
- 顺序执行：6 秒
- 并行执行：约 2.2 秒（**快 2.7 倍**）

## 常用模式

### 1. **A/B 测试**（对比多个提示词）

```python
BatchNode(
    nodes=[
        LLMNode(model_name="gpt-4", prompt_template="提示词 A: {task}", output_key="result_a"),
        LLMNode(model_name="gpt-4", prompt_template="提示词 B: {task}", output_key="result_b"),
    ]
)
```

### 2. **多模型共识**

```python
BatchNode(
    nodes=[
        LLMNode(model_name="gpt-4", prompt_template="{query}", output_key="gpt4_answer"),
        LLMNode(model_name="claude-3", prompt_template="{query}", output_key="claude_answer"),
        LLMNode(model_name="gemini-pro", prompt_template="{query}", output_key="gemini_answer"),
    ],
    next_node=vote_aggregator  # 多数投票决策
)
```

### 3. **并行数据摄取**

```python
BatchNode(
    nodes=[
        ToolNode(tool_function=fetch_twitter, input_keys=["query"], output_key="twitter_data"),
        ToolNode(tool_function=fetch_reddit, input_keys=["query"], output_key="reddit_data"),
        ToolNode(tool_function=fetch_news, input_keys=["query"], output_key="news_data"),
    ]
)
```

## 调试

### 查看审计日志

`BatchNode` 步骤的审计日志显示：
- `node`: "BatchNode"
- `state_diff`: 所有已合并的键
- 子节点**不会**被单独记录（设计使然 - 它们在线程中运行）

要调试子节点，请将它们包装在独立的图中并单独检查其日志。

## 验证

`BatchNode` 会验证构造参数：
- `nodes` 必须是一个非空列表。
- 所有元素必须是 `BaseNode` 实例。
- `next_node` 必须是 `BaseNode` 或 `None`。

**示例错误**：
```python
>>> BatchNode(nodes=["string"])  # 无效
ValueError: nodes[0] 必须是 BaseNode 实例，得到的是 str
```

## 另请参阅

- [多智能体编排指南](../guides/multi-agent-orchestration.md)
- [并行公司群 (Corporate Swarm) 示例](https://github.com/snath-ai/lar/blob/main/examples/scale/4_parallel_corporate_swarm.py)
- [RouterNode API](routernode.md) —— 用于顺序条件逻辑
