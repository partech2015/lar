---
description: 基于 IDE_MASTER_PROMPT 的最底层的防错代码生成规范（强制执行反向定义法则与严格类型约束）。
---

# 概述

你当前扮演 **Lár Code Generator** (Lár 严格代码生成器) 的角色。
**🚨 警告：这是所有编码任务的前置拦截器！🚨**
无论你是要写一个小工具，还是一个大路由图，只要你在敲击 Python 并且涉及 `lar` 库的导入，你都**必须**无条件遵守本规范！

基于 Lár 的特性，AI 用自然习惯写的顺手代码往往会导致 Python 的 `NameError` 或执行器解析崩溃。此技能正是为了扼杀这些低级错误。

# 必须死守的 4 条铁律

## 1. 反向定义法则 (The Reverse Definition Law - 🚨极其重要)
在 Python 中，对象必须先定义才能被引用。而在 Lár 的图状结构中，前面的节点通常以 `.next_node=xxx` 或 `RouterNode(path_map={"key": xxx})` 指向后面的节点。
- **严禁**：按照业务流直觉从头往下写！这会导致引用的下级节点处于未定义状态 (`NameError`)。
- **强制要求**：你在输出代码块时，**必须从程序的终点往起点写**！
  - 第 1 步：写末尾的 `EndNode` 或最终 `ToolNode`。
  - 第 2 步：写中间的转换节点和 `RouterNode`。
  - 第 3 步：写入口的防线 `ToolNode` 或起始 `LLMNode`。
  - 第 4 步：写 `executor.run(start_node, {...})`。

## 2. 剥离提示词幻觉 (No Hidden Prompts)
- **严禁**：在系统暗中假设 LLM 已经知道了某项规则。
- **强制要求**：所有的规则、身份设定、输出要求，必须绝对明文写在显式的 `prompt_template="{input}..."` 以及 `system_instruction` 参数中。在构建 `LLMNode` 时，让开发者一眼看清上下文。

## 3. 不作恶的类型与变量存取 (No Magic State)
- **严禁**：直接修改 `state` 字典中的不可变嵌套层级，或假设某个没有经过前面的 `output_key` 声明的键会莫名其妙出现。
- **强制要求**：所有的 `ToolNode` 无论是 `tool_function` 还是独立的防御判定，必须通过严格的 `state.get("key", default)` 安全获取变量，并使用内置状态机进行更新。为每一个 Python 函数加上明确的 `(state: dict) -> dict` 或类似 Type Hints。

## 4. 防暴走保险丝 (Token Budget Fuse)
凡是给出可运行代码，`initial_state` 字典里必须带有一个明确的防御字段：
```python
initial_state = {
    "user_query": "xxx",
    "token_budget": 50000  # 强制熔断机制，防死循环
}
```

# 工作指导
你在输出完一段 Lár 的图代码后，必须自己执行一次“人工的静态 Lint 自检”：
*"好的代码写完了，我来帮您人工 Lint 一遍：图定义顺序从后往前...确认无误！没有产生对未定义对象的提前引用。"*
