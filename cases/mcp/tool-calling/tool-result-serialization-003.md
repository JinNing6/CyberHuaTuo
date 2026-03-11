---
id: "mcp-tool-serialization-003"
title: "MCP CallToolResult 序列化失败导致工具调用无响应"
title_en: "MCP CallToolResult serialization fails causing tool call to hang"
framework: "mcp"
framework_version: ">=1.0.0"
language: "python"
tags:
  - "tool-calling"
  - "general"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.10"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/modelcontextprotocol/python-sdk/issues/987"
related_cases: []
---

## 🏥 症状描述
Symptom Description

MCP Server 的 Tool 执行成功，但客户端收不到响应，或收到序列化错误。Tool 返回的内容无法被正确序列化为 MCP 协议格式。

## 🔍 错误信息
Error Message

```python
TypeError: Object of type bytes is not JSON serializable
```

或

```python
pydantic.ValidationError: 1 validation error for CallToolResult
content -> 0
  value is not a valid dict (type=type_error.dict)
```

或

```
mcp.shared.exceptions.McpError: Tool result serialization failed
```

## 🔬 根因分析
Root Cause Analysis

1. **Tool 返回了非标准类型**：MCP 协议要求 Tool 返回 `list[TextContent | ImageContent | EmbeddedResource]`，而不是原始字符串或字典
2. **bytes 类型未转换**：文件内容或二进制数据直接返回而未转为 base64 字符串
3. **嵌套对象不可序列化**：返回了 Pydantic model、datetime 等非 JSON 原生类型

## 💊 药方
Prescriptions

### 药方 1：使用正确的返回类型 ✅ 推荐

```python
import mcp.types as types
from mcp.server import Server

server = Server("my-server")

@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[types.TextContent]:
    result = await do_something(arguments)
    
    # ✅ 正确：返回 TextContent 列表
    return [
        types.TextContent(
            type="text",
            text=str(result)  # 确保是字符串
        )
    ]
```

### 药方 2：返回图片内容

```python
import base64

@server.call_tool()
async def handle_screenshot(name: str, arguments: dict):
    image_bytes = await take_screenshot()
    
    # ✅ 二进制数据用 base64 编码
    return [
        types.ImageContent(
            type="image",
            data=base64.b64encode(image_bytes).decode("utf-8"),
            mimeType="image/png",
        )
    ]
```

### 药方 3：复杂对象序列化

```python
import json
from datetime import datetime

@server.call_tool()
async def handle_complex(name: str, arguments: dict):
    data = {
        "results": [{"id": 1, "name": "test"}],
        "timestamp": datetime.now().isoformat(),
        "count": 42,
    }
    
    # ✅ 复杂对象先 JSON 序列化
    return [
        types.TextContent(
            type="text",
            text=json.dumps(data, ensure_ascii=False, indent=2)
        )
    ]
```

## 🔗 参考资料
References

- [MCP Python SDK Issue #987](https://github.com/modelcontextprotocol/python-sdk/issues/987) — 6 条评论
- [MCP Specification - Tool Results](https://spec.modelcontextprotocol.io/specification/server/tools/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #987
