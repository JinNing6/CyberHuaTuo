# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-05-06
> **生成时间**: 2026-05-06T01:47:20.967701+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,589** |
| 📥 本周新增 New (7d) | **88** |
| ✅ 本周关闭 Closed (7d) | **99** |
| 💚 平均健康分 Avg Score | **45.3/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **llamaindex**
🥉 **crewai**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 46%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [crewai] 🐛 Bug 类 Issue 占比达 44%
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 63%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] ⚠️ 关闭率偏低：本周新增 15，仅关闭 2
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 48%

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **65.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 95 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 34 |
| 本周关闭 Closed (7d) | 4 |
| 本月关闭 Closed (30d) | 41 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [Support both callback and generator-based streaming in all Chat Generators](https://github.com/deepset-ai/haystack/issues/8742) (👍 4 / 💬 9)
- [Support for Crawler in Haystack 2.x](https://github.com/deepset-ai/haystack/issues/6609) (👍 3 / 💬 9)

---

### 🟡 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **60.1/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 168 |
| 本周新增 New (7d) | 7 |
| 本月新增 New (30d) | 49 |
| 本周关闭 Closed (7d) | 14 |
| 本月关闭 Closed (30d) | 67 |
| Bug 类 Issues | 67 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 3)
- [[Feature Request]: Support for multiple schemas in SQLDatabase](https://github.com/run-llama/llama_index/issues/16644) (👍 5 / 💬 6)
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: PydanticUserError: The `__modify_schema__` method is not supported in Pyd](https://github.com/run-llama/llama_index/issues/16540) (👍 2)
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Handoff Issue: System Replies with Function Agent Message Instead of Resp](https://github.com/run-llama/llama_index/issues/19906) (👍 2)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **57.8/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 27 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 77 |
| 本周关闭 Closed (7d) | 44 |
| 本月关闭 Closed (30d) | 152 |
| Bug 类 Issues | 12 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 44%

**🚨 高危 Issues / Critical Issues**:
- [[BUG] crewai 1.12.2 uninstallable on Intel Macs: mandatory lancedb>=0.29.2  depe](https://github.com/crewAIInc/crewAI/issues/5327) (👍 1)
- [[BUG] Pydantic Validation Error with `security_context` in MCP Tools](https://github.com/crewAIInc/crewAI/issues/4796) (👍 0)
- [[ Bug]:  YoutubeChannelSearchTool Fails for Valid Channel Inputs](https://github.com/crewAIInc/crewAI/issues/5429) (👍 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **57.1/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 368 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 93 |
| 本周关闭 Closed (7d) | 10 |
| 本月关闭 Closed (30d) | 155 |
| Bug 类 Issues | 58 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 27 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 22 / 💬 8)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 22 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [Google support both function tools and built-in tools](https://github.com/pydantic/pydantic-ai/issues/4788) (👍 6)
- [Parallel MCP servers: `RuntimeError: Attempted to exit cancel scope in a differe](https://github.com/pydantic/pydantic-ai/issues/2818) (👍 6)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **52.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 515 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 28 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 5 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **44.6/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 393 |
| 本周新增 New (7d) | 21 |
| 本月新增 New (30d) | 139 |
| 本周关闭 Closed (7d) | 22 |
| 本月关闭 Closed (30d) | 101 |
| Bug 类 Issues | 182 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 46%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 15)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 14)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 29 / 💬 7)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Bug bounty](https://github.com/langchain-ai/langchain/issues/36952) (👍 11)
- [MongoDB Toolkit fails with Firestore MongoDB-compatible endpoint due to unsuppor](https://github.com/langchain-ai/langchain/issues/36609) (👍 12)

---

### 🟠 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **42.8/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 303 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 26 |
| 本周关闭 Closed (7d) | 3 |
| 本月关闭 Closed (30d) | 19 |
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
**框架**: `mcp` | **健康分数 Health Score**: **33.1/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 243 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 27 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 6 |
| Bug 类 Issues | 82 |

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

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **23.1/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 284 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 57 |
| 本周关闭 Closed (7d) | 2 |
| 本月关闭 Closed (30d) | 15 |
| Bug 类 Issues | 136 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 15，仅关闭 2
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 48%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 47)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8 / 💬 11)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 5 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 8)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **17.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 193 |
| 本周新增 New (7d) | 2 |
| 本月新增 New (30d) | 18 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 1 |
| Bug 类 Issues | 122 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 63%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 20)
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