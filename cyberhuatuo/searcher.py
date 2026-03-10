"""
CyberHuaTuo 搜索引擎
支持向量语义搜索和元数据过滤
"""

from dataclasses import dataclass

import chromadb

from .config import config
from .indexer import get_case_content


@dataclass
class SearchResult:
    """搜索结果"""
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
    在知识库中搜索匹配的病例

    Args:
        client: ChromaDB 客户端
        query: 搜索查询（错误信息/问题描述）
        framework: 按框架过滤
        severity: 按严重性过滤
        complexity: 按复杂度过滤
        top_k: 返回结果数量
        include_content: 是否加载完整文件内容

    Returns:
        排序后的搜索结果列表
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

    for i, (doc_id, distance, metadata) in enumerate(zip(ids, distances, metadatas)):
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
        ))

    return search_results
