# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-09-26
> **生成时间**: 2026-09-26T02:23:13.320533+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **3,452** |
| 📥 本周新增 New (7d) | **319** |
| ✅ 本周关闭 Closed (7d) | **167** |
| 💚 平均健康分 Avg Score | **48.2/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **pydantic-ai**
🥉 **autogen**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] ⚠️ 本周新增 59 个 Issues，高于常规水平
- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 64%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] ⚠️ 关闭率偏低：本周新增 20，仅关闭 5
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 57%
- [dspy] ⚠️ 关闭率偏低：本周新增 12，仅关闭 0
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] ⚠️ 关闭率偏低：本周新增 18，仅关闭 0
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [pydantic-ai] ⚠️ 本周新增 90 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] ⚠️ 关闭率偏低：本周新增 23，仅关闭 4
- [langgraph] 🔴 存在 5 个高影响 Bug Issues

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **75.5/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 95 |
| 本周新增 New (7d) | 42 |
| 本月新增 New (30d) | 96 |
| 本周关闭 Closed (7d) | 35 |
| 本月关闭 Closed (30d) | 71 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟡 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **60.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 682 |
| 本周新增 New (7d) | 90 |
| 本月新增 New (30d) | 336 |
| 本周关闭 Closed (7d) | 65 |
| 本月关闭 Closed (30d) | 196 |
| Bug 类 Issues | 95 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 90 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 34 / 💬 4)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)
- [Support Anthropic and OpenAI Skills built-in tool](https://github.com/pydantic/pydantic-ai/issues/3365) (👍 19 / 💬 23)

**🚨 高危 Issues / Critical Issues**:
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)
- [`pydantic_graph`: `asyncio.get_event_loop()` is deprecated since python 3.12](https://github.com/pydantic/pydantic-ai/issues/1196) (👍 1)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **57.0/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 559 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 15 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 2 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **55.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 186 |
| 本周新增 New (7d) | 45 |
| 本月新增 New (30d) | 217 |
| 本周关闭 Closed (7d) | 18 |
| 本月关闭 Closed (30d) | 109 |
| Bug 类 Issues | 19 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [[BUG] AttributeError: 'int' object has no attribute 'get' in crew_run_tui.py dur](https://github.com/crewAIInc/crewAI/issues/7635) (👍 0)
- [[BUG] CSVLoader misparses headers in UTF-8 CSV files with a BOM](https://github.com/crewAIInc/crewAI/issues/7466) (👍 0)
- [[BUG] LanceDBStorage.delete() ignores scope/older_than filters and causes accide](https://github.com/crewAIInc/crewAI/issues/7419) (👍 0)

---

### 🟠 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **50.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 58 |
| 本周新增 New (7d) | 4 |
| 本月新增 New (30d) | 22 |
| 本周关闭 Closed (7d) | 9 |
| 本月关闭 Closed (30d) | 182 |
| Bug 类 Issues | 33 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 57%

**🔥 热门 Issues / Hot Issues**:
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 22)
- [Cancel for streaming Responses](https://github.com/openai/openai-python/issues/2643) (👍 11 / 💬 2)
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Moderation Endpoint Schema Mismatch for illicit and illicit_violent fields](https://github.com/openai/openai-python/issues/1786) (👍 6)
- [Error "Item ‘rs_ABCD’ of type ‘reasoning’ was provided without its required..." ](https://github.com/openai/openai-python/issues/2561) (👍 5)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **42.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 465 |
| 本周新增 New (7d) | 59 |
| 本月新增 New (30d) | 283 |
| 本周关闭 Closed (7d) | 31 |
| 本月关闭 Closed (30d) | 181 |
| Bug 类 Issues | 296 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 59 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 64%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 17)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 16 / 💬 19)
- [Prompts and Resources auto-discovery](https://github.com/langchain-ai/langchain/issues/40490) (👍 16 / 💬 7)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [Setting a custom `http_client` fails with unexpected keyword argument when using](https://github.com/langchain-ai/langchain/issues/30146) (👍 2)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **39.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 234 |
| 本周新增 New (7d) | 20 |
| 本月新增 New (30d) | 64 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 10 |
| Bug 类 Issues | 69 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 20，仅关闭 5
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)
- [[Security Vulnerability] Sandbox escape and Arbitrary Code Execution (RCE) via P](https://github.com/run-llama/llama_index/issues/22232) (👍 0)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **34.6/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 576 |
| 本周新增 New (7d) | 23 |
| 本月新增 New (30d) | 112 |
| 本周关闭 Closed (7d) | 4 |
| 本月关闭 Closed (30d) | 15 |
| Bug 类 Issues | 207 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 23，仅关闭 4
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 53)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 51)
- [Add support for Python 3.14](https://github.com/langchain-ai/langgraph/issues/5253) (👍 8 / 💬 15)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [Feature Request: Driver abstraction for checkpoint-postgres: to build support fo](https://github.com/langchain-ai/langgraph/issues/7692) (👍 4)

---

### 🔴 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **34.0/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 338 |
| 本周新增 New (7d) | 12 |
| 本月新增 New (30d) | 30 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 10 |
| Bug 类 Issues | 88 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 12，仅关闭 0
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
**框架**: `mcp` | **健康分数 Health Score**: **32.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 259 |
| 本周新增 New (7d) | 18 |
| 本月新增 New (30d) | 58 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 6 |
| Bug 类 Issues | 93 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 18，仅关闭 0
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 23 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 29)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)
- [cannot get response from  await session.call_tool()](https://github.com/modelcontextprotocol/python-sdk/issues/262) (👍 6)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*