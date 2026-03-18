---
id: "nourishing-sandbox-mcp-tool-security-005"
title: "MCP Tool 安全调用沙箱"
title_en: "Secure MCP Tool Calling Sandbox for AI Agents"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "mcp"
  - "tool-calling"
  - "sandbox"
  - "validation"
  - "audit"
severity: "critical"
complexity: "complex"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-18"
updated_at: "2026-03-18"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://modelcontextprotocol.io/docs/concepts/security"
related_cases:
  - "nourishing-sandbox-permission-boundary-004"
  - "nourishing-security-llm-output-sanitization-003"
---

## 🧬 滋补概述
Nourishing Overview

MCP（Model Context Protocol）是 AI Agent 调用外部工具的标准协议。每一次 MCP Tool 调用都是 Agent 与外部世界的交互边界 — 也是最容易被攻击利用的攻击面。本药方提供从参数校验到结果消毒的完整安全调用框架，在 Agent 和 Tool 之间建立一道「安全城墙」。

> ⚠️ **核心理念**：MCP Tool 调用 = 能力请求。每次调用必须经过「校验入参 → 权限确认 → 隔离执行 → 消毒出参 → 审计记录」五步闭环。

## 🏥 常见症状
Common Symptoms

- Agent 传递给 Tool 的参数未经校验（如 SQL 片段、文件路径）
- Tool 返回的结果包含系统敏感信息（环境变量、内部路径、数据库凭证）
- LLM 通过 Prompt 注入构造恶意 Tool 调用参数
- Tool 调用缺少超时和重试机制，导致 Agent 卡死
- 无法追溯「哪个 Agent 在什么时间调用了哪个 Tool」

## 🔬 MCP 安全调用架构
MCP Secure Call Architecture

```
┌─────────────────────────────────────────────────────┐
│                    AI Agent (LLM)                    │
│                 产出 Tool Call 请求                   │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│  🛡️ Layer 1: 参数校验 (Argument Validator)          │
│  ↓ Pydantic Schema 校验 + 危险模式过滤              │
├─────────────────────────────────────────────────────┤
│  🔑 Layer 2: 权限校验 (Permission Guard)            │
│  ↓ 能力注册表白名单 + 角色匹配                      │
├─────────────────────────────────────────────────────┤
│  📦 Layer 3: 隔离执行 (Execution Sandbox)           │
│  ↓ 独立进程/容器 + 超时控制 + 资源限制              │
├─────────────────────────────────────────────────────┤
│  🧹 Layer 4: 结果消毒 (Result Sanitizer)            │
│  ↓ 脱敏处理 + 长度截断 + 格式验证                   │
├─────────────────────────────────────────────────────┤
│  📊 Layer 5: 审计日志 (Audit Logger)                │
│  ↓ 结构化记录入参/出参/耗时/结果                    │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                MCP Tool Server                       │
└─────────────────────────────────────────────────────┘
```

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：MCP Tool 参数校验层 ✅ 核心必做

```python
import re
from pydantic import BaseModel, field_validator
from typing import Any, Optional


class ToolCallRequest(BaseModel):
    """MCP Tool 调用请求的安全校验模型"""
    tool_name: str
    arguments: dict[str, Any]
    caller_id: str = "unknown"  # 调用者标识

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        # 工具名只允许字母、数字、下划线、连字符
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_\-]{0,63}$", v):
            raise ValueError(f"非法工具名格式: {v}")
        return v

    @field_validator("arguments")
    @classmethod
    def validate_arguments(cls, v: dict) -> dict:
        for key, val in v.items():
            # 参数键名校验
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$", key):
                raise ValueError(f"非法参数名: {key}")

            # 字符串参数长度限制
            if isinstance(val, str) and len(val) > 50000:
                raise ValueError(
                    f"参数 '{key}' 长度超限: {len(val)} > 50000"
                )

            # 过滤危险模式
            if isinstance(val, str):
                dangerous_patterns = [
                    r";\s*(?:rm|del|drop|truncate)\s",
                    r"__import__\s*\(",
                    r"\beval\s*\(",
                    r"\bexec\s*\(",
                ]
                for pattern in dangerous_patterns:
                    if re.search(pattern, val, re.IGNORECASE):
                        raise ValueError(
                            f"参数 '{key}' 包含危险模式"
                        )
        return v


# 使用示例
try:
    request = ToolCallRequest(
        tool_name="search_knowledge_base",
        arguments={"query": "LangChain 配置错误", "top_k": 5},
        caller_id="agent-001",
    )
    print(f"✅ 参数校验通过: {request.tool_name}")
except ValueError as e:
    print(f"🚫 参数校验失败: {e}")
```

### 药方 2：Tool 执行结果消毒器

```python
import re
import os
from typing import Any


class ResultSanitizer:
    """
    MCP Tool 返回值消毒器

    防止 Tool 返回的结果中包含：
    1. 系统敏感信息（环境变量、内部路径）
    2. 数据库凭证或连接字符串
    3. 超长内容导致的 Token 浪费
    """

    # 需要脱敏的模式
    SENSITIVE_PATTERNS = [
        # API Keys
        (r"sk-[a-zA-Z0-9]{20,}", "sk-***REDACTED***"),
        (r"AKIA[A-Z0-9]{12,}", "AKIA***REDACTED***"),
        (r"ghp_[a-zA-Z0-9]{36,}", "ghp_***REDACTED***"),
        # 数据库连接串
        (
            r"(?:mysql|postgres|mongodb)://[^\s]+",
            "***DB_CONNECTION_REDACTED***"
        ),
        # IP 地址（内网）
        (
            r"\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)"
            r"\.\d{1,3}\.\d{1,3}\b",
            "***INTERNAL_IP***"
        ),
        # 文件系统绝对路径
        (r"/(?:home|root|etc|var)/[^\s]{5,}", "***PATH_REDACTED***"),
        (r"[A-Z]:\\(?:Users|Windows)[^\s]{5,}", "***PATH_REDACTED***"),
    ]

    @classmethod
    def sanitize(
        cls,
        result: Any,
        max_length: int = 10000,
    ) -> Any:
        """消毒 Tool 返回结果"""
        if isinstance(result, str):
            return cls._sanitize_string(result, max_length)
        elif isinstance(result, dict):
            return {
                k: cls.sanitize(v, max_length)
                for k, v in result.items()
            }
        elif isinstance(result, list):
            return [cls.sanitize(item, max_length) for item in result]
        return result

    @classmethod
    def _sanitize_string(cls, text: str, max_length: int) -> str:
        # 1. 过滤环境变量泄露
        for env_key in ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]:
            env_val = os.environ.get(env_key, "")
            if env_val and env_val in text:
                text = text.replace(env_val, "***REDACTED***")

        # 2. 正则脱敏
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            text = re.sub(pattern, replacement, text)

        # 3. 长度截断
        if len(text) > max_length:
            text = (
                text[:max_length]
                + f"\n\n[... 结果已截断，原始长度 {len(text)} 字符]"
            )

        return text
```

### 药方 3：结构化审计日志

```python
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class ToolCallAuditEntry:
    """MCP Tool 调用审计条目"""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    tool_name: str = ""
    caller_id: str = ""
    arguments_hash: str = ""     # 参数哈希（不记录明文）
    result_size: int = 0         # 返回结果大小
    duration_ms: float = 0       # 执行耗时
    status: str = "success"      # success / error / denied / timeout
    permission_check: str = ""   # 权限校验结果
    error_message: str = ""      # 错误信息（如有）


class ToolCallAuditor:
    """
    MCP Tool 调用审计器

    结构化记录每次 Tool 调用的完整生命周期。
    """

    def __init__(self, logger_name: str = "mcp.audit"):
        self._logger = logging.getLogger(logger_name)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [AUDIT] %(message)s")
        )
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def log_call(self, entry: ToolCallAuditEntry) -> None:
        """记录一次 Tool 调用"""
        self._logger.info(json.dumps(asdict(entry), ensure_ascii=False))

    def wrap_tool_call(self, tool_name: str, caller_id: str):
        """
        上下文管理器 — 自动记录 Tool 调用的审计信息

        Usage:
            with auditor.wrap_tool_call("search", "agent-1") as ctx:
                result = await tool.execute(args)
                ctx["result_size"] = len(str(result))
        """
        import hashlib
        from contextlib import contextmanager

        @contextmanager
        def _context():
            entry = ToolCallAuditEntry(
                tool_name=tool_name,
                caller_id=caller_id,
            )
            ctx = {}
            start = time.time()
            try:
                yield ctx
                entry.status = ctx.get("status", "success")
                entry.result_size = ctx.get("result_size", 0)
                entry.permission_check = ctx.get(
                    "permission_check", "passed"
                )
            except Exception as e:
                entry.status = "error"
                entry.error_message = str(e)[:200]
                raise
            finally:
                entry.duration_ms = round(
                    (time.time() - start) * 1000, 2
                )
                if "args_hash" in ctx:
                    entry.arguments_hash = ctx["args_hash"]
                self.log_call(entry)

        return _context()


# 使用示例
auditor = ToolCallAuditor()

# 在 Tool 调用中使用
# with auditor.wrap_tool_call("diagnose", "agent-001") as ctx:
#     result = await diagnose(query="...")
#     ctx["result_size"] = len(str(result))
```

## ⚠️ 安全要点

1. **参数校验不可跳过** — 即使 LLM 产出的参数「看起来正常」也必须校验
2. **结果消毒不可省略** — Tool 返回值在送回 LLM 前必须脱敏
3. **审计日志不可删改** — 考虑使用 append-only 存储或外部日志服务
4. **超时必须设置** — 每个 Tool 调用必须有超时限制（建议 30s）
5. **重试必须有退避** — 使用指数退避（exponential backoff）避免雪崩

## 🔗 参考资料
References

- [MCP Protocol Security](https://modelcontextprotocol.io/docs/concepts/security)
- [OWASP LLM06 - Excessive Agency](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
