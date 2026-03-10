---
id: "mcp-tool-timeout-001"
title: "MCP Server 工具调用超时，Agent 收到空响应"
title_en: "MCP Server tool call timeout with empty response to Agent"
framework: "mcp"
framework_version: ">=2024.11"
language: "python"
tags:
  - "timeout"
  - "tool-calling"
  - "server-connection"
  - "mcp-protocol"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.10"
  os: "any"
  dependencies:
    - "mcp>=1.0"
created_at: "2026-03-10"
updated_at: "2026-03-10"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases: []
---

## 🏥 症状描述
Symptom Description

在使用 MCP (Model Context Protocol) 连接外部工具服务器时，Agent 调用某个 MCP 工具后，长时间等待无响应，最终收到超时错误或空响应。客户端侧表现为 Agent 「卡住」或返回无意义的结果。

## 🔍 错误信息
Error Message

```
TimeoutError: MCP tool call 'web_search' timed out after 30s
```

或客户端日志中看到：

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "error": {
    "code": -32000,
    "message": "Tool execution timed out"
  }
}
```

## 🔬 根因分析
Root Cause Analysis

1. **MCP Server 端未处理长时间操作**：工具执行超过了客户端默认的 30 秒超时窗口（如网络请求、大文件处理）
2. **stdio 传输模式下的缓冲区阻塞**：Server 通过 stdio 通信时，大量输出堵塞了 stdout buffer
3. **Server 进程异常退出**：Server 进程崩溃但客户端未收到断开通知

## 💊 药方
Prescriptions

### 药方 1：在 MCP Server 端添加超时处理和 progress 通知

**适用版本**: `MCP SDK >= 1.0`

```python
from mcp.server import Server
from mcp.types import ProgressNotification
import asyncio

server = Server("my-server")

@server.tool("web_search")
async def web_search(query: str, ctx) -> str:
    # 发送进度通知，防止客户端超时
    await ctx.report_progress(0, 100, "Starting search...")
    
    try:
        result = await asyncio.wait_for(
            do_actual_search(query),
            timeout=25.0  # Server 侧主动控制超时，预留 5s 给客户端
        )
        await ctx.report_progress(100, 100, "Search complete")
        return result
    except asyncio.TimeoutError:
        return "Search timed out. Please try a more specific query."
```

### 药方 2：客户端侧配置超时参数

```python
from mcp import ClientSession

async with ClientSession(transport, timeout=60) as session:
    result = await session.call_tool("web_search", {"query": "test"})
```

### 药方 3：切换到 SSE 传输模式（避免 stdio 缓冲问题）

如果是 stdio 传输模式导致的阻塞，考虑切换到 HTTP+SSE：

```json
{
  "mcpServers": {
    "my-server": {
      "url": "http://localhost:3001/sse"
    }
  }
}
```

## 🔗 参考资料
References

- [MCP Protocol Specification - Timeouts](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
