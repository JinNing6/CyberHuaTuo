"""
🤖 CyberHuaTuo GitHub Bot — 轻量级药方匹配引擎
纯 Python 实现，无外部依赖（除 pyyaml），可在 GitHub Actions CI 中直接运行

匹配策略：
1. 框架名检测 — Issue 中是否提到已知框架
2. 错误类型匹配 — 关键词匹配（ImportError, OOM, timeout 等）
3. Tags 匹配 — 与药方 tags 交叉匹配
4. 文本相似度 — 基于词频的简单 TF-IDF 相似度
"""

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


# ============================================================
# 数据结构
# ============================================================

@dataclass
class Prescription:
    """一个药方（来自 cases/ 目录下的 .md 文件）"""
    id: str
    title: str
    title_en: str
    framework: str
    severity: str
    complexity: str
    tags: list[str]
    filepath: str               # 相对于项目根目录的路径
    content: str                # Markdown 正文
    error_patterns: list[str]   # 从内容中提取的错误关键词

    # 用于匹配的预处理文本
    _search_text: str = ""


@dataclass
class MatchResult:
    """匹配结果"""
    prescription: Prescription
    score: float                 # 0-100 的综合得分
    match_reasons: list[str]     # 匹配原因说明
    framework_matched: bool = False
    error_matched: bool = False
    tag_matched: bool = False
    text_similarity: float = 0.0


# ============================================================
# 已知框架名映射（用于检测 Issue 中提到的框架）
# ============================================================

FRAMEWORK_ALIASES: dict[str, list[str]] = {
    "langchain": ["langchain", "lang chain", "lang-chain", "lcel"],
    "llamaindex": ["llamaindex", "llama index", "llama-index", "llama_index"],
    "crewai": ["crewai", "crew ai", "crew-ai", "crew_ai"],
    "autogen": ["autogen", "auto gen", "auto-gen", "pyautogen"],
    "openai-sdk": ["openai", "openai-sdk", "openai sdk", "gpt-4", "gpt4", "chatgpt"],
    "mcp": ["mcp", "model context protocol", "model-context-protocol"],
    "dspy": ["dspy", "dsp-y"],
    "haystack": ["haystack", "deepset"],
    "semantic-kernel": ["semantic-kernel", "semantic kernel", "sk"],
    "pydantic-ai": ["pydantic-ai", "pydantic ai", "pydanticai"],
    "langgraph": ["langgraph", "lang graph", "lang-graph"],
    "pytorch": ["pytorch", "torch", "py-torch"],
    "transformers": ["transformers", "huggingface", "hugging face", "hf"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "custom-agent": ["custom agent", "自定义 agent", "自建 agent"],
    "platform-agent": ["gpts", "coze", "dify", "ragflow"],
    "ml-ops": ["mlops", "ml-ops", "kubeflow", "mlflow"],
    "general-ai": ["ai", "llm", "大模型", "机器学习"],
}

# 常见错误类型关键词
ERROR_KEYWORDS: list[str] = [
    "importerror", "import error", "cannot import",
    "modulenotfounderror", "module not found",
    "attributeerror", "attribute error", "has no attribute",
    "typeerror", "type error",
    "valueerror", "value error",
    "runtimeerror", "runtime error",
    "connectionerror", "connection error", "connection refused",
    "timeouterror", "timeout", "timed out",
    "memoryerror", "memory error", "oom", "out of memory",
    "keyerror", "key error",
    "filenotfounderror", "file not found",
    "permissionerror", "permission denied",
    "recursionerror", "recursion", "maximum recursion",
    "infinite loop", "无限循环", "死循环",
    "breaking change", "breaking-change", "deprecated",
    "api change", "api 变更",
    "rate limit", "rate-limit", "429",
    "token limit", "context length", "max tokens",
]


# ============================================================
# 药方加载器
# ============================================================

def _parse_case_file(filepath: Path) -> Prescription | None:
    """
    解析单个药方文件，提取 YAML 元数据和 Markdown 正文
    复用 indexer.py 的逻辑，但不依赖 config 模块
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    # 解析 YAML Front Matter
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not yaml_match:
        return None

    try:
        metadata = yaml.safe_load(yaml_match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(metadata, dict):
        return None

    content = yaml_match.group(2).strip()

    # 从内容中提取错误模式
    error_patterns = _extract_error_patterns(content)

    # 预处理 tags
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        tags = [str(tags)]

    prescription = Prescription(
        id=metadata.get("id", filepath.stem),
        title=metadata.get("title", ""),
        title_en=metadata.get("title_en", ""),
        framework=metadata.get("framework", "unknown"),
        severity=metadata.get("severity", "medium"),
        complexity=metadata.get("complexity", "moderate"),
        tags=tags,
        filepath=str(filepath),
        content=content,
        error_patterns=error_patterns,
    )

    # 构建搜索文本（用于文本相似度计算）
    prescription._search_text = " ".join([
        prescription.title,
        prescription.title_en,
        prescription.framework,
        " ".join(prescription.tags),
        content[:3000],  # 取前 3000 字符避免过长
    ]).lower()

    return prescription


def _extract_error_patterns(content: str) -> list[str]:
    """
    从药方内容中提取错误模式（代码块中的错误消息）
    """
    patterns = []

    # 提取 ``` 代码块中的错误关键行
    code_blocks = re.findall(r"```(?:\w+)?\s*\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        for line in block.split("\n"):
            line_stripped = line.strip()
            # 匹配常见的错误行
            if any(kw in line_stripped.lower() for kw in [
                "error", "exception", "traceback", "failed", "cannot",
            ]):
                if len(line_stripped) > 10:
                    patterns.append(line_stripped)

    return patterns[:10]  # 最多保留 10 个错误模式


def load_prescriptions(cases_dir: Path) -> list[Prescription]:
    """
    加载 cases/ 目录下所有药方文件

    Args:
        cases_dir: cases/ 目录的绝对路径

    Returns:
        所有成功解析的药方列表
    """
    if not cases_dir.exists():
        return []

    prescriptions = []
    for filepath in sorted(cases_dir.rglob("*.md")):
        # 跳过索引文件
        if filepath.name.startswith("_"):
            continue

        prescription = _parse_case_file(filepath)
        if prescription:
            # 将路径转为相对路径（相对于 cases/ 的父目录）
            try:
                rel_path = filepath.relative_to(cases_dir.parent)
                prescription.filepath = str(rel_path).replace("\\", "/")
            except ValueError:
                pass
            prescriptions.append(prescription)

    return prescriptions


# ============================================================
# 匹配引擎核心
# ============================================================

def _detect_frameworks(text: str) -> list[str]:
    """从文本中检测提到的框架名"""
    text_lower = text.lower()
    detected = []

    for framework, aliases in FRAMEWORK_ALIASES.items():
        for alias in aliases:
            if alias in text_lower:
                detected.append(framework)
                break

    return detected


def _detect_error_types(text: str) -> list[str]:
    """从文本中检测错误类型关键词"""
    text_lower = text.lower()
    detected = []

    for kw in ERROR_KEYWORDS:
        if kw in text_lower:
            detected.append(kw)

    return detected


def _tokenize(text: str) -> list[str]:
    """简单的分词器（英文空格分词 + 中文字符分词）"""
    # 移除 Markdown 标记
    text = re.sub(r"[#*`\[\](){}|>~_]", " ", text)
    # 移除 URL
    text = re.sub(r"https?://\S+", " ", text)

    tokens = []
    # 英文分词（按非字母数字分割）
    for word in re.findall(r"[a-zA-Z0-9_\-\.]+", text.lower()):
        if len(word) > 1:  # 忽略单字符
            tokens.append(word)

    # 中文分词（逐字，简单但有效）
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            tokens.append(char)

    return tokens


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    """计算词频 (TF)"""
    tf: dict[str, float] = {}
    total = len(tokens)
    if total == 0:
        return tf

    for token in tokens:
        tf[token] = tf.get(token, 0) + 1

    # 归一化
    for token in tf:
        tf[token] /= total

    return tf


def _compute_text_similarity(query_text: str, doc_text: str) -> float:
    """
    计算两段文本的简单相似度（基于共同词频）
    返回 0.0 - 1.0 的相似度分数
    """
    query_tokens = _tokenize(query_text)
    doc_tokens = _tokenize(doc_text)

    if not query_tokens or not doc_tokens:
        return 0.0

    query_tf = _compute_tf(query_tokens)
    doc_tf = _compute_tf(doc_tokens)

    # 计算余弦相似度
    common_tokens = set(query_tf.keys()) & set(doc_tf.keys())
    if not common_tokens:
        return 0.0

    dot_product = sum(query_tf[t] * doc_tf[t] for t in common_tokens)
    query_norm = math.sqrt(sum(v ** 2 for v in query_tf.values()))
    doc_norm = math.sqrt(sum(v ** 2 for v in doc_tf.values()))

    if query_norm == 0 or doc_norm == 0:
        return 0.0

    return dot_product / (query_norm * doc_norm)


def _compute_error_pattern_similarity(issue_text: str, prescription: Prescription) -> float:
    """
    计算 Issue 文本与药方错误模式的匹配度
    """
    if not prescription.error_patterns:
        return 0.0

    issue_lower = issue_text.lower()
    matched_count = 0

    for pattern in prescription.error_patterns:
        # 直接字符串包含匹配
        if pattern.lower() in issue_lower:
            matched_count += 1
            continue

        # 提取模式中的核心关键词进行匹配
        core_words = [w for w in pattern.lower().split() if len(w) > 3]
        if core_words:
            match_ratio = sum(1 for w in core_words if w in issue_lower) / len(core_words)
            if match_ratio > 0.5:
                matched_count += 0.5

    return min(1.0, matched_count / max(1, len(prescription.error_patterns)))


def match_prescriptions(
    issue_title: str,
    issue_body: str,
    prescriptions: list[Prescription],
    top_k: int = 3,
    min_score: float = 15.0,
) -> list[MatchResult]:
    """
    将 Issue 内容与药方库进行匹配

    Args:
        issue_title: Issue 标题
        issue_body: Issue 正文
        prescriptions: 药方列表
        top_k: 返回 Top-K 结果
        min_score: 最低匹配分数阈值

    Returns:
        按相关度降序排列的匹配结果列表
    """
    if not prescriptions:
        return []

    full_text = f"{issue_title} {issue_body}"

    # 1. 检测 Issue 中提到的框架
    detected_frameworks = _detect_frameworks(full_text)

    # 2. 检测 Issue 中的错误类型
    detected_errors = _detect_error_types(full_text)

    # 3. 对每个药方计算综合得分
    results = []
    for rx in prescriptions:
        score = 0.0
        reasons = []

        # —— 维度 1：框架匹配（权重 30）——
        framework_matched = rx.framework in detected_frameworks
        if framework_matched:
            score += 30.0
            reasons.append(f"框架匹配: {rx.framework}")

        # —— 维度 2：错误关键词匹配（权重 25）——
        error_matched = False
        rx_error_text = " ".join(rx.error_patterns + rx.tags).lower()
        common_errors = [e for e in detected_errors if e in rx_error_text or e in rx._search_text]
        if common_errors:
            error_matched = True
            error_score = min(25.0, len(common_errors) * 8.0)
            score += error_score
            reasons.append(f"错误匹配: {', '.join(common_errors[:3])}")

        # —— 维度 3：Tags 匹配（权重 15）——
        tag_matched = False
        issue_tags = set(_tokenize(full_text))
        rx_tags_flat = set()
        for tag in rx.tags:
            for part in tag.lower().replace("-", " ").split():
                rx_tags_flat.add(part)
        common_tags = issue_tags & rx_tags_flat
        if common_tags:
            tag_matched = True
            tag_score = min(15.0, len(common_tags) * 5.0)
            score += tag_score
            reasons.append(f"标签匹配: {', '.join(list(common_tags)[:3])}")

        # —— 维度 4：错误模式精确匹配（权重 20）——
        error_pattern_sim = _compute_error_pattern_similarity(full_text, rx)
        if error_pattern_sim > 0:
            pattern_score = error_pattern_sim * 20.0
            score += pattern_score
            reasons.append(f"错误模式匹配: {error_pattern_sim:.0%}")

        # —— 维度 5：文本相似度（权重 10）——
        text_sim = _compute_text_similarity(full_text, rx._search_text)
        if text_sim > 0.01:
            sim_score = text_sim * 10.0
            score += sim_score

        if score >= min_score:
            results.append(MatchResult(
                prescription=rx,
                score=round(score, 1),
                match_reasons=reasons,
                framework_matched=framework_matched,
                error_matched=error_matched,
                tag_matched=tag_matched,
                text_similarity=round(text_sim, 3),
            ))

    # 按分数降序排序
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


# ============================================================
# 回复格式化
# ============================================================

# 严重性图标映射
SEVERITY_ICONS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}

# 复杂度图标映射
COMPLEXITY_ICONS = {
    "extreme": "💀",
    "complex": "🧩",
    "moderate": "⚙️",
    "simple": "✅",
}


def _extract_quick_fix(content: str) -> str | None:
    """
    从药方内容中提取速效药（第一个代码块）
    """
    # 查找 "推荐" 或 "药方 1" 后面的代码块
    recommended_pattern = re.search(
        r"(?:推荐|药方\s*1|Prescription\s*1).*?```(\w*)\s*\n(.*?)```",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if recommended_pattern:
        lang = recommended_pattern.group(1) or ""
        code = recommended_pattern.group(2).strip()
        if code and len(code) < 500:
            return f"```{lang}\n{code}\n```"

    # 退而求其次：取第一个代码块
    first_code = re.search(r"```(\w*)\s*\n(.*?)```", content, re.DOTALL)
    if first_code:
        lang = first_code.group(1) or ""
        code = first_code.group(2).strip()
        if code and len(code) < 500:
            return f"```{lang}\n{code}\n```"

    return None


def format_bot_reply(
    matches: list[MatchResult],
    trigger_type: str = "auto",
    repo_url: str = "",
) -> str:
    """
    生成 Bot 回复的 Markdown 内容

    Args:
        matches: 匹配结果列表
        trigger_type: 触发类型 ("auto" = 新 Issue 自动匹配,
                                 "mention" = @CyberHuaTuo 提及)
        repo_url: 仓库 URL，用于生成药方链接

    Returns:
        格式化的 Markdown 回复
    """
    if not matches:
        if trigger_type == "mention":
            return (
                "## 🩺 赛博华佗 · 自动诊断\n"
                "CyberHuaTuo · Auto Diagnosis\n\n"
                "> 🤖 *华佗仔细检查了您的描述，但医书中暂未找到匹配的药方。*\n\n"
                "### 💡 建议\n\n"
                "- 请提供更多错误信息（完整的 Traceback、错误日志等）\n"
                "- 尝试描述您使用的框架名称和版本\n"
                "- 您也可以访问 [CyberHuaTuo 在线门诊](https://github.com/JinNing6/CyberHuaTuo) "
                "获取 AI 望闻问切诊断\n\n"
                "---\n"
                "*🤖 此回复由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*"
            )
        return ""  # 自动匹配没结果时不回复

    # 构建回复
    parts = []

    # Header
    parts.append("## 🩺 赛博华佗 · 自动诊断")
    parts.append("CyberHuaTuo · Auto Diagnosis\n")

    if trigger_type == "auto":
        parts.append("> 🤖 *华佗听闻此症，翻阅医书，为阁下找到了以下相关药方。*\n")
    else:
        parts.append("> 🤖 *赛博华佗在此！已为您检索知识库，找到以下匹配药方。*\n")

    # 药方列表
    for i, match in enumerate(matches, 1):
        rx = match.prescription
        sev_icon = SEVERITY_ICONS.get(rx.severity, "⚪")
        comp_icon = COMPLEXITY_ICONS.get(rx.complexity, "⚙️")

        # 药方标题
        parts.append(f"### 💊 药方 {i}：{rx.title}（相关度 {match.score:.0f}%）")
        parts.append(f"**{rx.title_en}**\n")

        # 元信息
        parts.append(
            f"| 框架 | 严重性 | 复杂度 | 匹配原因 |\n"
            f"|:----:|:------:|:------:|:--------:|\n"
            f"| `{rx.framework}` | {sev_icon} {rx.severity} "
            f"| {comp_icon} {rx.complexity} "
            f"| {' · '.join(match.match_reasons[:2]) if match.match_reasons else '文本相似'} |\n"
        )

        # 速效药
        quick_fix = _extract_quick_fix(rx.content)
        if quick_fix:
            parts.append("**⚡ 速效药:**\n")
            parts.append(quick_fix)
            parts.append("")

        # 药方链接
        if repo_url:
            filepath_link = f"{repo_url}/blob/main/{rx.filepath}"
            parts.append(f"📋 [查看完整药方]({filepath_link})\n")
        else:
            parts.append(f"📋 完整药方路径: `{rx.filepath}`\n")

        if i < len(matches):
            parts.append("---\n")

    # Footer
    parts.append("\n---\n")
    parts.append(
        "> 💡 **以上药方来自 CyberHuaTuo 知识库的自动匹配**\n"
        "> \n"
        "> 🏥 药方有效？请给 [CyberHuaTuo](https://github.com/JinNing6/CyberHuaTuo) "
        "一个 ⭐ 支持开源中医\n"
        "> \n"
        "> 📝 药方不对？欢迎 [贡献更好的药方]"
        "(https://github.com/JinNing6/CyberHuaTuo/issues/new?template=prescription.yml)\n"
        "> \n"
        "> 🔮 需要更精准的 AI 望闻问切诊断？访问 "
        "[CyberHuaTuo 在线门诊](https://github.com/JinNing6/CyberHuaTuo)\n\n"
        "*🤖 此回复由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成 · "
        "在你的仓库也安装 Bot？[查看指引](https://github.com/JinNing6/CyberHuaTuo/blob/main/docs/GITHUB_BOT.md)*"
    )

    return "\n".join(parts)
