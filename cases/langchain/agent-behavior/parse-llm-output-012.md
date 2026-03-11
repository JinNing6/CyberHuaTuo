---
id: "langchain-agent-parse-error-012"
title: "Agent 无法解析 LLM 输出导致 ValueError: Could not parse LLM output"
title_en: "ValueError: Could not parse LLM output in Agent execution"
framework: "langchain"
framework_version: ">=0.0.200"
language: "python"
tags:
  - "agent-behavior"
  - "general"
severity: "critical"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/1358"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 `AgentExecutor` 或 `create_react_agent` 时，LLM 返回的文本无法被 Agent 的输出解析器正确解析，导致整个执行链崩溃。这是 LangChain 仓库中最高赞（82 条评论）的 Issue 之一，影响了大量使用 ReAct Agent 的开发者。

## 🔍 错误信息
Error Message

```python
ValueError: Could not parse LLM output: `I'll help you with that. Let me search for the information.`
```

或

```python
OutputParserException: Could not parse LLM output: 
`Based on the information I found, here is the answer...`
```

## 🔬 根因分析
Root Cause Analysis

1. **LLM 不遵循 ReAct 格式**：Agent 期望 LLM 输出严格的 `Thought: / Action: / Action Input:` 格式，但 LLM 有时会直接给出最终答案而不遵循格式
2. **Prompt 不够严格**：默认的 Agent prompt 对输出格式的约束不够明确
3. **不同模型行为差异**：GPT-3.5 比 GPT-4 更容易偏离格式要求
4. **非英文输入**：使用中文等非英文输入时，LLM 更容易偏离 ReAct 格式

## 💊 药方
Prescriptions

### 药方 1：启用 handle_parsing_errors ✅ 推荐

```python
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # 自动处理解析错误
    # 或者提供自定义错误处理函数
    # handle_parsing_errors=lambda e: f"请重新格式化你的输出: {e}"
)
```

### 药方 2：使用 OpenAI Functions Agent 代替 ReAct Agent

OpenAI Functions Agent 使用结构化 function calling，完全避免输出解析问题：

```python
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### 药方 3：迁移到 LangGraph（推荐的长期方案）

```python
from langgraph.prebuilt import create_react_agent

# LangGraph 的 ReAct Agent 使用 tool calling 而非文本解析
agent = create_react_agent(model=llm, tools=tools)
result = agent.invoke({"messages": [("user", "你的问题")]})
```

### 药方 4：自定义输出解析器增加容错

```python
from langchain.agents import AgentOutputParser
from langchain_core.agents import AgentAction, AgentFinish
import re

class RobustOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> AgentAction | AgentFinish:
        # 尝试标准格式解析
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        
        # 尝试匹配 Action/Action Input
        action_match = re.search(r"Action\s*:\s*(.+)", llm_output)
        input_match = re.search(r"Action\s*Input\s*:\s*(.+)", llm_output)
        
        if action_match and input_match:
            return AgentAction(
                tool=action_match.group(1).strip(),
                tool_input=input_match.group(1).strip(),
                log=llm_output,
            )
        
        # Fallback: 将整个输出作为最终答案
        return AgentFinish(
            return_values={"output": llm_output.strip()},
            log=llm_output,
        )
```

## 🔗 参考资料
References

- [LangChain Issue #1358](https://github.com/langchain-ai/langchain/issues/1358) — 82 条评论，最高赞 Issue
- [LangGraph ReAct Agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #1358（82 条评论）
