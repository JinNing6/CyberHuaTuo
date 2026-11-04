# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-11-04
> **生成时间**: 2026-11-04T03:43:59.500881+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **4,293** |
| 📥 本周新增 New (7d) | **542** |
| ✅ 本周关闭 Closed (7d) | **296** |
| 💚 平均健康分 Avg Score | **44.5/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **langgraph**
🥈 **haystack**
🥉 **crewai**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 66%
- [crewai] ⚠️ 本周新增 98 个 Issues，高于常规水平
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] ⚠️ 关闭率偏低：本周新增 26，仅关闭 3
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 48%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] ⚠️ 关闭率偏低：本周新增 17，仅关闭 3
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🐛 Bug 类 Issue 占比达 62%
- [pydantic-ai] ⚠️ 本周新增 311 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] 🔴 存在 5 个高影响 Bug Issues

---

## 📋 各框架详情 / Framework Details

### 🟡 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **66.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 326 |
| 本周新增 New (7d) | 32 |
| 本月新增 New (30d) | 111 |
| 本周关闭 Closed (7d) | 63 |
| 本月关闭 Closed (30d) | 350 |
| Bug 类 Issues | 121 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 53)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 52)
- [Add support for Python 3.14](https://github.com/langchain-ai/langgraph/issues/5253) (👍 8 / 💬 16)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [/join endpoint returns HTTP 200 with error payload instead of proper HTTP error ](https://github.com/langchain-ai/langgraph/issues/6213) (👍 2)

---

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **64.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 109 |
| 本周新增 New (7d) | 19 |
| 本月新增 New (30d) | 78 |
| 本周关闭 Closed (7d) | 8 |
| 本月关闭 Closed (30d) | 64 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **53.5/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 437 |
| 本周新增 New (7d) | 98 |
| 本月新增 New (30d) | 399 |
| 本周关闭 Closed (7d) | 32 |
| 本月关闭 Closed (30d) | 188 |
| Bug 类 Issues | 56 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 98 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] A flow resumed from a checkpoint leaves a loop early: methods that ran aft](https://github.com/crewAIInc/crewAI/issues/8927) (👍 0)
- [[BUG] Native MCP tool discovery ignores pages after nextCursor](https://github.com/crewAIInc/crewAI/issues/8098) (👍 0)
- [[BUG] Restore Flow.chat() configuration when trace finalization fails](https://github.com/crewAIInc/crewAI/issues/8069) (👍 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **53.4/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 1,260 |
| 本周新增 New (7d) | 311 |
| 本月新增 New (30d) | 897 |
| 本周关闭 Closed (7d) | 171 |
| 本月关闭 Closed (30d) | 628 |
| Bug 类 Issues | 298 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 311 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)
- [Support Anthropic and OpenAI Skills built-in tool](https://github.com/pydantic/pydantic-ai/issues/3365) (👍 19 / 💬 23)
- [Improve "Ergonomics" of Graph Streaming](https://github.com/pydantic/pydantic-ai/issues/1452) (👍 11 / 💬 5)

**🚨 高危 Issues / Critical Issues**:
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [Extract thinking from thinking tags not occurring in individual chunks](https://github.com/pydantic/pydantic-ai/issues/3007) (👍 1)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **52.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 565 |
| 本周新增 New (7d) | 3 |
| 本月新增 New (30d) | 10 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 4 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🔴 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **39.6/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 574 |
| 本周新增 New (7d) | 25 |
| 本月新增 New (30d) | 181 |
| 本周关闭 Closed (7d) | 16 |
| 本月关闭 Closed (30d) | 118 |
| Bug 类 Issues | 376 |

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
**框架**: `llamaindex` | **健康分数 Health Score**: **37.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 355 |
| 本周新增 New (7d) | 26 |
| 本月新增 New (30d) | 103 |
| 本周关闭 Closed (7d) | 3 |
| 本月关闭 Closed (30d) | 9 |
| Bug 类 Issues | 103 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 26，仅关闭 3
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)
- [[Bug]: Nltk version v3.10.3 with important vul fixes cannot be used in llama-ind](https://github.com/run-llama/llama_index/issues/22839) (👍 1)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **35.4/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 341 |
| 本周新增 New (7d) | 9 |
| 本月新增 New (30d) | 39 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 48 |
| Bug 类 Issues | 79 |

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

### 🔴 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **27.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 284 |
| 本周新增 New (7d) | 17 |
| 本月新增 New (30d) | 80 |
| 本周关闭 Closed (7d) | 3 |
| 本月关闭 Closed (30d) | 47 |
| Bug 类 Issues | 177 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 17，仅关闭 3
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 62%

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 23 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29)
- [Critical Token Refresh Bugs - Prevents Proactive Refresh](https://github.com/modelcontextprotocol/python-sdk/issues/1318) (👍 7)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)

---

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **16.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 42 |
| 本周新增 New (7d) | 2 |
| 本月新增 New (30d) | 11 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 26 |
| Bug 类 Issues | 20 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 48%

**🔥 热门 Issues / Hot Issues**:
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6 / 💬 2)
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