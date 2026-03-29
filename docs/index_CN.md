# **构建可审计 AI 智能体所需的一切**

**Lár**（在爱尔兰语中意为“核心”或“中心”）是**确定性、可审计且支持物理隔离 (Air-Gap)** 的 AI 智能体的开源标准，由 **LiteLLM** 提供动力。

它是一个 **“运行即定义”(define-by-run)** 的框架，充当智能体的 **“飞行记录仪”**，为每一个步骤创建完整的审计轨迹。

!!! info "不是包装器"
    **Lár 不是一个包装器。**
    它是一个独立、从零开始构建的引擎，专为可靠性而设计。它没有包装 LangChain、OpenAI Swarm 或任何其他库。它是纯粹的、低依赖的 Python 代码，针对“图即代码”(Code-as-Graph) 的执行进行了优化。

## “黑盒”问题

你是一名开发者，正在发布一个**任务关键型 AI 智能体**。它在你的机器上运行良好，但在生产环境中却失败了。
你不知道**为什么**失败、是在**哪里**失败，或者花费了**多少成本**。你得到的只是来自某个“魔法”框架的 100 行堆栈跟踪。

## “玻盒”解决方案

**Lár 消除了这种魔法。**

它是一个简单的引擎，**一次运行一个节点**，并将每一个步骤记录到取证级的**飞行记录仪**中。

这意味着你可以获得：
1.  **即时调试**：查看导致崩溃的确切节点和错误。
2.  **免费审计**：内置默认提供每一个决策和 Token 成本的完整历史记录。
3.  **完全控制**：构建确定性的“流水线”，而不是混乱的聊天室。

> *“这证明了对于一个没有随机性或外部模型多变性的图，Lár 的执行是确定性的，并能产生完全相同的状态轨迹。”*

*停止猜测。开始构建你可以信赖的智能体。*

## v1.4.1 (2026年2月) 有什么新变化？

**推理模型（系统 2 思维）现已成为一等公民。**
Lár 原生支持 **DeepSeek R1**、**OpenAI o1** 和 **Liquid Thinking**。

*   **审计逻辑**：将“隐藏”的推理轨迹捕捉到元数据中。
*   **整洁状态**：仅将最终答案传递给下游节点。
*   **强健性**：可处理来自本地模型的不规范标签。

[阅读推理模型指南](core-concepts/5-reasoning-models.md)


## 演示与示例

通过我们准备好的演示项目来学习构建：

*   **[DMN: 核心展示](https://github.com/snath-ai/DMN)**：一个会睡觉、做梦和记忆的认知架构。
*   **[Lar-JEPA: 世界模型编排器](https://github.com/snath-ai/Lar-JEPA)**：一个后 LLM 时代的概念性测试平台，证明 Lár 可以安全地路由来自预测性世界模型（Predictive World Models）的抽象潜状态。
*   **[RAG 智能体演示](https://github.com/snath-ai/rag-demo)**：一个带有本地向量搜索的具体自愈能力的 RAG 智能体。
*   **[客户支持群 (Swarm)](https://github.com/snath-ai/customer-support-demo)**：一种多智能体编排模式。
*   **[模式库](core-concepts/4-core-patterns.md)**：包含 21 种以上强健的工程模式（RAG、Swarms、安全等）。

## 赋能你的 IDE (Cursor / Windsurf)

通过以下 **2 步工作流**，让你的 IDE 成为专家级的 Lár 架构师：

1.  **参考规则**：在聊天中输入 `@lar/IDE_MASTER_PROMPT.md`。这将加载严格的模型编写规则。
2.  **使用模板**：使用你的智能体需求填写 `@lar/IDE_PROMPT_TEMPLATE.md`。

[阅读完整指南](ide_setup.md)

## 准备好投入生产了吗？

Lár 被设计为以标准 Python 库的形式部署。
阅读我们的 **[部署指南](guides/deployment.md)**，了解如何将你的图包装在 **FastAPI** 中并部署到 AWS/Heroku。

3 分钟快速上手 [https://docs.snath.ai/getting-started/](https://docs.snath.ai/getting-started/)

## 作者
**[Lár](https://github.com/snath-ai/lar)** 由 **[Aadithya Vishnu Sajeev](https://github.com/axdithyaxo)** 创建。
