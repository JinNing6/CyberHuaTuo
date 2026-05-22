# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-05-22
> **生成时间**: 2026-05-22T02:07:27.096314+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,664** |
| 📥 本周新增 New (7d) | **128** |
| ✅ 本周关闭 Closed (7d) | **100** |
| 💚 平均健康分 Avg Score | **46.7/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **pydantic-ai**
🥈 **mcp**
🥉 **haystack**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **crewai**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 47%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] ⚠️ 关闭率偏低：本周新增 17，仅关闭 1
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 59%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 47%

---

## 📋 各框架详情 / Framework Details

### 🟡 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **70.1/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 368 |
| 本周新增 New (7d) | 17 |
| 本月新增 New (30d) | 108 |
| 本周关闭 Closed (7d) | 26 |
| 本月关闭 Closed (30d) | 97 |
| Bug 类 Issues | 58 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 28 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 22 / 💬 8)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 22 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [RuntimeError: Event loop is closed when using GoogleModel with asyncio.run()](https://github.com/pydantic/pydantic-ai/issues/3762) (👍 3)
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)

---

### 🟡 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **69.5/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 245 |
| 本周新增 New (7d) | 11 |
| 本月新增 New (30d) | 42 |
| 本周关闭 Closed (7d) | 24 |
| 本月关闭 Closed (30d) | 32 |
| Bug 类 Issues | 76 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[horizontal scaling] How to actually build session persistence in streamable htt](https://github.com/modelcontextprotocol/python-sdk/issues/880) (👍 24 / 💬 18)
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27 / 💬 24)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 22 / 💬 10)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27)
- [Bug Report: FastMCP `RuntimeError: Received request before initialization was co](https://github.com/modelcontextprotocol/python-sdk/issues/737) (👍 9)
- [FastMCP server with SSE transport fails to shut down on a signal](https://github.com/modelcontextprotocol/python-sdk/issues/514) (👍 6)

---

### 🟠 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **58.8/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 91 |
| 本周新增 New (7d) | 8 |
| 本月新增 New (30d) | 25 |
| 本周关闭 Closed (7d) | 2 |
| 本月关闭 Closed (30d) | 20 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [Support both callback and generator-based streaming in all Chat Generators](https://github.com/deepset-ai/haystack/issues/8742) (👍 4 / 💬 9)
- [Support for Crawler in Haystack 2.x](https://github.com/deepset-ai/haystack/issues/6609) (👍 3 / 💬 9)
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **52.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 526 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 24 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 8 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **45.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 414 |
| 本周新增 New (7d) | 26 |
| 本月新增 New (30d) | 126 |
| 本周关闭 Closed (7d) | 24 |
| 本月关闭 Closed (30d) | 99 |
| Bug 类 Issues | 196 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 47%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 15)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 15)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 30 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Bug bounty](https://github.com/langchain-ai/langchain/issues/36952) (👍 12)
- [MongoDB Toolkit fails with Firestore MongoDB-compatible endpoint due to unsuppor](https://github.com/langchain-ai/langchain/issues/36609) (👍 12)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **39.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 184 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 51 |
| 本周关闭 Closed (7d) | 8 |
| 本月关闭 Closed (30d) | 50 |
| Bug 类 Issues | 69 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 3)
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: Handoff Issue: System Replies with Function Agent Message Instead of Resp](https://github.com/run-llama/llama_index/issues/19906) (👍 2)
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)

---

### 🔴 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **38.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 35 |
| 本周新增 New (7d) | 10 |
| 本月新增 New (30d) | 50 |
| 本周关闭 Closed (7d) | 6 |
| 本月关闭 Closed (30d) | 101 |
| Bug 类 Issues | 11 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG]No AI assistant in the docuement](https://github.com/crewAIInc/crewAI/issues/5542) (👍 1)
- [[BUG] Problems with OpenRouter thinking models](https://github.com/crewAIInc/crewAI/issues/5537) (👍 0)
- [[BUG] A2A - pydantic error, when AgentCard-skill-id <> endpoint url. (1.3.0)](https://github.com/crewAIInc/crewAI/issues/3897) (👍 0)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **37.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 280 |
| 本周新增 New (7d) | 3 |
| 本月新增 New (30d) | 17 |
| 本周关闭 Closed (7d) | 2 |
| 本月关闭 Closed (30d) | 36 |
| Bug 类 Issues | 79 |

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
**框架**: `langgraph` | **健康分数 Health Score**: **32.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 306 |
| 本周新增 New (7d) | 16 |
| 本月新增 New (30d) | 51 |
| 本周关闭 Closed (7d) | 7 |
| 本月关闭 Closed (30d) | 9 |
| Bug 类 Issues | 145 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 47%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 48)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8 / 💬 11)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **22.9/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 215 |
| 本周新增 New (7d) | 17 |
| 本月新增 New (30d) | 31 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 2 |
| Bug 类 Issues | 127 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 17，仅关闭 1
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 59%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 21)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13 / 💬 3)

**🚨 高危 Issues / Critical Issues**:
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*