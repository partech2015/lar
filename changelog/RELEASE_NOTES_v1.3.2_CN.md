# Lár v1.3.2 发布说明

**“开发者体验更新”**

此版本通过为 `AuditLogger` 和 `TokenTracker` 添加详尽的使用示例和文档，弥补了 v1.3.0 中的文档缺失。

## 新增内容

### 文档改进

#### 1. 新示例：自定义 Logger/Tracker
**文件：** `examples/patterns/16_custom_logger_tracker.py`

演示内容：
- 默认自动创建（推荐用于大多数用例）
- 高级工作流的自定义依赖注入
- 在多个执行器之间共享 tracker 以进行成本汇总
- 直接访问 logger 历史记录和 token 摘要

**用法：**
```bash
python examples/patterns/16_custom_logger_tracker.py
```

#### 2. 增强型 v1.3.0 发布说明
添加了完整的“如何使用”章节，内容包括：
- 选项 1：自动（默认行为）
- 选项 2：自定义注入（高级）
- 两种模式的代码示例
- 自定义注入的用例

#### 3. 更新 README.md
- 在 `GraphExecutor` 文档中添加了可观测性特性章节
- 包含了默认和高级用法的代码示例
- 在元认知特性列表中添加了对新示例的引用

#### 4. 更新文档
**文件：** `docs/core-concepts/3-audit-log.md`

新章节：“模块化可观测性 (v1.3.0)”
- 详细的 `AuditLogger` 使用模式
- 详细的 `TokenTracker` 使用模式
- 成本汇总的真实场景示例
- 符合 GxP 标准的审计跟踪示例

## 影响

**在 v1.3.2 之前：**
- 用户必须阅读源代码才能理解 `AuditLogger` 和 `TokenTracker`
- 没有任何关于自定义注入的文档示例
- 对于何时使用自定义实例还是默认设置感到困惑

**在 v1.3.2 之后：**
- ✅ 在发布说明、README 和文档中提供了清晰的使用示例
- ✅ 包含了 4 种使用模式的专用示例文件
- ✅ 关于何时使用每种方法的指南
- ✅ 显著提升了开发者体验

## 无重大变更

这纯粹是一个文档发布。没有 API 变更，没有对核心框架的代码更改。

所有现有代码继续保持原样正常运行。

## 升级

```bash
pip install --upgrade lar-engine
```

或者使用 Poetry：
```bash
poetry add lar-engine@^1.3.2
```

## 文档覆盖情况

| 位置 | 状态 |
|----------|--------|
| 发布说明 (v1.3.0) | ✅ 已更新使用示例 |
| 示例 | ✅ 新增 16_custom_logger_tracker.py |
| README.md | ✅ GraphExecutor 章节已更新 |
| 文档 | ✅ core-concepts/3-audit-log.md 已更新 |

---

**开发者体验：** 反馈 v1.3.0 的可观测性特性体验得到显著改善。
