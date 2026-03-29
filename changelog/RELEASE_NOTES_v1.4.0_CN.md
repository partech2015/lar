# Lár v1.4.0 发布说明

**“打磨更新”**

此版本将 Lár 从一个强大的引擎转变为一款精致的产品。它引入了用于快速脚手架搭建的 CLI、用于简化代码的“低代码”装饰器，以及关键的开发者体验 (DX) 改进。

## 🚀 新特性

### 1. Lár CLI (`lar`)
不再需要手动创建文件。几秒钟内即可搭建立产就绪的智能体项目。
```bash
pip install lar-engine
lar new agent my-bot
```
这将生成包含 `pyproject.toml`、`.env` 和 `agent.py` 的完整项目结构。

### 2. “低代码”节点 (`@node`)
将节点定义为简单的 Python 函数。
```python
from lar import node

@node(output_key="summary")
def summarize(state):
    return llm.generate(state["text"])
```

### 3. 状态的字典式访问
以自然的方式与 `GraphState` 交互。
```python
# 旧方式
val = state.get("key")
state.set("key", val)

# 新方式
val = state["key"]
state["key"] = val
```

## 🛠 改进与修复

- **强健的并发性**：修复了 `BatchNode` 在使用 `functools.partial` 或动态可调用对象（Callables）时崩溃的问题。日志记录现在对所有对象类型都是安全的。
- **标识解析**：PyPI 上的包名仍为 `lar-engine`，但 CLI 确保您的项目已平衡设置，可以直接 `import lar` 而不会产生混淆。

## 🔄 向后兼容性
**安全升级。** Lár v1.4.0 与 v1.3 的代码完全兼容。
- 现有的 `LLMNode` / 基于类的设置无需更改即可运行。
- 您可以在同一个图中混合使用“旧”风格和“新”风格。
- 参见 `examples/v1_4_showcase.py` 查看演示。

## 📦 安装
```bash
pip install lar-engine==1.4.0
```
