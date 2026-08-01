# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-08-01
> **生成时间**: 2026-08-01T01:45:42.690872+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **2,924** |
| 📥 本周新增 New (7d) | **213** |
| ✅ 本周关闭 Closed (7d) | **121** |
| 💚 平均健康分 Avg Score | **45.3/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **mcp**
🥉 **pydantic-ai**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **crewai**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 65%
- [crewai] ⚠️ 关闭率偏低：本周新增 22，仅关闭 4
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 61%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] ⚠️ 本周新增 116 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🐛 Bug 类 Issue 占比达 42%

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **75.5/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 74 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 29 |
| 本周关闭 Closed (7d) | 9 |
| 本月关闭 Closed (30d) | 25 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟡 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **66.7/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 232 |
| 本周新增 New (7d) | 10 |
| 本月新增 New (30d) | 36 |
| 本周关闭 Closed (7d) | 22 |
| 本月关闭 Closed (30d) | 51 |
| Bug 类 Issues | 71 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 22 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28)
- [FastMCP server with SSE transport fails to shut down on a signal](https://github.com/modelcontextprotocol/python-sdk/issues/514) (👍 6)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)

---

### 🟡 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **60.0/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 418 |
| 本周新增 New (7d) | 116 |
| 本月新增 New (30d) | 271 |
| 本周关闭 Closed (7d) | 66 |
| 本月关闭 Closed (30d) | 234 |
| Bug 类 Issues | 71 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 116 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 32 / 💬 2)
- [Support for OpenAI Realtime API and equivalents (AWS Nova Sonic, etc)](https://github.com/pydantic/pydantic-ai/issues/1447) (👍 23 / 💬 8)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)

**🚨 高危 Issues / Critical Issues**:
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)
- [Extract thinking from thinking tags not occurring in individual chunks](https://github.com/pydantic/pydantic-ai/issues/3007) (👍 1)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **52.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 558 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 19 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 9 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **46.5/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 97 |
| 本周新增 New (7d) | 22 |
| 本月新增 New (30d) | 49 |
| 本周关闭 Closed (7d) | 4 |
| 本月关闭 Closed (30d) | 40 |
| Bug 类 Issues | 12 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 22，仅关闭 4
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [Tool re-execution on task retry has no idempotency guard — duplicate payments, e](https://github.com/crewAIInc/crewAI/issues/5802) (👍 0)
- [[BUG] Async tools are not awaited natively under native-function-calling models ](https://github.com/crewAIInc/crewAI/issues/6611) (👍 0)
- [[BUG] input_files (PDFFile) are passed as base64 via read_file tool, causing con](https://github.com/crewAIInc/crewAI/issues/5930) (👍 0)

---

### 🔴 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **38.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 390 |
| 本周新增 New (7d) | 27 |
| 本月新增 New (30d) | 137 |
| 本周关闭 Closed (7d) | 15 |
| 本月关闭 Closed (30d) | 90 |
| Bug 类 Issues | 252 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 65%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 15)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 18)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 30 / 💬 12)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [Performance: transformers are imported unconditionally on BaseChatModel import](https://github.com/langchain-ai/langchain/issues/36835) (👍 4)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **31.7/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 307 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 16 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 5 |
| Bug 类 Issues | 86 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [How do I optimise for F1 score?](https://github.com/stanfordnlp/dspy/issues/556) (👍 11 / 💬 6)
- [Better async support](https://github.com/stanfordnlp/dspy/issues/1975) (👍 13 / 💬 3)
- [[Notice] LiteLLM Supply Chain Attack](https://github.com/stanfordnlp/dspy/issues/9500) (👍 9 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [[Bug] TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_se](https://github.com/stanfordnlp/dspy/issues/8762) (👍 5)
- [[Bug] ChainOfThoughtWithHint is broken (at least for Azure)](https://github.com/stanfordnlp/dspy/issues/8205) (👍 2)
- [[Bug] Bus error on import when cache on network drive (occurs rarely on some mac](https://github.com/stanfordnlp/dspy/issues/8799) (👍 2)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **30.4/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 207 |
| 本周新增 New (7d) | 10 |
| 本月新增 New (30d) | 46 |
| 本周关闭 Closed (7d) | 3 |
| 本月关闭 Closed (30d) | 27 |
| Bug 类 Issues | 79 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: Handoff Issue: System Replies with Function Agent Message Instead of Resp](https://github.com/run-llama/llama_index/issues/19906) (👍 2)
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **27.5/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 219 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 13 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 4 |
| Bug 类 Issues | 133 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 61%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 51)
- [Consider migrating from httpx to httpx2](https://github.com/openai/openai-python/issues/3375) (👍 33 / 💬 4)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13 / 💬 3)

**🚨 高危 Issues / Critical Issues**:
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **24.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 422 |
| 本周新增 New (7d) | 8 |
| 本月新增 New (30d) | 55 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 5 |
| Bug 类 Issues | 177 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 42%

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 52)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 29)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [When invoking a graph of an agent with tools with "messages" streaming mode, the](https://github.com/langchain-ai/langgraph/issues/4653) (👍 3)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*