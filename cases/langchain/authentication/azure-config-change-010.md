---
id: "langchain-auth-azure-010"
title: "Azure OpenAI 配置参数在 LangChain 0.3 中变更"
title_en: "Azure OpenAI configuration parameters changed in LangChain 0.3"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "authentication"
  - "configuration"
  - "breaking-change"
severity: "medium"
complexity: "simple"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/langchain-ai/langchain/issues/21845"
related_cases: []
---

## 🏥 症状描述
Symptom Description

从 LangChain 0.2 升级到 0.3 后，使用 Azure OpenAI 的项目报认证错误。原有的 `AzureChatOpenAI` 配置方式无法正常工作。

## 🔍 错误信息
Error Message

```python
openai.AuthenticationError: Error code: 401 - {'error': {'code': '401', 
'message': 'Access denied due to invalid subscription key or wrong API endpoint.'}}
```

或

```python
TypeError: AzureChatOpenAI.__init__() got an unexpected keyword argument 'openai_api_base'
```

## 🔬 根因分析
Root Cause Analysis

LangChain 0.3 中 `AzureChatOpenAI` 的参数命名发生了变化：
- `openai_api_base` → `azure_endpoint`
- `openai_api_key` → `api_key`
- `openai_api_version` → `api_version`
- `deployment_name` → `azure_deployment`

## 💊 药方
Prescriptions

### 药方 1：更新参数名称 ✅ 推荐

```python
# ❌ 旧写法（0.2.x）
from langchain.chat_models import AzureChatOpenAI
llm = AzureChatOpenAI(
    openai_api_base="https://your-resource.openai.azure.com/",
    openai_api_key="your-key",
    openai_api_version="2024-02-15-preview",
    deployment_name="gpt-4o",
)

# ✅ 新写法（0.3.x）
from langchain_openai import AzureChatOpenAI
llm = AzureChatOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key",
    api_version="2024-02-15-preview",
    azure_deployment="gpt-4o",
)
```

### 药方 2：使用环境变量配置

```bash
# .env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
OPENAI_API_VERSION=2024-02-15-preview
```

```python
from langchain_openai import AzureChatOpenAI

# 自动从环境变量读取
llm = AzureChatOpenAI(azure_deployment="gpt-4o")
```

## 🔗 参考资料
References

- [LangChain Azure OpenAI](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)
- [Azure OpenAI Service API](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献
