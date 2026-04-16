# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-04-16
> **生成时间**: 2026-04-16T01:26:23.997241+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,582** |
| 📥 本周新增 New (7d) | **132** |
| ✅ 本周关闭 Closed (7d) | **109** |
| 💚 平均健康分 Avg Score | **46.7/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **pydantic-ai**
🥈 **haystack**
🥉 **autogen**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 44%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 64%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 50%

---

## 📋 各框架详情 / Framework Details

### 🟢 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **80.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 366 |
| 本周新增 New (7d) | 20 |
| 本月新增 New (30d) | 107 |
| 本周关闭 Closed (7d) | 39 |
| 本月关闭 Closed (30d) | 165 |
| Bug 类 Issues | 63 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 27 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 22 / 💬 7)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 22 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [Parallel MCP servers: `RuntimeError: Attempted to exit cancel scope in a differe](https://github.com/pydantic/pydantic-ai/issues/2818) (👍 6)
- [Google support both function tools and built-in tools](https://github.com/pydantic/pydantic-ai/issues/4788) (👍 3)

---

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **72.7/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 100 |
| 本周新增 New (7d) | 13 |
| 本月新增 New (30d) | 58 |
| 本周关闭 Closed (7d) | 11 |
| 本月关闭 Closed (30d) | 46 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [Support both callback and generator-based streaming in all Chat Generators](https://github.com/deepset-ai/haystack/issues/8742) (👍 4 / 💬 9)
- [Support for Crawler in Haystack 2.x](https://github.com/deepset-ai/haystack/issues/6609) (👍 3 / 💬 9)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **58.9/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 506 |
| 本周新增 New (7d) | 8 |
| 本月新增 New (30d) | 52 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 4 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **57.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 89 |
| 本周新增 New (7d) | 23 |
| 本月新增 New (30d) | 98 |
| 本周关闭 Closed (7d) | 29 |
| 本月关闭 Closed (30d) | 93 |
| Bug 类 Issues | 29 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] Do not invoke synchronous `call()` on LLM from asynchronous workflow in `_](https://github.com/crewAIInc/crewAI/issues/5230) (👍 1)
- [[BUG] crewai 1.12.2 uninstallable on Intel Macs: mandatory lancedb>=0.29.2  depe](https://github.com/crewAIInc/crewAI/issues/5327) (👍 1)
- [[BUG] / [HELP] "Model does not support multimodal input [...] Use a vision-capab](https://github.com/crewAIInc/crewAI/issues/5137) (👍 0)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **36.7/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 300 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 38 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 22 |
| Bug 类 Issues | 80 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [How do I optimise for F1 score?](https://github.com/stanfordnlp/dspy/issues/556) (👍 11 / 💬 6)
- [Better async support](https://github.com/stanfordnlp/dspy/issues/1975) (👍 12 / 💬 3)
- [[Notice] LiteLLM Supply Chain Attack](https://github.com/stanfordnlp/dspy/issues/9500) (👍 9 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [[Bug] TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_se](https://github.com/stanfordnlp/dspy/issues/8762) (👍 5)
- [[Bug] ChainOfThoughtWithHint is broken (at least for Azure)](https://github.com/stanfordnlp/dspy/issues/8205) (👍 2)
- [[Bug] Bus error on import when cache on network drive (occurs rarely on some mac](https://github.com/stanfordnlp/dspy/issues/8799) (👍 2)

---

### 🔴 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **36.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 228 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 26 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 35 |
| Bug 类 Issues | 75 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[horizontal scaling] How to actually build session persistence in streamable htt](https://github.com/modelcontextprotocol/python-sdk/issues/880) (👍 23 / 💬 17)
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27 / 💬 23)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 22 / 💬 10)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27)
- [sse_app() ignores mount prefix, resulting in 404 from client](https://github.com/modelcontextprotocol/python-sdk/issues/412) (👍 13)
- [Bug Report: FastMCP `RuntimeError: Received request before initialization was co](https://github.com/modelcontextprotocol/python-sdk/issues/737) (👍 9)

---

### 🔴 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **36.3/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 372 |
| 本周新增 New (7d) | 30 |
| 本月新增 New (30d) | 195 |
| 本周关闭 Closed (7d) | 13 |
| 本月关闭 Closed (30d) | 120 |
| Bug 类 Issues | 165 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 44%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 14)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 29 / 💬 5)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 13 / 💬 14)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [MongoDB Toolkit fails with Firestore MongoDB-compatible endpoint due to unsuppor](https://github.com/langchain-ai/langchain/issues/36609) (👍 13)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 11)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **34.3/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 183 |
| 本周新增 New (7d) | 10 |
| 本月新增 New (30d) | 74 |
| 本周关闭 Closed (7d) | 6 |
| 本月关闭 Closed (30d) | 77 |
| Bug 类 Issues | 72 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 3)
- [[Feature Request]: Support for multiple schemas in SQLDatabase](https://github.com/run-llama/llama_index/issues/16644) (👍 5 / 💬 5)
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: TypeError when parsing MCP tool schemas with `additionalProperties: false](https://github.com/run-llama/llama_index/issues/19899) (👍 3)
- [[Bug]: PydanticUserError: The `__modify_schema__` method is not supported in Pyd](https://github.com/run-llama/llama_index/issues/16540) (👍 2)
- [[Bug]: `thinking_delta` not populated on AgentStream events when thinking is ena](https://github.com/run-llama/llama_index/issues/20349) (👍 2)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **29.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 253 |
| 本周新增 New (7d) | 11 |
| 本月新增 New (30d) | 56 |
| 本周关闭 Closed (7d) | 7 |
| 本月关闭 Closed (30d) | 20 |
| Bug 类 Issues | 126 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 50%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 11 / 💬 47)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 7 / 💬 9)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 5 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 11)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 7)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **24.1/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 185 |
| 本周新增 New (7d) | 7 |
| 本月新增 New (30d) | 19 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 2 |
| Bug 类 Issues | 119 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 64%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 20)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 12 / 💬 3)

**🚨 高危 Issues / Critical Issues**:
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 12)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*