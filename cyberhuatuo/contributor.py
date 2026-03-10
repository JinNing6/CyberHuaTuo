"""
CyberHuaTuo 药方贡献生成器
帮助开发者快速生成规范格式的病例文件
"""

import re
from datetime import date
from pathlib import Path
from dataclasses import dataclass, field

from .config import config
from .doc_sources import get_agent_framework_keys


# 框架枚举值（从 doc_sources 动态获取 Agent 框架列表）
FRAMEWORKS = get_agent_framework_keys()

# 严重性枚举
SEVERITIES = ["low", "medium", "high", "critical"]

# 复杂度枚举
COMPLEXITIES = ["simple", "moderate", "complex", "extreme"]

# 复杂度对应的 emoji
COMPLEXITY_EMOJI = {
    "simple": "🟢",
    "moderate": "🟡",
    "complex": "🔴",
    "extreme": "⚫",
}


@dataclass
class CaseSubmission:
    """用户提交的药方数据"""
    framework: str
    title: str
    title_en: str = ""
    error_message: str = ""
    symptom: str = ""
    root_cause: str = ""
    prescription: str = ""
    severity: str = "medium"
    complexity: str = "moderate"
    tags: list[str] = field(default_factory=list)
    framework_version: str = ""
    language: str = "python"
    contributor_github: str = "anonymous"
    source_url: str = ""


def generate_case_id(framework: str, title: str) -> str:
    """基于框架和标题生成唯一病例 ID"""
    # 从标题中提取关键词
    keywords = re.sub(r"[^\w\s-]", "", title.lower())
    keywords = re.sub(r"\s+", "-", keywords.strip())
    # 最多取前 4 个词
    parts = keywords.split("-")[:4]
    keyword_slug = "-".join(parts)

    # 获取同框架下的下一个序号
    framework_dir = config.CASES_DIR / framework
    existing_ids = set()
    if framework_dir.exists():
        for f in framework_dir.rglob("*.md"):
            if not f.name.startswith("_"):
                existing_ids.add(f.stem)

    # 寻找可用序号
    for seq in range(1, 1000):
        case_id = f"{framework}-{keyword_slug}-{seq:03d}"
        if case_id not in existing_ids:
            return case_id

    return f"{framework}-{keyword_slug}-999"


def determine_category(tags: list[str], error_message: str) -> str:
    """根据标签和错误信息推断问题类别目录"""
    category_keywords = {
        "import-error": ["import", "module", "package"],
        "breaking-change": ["breaking", "migration", "upgrade", "deprecated"],
        "memory": ["memory", "leak", "oom", "out of memory"],
        "performance": ["slow", "performance", "timeout", "latency"],
        "tool-calling": ["tool", "function call", "mcp"],
        "agent-behavior": ["loop", "stuck", "infinite", "agent"],
        "authentication": ["api key", "auth", "token", "credential"],
        "configuration": ["config", "setup", "install", "environment"],
        "retrieval": ["retrieval", "rag", "vector", "embedding", "search"],
    }

    combined_text = " ".join(tags + [error_message]).lower()

    for category, keywords in category_keywords.items():
        if any(kw in combined_text for kw in keywords):
            return category

    return "general"


def generate_case_markdown(submission: CaseSubmission) -> str:
    """
    从用户提交数据生成规范的 YAML + Markdown 病例文件

    Returns:
        完整的 .md 文件内容
    """
    case_id = generate_case_id(submission.framework, submission.title)
    today = date.today().isoformat()

    # 构建 YAML Front Matter
    tags_yaml = "\n".join(f'  - "{tag}"' for tag in submission.tags) if submission.tags else '  - "general"'

    yaml_section = f"""---
id: "{case_id}"
title: "{submission.title}"
title_en: "{submission.title_en}"
framework: "{submission.framework}"
framework_version: "{submission.framework_version}"
language: "{submission.language}"
tags:
{tags_yaml}
severity: "{submission.severity}"
complexity: "{submission.complexity}"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "{today}"
updated_at: "{today}"
contributors:
  - github: "{submission.contributor_github}"
source_url: "{submission.source_url}"
related_cases: []
---"""

    # 构建 Markdown 正文
    sections = []

    sections.append(f"## 🏥 症状描述\nSymptom Description\n\n{submission.symptom or '（请补充症状描述）'}")

    if submission.error_message:
        sections.append(f"## 🔍 错误信息\nError Message\n\n```\n{submission.error_message}\n```")

    if submission.root_cause:
        sections.append(f"## 🔬 根因分析\nRoot Cause Analysis\n\n{submission.root_cause}")

    if submission.prescription:
        sections.append(f"## 💊 药方\nPrescriptions\n\n### 药方 1\n\n{submission.prescription}")
    else:
        sections.append("## 💊 药方\nPrescriptions\n\n### 药方 1\n\n（请补充解决方案）")

    sections.append("## 🔗 参考资料\nReferences\n\n- （请补充参考链接）")

    body = "\n\n".join(sections)

    return f"{yaml_section}\n\n{body}\n"


def save_case_file(submission: CaseSubmission) -> dict:
    """
    保存病例文件到 cases/ 目录

    Returns:
        dict 包含文件路径和 case_id
    """
    # 确定目标目录
    category = determine_category(submission.tags, submission.error_message)
    target_dir = config.CASES_DIR / submission.framework / category
    target_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件内容
    content = generate_case_markdown(submission)
    case_id = generate_case_id(submission.framework, submission.title)

    # 写入文件
    filename = f"{case_id.split(f'{submission.framework}-', 1)[-1]}.md"
    filepath = target_dir / filename
    filepath.write_text(content, encoding="utf-8")

    relative_path = str(filepath.relative_to(config.ROOT_DIR))

    return {
        "case_id": case_id,
        "filepath": relative_path,
        "absolute_path": str(filepath),
        "content_preview": content[:500],
    }
