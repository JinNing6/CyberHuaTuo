"""
CyberHuaTuo 索引构建器
解析 cases/ 目录下所有 .md 病例文件，构建 ChromaDB 向量索引
"""

import re
import hashlib
from pathlib import Path
from typing import Any

import yaml
import chromadb

from .config import config


def parse_case_file(filepath: Path) -> dict[str, Any] | None:
    """
    解析单个病例文件，提取 YAML 元数据和 Markdown 正文

    Returns:
        dict 包含 metadata 和 content，解析失败返回 None
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠️ 无法读取文件 {filepath}: {e}")
        return None

    # 解析 YAML Front Matter
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not yaml_match:
        print(f"  ⚠️ 文件缺少 YAML Front Matter: {filepath}")
        return None

    try:
        metadata = yaml.safe_load(yaml_match.group(1))
    except yaml.YAMLError as e:
        print(f"  ⚠️ YAML 解析错误 {filepath}: {e}")
        return None

    content = yaml_match.group(2).strip()

    # 构建用于 Embedding 的文本（标题 + 症状 + 错误信息 + 药方）
    embedding_text = f"{metadata.get('title', '')} {metadata.get('title_en', '')} {content}"

    return {
        "id": metadata.get("id", filepath.stem),
        "metadata": metadata,
        "content": content,
        "embedding_text": embedding_text,
        "filepath": str(filepath.relative_to(config.ROOT_DIR)),
    }


def scan_cases(cases_dir: Path | None = None) -> list[dict[str, Any]]:
    """
    扫描 cases/ 目录，解析所有病例文件

    Returns:
        解析成功的病例列表
    """
    cases_dir = cases_dir or config.CASES_DIR

    if not cases_dir.exists():
        print(f"⚠️ 病例目录不存在: {cases_dir}")
        return []

    cases = []
    md_files = sorted(cases_dir.rglob("*.md"))

    for filepath in md_files:
        # 跳过索引文件和非病例文件
        if filepath.name.startswith("_"):
            continue

        case = parse_case_file(filepath)
        if case:
            cases.append(case)

    return cases


def build_index(force_rebuild: bool = False) -> tuple[chromadb.ClientAPI, int]:
    """
    构建或加载 ChromaDB 向量索引

    Args:
        force_rebuild: 是否强制重建索引

    Returns:
        (chroma_client, 索引中的病例数量)
    """
    print("🩺 CyberHuaTuo 索引构建器")
    print("=" * 40)

    # 初始化 ChromaDB（持久化存储）
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

    # 检查是否需要重建
    try:
        collection = client.get_collection(name=config.COLLECTION_NAME)
        existing_count = collection.count()
        if existing_count > 0 and not force_rebuild:
            print(f"✅ 已有索引（{existing_count} 个病例），跳过构建")
            return client, existing_count
        # 强制重建时删除旧集合
        if force_rebuild:
            print("🔄 强制重建索引...")
            client.delete_collection(name=config.COLLECTION_NAME)
    except Exception:
        pass  # 集合不存在，正常创建

    # 扫描病例文件
    print(f"📂 扫描病例目录: {config.CASES_DIR}")
    cases = scan_cases()

    if not cases:
        print("⚠️ 未找到任何病例文件")
        collection = client.get_or_create_collection(name=config.COLLECTION_NAME)
        return client, 0

    print(f"📋 发现 {len(cases)} 个病例文件")

    # 创建集合（使用 ChromaDB 默认的 Embedding 函数）
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"description": "CyberHuaTuo 病例知识库"}
    )

    # 批量添加到向量数据库
    ids = []
    documents = []
    metadatas = []

    for case in cases:
        case_id = case["id"]
        # 用文件路径的 hash 确保 ID 唯一性
        unique_id = hashlib.md5(case["filepath"].encode()).hexdigest()[:12] + "_" + case_id
        ids.append(unique_id)
        documents.append(case["embedding_text"])

        # ChromaDB metadata 只支持 str/int/float/bool
        meta = {
            "case_id": case["id"],
            "title": case["metadata"].get("title", ""),
            "title_en": case["metadata"].get("title_en", ""),
            "framework": case["metadata"].get("framework", "unknown"),
            "severity": case["metadata"].get("severity", "medium"),
            "complexity": case["metadata"].get("complexity", "moderate"),
            "filepath": case["filepath"],
        }
        # 将 tags 列表转为逗号分隔字符串
        tags = case["metadata"].get("tags", [])
        if isinstance(tags, list):
            meta["tags"] = ",".join(tags)
        else:
            meta["tags"] = str(tags)

        metadatas.append(meta)

    # 添加到 ChromaDB
    print(f"🧠 生成向量并索引 {len(ids)} 个病例...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"✅ 索引构建完成！共 {collection.count()} 个病例已入库")
    return client, collection.count()


def get_case_content(filepath: str) -> str | None:
    """根据相对路径读取病例文件完整内容"""
    full_path = config.ROOT_DIR / filepath
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    return None
