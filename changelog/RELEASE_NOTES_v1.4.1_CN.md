# Lár v1.4.1 发布说明
*(补丁版本 - 2026年2月15日)*

此补丁版本解决了审计日志中的一个关键错误，并正式支持推理模型（系统 2 思维）。

## 关键修复

### 1. 强健的审计日志（修复“日志丢失”问题）
**问题**：在 v1.4.0 中，如果脚本提前退出（例如，用户在循环中执行了 `break`、调用了 `sys.exit` 或程序崩溃），`GraphExecutor` 会跳过保存日志的步骤。
**修复**：将执行循环包装在 `try...finally` 块中。
**影响**：日志现在**总是会保存**到 `lar_logs/run_{uuid}.json`（或您的自定义 `log_dir`），确保审计跟踪的完整性。

## 新特性

### 1. 推理模型支持（系统 2 思维）
Lár 现在可以自动检测并捕获“推理轨迹”（Reasoning Traces，即思维链），在保持最终答案整洁的同时，保留思考过程以便审计。

**支持的模型**：
- **DeepSeek R1** (API 及蒸馏版/Ollama)
- **OpenAI o1** (Preview/Mini)
- **Liquid Thinking** (`ollama/liquid-thinking`)

**工作原理**：
1.  **元数据捕获**：如果 API 返回 `reasoning_content`（标准字段），它会保存到 `state["__last_run_metadata"]["reasoning_content"]`。
2.  **强健的正则回退**：如果模型输出原始的 `<think>...</think>` 标签（在本地模型中常见），Lár 会将其提取出来。
    - **强健性**：可处理缺失闭合标签（被切断的思考）和缺失起始标签（幻觉起始）的情况。
    - **整洁的状态**：主 `output_key`（例如 `state['answer']`）仅包含最终回答。推理过程被安全地存储在元数据中。

### 2. 新示例
添加了专用目录 `examples/reasoning_models/`，包含以下模式：
- `1_deepseek_r1.py`：DeepSeek R1 / 通用 Ollama。
- `2_openai_o1.py`：OpenAI o1 系列。
- `3_liquid_thinking.py`：Liquid Thinking（水平逻辑）。

## 内部变更
- `executor.py`：为日志持久化添加了 `finally` 块。
- `node.py`：增强了 `LLMNode`，使用强健的正则表达式进行标签提取。
- `tracker.py`：确认了按模型进行 Token 追踪的有效逻辑。

---
*Lár v1.4.1 是推荐更新的版本。它能确保您的日志安全，并让您的推理模型开箱即用。*
