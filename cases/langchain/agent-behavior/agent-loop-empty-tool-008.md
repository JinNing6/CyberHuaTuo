---
id: "langchain-agent-loop-008"
title: "Agent 在工具返回空值时陷入无限循环"
title_en: "Agent enters infinite loop when tool returns empty value"
framework: "langchain"
framework_version: ">=0.2.0"
language: "python"
tags:
  - "agent-behavior"
  - "tool-calling"
severity: "critical"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/18732"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 `create_react_agent` 或 `AgentExecutor` 时，当某个自定义 Tool 返回空字符串或 `None` 时，Agent 会反复调用同一个工具，陷入无限循环，直到达到 `max_iterations` 限制。

## 🔍 错误信息
Error Message

```
Agent stopped due to iteration limit or time limit.
```

日志中会看到 Agent 重复调用同一工具：

```
> Entering new AgentExecutor chain...
Action: search_tool
Action Input: "query"
Observation: 
Thought: I need to search again...
Action: search_tool
Action Input: "query"
Observation: 
... (重复数十次)
```

## 🔬 根因分析
Root Cause Analysis

1. Tool 返回空字符串 `""` 或 `None` 时，Agent 认为没有获得有效信息，会再次尝试
2. Agent 缺乏 "工具无结果" 的处理逻辑
3. 默认的 `max_iterations=15` 可能导致大量无效 LLM 调用和 Token 浪费

## 💊 药方
Prescriptions

### 药方 1：Tool 中确保始终返回有意义的字符串 ✅ 推荐

```python
from langchain.tools import tool

@tool
def search_tool(query: str) -> str:
    """搜索知识库"""
    results = do_search(query)
    if not results:
        return "未找到相关结果。请尝试使用不同的关键词搜索。"
    return format_results(results)
```

### 药方 2：设置合理的 max_iterations 和错误处理

```python
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,           # 降低最大迭代次数
    max_execution_time=30,      # 设置超时（秒）
    handle_parsing_errors=True, # 自动处理解析错误
    early_stopping_method="generate",  # 达到限制后尝试生成最终答案
)
```

### 药方 3：使用 LangGraph 替代 AgentExecutor

LangGraph 提供更精细的循环控制：

```python
from langgraph.prebuilt import create_react_agent
from langgraph.errors import GraphRecursionError

agent = create_react_agent(
    model=llm,
    tools=tools,
)

try:
    result = agent.invoke(
        {"messages": [("user", query)]},
        config={"recursion_limit": 10},
    )
except GraphRecursionError:
    print("Agent 达到递归限制，停止执行")
```

## 🔗 参考资料
References

- [LangChain Agent Concepts](https://python.langchain.com/docs/concepts/agents/)
- [How to handle tool errors](https://python.langchain.com/docs/how_to/tools_error/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
