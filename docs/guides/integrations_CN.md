# 即时集成

> **“我们没有 500 多个陈旧的集成。但我们有无限个新鲜的集成。”**

传统框架通常自带大量的“包装器”库（例如 `LangChain.tools.HubSpotTool`）。这些通常存在以下问题：
1.  **过时**：API 的变化速度比框架维护者合并 PR 的速度还要快。
2.  **臃肿**：为了更新一条记录，你却必须导入一个庞大的库。
3.  **黑盒**：在崩溃之前，你根本不知道它是如何处理错误或重试的。

Lár 采取了不同的方法：**集成构建器 (Integration Builder)**。

## 工作流

与其等待我们为 `Stripe`、`Linear` 或 `Notion` 构建工具，不如在 30 秒内自行生成。

### 1. 集成提示词
我们提供了一个专门的提示词文件：`lar/IDE_MASTER_PROMPT.md`。
> “请先阅读 `lar/IDE_MASTER_PROMPT.md` 和 `lar/examples/`。”
这个文件会教你的 IDE（如 Cursor, Windsurf, Copilot）如何编写鲁棒的 Lár `ToolNode` 包装器的“黄金标准”。

### 2. 如何使用
1.  **打开你的 IDE**（推荐使用 Cursor 或 Windsurf）。
2.  **将 `lar/IDE_MASTER_PROMPT.md` 拖入**聊天上下文中。
3.  **提问**：*“帮我写一个搜索 Linear 任务（Tickets）的 Lár 工具。”*

### 3. 生成结果
你的 IDE 将读取提示词并生成一个**生产就绪**的文件，该文件：
1.  导入官方 SDK（例如 `linear-sdk`）。
2.  使用 `os.getenv` 进行身份验证。
3.  将逻辑封装在一个确定性函数中。
4.  返回一个扁平化的字典，以便与 `GraphState` 合并。
5.  将所有内容包装在一个 `ToolNode` 中。

**示例输出：**

```python
# 生成耗时 < 30s
from lar import ToolNode
import linear_sdk

def search_linear(state):
    # 身份验证
    # 搜索
    # 返回字典
    pass

linear_tool = ToolNode(
    tool_function=search_linear,
    input_keys=["query"],
    output_key="tickets",
    next_node=None
)
```

## 为什么这种方式更胜一筹
*   **完全掌控**：代码就在你的代码库中，可见且可编辑。
*   **始终保持最新**：你使用的是最新的官方 SDK，而不是变质的包装器。
*   **零冗余依赖**：你不需要安装 `lar-hubspot` 或 `lar-stripe`。只需安装 `lar` 和 `hubspot-client` 即可。

## 概念验证
请查看 [`examples/patterns/7_integration_test.py`](https://github.com/snath-ai/lar/blob/main/examples/patterns/7_integration_test.py)，了解为 CoinCap API 生成的集成示例。
