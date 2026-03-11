---
id: "openai-sdk-v1-migration-001"
title: "openai Python SDK v1.0 重大 API 变更迁移指南"
title_en: "openai Python SDK v1.0 major API migration guide"
framework: "openai-sdk"
framework_version: ">=1.0.0"
language: "python"
tags:
  - "breaking-change"
  - "migration"
severity: "critical"
complexity: "moderate"
environment:
  python_version: ">=3.8"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/openai/openai-python/issues/1062"
related_cases: []
---

## 🏥 症状描述
Symptom Description

从 openai Python SDK 0.x 升级到 1.0+ 后，几乎所有 API 调用方式都发生了变化。原有代码全面报错。该 Issue 是 openai-python 仓库最高赞的 Issue（90 条评论），影响了全球数百万开发者。

## 🔍 错误信息
Error Message

```python
AttributeError: module 'openai' has no attribute 'ChatCompletion'
```

或

```python
TypeError: 'module' object is not callable
```

或

```python
openai.APIError: You tried to access openai.ChatCompletion, but this is 
no longer supported in openai>=1.0.0
```

## 🔬 根因分析
Root Cause Analysis

openai Python SDK v1.0 进行了完整重写：
1. **模块级函数被废弃**：`openai.ChatCompletion.create()` → `client.chat.completions.create()`
2. **引入 Client 实例**：必须创建 `OpenAI()` 客户端，不再使用 `openai.api_key` 全局变量
3. **返回值从 dict 变为 Pydantic model**：`response["choices"][0]["message"]` → `response.choices[0].message`
4. **异步客户端独立**：`AsyncOpenAI` 替代了旧的异步方式

## 💊 药方
Prescriptions

### 药方 1：完整迁移到 v1.0 API ✅ 推荐

```python
# ❌ 旧写法 (0.x)
import openai
openai.api_key = "sk-xxx"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
)
answer = response["choices"][0]["message"]["content"]

# ✅ 新写法 (1.x+)
from openai import OpenAI
client = OpenAI(api_key="sk-xxx")  # 或自动从环境变量 OPENAI_API_KEY 读取
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
answer = response.choices[0].message.content
```

### 药方 2：异步客户端

```python
# ❌ 旧写法
response = await openai.ChatCompletion.acreate(...)

# ✅ 新写法
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

### 药方 3：流式响应

```python
# ✅ 新写法
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")
```

### 药方 4：Embedding API

```python
# ❌ 旧写法
response = openai.Embedding.create(input="text", model="text-embedding-ada-002")
embedding = response["data"][0]["embedding"]

# ✅ 新写法
response = client.embeddings.create(
    input="text",
    model="text-embedding-3-small"
)
embedding = response.data[0].embedding
```

### 常用迁移速查表

| 旧写法 (0.x) | 新写法 (1.x+) |
|-------------|-------------|
| `openai.api_key = "sk-xxx"` | `client = OpenAI(api_key="sk-xxx")` |
| `openai.ChatCompletion.create()` | `client.chat.completions.create()` |
| `openai.Embedding.create()` | `client.embeddings.create()` |
| `response["choices"][0]` | `response.choices[0]` |
| `response["usage"]["total_tokens"]` | `response.usage.total_tokens` |

## 🔗 参考资料
References

- [openai-python Issue #1062](https://github.com/openai/openai-python/issues/1062) — 90 条评论
- [OpenAI Python SDK v1.0 Migration Guide](https://github.com/openai/openai-python/discussions/742)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #1062（90 条评论，最高赞 Issue）
