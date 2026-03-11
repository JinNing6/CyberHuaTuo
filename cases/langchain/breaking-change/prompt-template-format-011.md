---
id: "langchain-breaking-prompt-011"
title: "ChatPromptTemplate.from_messages 参数格式变化导致运行报错"
title_en: "ChatPromptTemplate.from_messages parameter format change causes runtime error"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "breaking-change"
  - "configuration"
severity: "medium"
complexity: "simple"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/23019"
related_cases: []
---

## 🏥 症状描述
Symptom Description

升级到 LangChain 0.3 后，原有的 `ChatPromptTemplate.from_messages` 调用方式报错，特别是使用 `SystemMessagePromptTemplate` 和 `HumanMessagePromptTemplate` 时。

## 🔍 错误信息
Error Message

```python
TypeError: Can't instantiate abstract class MessagePromptTemplate
```

或

```python
ValidationError: 1 validation error for ChatPromptTemplate
messages -> 0
  value is not a valid dict (type=type_error.dict)
```

## 🔬 根因分析
Root Cause Analysis

LangChain 0.3 简化了 Prompt Template 的使用方式，推荐使用元组 (tuple) 语法代替显式的 Message 类。旧的 `SystemMessagePromptTemplate.from_template()` 等方法虽然仍可用，但导入路径已变。

## 💊 药方
Prescriptions

### 药方 1：使用简化的元组语法 ✅ 推荐

```python
from langchain_core.prompts import ChatPromptTemplate

# ❌ 旧写法（冗长）
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
    HumanMessagePromptTemplate.from_template("{question}"),
])

# ✅ 新写法（简洁）
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])
```

### 药方 2：使用 MessagesPlaceholder

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
```

## 🔗 参考资料
References

- [LangChain Prompt Templates](https://python.langchain.com/docs/concepts/prompt_templates/)
- [ChatPromptTemplate API](https://python.langchain.com/api_reference/core/prompts/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
