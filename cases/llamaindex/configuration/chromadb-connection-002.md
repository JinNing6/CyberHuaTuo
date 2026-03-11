---
id: "llamaindex-chromadb-error-002"
title: "LlamaIndex 使用 ChromaDB 时连接错误或数据丢失"
title_en: "LlamaIndex ChromaDB connection error or data loss"
framework: "llamaindex"
framework_version: ">=0.9.0"
language: "python"
tags:
  - "configuration"
  - "retrieval"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/run-llama/llama_index/issues/1237"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 LlamaIndex + ChromaDB 构建向量索引时，重启应用后索引数据消失，或调用时报连接错误。该 Issue 有 16 条评论。

## 🔍 错误信息
Error Message

```python
chromadb.errors.NoIndexException: Index not found
```

或重启后：

```python
ValueError: No existing collection found, pass documents to build index
```

## 🔬 根因分析
Root Cause Analysis

1. **默认使用 in-memory 模式**：ChromaDB 默认存储在内存中，重启后数据丢失
2. **persist_directory 配置遗漏**：未指定持久化路径
3. **ChromaDB 版本不兼容**：不同版本的数据格式不兼容

## 💊 药方
Prescriptions

### 药方 1：使用持久化存储 ✅ 推荐

```python
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# 使用持久化客户端
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_collection")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 首次构建
index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)

# 后续加载（无需重新构建）
index = VectorStoreIndex.from_vector_store(vector_store)
```

### 药方 2：确保 ChromaDB 版本兼容

```bash
pip install chromadb>=0.5.0 llama-index-vector-stores-chroma>=0.2.0
```

## 🔗 参考资料
References

- [LlamaIndex Issue #1237](https://github.com/run-llama/llama_index/issues/1237)
- [LlamaIndex ChromaDB Guide](https://docs.llamaindex.ai/en/stable/examples/vector_stores/ChromaIndexDemo/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #1237
