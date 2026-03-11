---
id: "openai-sdk-auth-no-key-002"
title: "AuthenticationError: No API key provided 但明明已配置"
title_en: "AuthenticationError: No API key provided despite being configured"
framework: "openai-sdk"
framework_version: ">=1.0.0"
language: "python"
tags:
  - "authentication"
  - "configuration"
severity: "high"
complexity: "simple"
environment:
  python_version: ">=3.8"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/openai/openai-python/issues/163"
related_cases: []
---

## 🏥 症状描述
Symptom Description

明确设置了 `OPENAI_API_KEY` 环境变量或在代码中传入了 API Key，但仍然报认证错误。该 Issue 有 30 条评论，是新手最常遇到的问题。

## 🔍 错误信息
Error Message

```python
openai.AuthenticationError: No API key provided. You can set your API key 
in code using 'openai.api_key = <API-KEY>', or you can set the environment 
variable OPENAI_API_KEY=<API-KEY>.
```

或（v1.x）

```python
openai.OpenAIError: The api_key client option must be set either by passing 
api_key to the client or by setting the OPENAI_API_KEY environment variable
```

## 🔬 根因分析
Root Cause Analysis

1. **环境变量未被加载**：使用 `.env` 文件但忘记调用 `load_dotenv()`
2. **环境变量名拼写错误**：`OPENAPI_API_KEY`（多了一个 A）vs `OPENAI_API_KEY`
3. **环境变量作用域问题**：在 IDE 终端中设置但在另一个终端中运行
4. **Key 格式错误**：Key 前后有空格或换行符
5. **虚拟环境问题**：在系统环境中设置变量，但 venv 中无法访问

## 💊 药方
Prescriptions

### 药方 1：检查环境变量是否正确加载 ✅ 推荐

```python
import os

# 1. 先检查环境变量
key = os.getenv("OPENAI_API_KEY")
print(f"Key loaded: {bool(key)}")
print(f"Key starts with: {key[:8] if key else 'NOT SET'}...")

# 2. 如果使用 .env 文件
from dotenv import load_dotenv
load_dotenv()  # 必须在使用前调用！

# 3. 创建客户端
from openai import OpenAI
client = OpenAI()  # 自动读取 OPENAI_API_KEY
```

### 药方 2：显式传入 API Key

```python
from openai import OpenAI

# 直接传入，绕过环境变量问题
client = OpenAI(api_key="sk-xxxxxxxxx")
```

### 药方 3：检查 .env 文件格式

```bash
# ❌ 错误格式
OPENAI_API_KEY = sk-xxx          # 等号两边有空格
OPENAI_API_KEY="sk-xxx"          # 有引号（部分情况有问题）
OPENAI_API_KEY=sk-xxx            # Key 后面有不可见换行符

# ✅ 正确格式
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
```

### 药方 4：调试环境变量

```python
import os
import subprocess

# 检查所有相关环境变量
for key in sorted(os.environ.keys()):
    if "OPENAI" in key.upper() or "API" in key.upper():
        val = os.environ[key]
        print(f"{key} = {val[:10]}... (len={len(val)})")
```

## 🔗 参考资料
References

- [openai-python Issue #163](https://github.com/openai/openai-python/issues/163) — 30 条评论
- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #163（30 条评论）
