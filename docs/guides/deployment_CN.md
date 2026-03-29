# 部署 Lár 智能体（生产指南）

最常见的问题之一是：*“我该如何部署它？”*

Lár 是一个**引擎**（类似于 PyTorch 或 Flask），而不是一个**应用程序**（如 ChatGPT）。
要部署它，您只需将其包装在标准的 Python Web 服务器中即可。

---

## 1. 策略：“无头”引擎

您应该将智能体作为**无状态 REST API** 运行。
*   **输入**：JSON（用户任务）
*   **输出**：JSON（最终状态）
*   **审计日志**：将 `result_log` 保存到数据库（如 Postgres/Mongo）中以备合规检查。

---

## 2. 使用 FastAPI（推荐）

在 `examples/` 文件夹深处有一个 **示例 4**。它是运行在 FastAPI 上的 Lár 智能体的完整、可直接分发的实现。

**[`examples/basic/4_fastapi_server.py`](https://github.com/snath-ai/lar/blob/main/examples/basic/4_fastapi_server.py)**

### 快速开始

1.  **安装 FastAPI**：
    ```bash
    pip install fastapi uvicorn
    ```

2.  **粘贴此代码**：
    ```python
    import uvicorn
    from fastapi import FastAPI
    from lar import LLMNode, GraphExecutor
    
    app = FastAPI()
    executor = GraphExecutor()
    
    # 定义一个简单的智能体
    agent = LLMNode(
        model_name="gpt-4o", 
        prompt_template="回复：{task}", 
        output_key="response"
    )
    
    @app.post("/run")
    def run_agent(task: str):
        # 运行标准 Lár 执行流程
        result = list(executor.run_step_by_step(agent, {"task": task}))
        return result[-1]["state_snapshot"]
        
    if __name__ == "__main__":
        uvicorn.run(app, port=8000)
    ```

3.  **部署**：
    您可以像部署其他 Python 应用一样，在 **Heroku**、**AWS Lambda**、**Railway** 或 **Render** 上运行此脚本。

---

## 3. 为什么不使用 LangServe？

像 LangChain 这样的框架会强迫您使用它们私有的“服务”层（`LangServe`），这通常会将您锁定在它们的生态系统中。

通过使用标准的 **FastAPI**，您实质上“拥有”了部署方案。您可以：

*   添加自定义身份验证（OAuth2, JWT）。
*   按 IP 对用户进行速率限制。
*   将日志保存到您自己的 SQL 数据库中。
*   与现有的 Stripe 支付流程集成。
