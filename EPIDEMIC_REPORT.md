# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-03-17
> **生成时间**: 2026-03-17T01:08:25.525825+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,445** |
| 📥 本周新增 New (7d) | **168** |
| ✅ 本周关闭 Closed (7d) | **92** |
| 💚 平均健康分 Avg Score | **45.3/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **mcp**
🥉 **llamaindex**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **crewai**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **pydantic-ai**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] ⚠️ 关闭率偏低：本周新增 50，仅关闭 14
- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 46%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🐛 Bug 类 Issue 占比达 41%
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 65%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] ⚠️ 关闭率偏低：本周新增 21，仅关闭 2
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] ⚠️ 关闭率偏低：本周新增 16，仅关闭 1
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 53%

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **73.8/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 88 |
| 本周新增 New (7d) | 8 |
| 本月新增 New (30d) | 37 |
| 本周关闭 Closed (7d) | 10 |
| 本月关闭 Closed (30d) | 50 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [Support both callback and generator-based streaming in all Chat Generators](https://github.com/deepset-ai/haystack/issues/8742) (👍 4 / 💬 9)
- [Support for Crawler in Haystack 2.x](https://github.com/deepset-ai/haystack/issues/6609) (👍 3 / 💬 7)

---

### 🟡 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **60.6/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 237 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 44 |
| 本周关闭 Closed (7d) | 12 |
| 本月关闭 Closed (30d) | 57 |
| Bug 类 Issues | 92 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[horizontal scaling] How to actually build session persistence in streamable htt](https://github.com/modelcontextprotocol/python-sdk/issues/880) (👍 23 / 💬 17)
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27 / 💬 23)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 21 / 💬 10)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 27)
- [sse_app() ignores mount prefix, resulting in 404 from client](https://github.com/modelcontextprotocol/python-sdk/issues/412) (👍 13)
- [MCP Server Session Lost in Multi-Worker Environment](https://github.com/modelcontextprotocol/python-sdk/issues/520) (👍 13)

---

### 🟠 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **59.1/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 191 |
| 本周新增 New (7d) | 22 |
| 本月新增 New (30d) | 64 |
| 本周关闭 Closed (7d) | 36 |
| 本月关闭 Closed (30d) | 126 |
| Bug 类 Issues | 78 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 41%

**🔥 热门 Issues / Hot Issues**:
- [[Bug]: Structured Outputs sometimes return string instead of Pydantic Model](https://github.com/run-llama/llama_index/issues/16604) (👍 14 / 💬 13)
- [[Documentation]: Suggestion: Adding llms.txt to llamaindex documentation website](https://github.com/run-llama/llama_index/issues/17752) (👍 7 / 💬 2)
- [[Feature Request]: Support for multiple schemas in SQLDatabase](https://github.com/run-llama/llama_index/issues/16644) (👍 5 / 💬 5)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: Structured Outputs sometimes return string instead of Pydantic Model](https://github.com/run-llama/llama_index/issues/16604) (👍 14)
- [[Bug]: VectorStoreIndex.delete_ref_doc not working](https://github.com/run-llama/llama_index/issues/15529) (👍 4)
- [[Bug]: TypeError when parsing MCP tool schemas with `additionalProperties: false](https://github.com/run-llama/llama_index/issues/19899) (👍 3)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **57.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 456 |
| 本周新增 New (7d) | 9 |
| 本月新增 New (30d) | 26 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 3 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **47.3/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 428 |
| 本周新增 New (7d) | 21 |
| 本月新增 New (30d) | 133 |
| 本周关闭 Closed (7d) | 2 |
| 本月关闭 Closed (30d) | 91 |
| Bug 类 Issues | 78 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 21，仅关闭 2
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 25 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 21 / 💬 7)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 19 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [OTel attributes are incomplete when using `Agent.run_stream_sync`](https://github.com/pydantic/pydantic-ai/issues/3714) (👍 7)
- [Parallel MCP servers: `RuntimeError: Attempted to exit cancel scope in a differe](https://github.com/pydantic/pydantic-ai/issues/2818) (👍 5)
- [RuntimeError: Event loop is closed when using GoogleModel with asyncio.run()](https://github.com/pydantic/pydantic-ai/issues/3762) (👍 3)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **40.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 86 |
| 本周新增 New (7d) | 21 |
| 本月新增 New (30d) | 79 |
| 本周关闭 Closed (7d) | 12 |
| 本月关闭 Closed (30d) | 43 |
| Bug 类 Issues | 32 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] TaskOutput.pydantic is None on first guardrail attempt but parsed on retri](https://github.com/crewAIInc/crewAI/issues/4369) (👍 1)
- [[BUG] Bedrock LLM Claude Sonnet returning empty Input Params on Tools calling wi](https://github.com/crewAIInc/crewAI/issues/4470) (👍 0)
- [[BUG] Regression in CrewAI 1.9.3: custom BaseTool wrapper around BedrockKBRetrie](https://github.com/crewAIInc/crewAI/issues/4495) (👍 0)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **39.0/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 284 |
| 本周新增 New (7d) | 14 |
| 本月新增 New (30d) | 29 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 33 |
| Bug 类 Issues | 76 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [How do I optimise for F1 score?](https://github.com/stanfordnlp/dspy/issues/556) (👍 10 / 💬 6)
- [Better async support](https://github.com/stanfordnlp/dspy/issues/1975) (👍 12 / 💬 3)
- [[Feature] Support for Video](https://github.com/stanfordnlp/dspy/issues/8507) (👍 14 / 💬 10)

**🚨 高危 Issues / Critical Issues**:
- [[Bug] TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_se](https://github.com/stanfordnlp/dspy/issues/8762) (👍 5)
- [[Bug] ChainOfThoughtWithHint is broken (at least for Azure)](https://github.com/stanfordnlp/dspy/issues/8205) (👍 2)
- [[Bug] Bus error on import when cache on network drive (occurs rarely on some mac](https://github.com/stanfordnlp/dspy/issues/8799) (👍 2)

---

### 🔴 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **38.0/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 293 |
| 本周新增 New (7d) | 50 |
| 本月新增 New (30d) | 126 |
| 本周关闭 Closed (7d) | 14 |
| 本月关闭 Closed (30d) | 68 |
| Bug 类 Issues | 136 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 50，仅关闭 14
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 46%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 12)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 12 / 💬 12)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 25 / 💬 2)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [`AnthropicPromptCachingMiddleware` breaks model fallback with `cache_control` pa](https://github.com/langchain-ai/langchain/issues/33709) (👍 5)
- [Unsupported early_stopping_method="generate" in AgentExecutor after reaching ite](https://github.com/langchain-ai/langchain/issues/16263) (👍 6)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **20.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 213 |
| 本周新增 New (7d) | 16 |
| 本月新增 New (30d) | 54 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 17 |
| Bug 类 Issues | 112 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 16，仅关闭 1
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 53%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 11 / 💬 47)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 6 / 💬 6)
- [In Langgraph studio the subgraph part is not shown when we invoke the subgraphs ](https://github.com/langchain-ai/langgraph/issues/3372) (👍 4 / 💬 15)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 11)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 6)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **17.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 169 |
| 本周新增 New (7d) | 2 |
| 本月新增 New (30d) | 26 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 7 |
| Bug 类 Issues | 110 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 65%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 20)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11 / 💬 2)

**🚨 高危 Issues / Critical Issues**:
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 11)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*