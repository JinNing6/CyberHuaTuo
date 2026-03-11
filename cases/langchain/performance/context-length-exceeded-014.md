---
id: "langchain-context-length-014"
title: "LLM 上下文长度超限导致 InvalidRequestError"
title_en: "Model context length exceeded causing InvalidRequestError"
framework: "langchain"
framework_version: ">=0.0.100"
language: "python"
tags:
  - "performance"
  - "configuration"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/1349"
related_cases:
  - "langchain-memory-leak-003"
---

## 🏥 症状描述
Symptom Description

使用 LangChain 构建 RAG 或 Agent 应用时，当文档内容过长或对话历史过多时，发送给 LLM 的 prompt 超过模型最大上下文长度限制，导致请求失败。

## 🔍 错误信息
Error Message

```python
openai.InvalidRequestError: This model's maximum context length is 4097 tokens. 
However, your messages resulted in 5231 tokens. 
Please reduce the length of the messages.
```

或

```python
openai.BadRequestError: Error code: 400 - {'error': {'message': 
"This model's maximum context length is 128000 tokens. 
However, your messages resulted in 150234 tokens."}}
```

## 🔬 根因分析
Root Cause Analysis

1. RAG 检索的文档 chunk 太大或 top-k 太高，导致上下文膨胀
2. ConversationBufferMemory 积累了过长的对话历史
3. System prompt + 用户输入 + 检索文档的总 token 数超限
4. 未根据选用的模型设置对应的 token 限额

## 💊 药方
Prescriptions

### 药方 1：限制检索文档的总长度 ✅ 推荐

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 使用更小的 chunk 以控制总 token 数
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

# 限制检索数量
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}  # 减少检索数量
)
```

### 药方 2：使用 Token 限制的 Memory

```python
from langchain.memory import ConversationTokenBufferMemory
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# 自动按 token 数截断历史
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=2000,  # 给历史记录预留的 token 数
)
```

### 药方 3：选择大上下文模型

```python
from langchain_openai import ChatOpenAI

# 使用大上下文窗口模型
llm = ChatOpenAI(
    model="gpt-4o",          # 128K context
    # model="gpt-4o-mini",   # 128K context  
    # model="claude-3-5-sonnet-latest",  # 200K context
)
```

### 药方 4：动态计算可用 token 预算

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 动态调整检索数量
MAX_CONTEXT = 128000
SYSTEM_TOKENS = count_tokens(system_prompt)
USER_TOKENS = count_tokens(user_query)
AVAILABLE = MAX_CONTEXT - SYSTEM_TOKENS - USER_TOKENS - 4000  # 预留回答空间

# 按可用空间动态决定检索数量
docs = retriever.invoke(user_query)
selected_docs = []
used_tokens = 0
for doc in docs:
    doc_tokens = count_tokens(doc.page_content)
    if used_tokens + doc_tokens < AVAILABLE:
        selected_docs.append(doc)
        used_tokens += doc_tokens
    else:
        break
```

## 🔗 参考资料
References

- [LangChain Issue #1349](https://github.com/langchain-ai/langchain/issues/1349) — 31 条评论
- [OpenAI Token Limits](https://platform.openai.com/docs/models)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #1349（31 条评论）
