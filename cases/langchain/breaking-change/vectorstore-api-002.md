---
id: "langchain-breaking-vectorstore-002"
title: "LangChain 0.3 向量存储 API 从 similarity_search 迁移到新接口"
title_en: "LangChain 0.3 VectorStore API migration from similarity_search"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "breaking-change"
  - "retrieval"
  - "migration"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/24069"
related_cases:
  - "langchain-import-chatmodel-001"
---

## 🏥 症状描述
Symptom Description

升级到 LangChain 0.3 后，使用 `FAISS.from_documents()` 或 `Chroma.from_documents()` 创建向量存储时报错，原有的 `VectorStore` 接口调用方式不再兼容。

## 🔍 错误信息
Error Message

```python
TypeError: VectorStore.__init__() got an unexpected keyword argument 'embedding_function'
```

或

```python
DeprecationWarning: Since langchain-core 0.3.0, VectorStore.from_documents 
has been deprecated. Use langchain_community or partner packages instead.
```

## 🔬 根因分析
Root Cause Analysis

LangChain 0.3 对向量存储进行了重大重构：
- `VectorStore` 基类的接口签名发生了变化
- 构造函数参数从 `embedding_function` 改为 `embedding`
- 所有具体实现被迁移到 `langchain-community` 或各自的 partner packages（如 `langchain-chroma`、`langchain-pinecone`）

## 💊 药方
Prescriptions

### 药方 1：安装并使用 partner package ✅ 推荐

**适用版本**: `langchain >= 0.3.0`

1. 安装对应的 partner package：

```bash
# FAISS
pip install langchain-community faiss-cpu

# Chroma
pip install langchain-chroma

# Pinecone
pip install langchain-pinecone
```

2. 更新导入路径和参数名：

```python
# ❌ 旧写法
from langchain.vectorstores import FAISS
db = FAISS.from_documents(docs, embedding_function=embeddings)

# ✅ 新写法 (FAISS)
from langchain_community.vectorstores import FAISS
db = FAISS.from_documents(docs, embedding=embeddings)

# ✅ 新写法 (Chroma)
from langchain_chroma import Chroma
db = Chroma.from_documents(docs, embedding=embeddings)
```

### 药方 2：检查 embedding 参数命名

```python
# 部分 partner package 仍使用旧参数名，需查阅各自文档
# 如遇到参数错误，尝试以下变体：
db = VectorStore.from_documents(docs, embedding=embeddings)
# 或
db = VectorStore.from_documents(docs, embeddings)
```

## 🔗 参考资料
References

- [LangChain 0.3 Migration Guide](https://python.langchain.com/docs/versions/v0_3/)
- [VectorStore Partner Packages](https://python.langchain.com/docs/integrations/vectorstores/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
