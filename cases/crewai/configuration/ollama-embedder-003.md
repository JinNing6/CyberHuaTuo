---
id: "crewai-ollama-embedder-003"
title: "CrewAI 配置 Ollama 本地 Embedding 时报 embedder provider not found"
title_en: "CrewAI Ollama not found in embedder provider list"
framework: "crewai"
framework_version: ">=0.20.0"
language: "python"
tags:
  - "configuration"
  - "authentication"
severity: "medium"
complexity: "simple"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/crewAIInc/crewAI/issues/439"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用 Ollama 作为本地 LLM 时，CrewAI 的 Knowledge/Memory 功能要求配置 Embedder，但 Ollama 不在默认的 embedder provider 列表中，导致无法使用本地模型进行 embedding。该 Issue 有 24 条评论。

## 🔍 错误信息
Error Message

```python
ValueError: Provider 'ollama' is not supported for embeddings. 
Supported providers: ['openai', 'google', 'azure', 'cohere']
```

或

```python
KeyError: 'ollama'
```

## 🔬 根因分析
Root Cause Analysis

CrewAI 早期版本的 Embedding 配置只支持少数云端提供商，没有将 Ollama 等本地方案纳入支持列表。这对想要完全本地化运行的开发者是严重阻碍。

## 💊 药方
Prescriptions

### 药方 1：显式配置 Ollama Embedder ✅ 推荐

```python
from crewai import Crew, Agent, Task

crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,
    embedder={
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "url": "http://localhost:11434/api/embeddings",
        }
    }
)
```

### 药方 2：先用 Ollama 拉取 embedding 模型

```bash
# 安装 embedding 专用模型
ollama pull nomic-embed-text
# 或
ollama pull mxbai-embed-large
```

### 药方 3：使用 HuggingFace 本地 Embedding 作为替代

```python
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,
    embedder={
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
        }
    }
)
```

### 药方 4：升级 CrewAI

```bash
pip install crewai --upgrade
```

CrewAI v0.55+ 版本已原生支持 Ollama embedder。

## 🔗 参考资料
References

- [CrewAI Issue #439](https://github.com/crewAIInc/crewAI/issues/439) — 24 条评论
- [CrewAI Memory Config](https://docs.crewai.com/concepts/memory/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #439（24 条评论）
