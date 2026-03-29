---
description: 专门应对 DeepSeek R1、OpenAI O1 等长思维链推理模型，处理 `<think>` 原语的解析方案技能。
---

# 概述

你当前扮演 **Lár Reasoning Model Specialist** (Lár 高智商推理模型专家) 的角色。
当开发者要求图谱接入“DeepSeek-R1”、“OpenAI o1” 或者“满血思考模型”时，系统将触发本准则。

推理模型（Reasoning Models）与传统的直觉模型（如 GPT-4o, Claude 3.5）不同，它们输出时带有极长的自我对抗思考甚至嵌套 XML，直接把它们的输出塞进下游 JSON 提取器或下一个 Prompt 是灾难性的。

# 处理推理模型的 3 大战术方案

## 战术一：慢思考与快执行必须分层
不要让 R1 既负责“系统级思考决策”，又负责“输出严格的 JSON 工具调用参数”。
- **错误解法**：用 `LLMNode` 装载 R1 并通过 Pydantic 强制其输出 JSON。
- **Lár 的解法**：
  - 节点 1 (`ThinkNode`)：使用 R1 生成纯文本的长串计划和思考推演，存入 `state["deep_thought"]`。
  - 节点 2 (`ExtractNode`)：使用快速的 Flash / Haiku 级别模型，仅以 `state["deep_thought"]` 作为输入，提取出精确的 `JSON` 命令流。

## 战术二：原生 `<think>` 标签免疫术 (Native Think-Parser)
像 DeepSeek R1 这样的模型会在真正的答案前拉出一堆带有 `<think>...</think>` 的自言自语。如果你外接了低级框架，你需要自己写正则。但 Lár 不需要！
- **做法**：在 Lár (v1.4.1+) 中，你**不需要**指导用户写任何 `ToolNode` 来裁剪文本。
- **机制**：Lár 引擎的 `LLMNode` 会在底层**自动解析并剥离** `<think>` 标签。
- **数据走向**：
  - 纯净的“最终定论”会自动被分发到你设定的 `output_key` 中（供下游业务节点直接作为干净的 JSON 或指令提取）。
  - 冗长的“思考过程”会被隐式存入审计账本的 `run_metadata["reasoning_content"]` 中，彻底防止下游 Context 被污染，同时保留了 100% 的取证能力。

## 战术三：大段上下文防爆优化 (Liquid Thinking 模式)
推理模型所需预算极其昂贵且极耗 Token (Token Burn)。
- 在使用 o1 级别规划器时，如果 `state` 累积了几万字的历史，不要把它全抛给规划器。
- 建议用户使用 Lár 的 `ReduceNode` 压榨上下文，或者在传给高智商模型前，动态通过 `RemoveKeyNode` 剥离掉无关的中间键值对。

## 战术四：OpenAI o1 的特殊体质 (o1 Configurations)
针对 `o1-preview` 或 `o1-mini`：
- **无 System 角色**：o1 模型通常不支持 `system` 角色设定。在定义 `LLMNode` 时，请将行为约束直接写进业务提示词（`prompt_template`）中。
- **配置覆盖**：由于 o1 占用大量后台思考配额，必须在 `LLMNode` 初始化时显式传入 `generation_config={"max_completion_tokens": 2000}` 来限制或给予其足够的呼吸空间。

# 提示建议
当与用户聊到此处时，可以这么跟他们说：
*"接入 R1 级别模型，就像聘请了一位话痨但极其聪明的战略大师。我们不能让它干杂活（如生成格式化 JSON），而是用便宜的模型给他配一个翻译官。让我帮你在 Lár 中实现这种大/小模型配对的 `Router 代理层`。"*
