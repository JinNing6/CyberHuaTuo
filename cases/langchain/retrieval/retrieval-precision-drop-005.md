---
id: "langchain-retrieval-precision-005"
title: "RetrievalQA 在大文档集上检索精度骤降"
title_en: "RetrievalQA retrieval precision drops significantly on large document sets"
framework: "langchain"
framework_version: ">=0.1.0"
language: "python"
tags:
  - "retrieval"
  - "performance"
severity: "medium"
complexity: "complex"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/discussions/15932"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 `RetrievalQA` 构建 RAG 应用时，在文档数量较少（<100）时检索精度很高，但当文档集扩大到数千份文档后，检索到的内容经常与问题无关，导致 LLM 给出错误或低质量的回答。

## 🔍 错误信息
Error Message

无明显报错，但 LLM 回答质量明显下降，或回答 "根据提供的上下文，我无法找到相关信息"。

## 🔬 根因分析
Root Cause Analysis

1. **默认 chunk 大小不合理**：默认的 `chunk_size=1000` 在大文档集上可能导致关键信息被分割到不同 chunk
2. **top-k 设置不当**：默认只检索 top-4 结果，在大文档集中召回率不足
3. **Embedding 模型质量**：默认嵌入模型对特定领域文档的语义理解不够精确
4. **缺少重排序（Reranking）**：向量相似度排序在大规模检索中精度有限

## 💊 药方
Prescriptions

### 药方 1：调优分块策略 ✅ 推荐

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 使用更小的 chunk size + overlap 提高精度
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # 减小 chunk 大小
    chunk_overlap=100,    # 增加重叠防止信息断裂
    separators=["\n\n", "\n", "。", ".", " "],
)
```

### 药方 2：增加检索数量 + 重排序

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# 先检索更多候选，再用 cross-encoder 精确重排
model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
compressor = CrossEncoderReranker(model=model, top_n=5)

retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20}),
)
```

### 药方 3：使用多查询检索器

```python
from langchain.retrievers import MultiQueryRetriever

# LLM 自动生成多个查询变体，提高召回率
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
    llm=llm,
)
```

### 药方 4：使用 BM25 + 向量混合检索

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(documents, k=10)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# 混合检索：结合关键词匹配和语义检索
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6],
)
```

## 🔗 参考资料
References

- [LangChain Retriever How-To](https://python.langchain.com/docs/how_to/#retrievers)
- [RAG Best Practices](https://python.langchain.com/docs/tutorials/rag/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
