# TopologyValidator API 参考

## 概述

`TopologyValidator` 为动态生成的图提供**静态分析和安全强制执行**。它能防止自修改智能体创建不安全的拓扑结构，如死循环、未经授权的工具调用或格式错误的结构。

## 类签名

```python
class TopologyValidator:
    def __init__(self, allowed_tools: List[callable] = None)
```

## 参数说明

| 参数 | 类型 | 是否必填 | 描述 |
|-----------|------|----------|-------------|
| `allowed_tools` | `List[callable]` | 否 | 可在 `ToolNode` 实例中使用的 Python 函数白名单。如果为 `None`，则允许所有工具（不安全）。 |

## 方法

### `validate(graph_spec: Dict[str, Any]) -> None`

验证 JSON 图规范的安全性和正确性。

**异常**：
- `SecurityError`：如果图违反了安全政策。

**执行的检查**：
1. **循环检测**：确保图是 DAG（有向无环图）。
2. **工具白名单**：验证所有 `ToolNode` 函数均在允许列表中。
3. **结构完整性**：验证所有 `next_node` 引用均存在。
4. **类型安全**：确保节点类型有效（LLMNode、ToolNode 等）。

## 安全保障

### 1. 死循环预防

`TopologyValidator` 使用循环检测来确保没有任何执行路径会无限循环：

```python
validator = TopologyValidator()

# 这将引发 SecurityError
invalid_graph = {
    "nodes": {
        "node_1": {"next_node": "node_2"},
        "node_2": {"next_node": "node_1"}  # 发现循环！
    },
    "start_node": "node_1"
}

validator.validate(invalid_graph)  # ❌ SecurityError: 发现循环
```

### 2. 工具限制

仅能调用预先批准的工具：

```python
def safe_tool():
    return "安全操作"

def dangerous_tool():
    import os
    os.system("rm -rf /")  # 恶意操作！

# 创建带有白名单的验证器
validator = TopologyValidator(allowed_tools=[safe_tool])

# 这将通过验证
safe_graph = {
    "nodes": {
        "node_1": {
            "type": "ToolNode",
            "config": {"tool_name": "safe_tool"},
            "next_node": null
        }
    },
    "start_node": "node_1"
}
validator.validate(safe_graph)  # ✅ 通过

# 这将失败
malicious_graph = {
    "nodes": {
        "node_1": {
            "type": "ToolNode",
            "config": {"tool_name": "dangerous_tool"},
            "next_node": null
        }
    },
    "start_node": "node_1"
}
validator.validate(malicious_graph)  # ❌ SecurityError: 工具不在白名单中
```

### 3. 引用完整性

所有 `next_node` 引用必须指向已存在的节点：

```python
broken_graph = {
    "nodes": {
        "node_1": {"next_node": "node_999"}  # node_999 不存在！
    },
    "start_node": "node_1"
}

validator.validate(broken_graph)  # ❌ SecurityError: 无效引用
```

## 使用示例

### 基础验证

```python
from lar.dynamic import TopologyValidator, SecurityError

def approved_search(query):
    return f"{query} 的结果"

def approved_filter(results):
    return [r for r in results if "important" in r]

# 创建验证器
validator = TopologyValidator(allowed_tools=[approved_search, approved_filter])

# 由 LLM 生成的图
llm_generated_graph = {
    "nodes": {
        "search": {
            "type": "ToolNode",
            "config": {
                "tool_name": "approved_search",
                "input_keys": ["query"],
                "output_key": "raw_results"
            },
            "next_node": "filter"
        },
        "filter": {
            "type": "ToolNode",
            "config": {
                "tool_name": "approved_filter",
                "input_keys": ["raw_results"],
                "output_key": "filtered_results"
            },
            "next_node": None
        }
    },
    "start_node": "search"
}

try:
    validator.validate(llm_generated_graph)
    print("✅ 图可安全执行")
except SecurityError as e:
    print(f"❌ 验证失败：{e}")
```

### 与 DynamicNode 集成

```python
from lar import DynamicNode, TopologyValidator

# 定义安全工具
def fetch_wikipedia(topic):
    # 模拟 API 调用
    return f"{topic} 的维基百科摘要"

def summarize_text(text):
    # 文本处理
    return text[:100]

# 创建验证器
validator = TopologyValidator(allowed_tools=[fetch_wikipedia, summarize_text])

# 创建元认知节点
research_agent = DynamicNode(
    llm_model="gpt-4",
    prompt_template="""
    为课题设计研究图：{research_topic}

    可用工具：
    - fetch_wikipedia
    - summarize_text

    返回 JSON 图规范。
    """,
    validator=validator,  # 验证过程会自动发生
    context_keys=["research_topic"]
)
```

## 验证算法

### 循环检测（基于 DFS）

```python
def has_cycle(graph):
    visited = set()
    rec_stack = set()
    
    def dfs(node_id):
        if node_id in rec_stack:
            return True  # 发现循环
        if node_id in visited:
            return False
        
        visited.add(node_id)
        rec_stack.add(node_id)
        
        next_node = graph["nodes"][node_id].get("next_node")
        if next_node and dfs(next_node):
            return True
        
        rec_stack.remove(node_id)
        return False
    
    return dfs(graph["start_node"])
```

**复杂度**：O(V + E)，其中 V = 节点数，E = 边数。

## 安全最佳实践

### 1. **最小权限原则**

仅允许必需的最低限度工具集：

```python
# ❌ 过于宽松
validator = TopologyValidator(allowed_tools=None)  # 允许所有工具！

# ✅ 严格限制
validator = TopologyValidator(allowed_tools=[read_only_function])
```

### 2. **分层验证**

将 `TopologyValidator` 与其他检查相结合：

```python
class CustomValidator(TopologyValidator):
    def validate(self, graph_spec):
        # 调用父类验证
        super().validate(graph_spec)
        
        # 添加自定义检查
        if len(graph_spec["nodes"]) > 10:
            raise SecurityError("图规模过大（最多 10 个节点）")
        
        for node in graph_spec["nodes"].values():
            if node["type"] == "LLMNode":
                # 确保不使用昂贵的模型
                if "gpt-4" in node["config"].get("model_name", ""):
                    raise SecurityError("禁止使用 GPT-4（出于成本控制）")
```

### 3. **审计日志记录**

始终记录验证结果：

```python
try:
    validator.validate(graph_spec)
    logger.info(f"图验证成功：{graph_spec}")
except SecurityError as e:
    logger.error(f"验证失败：{e}，图规范：{graph_spec}")
    raise
```

## 常见验证错误

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `Cycle detected in graph topology` | 节点 A → 节点 B → 节点 A | 移除循环引用 |
| `Tool 'X' not in allowlist` | 使用了未经授权的函数 | 将工具加入 `allowed_tools` 或从图中移除 |
| `start_node 'X' not found in nodes` | 入口点无效 | 确保 `start_node` 在 `nodes` 字典中存在 |
| `Invalid node type: 'X'` | 使用了不支持的节点类 | 仅使用：LLMNode, ToolNode, RouterNode |

## 合规性

### 欧盟 AI 法案第 13 条（透明度）

`TopologyValidator` 通过以下方式助力合规：
- 提供**确定性的验证**（非 AI，基于规则）。
- 记录**确切的拒绝理由**。
- 创建关于被限制行为的**审计轨迹**。

### OWASP 建议

遵循 OWASP 安全编码实践：
- ✅ 输入验证（图规范）。
- ✅ 白名单机制（工具）。
- ✅ 故障安全默认设置（拒绝无效图）。
- ✅ 纵深防御（多重检查）。

## 性能表现

- **验证时间**：O(V + E) - 与图规模呈线性关系。
- **内存占用**：O(V) 用于访问追踪。
- **推荐最大节点数**：100（出于性能考虑，而非安全性）。

对于超大规模图（>100 节点），请考虑：
1. 缓存验证结果。
2. 增量验证。
3. 简化图结构。

## 另请参阅

- [DynamicNode API](dynamicnode_CN.md) —— 使用了 TopologyValidator
- [元认知指南](../core-concepts/9-metacognition_CN.md) —— 自修改智能体
- [红队测试](../case-studies/red-teaming_CN.md) —— 安全测试
- [安全防火墙示例](https://github.com/snath-ai/lar/blob/main/examples/compliance/2_security_firewall.py)
