---
id: "langchain-import-chatmodel-001"
title: "LangChain 0.3 升级后 ChatOpenAI 导入失败"
title_en: "ChatOpenAI import error after upgrading to LangChain 0.3"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "import-error"
  - "breaking-change"
  - "migration"
severity: "medium"
complexity: "simple"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-10"
updated_at: "2026-03-10"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/discussions/xxxxx"
related_cases: []
---

## 🏥 症状描述
Symptom Description

从 LangChain 0.2.x 升级到 0.3.x 后，原有的 `from langchain import ChatOpenAI` 导入语句报错，无法正常运行已有项目。

## 🔍 错误信息
Error Message

```python
ImportError: cannot import name 'ChatOpenAI' from 'langchain'
```

完整堆栈：

```
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    from langchain import ChatOpenAI
ImportError: cannot import name 'ChatOpenAI' from 'langchain' (/usr/local/lib/python3.11/site-packages/langchain/__init__.py)
```

## 🔬 根因分析
Root Cause Analysis

LangChain 0.3 进行了重大包结构重组：
- 所有模型集成类（`ChatOpenAI`, `OpenAIEmbeddings` 等）已从主包 `langchain` 迁移到独立集成包 `langchain-openai`
- 这是一个 **Breaking Change**，官方迁移指南中有详细说明

## 💊 药方
Prescriptions

### 药方 1：更新导入路径 ✅ 推荐

**适用版本**: `langchain >= 0.3.0`

1. 安装独立的 OpenAI 集成包：

```bash
pip install langchain-openai
```

2. 更新导入语句：

```python
# ❌ 旧写法（0.2.x 及更早）
from langchain import ChatOpenAI

# ✅ 新写法（0.3.x）
from langchain_openai import ChatOpenAI
```

3. 其他常用类的迁移：

```python
# Embeddings
from langchain_openai import OpenAIEmbeddings

# LLM
from langchain_openai import OpenAI
```

### 药方 2：使用 langchain-community 兼容层（临时过渡）

**适用版本**: `langchain >= 0.3.0, < 0.4.0`

```python
pip install langchain-community
```

```python
from langchain_community.chat_models import ChatOpenAI
```

> ⚠️ 此方案为临时过渡，`langchain-community` 中的包装器将在未来版本中被移除。建议尽早迁移到药方 1。

## 🔗 参考资料
References

- [LangChain 0.3 迁移指南](https://python.langchain.com/docs/versions/v0_3/)
- [LangChain Integration Packages](https://python.langchain.com/docs/integrations/platforms/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 如有更好方案欢迎 [提交 PR](https://github.com/CyberHuaTuo/CyberHuaTuo/pulls)
