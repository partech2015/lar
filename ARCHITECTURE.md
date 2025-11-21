# Lár Architecture

## Overview
Lár is a define-by-run execution engine composed of four primitives:

### 1. GraphState  
Dictionary-like container with built-in diff tracking.

### 2. Node Types  
•⁠  ⁠*LLMNode* → For LLM reasoning  
•⁠  ⁠*ToolNode* → For Python tool execution  
•⁠  ⁠*RouterNode* → For conditional branching  

All nodes produce a structured log event.

### 3. GraphExecutor  
A simple loop:


while current_node:
    node.run(state)
    record_log()
    current_node = node.next(state)


This simplicity is the power — just like PyTorch’s eager execution.

---

## Why This Architecture Wins
•⁠  ⁠Deterministic  
•⁠  ⁠Composable  
•⁠  ⁠Observable  
•⁠  ⁠Debuggable  
•⁠  ⁠Production-ready  

Unlike agents built with chain-based systems (LangChain), Lár keeps:
•⁠  ⁠no hidden steps  
•⁠  ⁠no implicit transitions  
•⁠  ⁠no magical routing