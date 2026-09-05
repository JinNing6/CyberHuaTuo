# 🦠 Agent 生态疫情通报
# Agent Ecosystem Epidemic Report

> **报告日期**: 2026-09-05
> **生成时间**: 2026-09-05T01:48:46.389330+00:00
> **监控框架**: 10 个主流 Agent 框架

---

## 📊 全局概览 / Global Overview

| 指标 Metric | 数值 Value |
|:---|:---|
| 📈 监控框架数 Frameworks | **10** |
| 🔓 总开放 Issues Total Open | **3,082** |
| 📥 本周新增 New (7d) | **250** |
| ✅ 本周关闭 Closed (7d) | **150** |
| 💚 平均健康分 Avg Score | **46.3/100** |

### 🏆 健康度排行 / Health Ranking

🥇 **haystack**
🥈 **pydantic-ai**
🥉 **autogen**

### ⚠️ 需要关注 / Needs Attention

- 🔴 **langchain**
- 🔴 **llamaindex**
- 🔴 **openai-sdk**
- 🔴 **dspy**
- 🔴 **mcp**
- 🔴 **langgraph**

### 🚨 异常告警 / Anomaly Alerts

- [langchain] ⚠️ 本周新增 57 个 Issues，高于常规水平
- [langchain] 🔴 存在 5 个高影响 Bug Issues
- [langchain] 🐛 Bug 类 Issue 占比达 61%
- [crewai] 🔴 存在 5 个高影响 Bug Issues
- [llamaindex] ⚠️ 关闭率偏低：本周新增 11，仅关闭 0
- [llamaindex] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🔴 存在 5 个高影响 Bug Issues
- [openai-sdk] 🐛 Bug 类 Issue 占比达 61%
- [dspy] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🔴 存在 5 个高影响 Bug Issues
- [mcp] 🐛 Bug 类 Issue 占比达 44%
- [pydantic-ai] ⚠️ 本周新增 80 个 Issues，高于常规水平
- [pydantic-ai] 🔴 存在 5 个高影响 Bug Issues
- [langgraph] ⚠️ 关闭率偏低：本周新增 24，仅关闭 0
- [langgraph] 🔴 存在 5 个高影响 Bug Issues

---

## 📋 各框架详情 / Framework Details

### 🟡 deepset-ai/haystack
**框架**: `haystack` | **健康分数 Health Score**: **75.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 67 |
| 本周新增 New (7d) | 15 |
| 本月新增 New (30d) | 45 |
| 本周关闭 Closed (7d) | 17 |
| 本月关闭 Closed (30d) | 42 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [OpenAI's Batch API Support](https://github.com/deepset-ai/haystack/issues/8482) (👍 3 / 💬 0)

---

### 🟠 pydantic/pydantic-ai
**框架**: `pydantic-ai` | **健康分数 Health Score**: **59.9/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 575 |
| 本周新增 New (7d) | 80 |
| 本月新增 New (30d) | 310 |
| 本周关闭 Closed (7d) | 51 |
| 本月关闭 Closed (30d) | 200 |
| Bug 类 Issues | 77 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 80 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [support batch processing](https://github.com/pydantic/pydantic-ai/issues/1771) (👍 33 / 💬 3)
- [Prompt management, versioning, and optimization](https://github.com/pydantic/pydantic-ai/issues/921) (👍 23 / 💬 8)
- [Support Anthropic and OpenAI Skills built-in tool](https://github.com/pydantic/pydantic-ai/issues/3365) (👍 19 / 💬 23)

**🚨 高危 Issues / Critical Issues**:
- [Create LiteLLMModel to fix thinking parts not being sent to Anthropic on Vertex ](https://github.com/pydantic/pydantic-ai/issues/3113) (👍 2)
- [MCP embedded resource metadata is not passed to model](https://github.com/pydantic/pydantic-ai/issues/2288) (👍 1)
- [Extract thinking from thinking tags not occurring in individual chunks](https://github.com/pydantic/pydantic-ai/issues/3007) (👍 1)

---

### 🟠 microsoft/autogen
**框架**: `autogen` | **健康分数 Health Score**: **57.0/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 549 |
| 本周新增 New (7d) | 3 |
| 本月新增 New (30d) | 13 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 1 |
| Bug 类 Issues | 0 |

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Golang/Rust implementation](https://github.com/microsoft/autogen/issues/1700) (👍 34 / 💬 4)
- [autogen-magentic-one ModuleNotFoundError: No module named 'autogen_core'](https://github.com/microsoft/autogen/issues/4079) (👍 6 / 💬 27)
- [MCP tool JSON serialization lacks ensure_ascii=False, degrades LLM performance f](https://github.com/microsoft/autogen/issues/6995) (👍 5 / 💬 0)

---

### 🟠 crewAIInc/crewAI
**框架**: `crewai` | **健康分数 Health Score**: **56.4/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 79 |
| 本周新增 New (7d) | 42 |
| 本月新增 New (30d) | 68 |
| 本周关闭 Closed (7d) | 27 |
| 本月关闭 Closed (30d) | 90 |
| Bug 类 Issues | 13 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues

**🚨 高危 Issues / Critical Issues**:
- [Native Mistral API fails with `cache_breakpoint` validation error during Agent e](https://github.com/crewAIInc/crewAI/issues/6789) (👍 0)
- [[BUG] input_files (PDFFile) are passed as base64 via read_file tool, causing con](https://github.com/crewAIInc/crewAI/issues/5930) (👍 0)
- [[BUG] MCP HTTP client crashes with "asyncio.run() cannot be called from a runnin](https://github.com/crewAIInc/crewAI/issues/6843) (👍 0)

---

### 🟠 langchain-ai/langchain
**框架**: `langchain` | **健康分数 Health Score**: **46.3/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 363 |
| 本周新增 New (7d) | 57 |
| 本月新增 New (30d) | 231 |
| 本周关闭 Closed (7d) | 43 |
| 本月关闭 Closed (30d) | 239 |
| Bug 类 Issues | 222 |

**异常告警 Anomalies**:
- ⚠️ 本周新增 57 个 Issues，高于常规水平
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 61%

**🔥 热门 Issues / Hot Issues**:
- [The batch method from ChatModels and all the Runnables does not really support t](https://github.com/langchain-ai/langchain/issues/28508) (👍 37 / 💬 17)
- [Support dynamic tool addition/removal after agent creation and in middleware](https://github.com/langchain-ai/langchain/issues/33808) (👍 14 / 💬 18)
- [[Feature Request] Native Support for MCP Code Execution (Programmatic Tool Calli](https://github.com/langchain-ai/langchain/issues/34130) (👍 30 / 💬 12)

**🚨 高危 Issues / Critical Issues**:
- [`trim_messages` and `ChatAnthropic` token counter with tools](https://github.com/langchain-ai/langchain/issues/29637) (👍 8)
- [Doesn't honour pydantic model field datatype and randomly throws `langchain_core](https://github.com/langchain-ai/langchain/issues/36603) (👍 10)
- [Setting a custom `http_client` fails with unexpected keyword argument when using](https://github.com/langchain-ai/langchain/issues/30146) (👍 2)

---

### 🟠 stanfordnlp/dspy
**框架**: `dspy` | **健康分数 Health Score**: **44.2/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 321 |
| 本周新增 New (7d) | 7 |
| 本月新增 New (30d) | 27 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 14 |
| Bug 类 Issues | 87 |

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

### 🔴 openai/openai-python
**框架**: `openai-sdk` | **健康分数 Health Score**: **34.5/100** | **趋势 Trend**: ↓ declining

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 220 |
| 本周新增 New (7d) | 6 |
| 本月新增 New (30d) | 10 |
| 本周关闭 Closed (7d) | 5 |
| 本月关闭 Closed (30d) | 8 |
| Bug 类 Issues | 134 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 61%

**🔥 热门 Issues / Hot Issues**:
- [Support for File Inputs In Azure OpenAI](https://github.com/openai/openai-python/issues/2300) (👍 42 / 💬 52)
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13 / 💬 3)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13 / 💬 22)

**🚨 高危 Issues / Critical Issues**:
- [Unrestricted caching keyed by generated types causes memory leak in multi-thread](https://github.com/openai/openai-python/issues/2672) (👍 13)
- [beta.chat.completions.parse returns unhandled ValidationError](https://github.com/openai/openai-python/issues/1763) (👍 13)
- [Validation error for ResponseTextDeltaEvent after updating to 1.97.1](https://github.com/openai/openai-python/issues/2489) (👍 11)

---

### 🔴 modelcontextprotocol/python-sdk
**框架**: `mcp` | **健康分数 Health Score**: **30.9/100** | **趋势 Trend**: ↑ improving

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 210 |
| 本周新增 New (7d) | 5 |
| 本月新增 New (30d) | 46 |
| 本周关闭 Closed (7d) | 1 |
| 本月关闭 Closed (30d) | 76 |
| Bug 类 Issues | 93 |

**异常告警 Anomalies**:
- 🔴 存在 5 个高影响 Bug Issues
- 🐛 Bug 类 Issue 占比达 44%

**🔥 热门 Issues / Hot Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28 / 💬 25)
- [Option to not rewrite the logging configuration](https://github.com/modelcontextprotocol/python-sdk/issues/420) (👍 23 / 💬 11)
- [Improving how function docstring gets converted to tool's jsonschema for FastMCP](https://github.com/modelcontextprotocol/python-sdk/issues/226) (👍 16 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [MCP SSE Server: Received request before initialization was complete](https://github.com/modelcontextprotocol/python-sdk/issues/423) (👍 28)
- [Server hangs when shutting down if a connection is still open](https://github.com/modelcontextprotocol/python-sdk/issues/1272) (👍 6)
- [cannot get response from  await session.call_tool()](https://github.com/modelcontextprotocol/python-sdk/issues/262) (👍 6)

---

### 🔴 langchain-ai/langgraph
**框架**: `langgraph` | **健康分数 Health Score**: **30.4/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 505 |
| 本周新增 New (7d) | 24 |
| 本月新增 New (30d) | 87 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 6 |
| Bug 类 Issues | 198 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 24，仅关闭 0
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12 / 💬 53)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9 / 💬 48)
- [Reflect `pydantic` and `dataclass` types in final output](https://github.com/langchain-ai/langgraph/issues/5024) (👍 6 / 💬 1)

**🚨 高危 Issues / Critical Issues**:
- [langgraph-checkpoint-postgres (psycopg.OperationalError: sending query and param](https://github.com/langchain-ai/langgraph/issues/3716) (👍 12)
- [Run Cancellation Causes Loss of Streamed State Not Yet Persisted as a Checkpoint](https://github.com/langchain-ai/langgraph/issues/5672) (👍 9)
- [Feature Request: Driver abstraction for checkpoint-postgres: to build support fo](https://github.com/langchain-ai/langgraph/issues/7692) (👍 4)

---

### 🔴 run-llama/llama_index
**框架**: `llamaindex` | **健康分数 Health Score**: **28.4/100** | **趋势 Trend**: → stable

| 指标 | 数值 |
|:---|:---|
| 开放 Issues Open | 193 |
| 本周新增 New (7d) | 11 |
| 本月新增 New (30d) | 55 |
| 本周关闭 Closed (7d) | 0 |
| 本月关闭 Closed (30d) | 60 |
| Bug 类 Issues | 64 |

**异常告警 Anomalies**:
- ⚠️ 关闭率偏低：本周新增 11，仅关闭 0
- 🔴 存在 5 个高影响 Bug Issues

**🔥 热门 Issues / Hot Issues**:
- [[Feature Request]: Support Multiple Embeddings per Node](https://github.com/run-llama/llama_index/issues/10486) (👍 4 / 💬 13)

**🚨 高危 Issues / Critical Issues**:
- [[Bug]: No Input/Output Token count for Gemini 2.5 models](https://github.com/run-llama/llama_index/issues/19293) (👍 2)
- [[Bug]: Unable to use ChromaDB for vector memory](https://github.com/run-llama/llama_index/issues/15681) (👍 1)
- [[Bug]: llamaindex is unable to connect to Sagemaker endoint using the latest lla](https://github.com/run-llama/llama_index/issues/12101) (👍 0)

---


---

*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*
*📡 数据来源: GitHub REST API | 更新频率: 每日*
*🦠 掌握 Agent 生态脉搏，定义框架健康标准*