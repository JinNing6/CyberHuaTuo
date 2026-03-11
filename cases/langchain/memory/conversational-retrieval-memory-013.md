---
id: "langchain-memory-retrieval-chain-013"
title: "ConversationalRetrievalChain 与 Memory 结合时对话历史丢失"
title_en: "ConversationalRetrievalChain loses conversation history when combined with Memory"
framework: "langchain"
framework_version: ">=0.0.200"
language: "python"
tags:
  - "memory"
  - "retrieval"
severity: "high"
complexity: "complex"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/2303"
related_cases:
  - "langchain-memory-leak-003"
---

## 🏥 症状描述
Symptom Description

使用 `ConversationalRetrievalChain` 配合 `ConversationBufferMemory` 时，模型似乎"忘记"了之前的对话内容，每一轮都像全新对话。该 Issue 在 LangChain 仓库有 90 条评论，是使用率极高的痛点。

## 🔍 错误信息
Error Message

无明显报错，但行为异常：

```python
# 第一轮
Q: "我叫张三"
A: "你好张三！"

# 第二轮
Q: "我叫什么名字？"
A: "抱歉，你还没有告诉我你的名字。"  # 历史记忆丢失！
```

或出现参数冲突错误：

```python
ValueError: If using 'chat_history' as input variable, 
'memory_key' should also be set to 'chat_history'
```

## 🔬 根因分析
Root Cause Analysis

1. **memory_key 不匹配**：`ConversationBufferMemory` 默认 `memory_key="history"`，但 `ConversationalRetrievalChain` 期望 `memory_key="chat_history"`
2. **output_key 冲突**：Chain 的输出中如果有多个 key（如 `answer` 和 `source_documents`），Memory 不知道该保存哪个
3. **return_messages 参数缺失**：Chat 模型需要 `return_messages=True`，否则历史会被序列化为字符串格式

## 💊 药方
Prescriptions

### 药方 1：正确配置 Memory 参数 ✅ 推荐

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

memory = ConversationBufferMemory(
    memory_key="chat_history",      # 必须与 Chain 期望的 key 一致
    return_messages=True,           # Chat 模型需要 Message 格式
    output_key="answer",            # 指定保存哪个输出
)

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True,
)

# 使用
result = chain({"question": "你好"})
print(result["answer"])
```

### 药方 2：迁移到 LangGraph 的 RAG + Memory 方案

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

@tool
def search_docs(query: str) -> str:
    """搜索知识库"""
    docs = retriever.invoke(query)
    return "\n".join(d.page_content for d in docs)

checkpointer = MemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[search_docs],
    checkpointer=checkpointer,
)

# 使用同一个 thread_id 保持对话记忆
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({"messages": [("user", "你好")]}, config=config)
```

## 🔗 参考资料
References

- [LangChain Issue #2303](https://github.com/langchain-ai/langchain/issues/2303) — 90 条评论
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #2303（90 条评论）
