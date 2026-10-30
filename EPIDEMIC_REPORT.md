# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-10-30
> **生成时间**: 2026-10-30T03:20:11.712876+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **4,124** |
| 📥 本周新增 New (7d) | **511** |
| ✅ 本周关闭 Closed (7d) | **342** |
| 💚 平均健康分 Avg Score | **51.5/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **dspy**
🥈 **autogen**
🥉 **haystack**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 66%
- [crewai] ⚠️ 本周新增 110 个 Issues，高于常规水平
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] ⚠️ 关闭率偏低：本周新增 19，仅关闭 1
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 50%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🐛 Bug 类 Issue 占比达 61%
- [pydantic-ai] ⚠️ 本周新增 280 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues

---

## 📋 各框架详情 / Framework Details

### 🟡 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **70.4/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 335 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 43 |
| 本周关闭 Closed (7d) | 36 |
| 本月关闭 Closed (30d) | 50 |
| Bug 类 Issues | 78 |

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

### 🟡 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **67.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 562 |
| 本周新增 New (7d) | 0 |
| 本月新增 New (30d) | 9 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 7 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **63.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 106 |
| 本周新增 New (7d) | 20 |
| 本月新增 New (30d) | 77 |
| 本周关闭 Closed (7d) | 7 |
| 本月关闭 Closed (30d) | 69 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **57.7/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 1,153 |
| 本周新增 New (7d) | 280 |
| 本月新增 New (30d) | 749 |
| 本周关闭 Closed (7d) | 201 |
| 本月关闭 Closed (30d) | 592 |
| Bug 类 Issues | 232 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 280 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)
- [Support Anthropic and OpenAI Skills built-in tool](https://github.com/pydantic/pydantic-ai/issues/3365) (👍 19 / 💬 23)
- [Improve "Ergonomics" of Graph Streaming](https://github.com/pydantic/pydantic-ai/issues/1452) (👍 11 / 💬 5)

**🚨 高危 Issues / Critical Issues**:
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [`pydantic_graph`: `asyncio.get_event_loop()` is deprecated since python 3.12](https://github.com/pydantic/pydantic-ai/issues/1196) (👍 1)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **55.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 390 |
| 本周新增 New (7d) | 110 |
| 本月新增 New (30d) | 354 |
| 本周关闭 Closed (7d) | 44 |
| 本月关闭 Closed (30d) | 161 |
| Bug 类 Issues | 47 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 110 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] Native MCP tool discovery ignores pages after nextCursor](https://github.com/crewAIInc/crewAI/issues/8098) (👍 0)
- [[BUG] Flow method panels print out of execution order](https://github.com/crewAIInc/crewAI/issues/7878) (👍 0)
- [[BUG] Converter._coerce_response_to_pydantic drops agent reference on fallback r](https://github.com/crewAIInc/crewAI/issues/7984) (👍 0)

---

### 🟠 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **50.0/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 40 |
| 本周新增 New (7d) | 1 |
| 本月新增 New (30d) | 14 |
| 本周关闭 Closed (7d) | 7 |
| 本月关闭 Closed (30d) | 32 |
| Bug 类 Issues | 20 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 50%

**🔥 热门 Issues / Hot Issues**:
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6 / 💬 2)
- [Error "Item ‘rs_ABCD’ of type ‘reasoning’ was provided without its required..." ](https://github.com/openai/openai-python/issues/2561) (👍 5 / 💬 7)
- [Output response types are not usable as parameters](https://github.com/openai/openai-python/issues/2323) (👍 5 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6)
- [Error "Item ‘rs_ABCD’ of type ‘reasoning’ was provided without its required..." ](https://github.com/openai/openai-python/issues/2561) (👍 5)
- [Aborting a streaming Responses API request drops the function_call item, breakin](https://github.com/openai/openai-python/issues/3561) (👍 2)

---

### 🟠 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **48.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 361 |
| 本周新增 New (7d) | 24 |
| 本月新增 New (30d) | 103 |
| 本周关闭 Closed (7d) | 24 |
| 本月关闭 Closed (30d) | 298 |
| Bug 类 Issues | 123 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 53)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 52)
- [Add support for Python 3.14](https://github.com/langchain-ai/langgraph/issues/5253) (👍 8 / 💬 16)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [Feature Request: Driver abstraction for checkpoint-postgres: to build support fo](https://github.com/langchain-ai/langgraph/issues/7692) (👍 5)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **41.7/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 567 |
| 本周新增 New (7d) | 38 |
| 本月新增 New (30d) | 186 |
| 本周关闭 Closed (7d) | 17 |
| 本月关闭 Closed (30d) | 111 |
| Bug 类 Issues | 372 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 66%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 17)
- [Prompts and Resources auto-discovery](https://github.com/langchain-ai/langchain/issues/40490) (👍 16 / 💬 7)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 16 / 💬 19)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [Setting a custom `http_client` fails with unexpected keyword argument when using](https://github.com/langchain-ai/langchain/issues/30146) (👍 2)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **31.8/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 339 |
| 本周新增 New (7d) | 19 |
| 本月新增 New (30d) | 98 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 8 |
| Bug 类 Issues | 95 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 19，仅关闭 1
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)
- [[Bug]: Nltk version v3.10.3 with important vul fixes cannot be used in llama-ind](https://github.com/run-llama/llama_index/issues/22839) (👍 1)

---

### 🔴 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **30.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 271 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 75 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 73 |
| Bug 类 Issues | 165 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 61%

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 23 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29)
- [Critical Token Refresh Bugs - Prevents Proactive Refresh](https://github.com/modelcontextprotocol/python-sdk/issues/1318) (👍 7)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*