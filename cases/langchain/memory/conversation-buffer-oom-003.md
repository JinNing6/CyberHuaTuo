---
id: "langchain-memory-leak-003"
title: "ConversationBufferMemory 在长对话中导致 OOM 崩溃"
title_en: "ConversationBufferMemory causes OOM crash in long conversations"
framework: "langchain"
framework_version: ">=0.1.0"
language: "python"
tags:
  - "memory"
  - "performance"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/12500"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 `ConversationBufferMemory` 构建长对话应用时，随着对话轮次增加，内存使用量线性增长，最终导致 Python 进程 OOM（Out of Memory）崩溃。在约 200+ 轮对话后问题尤为明显。

## 🔍 错误信息
Error Message

```
MemoryError: Unable to allocate array with shape (xxxxx,) and data type float32
```

或进程直接被系统 Kill：

```
Killed (signal 9)
```

## 🔬 根因分析
Root Cause Analysis

`ConversationBufferMemory` 会将**所有历史对话**完整保存在内存中，并在每次 LLM 调用时将全部历史作为 prompt 发送。这导致：
1. 内存占用随对话轮次线性增长
2. Token 消耗急剧增加（发送完整历史给 LLM）
3. 达到 LLM 上下文窗口限制后报错

## 💊 药方
Prescriptions

### 药方 1：使用 ConversationBufferWindowMemory ✅ 推荐

只保留最近 K 轮对话：

```python
from langchain.memory import ConversationBufferWindowMemory

# 只保留最近 10 轮对话
memory = ConversationBufferWindowMemory(k=10)
```

### 药方 2：使用 ConversationSummaryMemory

自动对旧对话做摘要压缩：

```python
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
memory = ConversationSummaryMemory(llm=llm)
```

### 药方 3：使用 ConversationSummaryBufferMemory

结合窗口和摘要的混合方案：

```python
from langchain.memory import ConversationSummaryBufferMemory

# 保留最近 2000 token 的完整对话，更早的做摘要
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,
)
```

### 药方 4：在 LangGraph 中使用 checkpoint

如果使用 LangGraph，推荐使用 `MemorySaver` 做持久化：

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
```

## 🔗 参考资料
References

- [LangChain Memory Types](https://python.langchain.com/docs/modules/memory/types/)
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
