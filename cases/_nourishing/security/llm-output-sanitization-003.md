---
id: "nourishing-security-llm-output-sanitization-003"
title: "LLM 输出消毒指南"
title_en: "LLM Output Sanitization Guide for AI Agents"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "output-sanitization"
  - "xss"
  - "injection"
  - "llm-safety"
severity: "high"
complexity: "moderate"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases:
  - "nourishing-security-prompt-injection-002"
---

## 🧬 滋补概述
Nourishing Overview

LLM 的输出是不可信的 — 无论 System Prompt 如何约束，LLM 都可能生成包含恶意内容的输出。当 Agent 的输出被直接渲染到 Web 页面、执行为代码、或拼接到 SQL/Shell 命令中时，就形成了安全漏洞链。

## 🏥 常见症状
Common Symptoms

- LLM 输出的 HTML 被直接 innerHTML 渲染导致 XSS
- Agent 生成的 SQL 查询被直接执行导致 SQL 注入
- LLM 输出的 Shell 命令被 `os.system()` 执行
- Agent 生成的文件名包含路径遍历字符（`../../`）

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：分层输出消毒

```python
import html
import re
import shlex
from typing import Optional


class OutputSanitizer:
    """LLM 输出消毒器"""

    @staticmethod
    def for_html(text: str) -> str:
        """HTML 上下文消毒 — 防 XSS"""
        return html.escape(text)

    @staticmethod
    def for_sql_param(value: str) -> str:
        """SQL 参数消毒 — 但更推荐使用参数化查询"""
        # 移除 SQL 元字符
        return re.sub(r"[;'\"\\--]", "", value)

    @staticmethod
    def for_shell(command_part: str) -> str:
        """Shell 命令消毒"""
        return shlex.quote(command_part)

    @staticmethod
    def for_filename(name: str) -> str:
        """文件名消毒 — 防路径遍历"""
        # 移除路径分隔符和特殊字符
        sanitized = re.sub(r'[/\\:*?"<>|]', '_', name)
        # 移除路径遍历
        sanitized = sanitized.replace('..', '_')
        # 限制长度
        return sanitized[:255]

    @staticmethod
    def for_url(url: str) -> Optional[str]:
        """URL 消毒 — 只允许 http/https"""
        if re.match(r'^https?://', url, re.IGNORECASE):
            return url
        return None  # 拒绝非 HTTP URL（如 javascript:、data:）


# 使用示例
llm_output = '<script>alert("xss")</script> Hello!'

# Web 渲染
safe_html = OutputSanitizer.for_html(llm_output)
# → '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt; Hello!'

# 文件保存
safe_name = OutputSanitizer.for_filename("../../etc/passwd")
# → '____etc_passwd'
```

### 药方 2：结构化输出验证

```python
from pydantic import BaseModel, validator
from typing import List, Optional


class AgentToolCall(BaseModel):
    """强制 Agent 输出符合预定义结构"""
    tool_name: str
    arguments: dict
    reasoning: str

    @validator("tool_name")
    def validate_tool_name(cls, v):
        allowed_tools = ["search", "calculate", "summarize", "translate"]
        if v not in allowed_tools:
            raise ValueError(f"不允许的工具: {v}")
        return v

    @validator("arguments")
    def validate_arguments(cls, v):
        # 检查参数中是否有异常长度
        for key, val in v.items():
            if isinstance(val, str) and len(val) > 10000:
                raise ValueError(f"参数 {key} 长度异常")
        return v


# 使用：解析 LLM 的 JSON 输出
import json

try:
    raw = json.loads(llm_json_output)
    call = AgentToolCall(**raw)  # 自动验证
except (json.JSONDecodeError, ValueError) as e:
    print(f"⚠️ Agent 输出不合规: {e}")
```

## 🔗 参考资料
References

- [OWASP Output Encoding](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP LLM06 - Excessive Agency](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
