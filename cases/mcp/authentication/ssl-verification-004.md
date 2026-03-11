---
id: "mcp-ssl-verification-004"
title: "MCP Server SSL 证书验证失败导致连接被拒绝"
title_en: "MCP Server SSL certificate verification failure causes connection refused"
framework: "mcp"
framework_version: ">=1.0.0"
language: "python"
tags:
  - "authentication"
  - "configuration"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.10"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/modelcontextprotocol/python-sdk/issues/870"
related_cases: []
---

## 🏥 症状描述
Symptom Description

通过 SSE 或 Streamable HTTP 连接远程 MCP Server 时，因 SSL 证书问题导致连接失败。在企业内网或自签名证书环境中极为常见。该 Issue 有 23 条评论。

## 🔍 错误信息
Error Message

```python
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: unable to get local issuer certificate
```

或

```python
httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

## 🔬 根因分析
Root Cause Analysis

1. 企业内网使用自签名证书，Python 默认不信任
2. 代理/防火墙进行 SSL 拦截（MITM）
3. 系统 CA 证书包不完整或过期
4. MCP SDK 早期版本缺少 SSL 配置选项

## 💊 药方
Prescriptions

### 药方 1：配置自定义 SSL 上下文 ✅ 推荐

```python
import ssl
import httpx
from mcp.client.sse import sse_client

# 创建允许自签名证书的 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations("path/to/custom-ca.pem")

# 在 httpx 客户端中使用
async with httpx.AsyncClient(verify=ssl_context) as http_client:
    async with sse_client(
        url="https://your-mcp-server.com/sse",
        headers={"Authorization": "Bearer token"},
    ) as (read, write):
        # 使用 MCP 客户端...
        pass
```

### 药方 2：更新系统 CA 证书

```bash
# macOS
brew install ca-certificates

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# Python certifi
pip install --upgrade certifi
python -c "import certifi; print(certifi.where())"
```

### 药方 3：临时禁用 SSL 验证（仅开发环境）

```python
import httpx

# ⚠️ 仅用于开发/调试环境！
client = httpx.AsyncClient(verify=False)
```

> ⚠️ 生产环境中**绝对不要**禁用 SSL 验证。

## 🔗 参考资料
References

- [MCP Python SDK Issue #870](https://github.com/modelcontextprotocol/python-sdk/issues/870) — 23 条评论
- [Python SSL Documentation](https://docs.python.org/3/library/ssl.html)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #870
