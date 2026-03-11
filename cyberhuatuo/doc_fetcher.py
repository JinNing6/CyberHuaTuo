"""
CyberHuaTuo 官方文档检索器
通过 Context7 REST API 获取最新官方技术文档，支持智能体直接检索
"""

import asyncio
from dataclasses import dataclass
from typing import Any

import httpx

from .config import config
from .doc_sources import (
    ALL_FRAMEWORKS,
    get_framework,
    search_frameworks,
)


@dataclass
class DocSnippet:
    """检索到的文档片段"""
    title: str
    content: str
    source: str = ""
    framework: str = ""
    framework_name: str = ""
    context7_id: str = ""


# ===== 内存缓存：library_id 动态映射 =====
_library_id_cache: dict[str, str] = {}


async def _api_request(
    endpoint: str,
    params: dict[str, str],
    timeout: float = 15.0,
) -> list[dict[str, Any]] | None:
    """
    发送 Context7 REST API 请求

    Args:
        endpoint: API 端点路径（如 /libs/search 或 /context）
        params: 查询参数
        timeout: 请求超时（秒）

    Returns:
        JSON 响应列表，失败返回 None
    """
    base_url = config.CONTEXT7_BASE_URL.rstrip("/")
    url = f"{base_url}{endpoint}"

    headers = {}
    if config.CONTEXT7_API_KEY:
        headers["Authorization"] = f"Bearer {config.CONTEXT7_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params, headers=headers)

            if response.status_code == 429:
                print("  ⚠️ Context7 API 速率限制，稍后重试")
                return None

            if response.status_code != 200:
                print(f"  ⚠️ Context7 API 错误: HTTP {response.status_code}")
                return None

            data = response.json()

            # API 可能返回列表或带 data 字段的对象
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, dict):
                # 单个结果包装为列表
                return [data]
            return None

    except httpx.TimeoutException:
        print("  ⚠️ Context7 API 请求超时")
        return None
    except Exception as e:
        print(f"  ⚠️ Context7 API 请求失败: {e}")
        return None


async def search_library(
    library_name: str,
    query: str = "",
) -> list[dict[str, Any]]:
    """
    搜索框架库，获取 Context7 Library ID

    Args:
        library_name: 框架名称（如 "react", "langchain"）
        query: 搜索意图描述

    Returns:
        Context7 库列表（包含 id, name, description 等）
    """
    params = {
        "libraryName": library_name,
    }
    if query:
        params["query"] = query

    result = await _api_request("/libs/search", params)
    return result or []


async def fetch_docs(
    library_id: str,
    query: str,
) -> list[DocSnippet]:
    """
    获取指定框架的官方文档片段

    Args:
        library_id: Context7 Library ID（如 /facebook/react）
        query: 查询内容

    Returns:
        文档片段列表
    """
    params = {
        "libraryId": library_id,
        "query": query,
    }

    result = await _api_request("/context", params)
    if not result:
        return []

    snippets = []
    for item in result:
        if isinstance(item, dict):
            snippets.append(DocSnippet(
                title=item.get("title", ""),
                content=item.get("content", ""),
                source=item.get("source", ""),
                context7_id=library_id,
            ))

    return snippets


async def resolve_library_id(framework_key: str, query: str = "") -> str | None:
    """
    解析框架的 Context7 Library ID

    优先使用预映射表，未命中时动态搜索并缓存

    Args:
        framework_key: 框架标识（如 "langchain"）
        query: 可选的搜索意图

    Returns:
        Context7 Library ID，解析失败返回 None
    """
    # 1. 先查预映射表
    fw = get_framework(framework_key)
    if fw:
        return fw.context7_id

    # 2. 查内存缓存
    if framework_key in _library_id_cache:
        return _library_id_cache[framework_key]

    # 3. 动态搜索
    results = await search_library(framework_key, query)
    if results:
        best = results[0]
        lib_id = best.get("id", "")
        if lib_id:
            _library_id_cache[framework_key] = lib_id
            return lib_id

    return None


async def smart_fetch(
    framework_name: str,
    query: str,
    top_k: int = 5,
) -> list[DocSnippet]:
    """
    智能检索：自动解析框架 ID 并获取官方文档

    Args:
        framework_name: 框架名称或 key
        query: 查询内容
        top_k: 返回片段数量上限

    Returns:
        文档片段列表
    """
    if not config.CONTEXT7_ENABLED:
        return []

    # 尝试解析 library_id
    library_id = await resolve_library_id(framework_name, query)

    if not library_id:
        # 尝试用 name 搜索框架
        matched = search_frameworks(framework_name)
        if matched:
            library_id = matched[0].context7_id

    if not library_id:
        return []

    snippets = await fetch_docs(library_id, query)

    # 回填 framework 信息
    fw = get_framework(framework_name)
    for s in snippets:
        s.framework = framework_name
        s.framework_name = fw.name if fw else framework_name

    return snippets[:top_k]


async def multi_framework_fetch(
    query: str,
    framework_keys: list[str] | None = None,
    top_k_per_framework: int = 3,
    max_frameworks: int = 3,
) -> list[DocSnippet]:
    """
    跨多个框架检索官方文档（并发请求）

    Args:
        query: 查询内容
        framework_keys: 指定的框架列表，None 则自动匹配
        top_k_per_framework: 每个框架返回的片段数
        max_frameworks: 最多查询的框架数

    Returns:
        合并后的文档片段列表
    """
    if not config.CONTEXT7_ENABLED:
        return []

    # 自动匹配框架
    if not framework_keys:
        matched = search_frameworks(query)
        framework_keys = [fw.key for fw in matched[:max_frameworks]]

    if not framework_keys:
        return []

    # 并发获取各框架文档
    tasks = [
        smart_fetch(key, query, top_k=top_k_per_framework)
        for key in framework_keys[:max_frameworks]
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_snippets = []
    for result in results:
        if isinstance(result, list):
            all_snippets.extend(result)

    return all_snippets


def get_supported_frameworks_info() -> list[dict[str, Any]]:
    """
    获取所有支持的框架信息（用于 API 展示）

    Returns:
        框架信息列表
    """
    return [
        {
            "key": fw.key,
            "name": fw.name,
            "category": fw.category,
            "language": fw.language,
            "description": fw.description,
            "context7_id": fw.context7_id,
            "tags": list(fw.tags),
        }
        for fw in ALL_FRAMEWORKS
    ]
