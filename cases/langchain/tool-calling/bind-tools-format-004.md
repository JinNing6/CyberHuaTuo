---
id: "langchain-tool-calling-bind-004"
title: "bind_tools 返回格式不一致导致 Agent 无法解析工具调用"
title_en: "bind_tools returns inconsistent format causing Agent tool call parsing failure"
framework: "langchain"
framework_version: ">=0.2.0"
language: "python"
tags:
  - "tool-calling"
  - "agent-behavior"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/20834"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 `llm.bind_tools(tools)` 后，Agent 执行工具调用时返回的格式不一致：有时 `tool_calls` 字段为空列表，有时工具参数格式不正确（字符串而非 JSON）。不同 LLM 提供商之间行为差异明显。

## 🔍 错误信息
Error Message

```python
OutputParserException: Could not parse tool calls from response. 
Expected 'tool_calls' in message.additional_kwargs, got: {}
```

或

```python
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

## 🔬 根因分析
Root Cause Analysis

1. 不同 LLM 提供商的 function calling / tool calling 实现不统一
2. LangChain 的 `bind_tools` 在底层使用不同的序列化方式
3. 某些模型（特别是开源模型通过 Ollama）不严格遵循 OpenAI 的 function calling schema
4. `tool_choice` 参数在不同提供商间行为不同

## 💊 药方
Prescriptions

### 药方 1：指定 tool_choice 强制工具调用 ✅ 推荐

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# 强制模型必须调用工具
llm_with_tools = llm.bind_tools(
    tools,
    tool_choice="required"  # 或指定具体工具名
)
```

### 药方 2：使用 with_structured_output 代替手动解析

```python
from pydantic import BaseModel

class SearchQuery(BaseModel):
    query: str
    max_results: int = 5

# 使用 structured output 获得类型安全的输出
structured_llm = llm.with_structured_output(SearchQuery)
result = structured_llm.invoke("搜索 LangChain 教程")
# result 是 SearchQuery 实例
```

### 药方 3：添加 fallback 处理逻辑

```python
from langchain_core.messages import AIMessage

response = llm_with_tools.invoke(messages)

# 安全检查 tool_calls
if isinstance(response, AIMessage) and response.tool_calls:
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        # 处理工具调用
else:
    # fallback: 当模型未调用工具时的处理
    print("模型选择了直接回复而非调用工具")
```

## 🔗 参考资料
References

- [LangChain Tool Calling](https://python.langchain.com/docs/how_to/tool_calling/)
- [How to handle tool calling errors](https://python.langchain.com/docs/how_to/tools_error/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
