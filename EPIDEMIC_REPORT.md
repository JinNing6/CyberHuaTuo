# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-11-19
> **生成时间**: 2026-11-19T04:53:34.402492+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **4,588** |
| 📥 本周新增 New (7d) | **432** |
| ✅ 本周关闭 Closed (7d) | **415** |
| 💚 平均健康分 Avg Score | **44.9/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **crewai**
🥈 **haystack**
🥉 **pydantic-ai**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 67%
- [crewai] ⚠️ 本周新增 52 个 Issues，高于常规水平
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] ⚠️ 关闭率偏低：本周新增 20，仅关闭 0
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 44%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] ⚠️ 关闭率偏低：本周新增 15，仅关闭 1
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🐛 Bug 类 Issue 占比达 62%
- [pydantic-ai] ⚠️ 本周新增 263 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues

---

## 📋 各框架详情 / Framework Details

### 🟡 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **70.5/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 478 |
| 本周新增 New (7d) | 52 |
| 本月新增 New (30d) | 419 |
| 本周关闭 Closed (7d) | 74 |
| 本月关闭 Closed (30d) | 246 |
| Bug 类 Issues | 56 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 52 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] A flow resumed from a checkpoint leaves a loop early: methods that ran aft](https://github.com/crewAIInc/crewAI/issues/8927) (👍 0)
- [[BUG] Restore Flow.chat() configuration when trace finalization fails](https://github.com/crewAIInc/crewAI/issues/8069) (👍 0)
- [[docs] Fix custom LLM stop-word example to stop at the earliest match](https://github.com/crewAIInc/crewAI/issues/8002) (👍 0)

---

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **65.5/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 102 |
| 本周新增 New (7d) | 26 |
| 本月新增 New (30d) | 98 |
| 本周关闭 Closed (7d) | 13 |
| 本月关闭 Closed (30d) | 84 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **59.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 1,340 |
| 本周新增 New (7d) | 263 |
| 本月新增 New (30d) | 1241 |
| 本周关闭 Closed (7d) | 297 |
| 本月关闭 Closed (30d) | 945 |
| Bug 类 Issues | 395 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 263 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 9)
- [Support Anthropic and OpenAI Skills built-in tool](https://github.com/pydantic/pydantic-ai/issues/3365) (👍 19 / 💬 24)
- [Improve "Ergonomics" of Graph Streaming](https://github.com/pydantic/pydantic-ai/issues/1452) (👍 11 / 💬 6)

**🚨 高危 Issues / Critical Issues**:
- [`MistralModel` streaming raises a bare `ValueError` (or drops the text) when out](https://github.com/pydantic/pydantic-ai/issues/8039) (👍 2)
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [Vercel AI adapter: emit `reset-step` when a retried durable model activity repub](https://github.com/pydantic/pydantic-ai/issues/12829) (👍 1)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **52.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 575 |
| 本周新增 New (7d) | 1 |
| 本月新增 New (30d) | 17 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 2 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **47.4/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 352 |
| 本周新增 New (7d) | 11 |
| 本月新增 New (30d) | 102 |
| 本周关闭 Closed (7d) | 11 |
| 本月关闭 Closed (30d) | 106 |
| Bug 类 Issues | 124 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 53)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 52)
- [Add support for Python 3.14](https://github.com/langchain-ai/langgraph/issues/5253) (👍 8 / 💬 17)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [【Command】：Can't use update and List[Send] at the same time if graph==Command.PAR](https://github.com/langchain-ai/langgraph/issues/5062) (👍 2)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **42.5/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 617 |
| 本周新增 New (7d) | 34 |
| 本月新增 New (30d) | 159 |
| 本周关闭 Closed (7d) | 17 |
| 本月关闭 Closed (30d) | 79 |
| Bug 类 Issues | 413 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 67%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 17)
- [Prompts and Resources auto-discovery](https://github.com/langchain-ai/langchain/issues/40490) (👍 16 / 💬 7)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 16 / 💬 19)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [Setting a custom `http_client` fails with unexpected keyword argument when using](https://github.com/langchain-ai/langchain/issues/30146) (👍 2)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **39.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 349 |
| 本周新增 New (7d) | 7 |
| 本月新增 New (30d) | 27 |
| 本周关闭 Closed (7d) | 2 |
| 本月关闭 Closed (30d) | 40 |
| Bug 类 Issues | 84 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [How do I optimise for F1 score?](https://github.com/stanfordnlp/dspy/issues/556) (👍 11 / 💬 6)
- [Better async support](https://github.com/stanfordnlp/dspy/issues/1975) (👍 13 / 💬 3)
- [[Notice] LiteLLM Supply Chain Attack](https://github.com/stanfordnlp/dspy/issues/9500) (👍 9 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [[Bug] TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_se](https://github.com/stanfordnlp/dspy/issues/8762) (👍 5)
- [[Bug] Bus error on import when cache on network drive (occurs rarely on some mac](https://github.com/stanfordnlp/dspy/issues/8799) (👍 2)
- [[Bug] dspy.utils.exceptions.AdapterParseError: Adapter ChatAdapter failed to par](https://github.com/stanfordnlp/dspy/issues/8276) (👍 1)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **29.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 421 |
| 本周新增 New (7d) | 20 |
| 本月新增 New (30d) | 124 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 10 |
| Bug 类 Issues | 135 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 20，仅关闭 0
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)
- [[Bug]: Ollama: per-call think=False is silently dropped by the "or self.thinking](https://github.com/run-llama/llama_index/issues/22467) (👍 3 / 💬 4)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)
- [[Bug]: Nltk version v3.10.3 with important vul fixes cannot be used in llama-ind](https://github.com/run-llama/llama_index/issues/22839) (👍 1)

---

### 🔴 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **26.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 309 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 62 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 10 |
| Bug 类 Issues | 193 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 15，仅关闭 1
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 62%

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29 / 💬 26)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 23 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 14)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29)
- [Critical Token Refresh Bugs - Prevents Proactive Refresh](https://github.com/modelcontextprotocol/python-sdk/issues/1318) (👍 8)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **17.8/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 45 |
| 本周新增 New (7d) | 3 |
| 本月新增 New (30d) | 8 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 23 |
| Bug 类 Issues | 20 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 44%

**🔥 热门 Issues / Hot Issues**:
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6 / 💬 3)
- [Error "Item ‘rs_ABCD’ of type ‘reasoning’ was provided without its required..." ](https://github.com/openai/openai-python/issues/2561) (👍 5 / 💬 7)
- [Output response types are not usable as parameters](https://github.com/openai/openai-python/issues/2323) (👍 5 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6)
- [Error "Item ‘rs_ABCD’ of type ‘reasoning’ was provided without its required..." ](https://github.com/openai/openai-python/issues/2561) (👍 5)
- [Aborting a streaming Responses API request drops the function_call item, breakin](https://github.com/openai/openai-python/issues/3561) (👍 2)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*