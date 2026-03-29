# DynamicNode API 参考

## 概述

`DynamicNode` 赋能**元认知智能体 (Metacognitive Agents)**，使其能够在运行时修改自身的行为。它要求 LLM 生成一个 JSON 格式的图规范，验证其安全性，然后执行生成的子图。

> [!CAUTION]
> **自修改代码具有风险**：`DynamicNode` 引入了固有的安全风险。请务必配合 `TopologyValidator` 使用，以强制执行安全政策。

## 类签名

```python
class DynamicNode(BaseNode):
    def __init__(
        self,
        llm_model: str,
        prompt_template: str,
        validator: TopologyValidator,
        next_node: BaseNode = None,
        context_keys: List[str] = [],
        system_instruction: str = None
    )
```

## 参数说明

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----------|-------------|
| `llm_model` | `str` | 是 | 用于生成图 JSON 的模型（例如 "gpt-4", "gemini-pro"） |
| `prompt_template` | `str` | 是 | 要求 LLM 设计图的提示词。必须包含 Schema（模式）说明。 |
| `validator` | `TopologyValidator` | 是 | 安全验证器，用于强制执行安全政策（循环检测、工具白名单） |
| `next_node` | `BaseNode` | 否 | 动态子图完成后执行的节点 |
| `context_keys` | `List[str]` | 否 | 设计图时要包含在 LLM 上下文中的状态键 |
| `system_instruction` | `str` | 否 | 给 LLM 的系统指令 |

## 行为

### 执行流程

1. **生成图 JSON**：配合 `prompt_template` 和 `context_keys` 调用 LLM。
2. **解析 JSON**：从 LLM 的响应中提取图规范。
3. **验证**：运行 `TopologyValidator` 以检查是否存在循环、未经授权的工具等。
4. **构建**：根据 JSON 规范实例化节点。
5. **执行**：运行生成的子图。
6. **继续**：继续运行 `next_node`。

### JSON 图 Schema

LLM 必须生成符合以下格式的 JSON：

```json
{
  "nodes": {
    "node_1": {
      "type": "LLMNode",
      "config": {
        "model_name": "gpt-4",
        "prompt_template": "分析：{input}",
        "output_key": "analysis"
      },
      "next_node": "node_2"
    },
    "node_2": {
      "type": "ToolNode",
      "config": {
        "tool_name": "approved_tool",  // 必须在验证器白名单中
        "input_keys": ["analysis"],
        "output_key": "result"
      },
      "next_node": null
    }
  },
  "start_node": "node_1"
}
```

## 安全与验证

### 为什么验证至关重要

自修改代码可能会：
- 创建死循环
- 调用黑名单 API
- 泄露数据
- 执行任意代码

### TopologyValidator 提供的保护

1. **循环检测**：确保图是一个 DAG（有向无环图），防止死循环。
2. **工具白名单**：仅允许预先批准的 `ToolNode` 函数。
3. **结构完整性**：验证所有 `next_node` 引用确实存在。

详见 [`TopologyValidator` API](topologyvalidator.md)。

## 使用示例

### 1. 适应性深度（可变复杂度）

```python
from lar import DynamicNode, TopologyValidator, GraphExecutor

# 定义允许的工具
def simple_search(query): 
    return f"{query} 的快速结果"

def deep_research(query):
    return f"{query} 的详细分析"

# 创建验证器
validator = TopologyValidator(allowed_tools=[simple_search, deep_research])

# 创建元认知节点
adapter = DynamicNode(
    llm_model="gpt-4",
    prompt_template="""
    根据查询复杂度，设计一个图：
    - 简单查询：使用 simple_search
    - 复杂查询：使用 deep_research

    查询：{user_query}

    输出包含 'nodes' 和 'start_node' 的 JSON 图规范。
    """,
    validator=validator,
    context_keys=["user_query"]
)

executor = GraphExecutor()
result = list(executor.run_step_by_step(adapter, {"user_query": "2+2 等于多少？"}))
```

**发生了什么**：
- 对于 "2+2 等于多少？" → LLM 生成一个包含 `simple_search` 的单节点图。
- 对于 "解释量子纠缠" → LLM 生成一个包含 `deep_research` + 综合分析的 3 节点图。

### 2. 工具发明家（运行时代码生成）

```python
def execute_generated_function(code: str):
    """执行 LLM 生成的 Python 代码（危险 - 请谨慎使用）"""
    exec(code)  # 需要极高的信任度

validator = TopologyValidator(allowed_tools=[execute_generated_function])

inventor = DynamicNode(
    llm_model="gpt-4",
    prompt_template="""
    用户需要一个工具来：{task_description}

    为此功能生成 Python 代码，然后创建一个 ToolNode 图来执行它。

    返回包含以下内容的 JSON：
    - 'code': Python 函数
    - 'nodes': 使用 execute_generated_function 的图规范
    """,
    validator=validator,
    context_keys=["task_description"]
)
```

> [!WARNING]
> **代码执行风险**：此模式会执行任意代码。仅在沙盒环境中或存在严格的人机回环（Human-in-the-loop）监督下使用。

### 3. 自愈（错误恢复）

```python
from lar import DynamicNode, TopologyValidator

# 允许错误修正工具
validator = TopologyValidator(allowed_tools=[retry_with_backoff, use_fallback_api])

healer = DynamicNode(
    llm_model="gpt-4",
    prompt_template="""
    发生错误：{last_error}

    使用允许的工具设计一个修复子图：
    - retry_with_backoff
    - use_fallback_api

    返回解决错误的 JSON 图。
    """,
    validator=validator,
    context_keys=["last_error"]
)
```

## 审计轨迹

`DynamicNode` 会在审计轨迹中记录**确切生成的 JSON**：

```json
{
  "step": 5,
  "node": "DynamicNode",
  "state_diff": {
    "added": {
      "_generated_graph_spec": {...},  // 记录完整 JSON
      "_dynamic_result": "Success"
    }
  }
}
```

这确保了**完全的合规可审计性** —— 您始终可以查看智能体决定做了什么。

## 最佳实践

### ✅ 推荐做法

1. **务必使用 TopologyValidator** —— 绝无例外。
2. **限制工具白名单** —— 遵循最小权限原则。
3. **记录生成的图** —— 用于调试和合规。
4. **使用系统指令** —— 引导 LLM 的设计选择。
5. **加入人工监督** —— 针对高风险决策。

### ❌ 严禁做法

1. **允许不受限制的 `exec()`** —— 极大的安全风险。
2. **跳过验证** —— 会导致注入攻击。
3. **未经测试即在生产环境使用** —— 应先测试生成的图。
4. **在验证器中允许网络工具** —— 存在数据外泄风险。

## 真实案例

请查看 [`examples/metacognition/`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/) 目录：

| 示例 | 能力 |
|---------|------------|
| [`1_dynamic_depth.py`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/1_dynamic_depth.py) | 适应性复杂度（1 节点 vs N 节点） |
| [`2_tool_inventor.py`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/2_tool_inventor.py) | 自主编程（在运行时编写工具） |
| [`3_self_healing.py`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/3_self_healing.py) | 错误恢复（注入修复子图） |
| [`4_adaptive_deep_dive.py`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/4_adaptive_deep_dive.py) | 递归研究（生成子智能体） |
| [`5_expert_summoner.py`](https://github.com/snath-ai/lar/blob/main/examples/metacognition/5_expert_summoner.py) | 动态 Persona 实例化 |

## 合规性

### 欧盟 AI 法案第 13 条（透明度）

`DynamicNode` 通过以下方式满足透明度要求：
- 记录确切生成的图 JSON。
- 记录调用了哪些工具。
- 提供确定性的验证结果。

### 安全审计

每一次 `DynamicNode` 的执行都会创建包含以下内容的审计条目：
- `input`：上下文键和提示词。
- `output`：生成的 JSON 图。
- `validation_result`：通过/失败及其原因。

## 另请参阅

- [TopologyValidator API](topologyvalidator.md) —— 安全执行
- [元认知指南](../core-concepts/9-metacognition.md) —— 深入了解自修改智能体
- [红队测试](../case-studies/red-teaming.md) —— 动态图安全测试
