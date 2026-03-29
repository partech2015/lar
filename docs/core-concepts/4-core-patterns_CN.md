# 模式库

#### 1. 基础原语 (`examples/basic/`)
| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_simple_triage.py`](../../examples/basic/1_simple_triage.py)** | 分类与线性路由 |
| **2** | **[`2_reward_code_agent.py`](../../examples/basic/2_reward_code_agent.py)** | 代码优先的智能体逻辑 |
| **3** | **[`3_support_helper_agent.py`](../../examples/basic/3_support_helper_agent.py)** | 轻量级工具助手 |
| **4** | **[`4_fastapi_server.py`](../../examples/basic/4_fastapi_server.py)** | FastAPI 包装器（随处部署） |

#### 2. 核心模式 (`examples/patterns/`)
| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_rag_researcher.py`](../../examples/patterns/1_rag_researcher.py)** | RAG (ToolNode) 与状态合并 |
| **2** | **[`2_self_correction.py`](../../examples/patterns/2_self_correction.py)** | “判定”模式与错误循环 |
| **3** | **[`3_parallel_execution.py`](../../examples/patterns/3_parallel_execution.py)** | 扇出 / 扇入聚合 |
| **4** | **[`4_structured_output.py`](../../examples/patterns/4_structured_output.py)** | 严格的 JSON 强制执行 |
| **5** | **[`5_multi_agent_handoff.py`](../../examples/patterns/5_multi_agent_handoff.py)** | 多智能体协作 |
| **6** | **[`6_meta_prompt_optimizer.py`](../../examples/patterns/6_meta_prompt_optimizer.py)** | 自修改智能体（元推理） |
| **7** | **[`7_integration_test.py`](../../examples/patterns/7_integration_test.py)** | 集成构建器 (CoinCap) |
| **8** | **[`8_ab_tester.py`](../../examples/patterns/8_ab_tester.py)** | A/B 测试器（并行提示词） |
| **9** | **[`9_resumable_graph.py`](../../examples/patterns/9_resumable_graph.py)** | 时间旅行者（崩溃与恢复） |
| **10** | **[`16_custom_logger_tracker.py`](../../examples/patterns/16_custom_logger_tracker.py)** | 高级可观测性 |

#### 3. 推理模型与对比 (`examples/reasoning_models/`, `examples/comparisons/`)
| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_deepseek_r1.py`](../../examples/reasoning_models/1_deepseek_r1.py)** | 原生 `<think>` 标签解析 |
| **2** | **[`2_openai_o1.py`](../../examples/reasoning_models/2_openai_o1.py)** | 高智商 O1 规划节点 |
| **3** | **[`3_liquid_thinking.py`](../../examples/reasoning_models/3_liquid_thinking.py)** | 快速本地边缘推理 |
| **4** | **[`langchain_swarm_fail.py`](../../examples/comparisons/langchain_swarm_fail.py)** | 上下文崩溃证明 |

#### 4. 合规性与安全 (`examples/compliance/`)
| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_human_in_the_loop.py`](../../examples/compliance/1_human_in_the_loop.py)** | 用户批准与中断 |
| **2** | **[`2_security_firewall.py`](../../examples/compliance/2_security_firewall.py)** | 使用代码阻断越狱攻击 |
| **3** | **[`3_juried_layer.py`](../../examples/compliance/3_juried_layer.py)** | 提议者 -> 陪审团 -> 内核 |
| **4** | **[`4_access_control_agent.py`](../../examples/compliance/4_access_control_agent.py)** | **旗舰级访问控制** |
| **5** | **[`5_context_contamination_test.py`](../../examples/compliance/5_context_contamination_test.py)** | 红队测试：社会工程学 |
| **6** | **[`6_zombie_action_test.py`](../../examples/compliance/6_zombie_action_test.py)** | 红队测试：陈旧权限 |
| **7** | **[`7_hitl_agent.py`](../../examples/compliance/7_hitl_agent.py)** | 符合第 14 条的合规节点 |
| **8** | **[`8_hmac_audit_log.py`](../../examples/compliance/8_hmac_audit_log.py)** | 不可变的加密日志 |
| **9** | **[`9_high_risk_trading_hmac.py`](../../examples/compliance/9_high_risk_trading_hmac.py)** | 算法交易 (SEC) |
| **10** | **[`10_pharma_clinical_trials_hmac.py`](../../examples/compliance/10_pharma_clinical_trials_hmac.py)** | FDA 21 CFR Part 11 试验逻辑 |
| **11** | **[`11_verify_audit_log.py`](../../examples/compliance/11_verify_audit_log.py)** | 独立审计员脚本 |

#### 5. 高规模与高级模式 (`examples/scale/`, `examples/advanced/`)
| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_corporate_swarm.py`](../../examples/scale/1_corporate_swarm.py)** | **压力测试**：60 多个节点的图 |
| **2** | **[`2_mini_swarm_pruner.py`](../../examples/scale/2_mini_swarm_pruner.py)** | 动态图剪枝 |
| **3** | **[`3_parallel_newsroom.py`](../../examples/scale/3_parallel_newsroom.py)** | 真正并行 (`BatchNode`) |
| **4** | **[`4_parallel_corporate_swarm.py`](../../examples/scale/4_parallel_corporate_swarm.py)** | 并发分支执行 |
| **5** | **[`11_map_reduce_budget.py`](../../examples/advanced/11_map_reduce_budget.py)** | **内存压缩与 Token 预算** |
| **6** | **[`fractal_polymath.py`](../../examples/advanced/fractal_polymath.py)** | **分形代理**（递归 + 并行） |
| **7** | **[`13_world_model_jepa.py`](../../examples/advanced/13_world_model_jepa.py)** | **预测性世界模型** |

#### 6. 元认知 (`examples/metacognition/`)
详见 **[元认知文档](9-metacognition_CN.md)** 以深入了解。

| # | 模式 | 概念 |
| :---: | :--- | :--- |
| **1** | **[`1_dynamic_depth.py`](../../examples/metacognition/1_dynamic_depth.py)** | **适应性复杂度**（1 节点 vs N 节点） |
| **2** | **[`2_tool_inventor.py`](../../examples/metacognition/2_tool_inventor.py)** | **自主编程**（在运行时编写工具） |
| **3** | **[`3_self_healing.py`](../../examples/metacognition/3_self_healing.py)** | **错误恢复**（注入修复子图） |
| **4** | **[`4_adaptive_deep_dive.py`](../../examples/metacognition/4_adaptive_deep_dive.py)** | **递归研究**（生成子智能体） |
| **5** | **[`5_expert_summoner.py`](../../examples/metacognition/5_expert_summoner.py)** | **动态 Persona 实例化** |
