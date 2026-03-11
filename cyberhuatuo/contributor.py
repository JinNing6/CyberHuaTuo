"""
CyberHuaTuo 药方贡献生成器
帮助开发者快速生成规范格式的病例文件
"""

import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import litellm

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


async def smart_extract_contribution(
    issue_text: str,
    prescription: str,
    framework_hint: str = "auto",
    source_url: str = "",
    api_key: str = None,
    provider: str = "openai"
) -> dict[str, Any]:
    """
    使用 LLM 自动提取诊断病例所需的详细信息
    """
    prompt = f"""
你是一个资深的主治医师和程序员专家，正在整理一份《赛博华佗》的 AI 技术纠错药方。
下面是用户提交的极简报错和修复记录，你需要推断并提取出所有必须的结构化字段。

用户遇到的问题（症状/报错）：
{issue_text}

用户的解决方案（药方）：
{prescription}

用户提示的框架：{framework_hint}
参考链接：{source_url}

请输出纯合法的 JSON 内容，不要包含任何 Markdown code block 头尾包裹！
返回字段说明：
- "framework": 如果用户提示了非 auto 框架，请尊重。如果是 auto，请根据代码识别归类出具体框架或工具名（如 langchain, pytorch, transformers, crewai, openai-sdk, fastapi 等小写短名）。覆盖范围包括 AI Agent 框架、LLM SDK、深度学习框架、ML 工具、MLOps 工具等所有 AI 相关技术栈。
- "title": 中文问题标题，20字内简洁有力。
- "title_en": 匹配的英文问题标题。
- "symptom": 症状详细描述（基于输入总结提炼清晰的现象）。
- "error_message": 提取出的纯报错日志或 Traceback（若无也可适当放空）。
- "root_cause": 你根据经验推断的根本原因分析。
- "prescription": 使用 Markdown 格式详细描述修复方案，尽量给出带有 diff 标志的代码块。
- "severity": 只能是 "low", "medium", "high", "critical" 之一。
- "complexity": 只能是 "simple", "moderate", "complex", "extreme" 之一。
- "tags": ["tag1", "tag2"]（2-4个英文或中文标签串）。

一定要确保输出纯正 JSON 能够被 python 的 json.loads 成功解析！
"""
    model_name = "gpt-4o"
    if provider == "anthropic":
        model_name = "claude-3-5-sonnet-20241022"

    try:
        kwargs = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        if api_key:
            kwargs["api_key"] = api_key

        response = await litellm.acompletion(**kwargs)
        raw_content = response.choices[0].message.content.strip()

        # Clean up any potential markdown formatting from the response
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        return json.loads(raw_content.strip())
    except Exception as e:
        print(f"Error extracting contribution via LLM: {e}")
        # Default fallback
        return {
            "framework": framework_hint if framework_hint and framework_hint.lower() != 'auto' else "unknown",
            "title": "自动分析失败请手动修改",
            "title_en": "Auto-generation failed",
            "symptom": issue_text,
            "error_message": "",
            "root_cause": "AI extraction failed.",
            "prescription": prescription,
            "severity": "medium",
            "complexity": "moderate",
            "tags": ["needs-review"]
        }
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
