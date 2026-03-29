# 快速上手

## 3 分钟构建一个生产就绪的“主规划器”

本快速入门指南将帮助你构建第一个**可审计智能体 (Auditable Agent)**。与普通的聊天机器人不同，该智能体是一个**确定性工作流**：它接受任务、进行评估，然后将其路由到确切的专家节点。
由于它是基于 Lár 构建的，因此默认会生成一份**符合 21 CFR Part 11 标准的审计轨迹**。

---

### 1. 优化你的 IDE（智能体工作流）

**正在使用 Cursor、Windsurf 或 Antigravity 吗？**
Lár 被设计为由 AI 编写。

1.  **打开仓库**：在 IDE 中打开 `lar` 文件夹。
2.  **提问**： “构建一个可以检查股票的 Lár 智能体。”
3.  **交互模式**：IDE 要么会为你**起草蓝图**，要么会要求你提供 `IDE_PROMPT_TEMPLATE.md`。

*如果 IDE 出现幻觉，告诉它：*
> “先阅读 `lar/IDE_MASTER_PROMPT.md` 和 `lar/examples/`。”

### 2. 安装与项目脚手架（v1.4.0 新特性）

你可以直接从 PyPI 安装 Lár 核心引擎和新的 CLI：

```bash
pip install lar-engine
```

然后，立即生成一个新的智能体项目：

```bash
lar new agent my-agent
cd my-agent
poetry install
```

这将创建一个包含 `pyproject.toml`、`.env` 和模板智能体的生产级文件夹结构。

### 3. 设置环境变量

`Lár` 使用统一的适配器 `(LiteLLM)`。根据你运行的模型，你必须在 `.env` 文件中设置相应的 API 密钥：

创建一个 `.env` 文件：

```bash
# 运行 Gemini 模型所需：
GEMINI_API_KEY="你的_GEMINI_密钥" 
# 运行 OpenAI 模型（如 gpt-4o）所需：
OPENAI_API_KEY="你的_OPENAI_密钥"
# 运行 Anthropic 模型（如 Claude）所需：
ANTHROPIC_API_KEY="你的_ANTHROPIC_密钥"
```

### 4. 万能模型支持（由 LiteLLM 驱动）

为了切换供应商而重构代码已成为过去。Lár 构建于 **LiteLLM** 之上，让你能够即时访问 100 多个供应商（OpenAI、Anthropic、VertexAI、Bedrock 等）以及本地模型。

切换仅需更改**一个字符串**。

**云端 (OpenAI):**
```python
node = LLMNode(model_name="gpt-4o", ...)
```

**本地 (Ollama):**
```python
# 只需更改字符串！无需导入，无需重构。
node = LLMNode(model_name="ollama/phi4:latest", ...)
```

**本地 (Llama.cpp / vLLM):**
```python
# 使用任何通用的 OpenAI 端点
node = LLMNode(
    model_name="openai/custom", 
    generation_config={"api_base": "http://localhost:8080/v1"}
)
```

### 5. 创建你的第一个“玻盒”智能体

现在，构建一个简单的“主规划器”智能体，它接受用户的任务，进行评估，并将其路由到确切的专家。

## 后续步骤：投入生产

一旦你的智能体在本地运行良好，你会希望将其部署为 API。
查看我们的 **[部署指南](guides/deployment.md)**，了解如何在 5 分钟内将你的智能体包装在 **FastAPI** 服务器中。

[查看部署指南 →](guides/deployment.md)

```python
import os
from lar import *
from lar.utils import compute_state_diff
from dotenv import load_dotenv
# 加载 .env 文件
load_dotenv()

# 1. 为我们的路由器定义“选择”逻辑
def plan_router_function(state: GraphState) -> str:
    """读取状态中的 'plan' 并返回路由键。"""
    plan = state.get("plan", "").strip().upper()
    
    if "CODE" in plan:
        return "CODE_PATH"
    else:
        return "TEXT_PATH"

# 2. 定义智能体的节点（积木）
# 我们采取从尾到头的构建方式。

# --- 结束节点（目的地） ---
success_node = AddValueNode(
    key="final_status", 
    value="SUCCESS", 
    next_node=None # 'None' 表示图停止运行
)

chatbot_node = LLMNode(
    model_name="gemini/gemini-2.0-flash",
    prompt_template="你是一个得力的助手。回答用户的任务：{task}",
    output_key="final_response",
    next_node=success_node # 回答后，转到成功节点
)

code_writer_node = LLMNode(
    model_name="gemini/gemini-2.0-flash",
    prompt_template="为该任务编写一个 Python 函数：{task}",
    output_key="code_string",
    next_node=success_node 
)

# --- 2. 定义“选择”（路由器） ---
master_router_node = RouterNode(
    decision_function=plan_router_function,
    path_map={
        "CODE_PATH": code_writer_node,
        "TEXT_PATH": chatbot_node
    },
    default_node=chatbot_node # 默认仅进行聊天
)

# --- 3. 定义“起点”（规划器） ---
planner_node = LLMNode(
    model_name="gemini/gemini-2.0-flash",
    prompt_template="""
    分析该任务："{task}"
    它需要编写代码还是仅需文本回答？
    仅回答单词 "CODE" 或 "TEXT"。
    """,
    output_key="plan",
    next_node=master_router_node # 规划后，转到路由器
)

# --- 4. 运行智能体 ---
executor = GraphExecutor()
initial_state = {"task": "法国的首都是哪里？"}

# 执行器运行图并返回完整的日志
result_log = list(executor.run_step_by_step(
    start_node=planner_node, 
    initial_state=initial_state
))

# --- 5. 检查“玻盒” ---

print("--- 智能体运行结束！ ---")

# 重构最终状态
import json
from lar.state import apply_diff
final_state = initial_state
for step in result_log:
    final_state = apply_diff(final_state, step["state_diff"])

print(f"\n最终回答: {final_state.get('final_response')}")
print("\n--- 完整审计日志（“玻盒”） ---")
print(json.dumps(result_log, indent=2, ensure_ascii=False))
```

### 输出结果（你的取证飞行记录仪）

运行之后，你不只是得到了一个答案，还获得了一个**合规资产**。
这份日志是智能体每一步具体操作的证据。

```json
[
  {
    "step": 0,
    "node": "LLMNode",
    "state_before": {
      "task": "法国的首都是哪里？"
    },
    "state_diff": {
      "added": {
        "plan": "TEXT"
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {
      "prompt_tokens": 42,
      "output_tokens": 1,
      "total_tokens": 43
    },
    "outcome": "success"
  },
  {
    "step": 1,
    "node": "RouterNode",
    "state_before": {
      "task": "法国的首都是哪里？",
      "plan": "TEXT"
    },
    "state_diff": {
      "added": {},
      "removed": {},
      "modified": {}
    },
    "run_metadata": {},
    "outcome": "success"
  },
  {
    "step": 2,
    "node": "LLMNode",
    "state_before": {
      "task": "法国的首都是哪里？",
      "plan": "TEXT"
    },
    "state_diff": {
      "added": {
        "final_response": "法国的首都是巴黎。"
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {
      "prompt_tokens": 30,
      "output_tokens": 6,
      "total_tokens": 36
    },
    "outcome": "success"
  },
  {
    "step": 3,
    "node": "AddValueNode",
    "state_before": {
      "task": "法国的首都是哪里？",
      "plan": "TEXT",
      "final_response": "法国的首都是巴黎。"
    },
    "state_diff": {
      "added": {
        "final_status": "SUCCESS"
      },
      "removed": {},
      "modified": {}
    },
    "run_metadata": {},
    "outcome": "success"
  }
]
```

**就是这样。你刚刚构建了一个确定性智能体。**
