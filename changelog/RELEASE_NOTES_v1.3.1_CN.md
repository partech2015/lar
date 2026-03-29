# Lár v1.3.1 发布说明

**“安全补丁”**

此补丁版本解决了 `TopologyValidator` 结构完整性检查中的一个关键安全缺陷。

## 安全修复

### 1. 强化结构完整性执行
- **修复**：如果动态图中的节点链接到不存在的 `next` 节点，`TopologyValidator` 现在可以正确引发 `SecurityError`。此前，此检查只是一个占位符（`pass`）。
- **影响**：防止“断链”攻击或畸形的动态图在执行过程中进入未定义状态。

## 验证
- 已通过 `tests/test_v1_3_features.py::test_validator_structural_integrity` 验证。
