---
id: "llamaindex-breaking-v10-001"
title: "LlamaIndex 0.10+ 核心包拆分迁移"
title_en: "LlamaIndex 0.10+ core package split migration"
framework: "llamaindex"
framework_version: ">=0.10.0"
language: "python"
tags:
  - "breaking-change"
  - "import-error"
  - "migration"
severity: "critical"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/run-llama/llama_index/issues/13477"
related_cases: []
---

## 🏥 症状描述
Symptom Description

升级到 LlamaIndex 0.10+ 后，所有 `from llama_index import ...` 导入报错。核心类被拆分到多个独立包。

## 🔍 错误信息
Error Message

```python
ImportError: cannot import name 'VectorStoreIndex' from 'llama_index'
```

```python
ImportError: cannot import name 'ServiceContext' from 'llama_index'
```

## 🔬 根因分析
Root Cause Analysis

LlamaIndex 0.10 进行了大规模包拆分：核心到 `llama-index-core`，各集成到独立包，`ServiceContext` 废弃改为全局 `Settings`。

## 💊 药方
Prescriptions

### 药方 1：更新导入路径 ✅ 推荐

```python
# ❌ 旧写法
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI

# ✅ 新写法
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
```

安装必要的包：

```bash
pip install llama-index-core llama-index-llms-openai llama-index-embeddings-openai
```

### 药方 2：用 Settings 替代 ServiceContext

```python
from llama_index.core import Settings
Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding()
Settings.chunk_size = 512
index = VectorStoreIndex.from_documents(docs)
```

## 🔗 参考资料
References

- [LlamaIndex Issue #13477](https://github.com/run-llama/llama_index/issues/13477)
- [LlamaIndex 0.10 Migration Guide](https://docs.llamaindex.ai/en/stable/getting_started/v0_10_0_migration/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
