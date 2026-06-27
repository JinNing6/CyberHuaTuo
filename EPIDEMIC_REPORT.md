# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-06-27
> **生成时间**: 2026-06-27T02:03:43.088112+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,758** |
| 📥 本周新增 New (7d) | **105** |
| ✅ 本周关闭 Closed (7d) | **98** |
| 💚 平均健康分 Avg Score | **45.3/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **mcp**
🥉 **autogen**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **crewai**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 61%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🐛 Bug 类 Issue 占比达 42%
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 63%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 44%

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **73.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 81 |
| 本周新增 New (7d) | 11 |
| 本月新增 New (30d) | 47 |
| 本周关闭 Closed (7d) | 11 |
| 本月关闭 Closed (30d) | 55 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟡 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **69.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 256 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 52 |
| 本周关闭 Closed (7d) | 28 |
| 本月关闭 Closed (30d) | 49 |
| Bug 类 Issues | 82 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[horizontal scaling] How to actually build session persistence in streamable htt](https://github.com/modelcontextprotocol/python-sdk/issues/880) (👍 24 / 💬 22)
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 22 / 💬 11)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28)
- [Bug Report: FastMCP `RuntimeError: Received request before initialization was co](https://github.com/modelcontextprotocol/python-sdk/issues/737) (👍 9)
- [FastMCP server with SSE transport fails to shut down on a signal](https://github.com/modelcontextprotocol/python-sdk/issues/514) (👍 6)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **59.5/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 544 |
| 本周新增 New (7d) | 2 |
| 本月新增 New (30d) | 22 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 6 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **59.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 415 |
| 本周新增 New (7d) | 21 |
| 本月新增 New (30d) | 120 |
| 本周关闭 Closed (7d) | 20 |
| 本月关闭 Closed (30d) | 88 |
| Bug 类 Issues | 83 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 31 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 23 / 💬 8)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **44.1/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 77 |
| 本周新增 New (7d) | 12 |
| 本月新增 New (30d) | 62 |
| 本周关闭 Closed (7d) | 6 |
| 本月关闭 Closed (30d) | 27 |
| Bug 类 Issues | 13 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] dependency conflict with OpenLIT](https://github.com/crewAIInc/crewAI/issues/5845) (👍 2)
- [Tool re-execution on task retry has no idempotency guard — duplicate payments, e](https://github.com/crewAIInc/crewAI/issues/5802) (👍 0)
- [[BUG] _parse_native_tool_call drops Bedrock Converse API tool arguments — always](https://github.com/crewAIInc/crewAI/issues/4972) (👍 0)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **41.8/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 336 |
| 本周新增 New (7d) | 32 |
| 本月新增 New (30d) | 147 |
| 本周关闭 Closed (7d) | 21 |
| 本月关闭 Closed (30d) | 236 |
| Bug 类 Issues | 205 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 61%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 15)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 30 / 💬 11)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 17)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [`AnthropicPromptCachingMiddleware` breaks model fallback with `cache_control` pa](https://github.com/langchain-ai/langchain/issues/33709) (👍 5)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **39.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 190 |
| 本周新增 New (7d) | 14 |
| 本月新增 New (30d) | 46 |
| 本周关闭 Closed (7d) | 10 |
| 本月关闭 Closed (30d) | 39 |
| Bug 类 Issues | 79 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 42%

**🔥 热门 Issues / Hot Issues**:
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 4)
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Handoff Issue: System Replies with Function Agent Message Instead of Resp](https://github.com/run-llama/llama_index/issues/19906) (👍 2)
- [[Bug]: S3 Vector Store: Filterable metadata must have at most 2048 bytes](https://github.com/run-llama/llama_index/issues/21062) (👍 1)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **27.3/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 293 |
| 本周新增 New (7d) | 2 |
| 本月新增 New (30d) | 20 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 9 |
| Bug 类 Issues | 86 |

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

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **21.6/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 357 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 53 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 12 |
| Bug 类 Issues | 158 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 44%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 50)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8 / 💬 17)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **17.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 209 |
| 本周新增 New (7d) | 3 |
| 本月新增 New (30d) | 9 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 20 |
| Bug 类 Issues | 131 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 63%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13 / 💬 3)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 22)

**🚨 高危 Issues / Critical Issues**:
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*