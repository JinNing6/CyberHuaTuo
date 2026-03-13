"""
CyberHuaTuo 搜索引擎 — 双层药方库架构
Search Engine — Dual-layer Prescription Architecture

支持两个搜索源：
  1. 常驻药方库（ChromaDB 向量语义搜索）
  2. 瞬时药方库（GitHub Issues API 搜索）
"""

import json
import logging
import re
from dataclasses import dataclass

import chromadb
import httpx

from .config import config
from .indexer import get_case_content

logger = logging.getLogger("cyberhuatuo.searcher")


@dataclass
class SearchResult:
    """搜索结果 / Search result"""
    case_id: str
    title: str
    title_en: str
    framework: str
    severity: str
    complexity: str
    tags: str
    filepath: str
    distance: float        # 向量距离（越小越相关）
    relevance: float       # 相关度得分（0-100，越高越相关）
    content: str | None    # 病例完整内容（可选加载）
    source: str = "常驻"    # 来源标识 / Source: "常驻" (permanent) or "瞬时" (ephemeral)
    contributor: str = ""  # 贡献者 Github / Contributor Github


def search_cases(
    client: chromadb.ClientAPI,
    query: str,
    framework: str | None = None,
    severity: str | None = None,
    complexity: str | None = None,
    top_k: int | None = None,
    include_content: bool = True,
) -> list[SearchResult]:
    """
    在常驻知识库中搜索匹配的病例
    Search permanent knowledge base for matching cases.

    Args:
        client: ChromaDB 客户端
        query: 搜索查询（错误信息/问题描述）
        framework: 按框架过滤
        severity: 按严重性过滤
        complexity: 按复杂度过滤
        top_k: 返回结果数量
        include_content: 是否加载完整文件内容

    Returns:
        排序后的搜索结果列表（source="常驻"）
    """
    top_k = top_k or config.TOP_K

    # 获取集合
    try:
        collection = client.get_collection(name=config.COLLECTION_NAME)
    except Exception:
        return []

    if collection.count() == 0:
        return []

    # 构建过滤条件
    where_filter = {}
    if framework:
        where_filter["framework"] = framework
    if severity:
        where_filter["severity"] = severity
    if complexity:
        where_filter["complexity"] = complexity

    # 执行向量搜索
    query_params = {
        "query_texts": [query],
        "n_results": min(top_k, collection.count()),
    }
    if where_filter:
        where_filter_list = [{"$and": [{k: v} for k, v in where_filter.items()]}] if len(where_filter) > 1 else None
        if len(where_filter) == 1:
            query_params["where"] = where_filter
        elif where_filter_list:
            query_params["where"] = where_filter_list[0]

    results = collection.query(**query_params)

    if not results["ids"] or not results["ids"][0]:
        return []

    # 构造搜索结果
    search_results = []
    ids = results["ids"][0]
    distances = results["distances"][0] if results["distances"] else [0] * len(ids)
    metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)

    for _i, (doc_id, distance, metadata) in enumerate(zip(ids, distances, metadatas)):
        # 将距离转换为 0-100 的相关度分数
        # ChromaDB 默认使用 L2 距离，越小越相关
        relevance = max(0.0, min(100.0, 100.0 * (1.0 / (1.0 + distance))))

        content = None
        if include_content:
            content = get_case_content(metadata.get("filepath", ""))

        search_results.append(SearchResult(
            case_id=metadata.get("case_id", doc_id),
            title=metadata.get("title", ""),
            title_en=metadata.get("title_en", ""),
            framework=metadata.get("framework", "unknown"),
            severity=metadata.get("severity", "medium"),
            complexity=metadata.get("complexity", "moderate"),
            tags=metadata.get("tags", ""),
            filepath=metadata.get("filepath", ""),
            distance=distance,
            relevance=round(relevance, 1),
            content=content,
            source="常驻",
            contributor=metadata.get("contributor", ""),
        ))

    return search_results


async def search_ephemeral_issues(
    query: str,
    framework: str | None = None,
    severity: str | None = None,
    top_k: int = 5,
) -> list[SearchResult]:
    """
    搜索瞬时药方库（GitHub Issues）
    Search ephemeral prescription layer (GitHub Issues).

    通过 GitHub Issues API 搜索 label 为 'prescription' 且状态为 'open' 的 Issues，
    解析 Issue body 中的结构化 JSON 数据并转换为 SearchResult。

    Args:
        query: 搜索关键词 / Search keywords
        framework: 按框架过滤 / Filter by framework
        severity: 按严重性过滤 / Filter by severity
        top_k: 返回结果数量 / Max results

    Returns:
        瞬时药方搜索结果列表（source="瞬时"）
    """
    if not config.EPHEMERAL_SEARCH_ENABLED:
        return []

    owner = config.GITHUB_SYNC_OWNER
    repo = config.GITHUB_SYNC_REPO

    # 构建 GitHub Issues 搜索查询
    # 使用 GitHub Search API 进行全文搜索
    search_query_parts = [
        f'repo:{owner}/{repo}',
        'is:issue',
        'is:open',
        'label:prescription',
        query,  # 用户的搜索关键词
    ]

    if framework:
        search_query_parts.append(f'label:framework:{framework}')
    if severity:
        search_query_parts.append(f'label:severity:{severity}')

    search_q = " ".join(search_query_parts)

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"

    url = "https://api.github.com/search/issues"
    params = {
        "q": search_q,
        "per_page": min(top_k, 10),
        "sort": "created",
        "order": "desc",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            logger.warning(f"GitHub Issues 搜索失败: {resp.status_code}")
            return []

        data = resp.json()
        items = data.get("items", [])

        results = []
        for item in items:
            parsed = _parse_issue_to_result(item)
            if parsed:
                results.append(parsed)

        return results

    except Exception as e:
        logger.warning(f"瞬时药方搜索异常: {e}")
        return []


def _parse_issue_to_result(issue: dict) -> SearchResult | None:
    """
    将 GitHub Issue 数据解析为 SearchResult
    Parse a GitHub Issue into a SearchResult.
    """
    body = issue.get("body", "") or ""
    title = issue.get("title", "")

    # 提取结构化 JSON 数据（在 <details> 块中的 ```json ... ``` ）
    structured_data = _extract_structured_data(body)

    # 从标签中提取元数据
    labels = [l.get("name", "") for l in issue.get("labels", [])]
    framework = "unknown"
    severity = "medium"
    for label in labels:
        if label.startswith("framework:"):
            framework = label.split(":", 1)[1]
        elif label.startswith("severity:"):
            severity = label.split(":", 1)[1]

    # 优先使用结构化数据，回退到标签/标题
    if structured_data:
        result_title = structured_data.get("title", title)
        title_en = structured_data.get("title_en", "")
        framework = structured_data.get("framework", framework)
        severity = structured_data.get("severity", severity)
        complexity = structured_data.get("complexity", "moderate")
        tags_list = structured_data.get("tags", [])
        tags_str = ",".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
    else:
        # 从 Issue 标题中提取: 🩺 [framework] 实际标题
        match = re.match(r"🩺\s*\[(\w+)\]\s*(.+)", title)
        if match:
            framework = match.group(1)
            result_title = match.group(2).strip()
        else:
            result_title = title
        title_en = ""
        complexity = "moderate"
        tags_str = ""

    # 构建内容摘要：使用 Issue body（去除 JSON 块）
    content = _clean_issue_body(body)

    return SearchResult(
        case_id=f"issue-{issue.get('number', 0)}",
        title=result_title,
        title_en=title_en,
        framework=framework,
        severity=severity,
        complexity=complexity,
        tags=tags_str,
        filepath=issue.get("html_url", ""),
        distance=0.0,
        relevance=75.0,  # 瞬时药方给固定相关度（无向量距离可比较）
        content=content,
        source="瞬时",
        contributor=issue.get("user", {}).get("login", ""),
    )


def _extract_structured_data(body: str) -> dict | None:
    """
    从 Issue body 中提取结构化 JSON 数据
    Extract structured JSON data from Issue body.
    """
    # 匹配 <details> 中的 ```json ... ``` 块
    pattern = r'```json\s*\n(.*?)\n```'
    match = re.search(pattern, body, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except (json.JSONDecodeError, ValueError):
            pass
    return None


def _clean_issue_body(body: str) -> str:
    """
    清理 Issue body，移除 <details> 块和自动生成的签名
    Clean Issue body by removing <details> blocks and auto-generated signatures.
    """
    # 移除 <details> 块
    cleaned = re.sub(r'<details>.*?</details>', '', body, flags=re.DOTALL)
    # 移除自动生成签名
    cleaned = re.sub(r'\*此 Issue 由.*$', '', cleaned, flags=re.DOTALL)
    # 移除分隔线
    cleaned = re.sub(r'\n---\s*$', '', cleaned.strip())
    return cleaned.strip()
