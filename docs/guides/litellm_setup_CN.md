# 通用模型支持 (LiteLLM)

Lár 构建在 **LiteLLM** 之上，这意味着它开箱即支持 **100 多个 LLM 供应商**。

您无需安装独立的 SDK（如 `openai`、`anthropic`、`google-generativeai`）。Lár 会为您管理统一的接口。

---

## 1. 快速开始：`.env` 文件

要切换供应商，您只需要：
1.  为该供应商设置正确的**环境变量**。
2.  在您的 `LLMNode` 中使用正确的**模型字符串**。

在项目根目录下创建一个 `.env` 文件：

```bash
# --- OpenAI ---
OPENAI_API_KEY="sk-..."

# --- Anthropic ---
ANTHROPIC_API_KEY="sk-ant-..."

# --- Google Gemini ---
GEMINI_API_KEY="AIza..."

# --- AWS Bedrock ---
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="abc..."
AWS_REGION_NAME="us-east-1"

# --- Azure OpenAI ---
AZURE_API_KEY="..."
AZURE_API_BASE="https://my-resource.openai.azure.com/"
AZURE_API_VERSION="2023-05-15"
```

---

## 2. 受支持的模型字符串（速查表）

将这些字符串传递给 `LLMNode` 的 `model_name` 参数。

| 供应商 | 模型字符串 | 备注 |
| :--- | :--- | :--- |
| **OpenAI** | `gpt-4o` | 标准。 |
| **OpenAI** | `gpt-3.5-turbo` | |
| **Anthropic** | `claude-3-opus-20240229` | |
| **Anthropic** | `claude-3-5-sonnet-20240620` | |
| **Google** | `gemini/gemini-1.5-pro` | 前缀需带 `gemini/`。 |
| **Google** | `gemini/gemini-1.5-flash` | |
| **Ollama** | `ollama/phi4` | 前缀需带 `ollama/`。 |
| **Ollama** | `ollama/llama3` | |
| **Bedrock** | `bedrock/anthropic.claude-3-sonnet-20240229-v1:0` | 前缀需带 `bedrock/`。 |
| **Azure** | `azure/gpt-4-turbo` | 需要设置 `AZURE_API_BASE`。 |
| **Groq** | `groq/llama3-70b-8192` | 速度极快。 |

---

## 3. 如何使用本地模型

Lár 将本地模型视为一等公民。

### 选项 A：Ollama（最简单）
1.  **安装 Ollama**：访问 [ollama.com](https://ollama.com)。
2.  **获取模型**：`ollama pull phi4`。
3.  **运行**：确保应用程序正在运行（它监听 11434 端口）。
4.  **代码实现**：

```python
node = LLMNode(
    model_name="ollama/phi4", 
    prompt_template="分析：{task}",
    output_key="result"
)
```

### 选项 B：Llama.cpp / LM Studio / LocalAI
大多数本地服务器提供“OpenAI 兼容端点”。您可以使用 `api_base` 将 Lár 指向此端点。

1.  **启动服务器**：例如 `python -m llama_cpp.server --model model.gguf --port 8080`。
2.  **代码实现**：使用 `openai/custom` 前缀来强制使用 OpenAI 协议。

```python
node = LLMNode(
    model_name="openai/my-local-model",
    prompt_template="...",
    output_key="res",
    generation_config={
        "api_base": "http://localhost:8080/v1",  # 本地服务器的 URL
        "api_key": "sk-local-key"                # 某些服务器需要设置（可以使用虚假密钥）
    }
)
```

---

## 4. 高级配置

您可以使用 `generation_config` 字典来调整模型参数。这些参数将直接传递给供应商的 API。

```python
node = LLMNode(
    model_name="gpt-4o",
    prompt_template="...",
    output_key="res",
    generation_config={
        "temperature": 0.2,       # 越低 = 越确定, 越高 = 越有创意
        "max_tokens": 1000,       # 限制输出长度
        "top_p": 0.9,             # 核采样 (Nucleus sampling)
        "frequency_penalty": 0.0, # 减少重复
        "stop": ["User:", "\n"]   # 停止序列
    }
)
```

---

## 5. 故障排除 / 常见问题

#### “ProviderNotFoundError: Model not found”（未找到模型）
*   **检查前缀**：是否漏掉了 `gemini/` 或 `ollama/`？
*   **检查 LiteLLM**：运行 `pip install -U litellm` 以获取最新的模型列表。

#### “AuthenticationError”（身份验证错误）
*   **检查 .env**：确保在脚本**头部**调用了 `load_dotenv()`。
*   **检查密钥名称**：LiteLLM 期望特定的名称（例如 `ANTHROPIC_API_KEY`，而不是 `CLAUDE_KEY`）。

#### “我想查看原始 API 请求”
您可以开启详细日志，以调试具体发送给 LLM 的内容。

```python
import os
os.environ["LITELLM_LOG"] = "DEBUG"
```
