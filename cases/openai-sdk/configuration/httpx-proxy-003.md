---
id: "openai-sdk-httpx-proxy-003"
title: "openai SDK 升级 httpx 后代理配置报错"
title_en: "openai SDK proxy configuration breaks after httpx upgrade"
framework: "openai-sdk"
framework_version: ">=1.40.0"
language: "python"
tags:
  - "configuration"
  - "breaking-change"
severity: "high"
complexity: "simple"
environment:
  python_version: ">=3.8"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/openai/openai-python/issues/1902"
related_cases: []
---

## 🏥 症状描述
Symptom Description

使用代理（如 Clash、V2Ray）访问 OpenAI API 时，httpx 升级到 0.28.0 后原有的代理配置方式失效，导致连接超时或报错。该 Issue 有 12 条评论，影响大量中国开发者。

## 🔍 错误信息
Error Message

```python
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

或

```python
httpx.ConnectTimeout: timed out
```

## 🔬 根因分析
Root Cause Analysis

httpx 0.28.0 废弃了 `proxies` 参数，改为 `proxy`（单数），openai SDK 底层依赖的 httpx 版本升级后触发了这个 breaking change。

## 💊 药方
Prescriptions

### 药方 1：使用新的 proxy 参数 ✅ 推荐

```python
from openai import OpenAI
import httpx

# httpx >= 0.28.0 使用 proxy（单数）
client = OpenAI(
    http_client=httpx.Client(
        proxy="http://127.0.0.1:7890",  # 你的代理地址
    )
)
```

### 药方 2：使用环境变量设置代理

```bash
# 通用方式，不修改代码
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

```python
# OpenAI 客户端会自动使用环境变量中的代理
client = OpenAI()
```

### 药方 3：锁定 httpx 版本（临时方案）

```bash
pip install httpx==0.27.2 openai
```

> ⚠️ 此方案仅为临时过渡，建议尽早迁移到药方 1。

## 🔗 参考资料
References

- [openai-python Issue #1902](https://github.com/openai/openai-python/issues/1902)
- [httpx 0.28.0 Changelog](https://github.com/encode/httpx/releases/tag/0.28.0)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #1902（12 条评论）
