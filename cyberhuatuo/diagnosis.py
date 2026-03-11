"""
CyberHuaTuo 望闻问切诊断引擎
基于 LLM 的智能诊断（需要 API Key）
支持注入 Context7 官方技术文档上下文
"""

from .config import config
from .searcher import SearchResult
from .doc_fetcher import smart_fetch, DocSnippet


SYSTEM_PROMPT = """你是赛博华佗（CyberHuaTuo），一个专精于 AI 技术问题诊断的智能医师。

你的诊疗范围涵盖所有 AI 相关领域：
- AI Agent 框架（LangChain、CrewAI、AutoGen、LlamaIndex 等）
- 自研/自建 Agent 系统
- 平台型 Agent（GPTs、Coze、Dify 等）
- LLM SDK 与 API（OpenAI、Anthropic、Google GenAI 等）
- 深度学习框架（PyTorch、TensorFlow、Transformers 等）
- 数据处理与 ML 工具（NumPy、Pandas、scikit-learn 等）
- MLOps 与基础设施（Docker、向量数据库、模型部署等）
- 以及任何具备"感知-决策-行动"能力的 AI 系统

你的职责：
1. 分析用户提交的报错信息或问题描述
2. 基于检索到的知识库病例，给出精准的诊断和药方
3. 使用「望闻问切」的医疗隐喻来组织回答

回答规范：
- 🔍 望（Look）：先识别出框架/工具名称、版本、错误类型
- 🩺 闻（Listen）：分析错误的可能原因类别
- 💊 切（Diagnose）：基于知识库匹配结果，给出具体的解决方案
- 语言要清晰、简洁，代码示例要可直接复制使用
- 如果知识库中有精确匹配的病例，直接引用其药方
- 如果没有精确匹配，基于最接近的病例推理给出建议
- 始终标注信息来源（来自知识库、官方文档还是 AI 推理）
- 当官方文档与病例药方冲突时，以最新官方文档为准
- 引用官方文档时标注出处链接"""


def build_diagnosis_prompt(
    query: str,
    results: list[SearchResult],
    doc_snippets: list[DocSnippet] | None = None,
) -> list[dict]:
    """
    构建诊断 Prompt，将检索到的病例和官方文档作为上下文注入

    Args:
        query: 用户的问题/报错
        results: 检索到的相关病例
        doc_snippets: 从 Context7 检索到的官方文档片段

    Returns:
        LLM messages 列表
    """
    # 构建知识库上下文
    context_parts = []
    for i, r in enumerate(results, 1):
        content_preview = r.content[:2000] if r.content else "（内容未加载）"
        context_parts.append(
            f"### 病例 {i}（相关度 {r.relevance}%）\n"
            f"- 标题: {r.title}\n"
            f"- 框架: {r.framework}\n"
            f"- 复杂度: {r.complexity}\n"
            f"- 严重性: {r.severity}\n"
            f"- 文件: {r.filepath}\n\n"
            f"{content_preview}\n"
        )

    knowledge_context = "\n---\n".join(context_parts) if context_parts else "（知识库中未找到相关病例）"

    # 构建官方文档上下文
    official_doc_context = "（未检索到官方文档）"
    if doc_snippets:
        doc_parts = []
        for i, s in enumerate(doc_snippets, 1):
            content_preview = s.content[:1500] if s.content else ""
            source_info = f"\n- 出处: {s.source}" if s.source else ""
            doc_parts.append(
                f"### 官方文档 {i}\n"
                f"- 标题: {s.title}\n"
                f"- 框架: {s.framework_name or s.framework}"
                f"{source_info}\n\n"
                f"{content_preview}\n"
            )
        official_doc_context = "\n---\n".join(doc_parts)

    user_content = (
        f"## 用户提交的问题\n\n{query}\n\n"
        f"## 知识库检索结果（按相关度排序）\n\n{knowledge_context}\n\n"
    )

    if doc_snippets:
        user_content += f"## 最新官方技术文档（来自 Context7）\n\n{official_doc_context}\n\n"

    user_content += "请根据以上信息，使用望闻问切的方式进行诊断，并给出具体的药方。如有引用官方文档，请标注出处。"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    return messages


async def _fetch_official_docs_for_diagnosis(
    query: str,
    results: list[SearchResult],
) -> list[DocSnippet]:
    """
    为诊断获取相关的官方文档
    根据检索到的病例中的框架信息，自动获取对应的官方文档
    """
    if not config.CONTEXT7_ENABLED:
        return []

    # 从病例结果中提取框架信息
    frameworks_found = set()
    for r in results:
        if r.framework and r.framework != "unknown":
            frameworks_found.add(r.framework)

    # 如果没有从病例中找到框架，尝试从查询中匹配
    if not frameworks_found:
        from .doc_sources import search_frameworks
        matched = search_frameworks(query)
        for fw in matched[:2]:
            frameworks_found.add(fw.key)

    if not frameworks_found:
        return []

    # 获取每个相关框架的官方文档（最多 2 个框架，每个 3 个片段）
    all_snippets = []
    for fw_key in list(frameworks_found)[:2]:
        try:
            snippets = await smart_fetch(fw_key, query, top_k=3)
            all_snippets.extend(snippets)
        except Exception:
            pass  # 官方文档获取失败不影响诊断

    return all_snippets[:5]  # 最多 5 个片段，避免上下文过长


async def diagnose(
    query: str,
    results: list[SearchResult],
    user_api_key: str | None = None,
    user_provider: str | None = None,
    user_model: str | None = None,
) -> str:
    """
    使用 LLM 进行望闻问切诊断
    同时注入病例库和最新官方技术文档上下文

    Args:
        query: 用户的问题/报错
        results: 检索到的相关病例
        user_api_key: 用户前端传入的 API Key（可选）
        user_provider: 用户选择的 LLM 提供商（可选）
        user_model: 用户传入的模型名称或接入点（可选）

    Returns:
        诊断结果文本
    """
    # 判断是否有可用的 LLM Key（服务端配置或用户传入）
    has_key = config.has_llm_key() or bool(user_api_key)

    if not has_key:
        return (
            "⚠️ 未配置 LLM API Key，无法使用 AI 诊断功能。\n\n"
            "你可以：\n"
            "1. 在搜索框下方的「开发者设置」中填入你的 API Key\n"
            "2. 或在 `.env` 文件中配置相应的 Key（如 OPENAI_API_KEY, DEEPSEEK_API_KEY 等）\n"
            "   - 支持本地模型，通过 OLLAMA_BASE_URL 接入无需 Key\n\n"
            "配置后即可使用 AI 望闻问切诊断。\n\n"
            "当前可以使用「向量搜索」模式直接搜索知识库中的病例。"
        )

    # 异步获取官方文档上下文
    doc_snippets = await _fetch_official_docs_for_diagnosis(query, results)

    messages = build_diagnosis_prompt(query, results, doc_snippets=doc_snippets)

    try:
        import litellm
        import os

        # 确定模型和 API Key
        api_base = None
        api_key = None
        model = config.DIAGNOSIS_MODEL

        if user_api_key:
            # 使用用户自定义的 API Key
            api_key = user_api_key
            provider = (user_provider or "openai").lower()
            if provider == "anthropic":
                model = user_model or "claude-3-5-sonnet-latest"
            elif provider == "openai":
                model = user_model or "gpt-4o-mini"
            elif provider == "deepseek":
                model = "deepseek/" + (user_model or "deepseek-chat")
            elif provider == "kimi":
                model = "openai/" + (user_model or "moonshot-v1-8k")
                api_base = "https://api.moonshot.cn/v1"
            elif provider == "doubao":
                model = "openai/" + (user_model or "ep-xxxx")  # 豆包需接入点
                api_base = "https://ark.cn-beijing.volces.com/api/v3"
            elif provider == "minimax":
                model = "openai/" + (user_model or "abab6.5s-chat")
                api_base = "https://api.minimax.chat/v1"
            elif provider == "groq":
                model = "groq/" + (user_model or "llama3-8b-8192")
            elif provider == "google" or provider == "gemini":
                model = "gemini/" + (user_model or "gemini-1.5-pro")
            elif provider == "cohere":
                model = "cohere/" + (user_model or "command-r-plus")
            else:
                # 自定义 provider
                model = user_model or config.DIAGNOSIS_MODEL
        else:
            # 使用服务端配置
            if os.getenv("DEEPSEEK_API_KEY") and "deepseek" in model.lower():
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not model.startswith("deepseek/"):
                    model = f"deepseek/{model}"
            elif os.getenv("KIMI_API_KEY") and ("kimi" in model.lower() or "moonshot" in model.lower()):
                api_key = os.getenv("KIMI_API_KEY")
                api_base = "https://api.moonshot.cn/v1"
                if not model.startswith("openai/"):
                    model = f"openai/{model}"
            elif os.getenv("DOUBAO_API_KEY") and ("doubao" in model.lower() or "ep-" in model.lower()):
                api_key = os.getenv("DOUBAO_API_KEY")
                api_base = "https://ark.cn-beijing.volces.com/api/v3"
                if not model.startswith("openai/"):
                    model = f"openai/{model}"
            elif os.getenv("MINIMAX_API_KEY") and "minimax" in model.lower():
                api_key = os.getenv("MINIMAX_API_KEY")
                api_base = "https://api.minimax.chat/v1"
                if not model.startswith("openai/"):
                    model = f"openai/{model}"
            elif os.getenv("GROQ_API_KEY") and "groq" in model.lower():
                api_key = os.getenv("GROQ_API_KEY")
                if not model.startswith("groq/"):
                    model = f"groq/{model}"
            elif os.getenv("GEMINI_API_KEY") and ("gemini" in model.lower() or "google" in model.lower()):
                api_key = os.getenv("GEMINI_API_KEY")
                if not model.startswith("gemini/"):
                    model = f"gemini/{model}"
            elif os.getenv("COHERE_API_KEY") and "cohere" in model.lower():
                api_key = os.getenv("COHERE_API_KEY")
                if not model.startswith("cohere/"):
                    model = f"cohere/{model}"
            elif config.OLLAMA_BASE_URL and model.startswith("ollama/"):
                api_base = config.OLLAMA_BASE_URL

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=0.3,      # 低温度，诊断要精确
            max_tokens=2000,
            api_base=api_base,
            api_key=api_key,
        )

        return response.choices[0].message.content

    except ImportError:
        return "⚠️ 请安装 litellm: `pip install litellm`"
    except Exception as e:
        return f"⚠️ LLM 调用失败: {str(e)}\n\n请检查 API Key 配置和网络连接。"
