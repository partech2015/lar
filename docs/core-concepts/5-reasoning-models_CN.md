# 推理模型 (系统 2)

**v1.4.1 新特性**

Lár 将“推理轨迹”（也称为思维链或系统 2 思维）视为一等公民。

Lár 不会使用 `<think>` 标签或内部独白来干扰您的最终答案，而是会自动提取此思考过程，将其保存到隐藏的元数据字段中以供审计，并仅将整洁的答案交付给您的下游节点。

## 支持的模型

Lár 支持所有主要“思考”模型的推理捕获：

| 供应商 | 模型 | 方法 |
| :--- | :--- | :--- |
| **DeepSeek** | `deepseek-reasoner` (R1) | API 元数据 (`reasoning_content`) |
| **OpenAI** | `o1-preview`, `o1-mini` | API 元数据 (`reasoning_content`) |
| **Ollama** | `deepseek-r1`, `liquid-thinking` | 正则表达式回退 (`<think>` 标签) |
| **Liquid** | `liquid-thinking` | 正则表达式回退 (`<think>` 标签) |

## 工作原理

当 `LLMNode` 执行时，它会执行两步提取：

1.  **API 检查**：首先检查 API 响应是否包含特定的 `reasoning_content` 字段（OpenAI/DeepSeek API 的标准字段）。
2.  **正则回退**：如果未找到，则扫描文本中是否存在类似 `<think>...</think>` 的 XML 标签。
    *   提取标签内部的内容。
    *   从 `output_key`（即状态）中**移除**这些标签及其内容。
    *   将提取的内容保存到 `run_metadata` 中。

### 强健性 (v1.4.1)
正则表达式引擎对较小的本地模型中常见的格式错误输出具有强健性：
*   **缺少闭合标签**：捕获 `<think>` 之后的所有内容（例如，如果模型达到了 Token 限制）。
*   **缺少开启标签**：捕获 `</think>` 之前的所有内容（例如，如果模型开始了“静默”思考）。

## 用法

您不需要进行特殊配置。只需照常使用 `LLMNode` 即可。

### 1. 使用 DeepSeek R1 (Ollama)

```python
from lar import LLMNode

node = LLMNode(
    model_name="ollama/deepseek-r1:7b",
    prompt_template="解开这个谜题：{riddle}",
    output_key="answer"
)
```

**结果如下：**

*   **状态 (`state['answer']`)**：
    ```text
    答案是海绵。
    ```
*   **审计日志 (`run_metadata`)**：
    ```json
    {
      "model": "ollama/deepseek-r1:7b",
      "total_tokens": 150,
      "reasoning_content": "首先我需要分析属性... 它能吸水... 它有孔..."
    }
    ```

### 2. 使用 OpenAI o1

```python
node = LLMNode(
    model_name="openai/o1-mini",
    prompt_template="为此任务编写一个安全的 Python 函数：{task}",
    output_key="code"
)
```

## 最佳实践

1.  **审计日志**：始终检查 `lar_logs/`（或您的自定义日志目录）以查看推理过程。这是它被存储的唯一地方。
2.  **提示词编写**：对于本地模型（如 Liquid Thinking），如果模型不配合，您可能需要在系统提示词中显式要求使用标签：
    ```python
    system_instruction="你是一个推理引擎。你必须将你的内心独白封装在 <think> 标签中。"
    ```
