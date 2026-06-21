# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-06-21
> **生成时间**: 2026-06-21T02:34:44.358603+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,753** |
| 📥 本周新增 New (7d) | **125** |
| ✅ 本周关闭 Closed (7d) | **72** |
| 💚 平均健康分 Avg Score | **45.6/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **autogen**
🥉 **pydantic-ai**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **crewai**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 60%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 63%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] ⚠️ 关闭率偏低：本周新增 18，仅关闭 5
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 45%

---

## 📋 各框架详情 / Framework Details

### 🟢 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **83.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 81 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 45 |
| 本周关闭 Closed (7d) | 13 |
| 本月关闭 Closed (30d) | 51 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **58.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 544 |
| 本周新增 New (7d) | 8 |
| 本月新增 New (30d) | 23 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 5 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **54.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 414 |
| 本周新增 New (7d) | 24 |
| 本月新增 New (30d) | 139 |
| 本周关闭 Closed (7d) | 16 |
| 本月关闭 Closed (30d) | 94 |
| Bug 类 Issues | 84 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 30 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 23 / 💬 8)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)

---

### 🟠 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **45.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 280 |
| 本周新增 New (7d) | 18 |
| 本月新增 New (30d) | 57 |
| 本周关闭 Closed (7d) | 6 |
| 本月关闭 Closed (30d) | 23 |
| Bug 类 Issues | 84 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[horizontal scaling] How to actually build session persistence in streamable htt](https://github.com/modelcontextprotocol/python-sdk/issues/880) (👍 24 / 💬 22)
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27 / 💬 24)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 22 / 💬 10)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27)
- [Bug Report: FastMCP `RuntimeError: Received request before initialization was co](https://github.com/modelcontextprotocol/python-sdk/issues/737) (👍 9)
- [FastMCP server with SSE transport fails to shut down on a signal](https://github.com/modelcontextprotocol/python-sdk/issues/514) (👍 6)

---

### 🟠 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **44.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 186 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 36 |
| 本周关闭 Closed (7d) | 7 |
| 本月关闭 Closed (30d) | 34 |
| Bug 类 Issues | 68 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 3)
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Handoff Issue: System Replies with Function Agent Message Instead of Resp](https://github.com/run-llama/llama_index/issues/19906) (👍 2)
- [[Bug]: S3 Vector Store: Filterable metadata must have at most 2048 bytes](https://github.com/run-llama/llama_index/issues/21062) (👍 1)

---

### 🟠 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **43.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 291 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 23 |
| 本周关闭 Closed (7d) | 3 |
| 本月关闭 Closed (30d) | 12 |
| Bug 类 Issues | 85 |

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

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **41.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 71 |
| 本周新增 New (7d) | 14 |
| 本月新增 New (30d) | 59 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 26 |
| Bug 类 Issues | 13 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] dependency conflict with OpenLIT](https://github.com/crewAIInc/crewAI/issues/5845) (👍 2)
- [[BUG] Problems with OpenRouter thinking models](https://github.com/crewAIInc/crewAI/issues/5537) (👍 0)
- [[BUG] _parse_native_tool_call drops Bedrock Converse API tool arguments — always](https://github.com/crewAIInc/crewAI/issues/4972) (👍 0)

---

### 🔴 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **36.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 325 |
| 本周新增 New (7d) | 26 |
| 本月新增 New (30d) | 146 |
| 本周关闭 Closed (7d) | 16 |
| 本月关闭 Closed (30d) | 235 |
| Bug 类 Issues | 194 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 60%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 15)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 30 / 💬 11)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 17)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [`AnthropicPromptCachingMiddleware` breaks model fallback with `cache_control` pa](https://github.com/langchain-ai/langchain/issues/33709) (👍 5)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **31.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 355 |
| 本周新增 New (7d) | 18 |
| 本月新增 New (30d) | 61 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 12 |
| Bug 类 Issues | 158 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 18，仅关闭 5
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 45%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 50)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8 / 💬 15)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **17.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 206 |
| 本周新增 New (7d) | 1 |
| 本月新增 New (30d) | 12 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 20 |
| Bug 类 Issues | 129 |

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