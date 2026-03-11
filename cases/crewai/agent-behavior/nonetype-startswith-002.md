---
id: "crewai-nonetype-startswith-002"
title: "CrewAI Agent 执行时报 NoneType object has no attribute startswith"
title_en: "CrewAI Agent raises NoneType object has no attribute startswith during execution"
framework: "crewai"
framework_version: ">=0.30.0"
language: "python"
tags:
  - "agent-behavior"
  - "tool-calling"
severity: "high"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://github.com/crewAIInc/crewAI/issues/668"
related_cases: []
---

## 🏥 症状描述
Symptom Description

CrewAI Agent 在执行 Task 时，调用 Tool 后返回 `None`，导致后续处理逻辑尝试对 `None` 调用字符串方法而崩溃。该 Issue 有 18 条评论，是 CrewAI 中最常见的运行时错误之一。

## 🔍 错误信息
Error Message

```python
AttributeError: 'NoneType' object has no attribute 'startswith'
```

完整堆栈通常指向 CrewAI 内部的工具调用处理逻辑：

```
File "crewai/tools/tool_calling.py", line XX, in _run
    if result.startswith("Error"):
AttributeError: 'NoneType' object has no attribute 'startswith'
```

## 🔬 根因分析
Root Cause Analysis

1. **自定义 Tool 返回了 None**：CrewAI 期望所有 Tool 返回字符串类型，但自定义 Tool 在某些分支路径上返回了 `None`
2. **异常被静默吞掉**：Tool 内部发生异常但被 `try/except` 捕获后没有返回有意义的信息
3. **LLM 传递了错误的参数给 Tool**：导致 Tool 执行失败返回空值

## 💊 药方
Prescriptions

### 药方 1：确保 Tool 始终返回字符串 ✅ 推荐

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")

class SearchTool(BaseTool):
    name: str = "search"
    description: str = "搜索知识库"
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        try:
            results = do_search(query)
            if not results:
                return "未找到相关结果，请尝试其他关键词。"
            return str(results)  # 确保返回字符串
        except Exception as e:
            return f"搜索工具执行出错: {str(e)}"  # 异常也返回字符串
```

### 药方 2：使用 @tool 装饰器并添加类型注解

```python
from crewai import tool

@tool("Search Tool")
def search_tool(query: str) -> str:
    """搜索知识库获取信息"""
    result = do_search(query)
    return result if result else "No results found."
```

### 药方 3：升级 CrewAI 到最新版本

```bash
pip install crewai --upgrade
```

较新版本的 CrewAI 已增加了对 Tool 返回值的空值保护。

## 🔗 参考资料
References

- [CrewAI Issue #668](https://github.com/crewAIInc/crewAI/issues/668) — 18 条评论
- [CrewAI Custom Tools](https://docs.crewai.com/how-to/create-custom-tools/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 来源于 GitHub Issue #668（18 条评论）
