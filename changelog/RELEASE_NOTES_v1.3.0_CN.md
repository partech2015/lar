# Lár v1.3.0 发布说明

**“合规与架构更新”**

此版本专注于强化框架以满足企业和监管合规（如欧盟 AI 法案）要求，同时重构了核心执行引擎以更好地实现关注点分离。

## 关键特性

### 1. “人机回环”原语 (`HumanJuryNode`)
一种新的节点类型，可暂停执行以通过 CLI 请求显式的人工反馈。
- **原因**：直接满足欧盟 AI 法案第 14 条（“人类监督”）的要求。
- **如何使用**：
  ```python
  jury = HumanJuryNode(
      prompt="批准敏感操作？",
      choices=["approve", "reject"],
      output_key="approval_status"
  )
  ```

### 2. 静态安全分析 (`TopologyValidator`)
我们添加了 `TopologyValidator`（由 NetworkX 提供支持），用于在**动态图**执行*之前*对其运行全面的检查。
- **循环检测**：捕捉生成的子图中的死循环。
- **结构完整性**：验证 `next_node` 引用。
- **工具白名单**：对动态智能体可以访问的工具施加严格限制。

### 3. 核心重构：模块化可观测性
`GraphExecutor` 经过重构，将职责委托给专用组件，保持引擎轻量化。
- **`AuditLogger`**：集中管理审计跟踪日志和文件持久化。
- **`TokenTracker`**：精确汇总跨多个供应商和模型的 Token 使用情况。

## 使用更新

### 重大变更 (Breaking Changes)
- `GraphExecutor` 构造函数现在接受可选的 `logger` 和 `tracker` 实例用于依赖注入。
- **合规性**：随着日志中元数据精度的提高，“玻盒”现在变得更加透明。

### 如何使用（v1.3.0 新增）

#### 选项 1：自动（默认行为）
```python
from lar import GraphExecutor, LLMNode

# Logger 和 Tracker 会自动创建
executor = GraphExecutor(log_dir="my_logs")

node = LLMNode(model_name="ollama/phi4", prompt_template="test", output_key="result")
result = executor.run(node, {})

# 访问自动创建的实例
print(executor.logger.get_history())  # 审计跟踪
print(executor.tracker.get_summary())  # Token 使用情况
```

#### 选项 2：自定义注入（高级）
```python
from lar import GraphExecutor, AuditLogger, TokenTracker

# 创建自定义实例
custom_logger = AuditLogger(log_dir="advanced_logs")
custom_tracker = TokenTracker()

# 注入到执行器中
executor = GraphExecutor(
    logger=custom_logger,
    tracker=custom_tracker
)

# 在多个执行器之间共享 tracker 以统计汇总成本
executor2 = GraphExecutor(
    logger=AuditLogger(log_dir="other_logs"),
    tracker=custom_tracker  # 同一个 tracker = 累计 Token
)
```

**为什么使用自定义注入？**
- 集中式审计跟踪管理
- 跨工作流的成本汇总
- 自定义日志格式/持久化
- 与现有监控系统集成

**参考：** `examples/patterns/16_custom_logger_tracker.py` 查看完整演示。


## 从链 (Chains) 到状态机
在 `v1.3` 版本中，争论尘埃落定。Lár 的状态机架构现在提供原生的合规特性（断点、静态分析），而基于链的框架很难实现这些特性。

## 更新日志
- **[新增]** `src/lar/node.py` 中的 `HumanJuryNode`
- **[新增]** `src/lar/dynamic.py` 中的 `TopologyValidator`
- **[新增]** `src/lar/logger.py` 中的 `AuditLogger`
- **[新增]** `src/lar/tracker.py` 中的 `TokenTracker`
- **[重构]** `GraphExecutor` 以使用新的辅助类。
