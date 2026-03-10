"""
CyberHuaTuo 望闻问切诊断引擎
基于 LLM 的智能诊断（需要 API Key）
支持注入 Context7 官方技术文档上下文
"""

from .config import config
from .searcher import SearchResult
from .doc_fetcher import smart_fetch, DocSnippet


SYSTEM_PROMPT = """你是赛博华佗（CyberHuaTuo），一个专精于 AI Agent 框架问题诊断的智能医师。

你的职责：
1. 分析用户提交的报错信息或问题描述
2. 基于检索到的知识库病例，给出精准的诊断和药方
3. 使用「望闻问切」的医疗隐喻来组织回答

回答规范：
- 🔍 望（Look）：先识别出框架名称、版本、错误类型
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


async def diagnose(query: str, results: list[SearchResult]) -> str:
    """
    使用 LLM 进行望闻问切诊断
    同时注入病例库和最新官方技术文档上下文

    Args:
        query: 用户的问题/报错
        results: 检索到的相关病例

    Returns:
        诊断结果文本
    """
    if not config.has_llm_key():
        return (
            "⚠️ 未配置 LLM API Key，无法使用 AI 诊断功能。\n\n"
            "请在 `.env` 文件中配置以下任一 Key：\n"
            "- `OPENAI_API_KEY`\n"
            "- `ANTHROPIC_API_KEY`\n"
            "- `OLLAMA_BASE_URL`（本地模型，无需 Key）\n\n"
            "配置后重启服务即可使用 AI 望闻问切诊断。\n\n"
            "当前可以使用「向量搜索」模式直接搜索知识库中的病例。"
        )

    # 异步获取官方文档上下文
    doc_snippets = await _fetch_official_docs_for_diagnosis(query, results)

    messages = build_diagnosis_prompt(query, results, doc_snippets=doc_snippets)

    try:
        import litellm

        # 配置 Ollama base URL
        api_base = None
        model = config.DIAGNOSIS_MODEL
        if config.OLLAMA_BASE_URL and model.startswith("ollama/"):
            api_base = config.OLLAMA_BASE_URL

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=0.3,      # 低温度，诊断要精确
            max_tokens=2000,
            api_base=api_base,
        )

        return response.choices[0].message.content

    except ImportError:
        return "⚠️ 请安装 litellm: `pip install litellm`"
    except Exception as e:
        return f"⚠️ LLM 调用失败: {str(e)}\n\n请检查 API Key 配置和网络连接。"
