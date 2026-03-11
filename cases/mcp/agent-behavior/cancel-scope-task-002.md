---
id: "mcp-cancel-scope-task-002"
title: "MCP Server RuntimeError: Attempted to exit cancel scope in different task"
title_en: "MCP Server RuntimeError: Attempted to exit cancel scope in different task"
framework: "mcp"
framework_version: ">=1.0.0"
language: "python"
tags:
  - "agent-behavior"
  - "performance"
severity: "critical"
complexity: "complex"
environment:
  python_version: ">=3.10"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/modelcontextprotocol/python-sdk/issues/521"
related_cases: []
---

## 🏥 症状描述
Symptom Description

MCP Server 在处理并发请求时突然崩溃，抛出 `RuntimeError` 关于 cancel scope 的异步任务冲突。该问题在 MCP Python SDK 中是高赞 Issue，影响所有使用 anyio/trio 风格异步的 MCP Server。

## 🔍 错误信息
Error Message

```python
RuntimeError: Attempted to exit cancel scope in a different task 
than it was entered in
```

或

```
RuntimeError: This cancel scope is not active
```

完整堆栈通常涉及 anyio 的 cancel scope：

```
File "anyio/_backends/_asyncio.py", line XXX, in __aexit__
    raise RuntimeError("Attempted to exit cancel scope in a different task")
```

## 🔬 根因分析
Root Cause Analysis

1. **anyio CancelScope 在不同 Task 之间被共享**：MCP Python SDK 使用 anyio 进行异步操作，CancelScope 对象不能跨 Task 使用
2. **并发请求导致 Context 混淆**：多个客户端同时请求时，Server 端的异步上下文管理出现问题
3. **生命周期管理不当**：Server 的某些资源在异步 Context Manager 之外被访问

## 💊 药方
Prescriptions

### 药方 1：升级 MCP Python SDK ✅ 推荐

```bash
pip install mcp --upgrade
```

多个 cancel scope 相关的 bug 在 v1.2+ 版本中已修复。

### 药方 2：确保 Tool Handler 是 async 安全的

```python
from mcp.server import Server
import mcp.types as types

server = Server("my-server")

@server.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # ✅ 不要在 tool handler 里创建新的 Task
    # ✅ 不要使用 threading 混合 asyncio
    result = await async_operation(arguments)
    return [types.TextContent(type="text", text=str(result))]
```

### 药方 3：避免在 handler 中使用 asyncio.create_task

```python
# ❌ 错误：在 handler 中创建新 Task
@server.call_tool()
async def bad_handler(name: str, arguments: dict):
    task = asyncio.create_task(some_operation())  # 会导致 cancel scope 问题
    result = await task
    return [types.TextContent(type="text", text=result)]

# ✅ 正确：直接 await
@server.call_tool()
async def good_handler(name: str, arguments: dict):
    result = await some_operation()  # 在同一个 task 中执行
    return [types.TextContent(type="text", text=result)]
```

### 药方 4：使用 anyio.create_task_group 替代

```python
import anyio

@server.call_tool()
async def handler(name: str, arguments: dict):
    results = []
    async with anyio.create_task_group() as tg:
        # 在 task group 内安全地运行并发操作
        tg.start_soon(fetch_data, "source1", results)
        tg.start_soon(fetch_data, "source2", results)
    return [types.TextContent(type="text", text=str(results))]
```

## 🔗 参考资料
References

- [MCP Python SDK Issue #521](https://github.com/modelcontextprotocol/python-sdk/issues/521) — 7 条评论
- [anyio Documentation - Cancel Scopes](https://anyio.readthedocs.io/en/stable/cancellation.html)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #521
