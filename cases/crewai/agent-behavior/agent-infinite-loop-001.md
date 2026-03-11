---
id: "crewai-agent-infinite-loop-001"
title: "CrewAI Agent 陷入无限循环，不断重复相同工具调用"
title_en: "CrewAI Agent stuck in infinite loop repeating the same tool call"
framework: "crewai"
framework_version: ">=0.28.0"
language: "python"
tags:
  - "infinite-loop"
  - "tool-calling"
  - "agent-behavior"
  - "llm-reasoning"
severity: "high"
complexity: "complex"
environment:
  python_version: ">=3.10"
  os: "any"
  dependencies:
    - "openai>=1.0"
    - "langchain-openai"
created_at: "2026-03-10"
updated_at: "2026-03-10"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases:
  - "autogen-agent-loop-001"
---

## 🏥 症状描述
Symptom Description

CrewAI Agent 在执行任务时，反复调用同一个工具（通常是搜索工具或网页抓取工具），进入无限循环。表现为：
- Agent 不断输出相同的思考和行动
- Token 消耗飙升，费用快速增长
- 任务永远无法完成

## 🔍 错误信息
Error Message

没有明确的错误消息，但日志中会出现类似以下的重复模式：

```
[Agent] Thinking: I need to search for more information about X
[Agent] Action: search_tool
[Agent] Input: "X related topic"
[Agent] Observation: [搜索结果]
[Agent] Thinking: I need to search for more information about X  ← 重复
[Agent] Action: search_tool                                      ← 重复
...（无限循环）
```

最终可能因 `max_iter` 或 Token 限制触发以下异常：

```python
CrewAIError: Agent exceeded maximum iterations (25)
```

## 🔬 根因分析
Root Cause Analysis

此问题通常由多个因素叠加导致：

### 1. LLM 推理能力不足
使用推理能力较弱的模型（如 GPT-3.5-turbo）时，Agent 难以判断何时「已收集到足够信息」，陷入不断搜索的循环。

### 2. 任务描述模糊
`Task.description` 缺乏明确的完成标准（Acceptance Criteria），导致 Agent 无法判断任务是否已完成。

### 3. 工具返回结果不够结构化
工具返回的是大段非结构化文本，Agent 难以从中提取关键信息，误认为需要继续搜索。

### 4. 上下文窗口溢出
当对话历史超过模型的上下文窗口后，Agent 丢失了之前的思考和行动记录。

## 📋 复现步骤
Steps to Reproduce

```python
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

researcher = Agent(
    role="Research Analyst",
    goal="Research everything about topic X",      # ← 目标过于宽泛
    backstory="You are a thorough researcher.",
    tools=[search_tool],
    llm="gpt-3.5-turbo",                          # ← 推理能力不足
    verbose=True,
)

task = Task(
    description="Research topic X thoroughly.",     # ← 无明确完成标准
    agent=researcher,
    expected_output="A comprehensive report.",
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()   # → 陷入无限循环
```

## 💊 药方
Prescriptions

### 药方 1：明确任务完成标准 + 限制迭代次数 ✅ 推荐

```python
researcher = Agent(
    role="Research Analyst",
    goal="Find the top 3 key facts about topic X and summarize them",  # ← 明确量化
    backstory="You are an efficient researcher who focuses on key findings.",
    tools=[search_tool],
    llm="gpt-4o",           # ← 使用更强的模型
    max_iter=10,             # ← 限制最大迭代次数
    verbose=True,
)

task = Task(
    description="""Research topic X. Your task is complete when you have:
    1. Found at least 3 credible sources
    2. Identified the top 3 key findings
    3. Written a summary of no more than 500 words
    
    DO NOT search more than 5 times. Synthesize from what you have.""",  # ← 明确完成标准
    agent=researcher,
    expected_output="A 500-word summary with 3 key findings and source links.",
)
```

### 药方 2：添加自定义工具调用限制

```python
class RateLimitedSearchTool:
    """包装搜索工具，添加调用次数限制"""
    def __init__(self, base_tool, max_calls=5):
        self.base_tool = base_tool
        self.max_calls = max_calls
        self.call_count = 0
    
    def run(self, query: str) -> str:
        self.call_count += 1
        if self.call_count > self.max_calls:
            return (
                f"Search limit reached ({self.max_calls} calls). "
                "Please synthesize findings from previous searches."
            )
        return self.base_tool.run(query)
```

### 药方 3：使用 CrewAI 内置的 `max_rpm` 和回调机制

```python
researcher = Agent(
    role="Research Analyst",
    goal="...",
    tools=[search_tool],
    max_iter=15,        # 最大迭代次数
    max_rpm=10,         # 每分钟最大请求数
    step_callback=lambda step: print(f"Step {step.step_number}: {step.action}"),
)
```

### 药方 4：切换为更强的 LLM

将 `gpt-3.5-turbo` 升级为 `gpt-4o` 或 `claude-sonnet-4-20250514`，显著降低循环概率。强模型更善于判断何时已收集到足够信息。

## 🧪 调试建议
Debugging Tips

1. 开启 `verbose=True` 观察 Agent 的思考链
2. 检查每次工具调用的输入是否在变化——如果完全相同，说明 Agent 已进入循环
3. 考虑将大任务拆分为多个小任务，每个任务有明确的输入/输出

## 🔗 参考资料
References

- [CrewAI Agent Configuration Docs](https://docs.crewai.com/core-concepts/agents/)
- [CrewAI Task Design Best Practices](https://docs.crewai.com/core-concepts/tasks/)

---

> 📝 本药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 如有更好方案欢迎 [提交 PR](https://github.com/CyberHuaTuo/CyberHuaTuo/pulls)
