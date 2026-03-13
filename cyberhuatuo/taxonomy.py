"""
CyberHuaTuo Root Cause Taxonomy -- CHT (CyberHuaTuo) Coding System
Inspired by ICD (International Classification of Diseases)

CHT codes follow standard: CHT-{CATEGORY}-{NUMBER}
Example: CHT-CFG-001 Configuration Error

This module provides:
  1. Root cause code definitions
  2. Keyword-based auto-classification
  3. Query/lookup utilities
"""

from __future__ import annotations

from dataclasses import dataclass

# ============================================================
# CHT Root Cause Code Definitions
# ============================================================

@dataclass(frozen=True)
class CHTCode:
    """A single CHT root cause code entry."""
    code: str            # e.g. "CHT-CFG-001"
    category: str        # e.g. "CFG"
    name_cn: str         # Chinese name
    name_en: str         # English name
    description_cn: str  # Chinese description
    description_en: str  # English description
    keywords: tuple[str, ...]  # keywords for auto-classification


# ---- Category definitions ----

_CODES: list[CHTCode] = [
    # ======= CFG: Configuration Errors =======
    CHTCode(
        code="CHT-CFG-001",
        category="CFG",
        name_cn="环境变量缺失/错误",
        name_en="Missing or Invalid Environment Variable",
        description_cn="环境变量未设置或值不正确导致的启动/运行失败",
        description_en="Startup or runtime failure due to missing or invalid environment variables",
        keywords=("env", "environment", "variable", "config", "missing key",
                  "not set", "undefined", "api_key", "api key", ".env"),
    ),
    CHTCode(
        code="CHT-CFG-002",
        category="CFG",
        name_cn="配置文件格式错误",
        name_en="Malformed Configuration File",
        description_cn="YAML/JSON/TOML 等配置文件格式不正确",
        description_en="Incorrectly formatted configuration file (YAML/JSON/TOML etc.)",
        keywords=("yaml", "json", "toml", "config file", "parse error",
                  "syntax error", "malformed", "invalid format"),
    ),
    CHTCode(
        code="CHT-CFG-003",
        category="CFG",
        name_cn="参数类型/取值错误",
        name_en="Invalid Parameter Type or Value",
        description_cn="函数或类接收到不期望的参数类型或取值范围",
        description_en="Function or class received unexpected parameter type or value range",
        keywords=("parameter", "argument", "type error", "invalid value",
                  "typeerror", "expected", "got", "invalid argument"),
    ),

    # ======= DEP: Dependency Conflicts =======
    CHTCode(
        code="CHT-DEP-001",
        category="DEP",
        name_cn="依赖版本冲突",
        name_en="Dependency Version Conflict",
        description_cn="不同包之间的版本依赖冲突",
        description_en="Version conflict between different packages",
        keywords=("version", "conflict", "incompatible", "requires",
                  "dependency", "pip", "no matching distribution", "upgrade"),
    ),
    CHTCode(
        code="CHT-DEP-002",
        category="DEP",
        name_cn="依赖缺失/未安装",
        name_en="Missing Dependency",
        description_cn="所需包未安装或未找到模块",
        description_en="Required package not installed or module not found",
        keywords=("modulenotfounderror", "import error", "no module named",
                  "not installed", "pip install", "package not found"),
    ),
    CHTCode(
        code="CHT-DEP-003",
        category="DEP",
        name_cn="API 变更/弃用",
        name_en="API Breaking Change or Deprecation",
        description_cn="框架升级后 API 变更导致代码不兼容",
        description_en="Code incompatibility due to API changes after framework upgrade",
        keywords=("deprecated", "removed", "breaking change", "migration",
                  "no longer supported", "was removed", "changed in", "rename"),
    ),

    # ======= MEM: Memory and Resource =======
    CHTCode(
        code="CHT-MEM-001",
        category="MEM",
        name_cn="内存溢出/OOM",
        name_en="Out of Memory (OOM)",
        description_cn="系统或 GPU 内存不足导致崩溃",
        description_en="System or GPU memory exhaustion causing crash",
        keywords=("oom", "out of memory", "memory error", "cuda out of memory",
                  "killed", "memory leak", "allocation failed"),
    ),
    CHTCode(
        code="CHT-MEM-002",
        category="MEM",
        name_cn="资源泄漏",
        name_en="Resource Leak",
        description_cn="文件句柄、连接、线程池等资源未正确释放",
        description_en="Unreleased resources such as file handles, connections, or thread pools",
        keywords=("resource leak", "connection leak", "file handle", "not closed",
                  "too many open files", "pool exhausted", "connection pool"),
    ),
    CHTCode(
        code="CHT-MEM-003",
        category="MEM",
        name_cn="上下文窗口溢出",
        name_en="Context Window Overflow",
        description_cn="LLM 输入超过上下文窗口限制",
        description_en="LLM input exceeds context window limit",
        keywords=("context window", "token limit", "max tokens", "context length",
                  "too many tokens", "exceeds maximum", "truncat"),
    ),

    # ======= NET: Network and Communication =======
    CHTCode(
        code="CHT-NET-001",
        category="NET",
        name_cn="网络连接失败",
        name_en="Network Connection Failure",
        description_cn="API 请求超时、DNS 解析失败或连接被拒绝",
        description_en="API request timeout, DNS resolution failure, or connection refused",
        keywords=("timeout", "connection refused", "dns", "network error",
                  "connection error", "unreachable", "connection reset"),
    ),
    CHTCode(
        code="CHT-NET-002",
        category="NET",
        name_cn="API 速率限制",
        name_en="API Rate Limit Exceeded",
        description_cn="API 调用频率超过限制被拒绝",
        description_en="API call frequency exceeded, request rejected",
        keywords=("rate limit", "429", "too many requests", "quota exceeded",
                  "throttle", "retry after"),
    ),
    CHTCode(
        code="CHT-NET-003",
        category="NET",
        name_cn="认证/鉴权失败",
        name_en="Authentication or Authorization Failure",
        description_cn="API Key 无效、过期或权限不足",
        description_en="Invalid or expired API key, or insufficient permissions",
        keywords=("401", "403", "unauthorized", "forbidden", "invalid api key",
                  "authentication", "permission denied", "access denied"),
    ),

    # ======= PRM: Prompt Engineering =======
    CHTCode(
        code="CHT-PRM-001",
        category="PRM",
        name_cn="Prompt 注入攻击",
        name_en="Prompt Injection Attack",
        description_cn="恶意输入绕过 Prompt 限制执行非预期操作",
        description_en="Malicious input bypasses prompt constraints to execute unintended operations",
        keywords=("prompt injection", "jailbreak", "ignore previous",
                  "system prompt leak", "prompt attack"),
    ),
    CHTCode(
        code="CHT-PRM-002",
        category="PRM",
        name_cn="输出格式不稳定",
        name_en="Unstable Output Format",
        description_cn="LLM 输出格式不符合期望导致解析失败",
        description_en="LLM output format does not match expectations, causing parsing failure",
        keywords=("json parse", "output format", "parsing error", "expected json",
                  "invalid json", "structured output", "format error"),
    ),
    CHTCode(
        code="CHT-PRM-003",
        category="PRM",
        name_cn="幻觉/事实错误",
        name_en="Hallucination or Factual Error",
        description_cn="LLM 生成不准确或虚假的信息",
        description_en="LLM generates inaccurate or fabricated information",
        keywords=("hallucination", "factual error", "incorrect answer",
                  "made up", "fabricate", "not accurate"),
    ),

    # ======= SEC: Security Vulnerabilities =======
    CHTCode(
        code="CHT-SEC-001",
        category="SEC",
        name_cn="代码注入风险",
        name_en="Code Injection Risk",
        description_cn="不安全的 eval/exec/subprocess 使用",
        description_en="Unsafe usage of eval/exec/subprocess",
        keywords=("eval(", "exec(", "code injection", "subprocess",
                  "shell injection", "command injection", "os.system"),
    ),
    CHTCode(
        code="CHT-SEC-002",
        category="SEC",
        name_cn="密钥泄漏",
        name_en="Secret or Credential Leakage",
        description_cn="API Key、密码等敏感信息在代码或日志中泄漏",
        description_en="API keys, passwords, or other secrets exposed in code or logs",
        keywords=("hardcoded", "secret", "credential", "password in code",
                  "key leak", "exposed", "plaintext password"),
    ),
    CHTCode(
        code="CHT-SEC-003",
        category="SEC",
        name_cn="输出未消毒",
        name_en="Unsanitized Output",
        description_cn="LLM 输出未经消毒直接渲染或执行",
        description_en="LLM output rendered or executed without sanitization",
        keywords=("xss", "unsanitized", "output validation", "script injection",
                  "sql injection", "html injection"),
    ),

    # ======= AGT: Agent Architecture =======
    CHTCode(
        code="CHT-AGT-001",
        category="AGT",
        name_cn="Agent 死循环",
        name_en="Agent Infinite Loop",
        description_cn="Agent 在工具调用或推理中陷入无限循环",
        description_en="Agent stuck in infinite loop during tool calling or reasoning",
        keywords=("infinite loop", "stuck", "max iterations", "recursion",
                  "loop detected", "never terminates", "keeps calling"),
    ),
    CHTCode(
        code="CHT-AGT-002",
        category="AGT",
        name_cn="工具调用失败",
        name_en="Tool Invocation Failure",
        description_cn="Agent 无法正确调用或解析工具结果",
        description_en="Agent fails to correctly invoke tools or parse tool results",
        keywords=("tool call", "function call", "tool error", "tool not found",
                  "invalid tool", "tool execution", "action input"),
    ),
    CHTCode(
        code="CHT-AGT-003",
        category="AGT",
        name_cn="多 Agent 通信异常",
        name_en="Multi-Agent Communication Error",
        description_cn="多 Agent 系统中的消息传递和协调失败",
        description_en="Message passing and coordination failure in multi-agent systems",
        keywords=("multi-agent", "agent communication", "message passing",
                  "coordination", "crew", "swarm", "handoff"),
    ),

    # ======= DAT: Data and Pipeline =======
    CHTCode(
        code="CHT-DAT-001",
        category="DAT",
        name_cn="数据格式/编码错误",
        name_en="Data Format or Encoding Error",
        description_cn="数据文件格式不正确或编码不匹配",
        description_en="Incorrect data file format or encoding mismatch",
        keywords=("encoding", "utf-8", "gbk", "unicode", "decode error",
                  "encode error", "data format", "corrupted"),
    ),
    CHTCode(
        code="CHT-DAT-002",
        category="DAT",
        name_cn="向量化/嵌入失败",
        name_en="Embedding or Vectorization Failure",
        description_cn="文本向量化或嵌入模型调用失败",
        description_en="Text vectorization or embedding model call failure",
        keywords=("embedding", "vectorize", "vector", "dimension mismatch",
                  "embedding model", "chunk", "tokenize"),
    ),
    CHTCode(
        code="CHT-DAT-003",
        category="DAT",
        name_cn="RAG 检索质量差",
        name_en="Poor RAG Retrieval Quality",
        description_cn="检索增强生成中检索结果不相关或质量低",
        description_en="Irrelevant or low-quality retrieval results in RAG pipeline",
        keywords=("rag", "retrieval", "relevance", "search quality",
                  "wrong results", "not relevant", "retrieval augmented"),
    ),

    # ======= OPS: Operations and Infrastructure =======
    CHTCode(
        code="CHT-OPS-001",
        category="OPS",
        name_cn="Docker/容器启动失败",
        name_en="Docker or Container Startup Failure",
        description_cn="Docker 容器构建或启动过程中失败",
        description_en="Failure during Docker container build or startup",
        keywords=("docker", "container", "dockerfile", "docker-compose",
                  "build failed", "image", "port mapping"),
    ),
    CHTCode(
        code="CHT-OPS-002",
        category="OPS",
        name_cn="模型部署/推理失败",
        name_en="Model Deployment or Inference Failure",
        description_cn="模型加载、部署或推理过程中出错",
        description_en="Error during model loading, deployment, or inference",
        keywords=("model load", "deployment", "inference", "serve", "checkpoint",
                  "weights", "onnx", "tensorrt", "triton"),
    ),
    CHTCode(
        code="CHT-OPS-003",
        category="OPS",
        name_cn="CUDA/GPU 异常",
        name_en="CUDA or GPU Error",
        description_cn="GPU 驱动、CUDA 版本或显存相关错误",
        description_en="GPU driver, CUDA version, or GPU memory related errors",
        keywords=("cuda", "gpu", "nvidia", "cudnn", "gpu driver",
                  "device", "nccl", "distributed"),
    ),

    # ======= UNK: Unknown / Other =======
    CHTCode(
        code="CHT-UNK-000",
        category="UNK",
        name_cn="未分类问题",
        name_en="Unclassified Issue",
        description_cn="无法归入已知类别的问题",
        description_en="Issue that cannot be classified into known categories",
        keywords=(),
    ),
]

# ============================================================
# Lookup tables
# ============================================================

# code string -> CHTCode
CODE_MAP: dict[str, CHTCode] = {c.code: c for c in _CODES}

# category string -> list of CHTCodes
CATEGORY_MAP: dict[str, list[CHTCode]] = {}
for _c in _CODES:
    CATEGORY_MAP.setdefault(_c.category, []).append(_c)

CATEGORY_NAMES = {
    "CFG": ("配置错误", "Configuration Error"),
    "DEP": ("依赖冲突", "Dependency Conflict"),
    "MEM": ("内存与资源", "Memory & Resource"),
    "NET": ("网络与通信", "Network & Communication"),
    "PRM": ("Prompt 工程", "Prompt Engineering"),
    "SEC": ("安全漏洞", "Security Vulnerability"),
    "AGT": ("Agent 架构", "Agent Architecture"),
    "DAT": ("数据与管线", "Data & Pipeline"),
    "OPS": ("运维与基建", "Operations & Infrastructure"),
    "UNK": ("未分类", "Unclassified"),
}


# ============================================================
# Auto-classification
# ============================================================


def classify_root_cause(text: str) -> CHTCode:
    """
    Classify a text (error message, symptom, or root cause description)
    into the best-matching CHT root cause code via keyword matching.

    Args:
        text: The text to classify (case-insensitive)

    Returns:
        Best matching CHTCode (defaults to CHT-UNK-000)
    """
    text_lower = text.lower()
    best_code = CODE_MAP["CHT-UNK-000"]
    best_score = 0

    for c in _CODES:
        if c.code == "CHT-UNK-000":
            continue
        score = sum(1 for kw in c.keywords if kw.lower() in text_lower)
        if score > best_score:
            best_score = score
            best_code = c

    return best_code


def classify_multi(text: str, top_k: int = 3) -> list[tuple[CHTCode, int]]:
    """
    Return the top-k matching CHT codes with their match scores.

    Args:
        text: The text to classify
        top_k: Number of top results to return

    Returns:
        List of (CHTCode, score) tuples, sorted by score descending
    """
    text_lower = text.lower()
    scored = []
    for c in _CODES:
        if c.code == "CHT-UNK-000":
            continue
        score = sum(1 for kw in c.keywords if kw.lower() in text_lower)
        if score > 0:
            scored.append((c, score))

    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]


def format_cht_code(code: CHTCode) -> str:
    """Format a CHT code for display (bilingual)."""
    return f"`{code.code}` {code.name_cn} / {code.name_en}"


def get_taxonomy_table() -> str:
    """Generate the full taxonomy table in Markdown format."""
    lines = [
        "# CHT Root Cause Taxonomy",
        "",
        "| Code | Category | CN | EN |",
        "|:-----|:---------|:---|:---|",
    ]
    for c in _CODES:
        if c.code == "CHT-UNK-000":
            continue
        cat_cn, cat_en = CATEGORY_NAMES.get(c.category, ("", ""))
        lines.append(f"| `{c.code}` | {cat_cn} | {c.name_cn} | {c.name_en} |")
    return "\n".join(lines)


# ============================================================
# Trend Analysis — CHT 编码趋势分析
# ============================================================

import json
import time
from pathlib import Path


def _collect_cht_data_from_cases() -> list[dict]:
    """
    Collect CHT code data from knowledge base cases.
    Each entry: {code, category, framework, timestamp}
    """
    from .indexer import scan_cases

    entries = []
    cases = scan_cases()

    for case in cases:
        meta = case.get("metadata", {})
        content = case.get("content", "")
        framework = meta.get("framework", "unknown")

        # Get file modification time as proxy for creation date
        filepath = case.get("filepath", "")
        ts = ""
        if filepath:
            try:
                mtime = Path(filepath).stat().st_mtime
                ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime))
            except (OSError, FileNotFoundError):
                pass

        # Classify the case content
        text = f"{meta.get('title', '')} {meta.get('symptom', '')} {meta.get('error_message', '')} {meta.get('root_cause', '')} {content[:500]}"
        cht = classify_root_cause(text)

        entries.append({
            "code": cht.code,
            "category": cht.category,
            "framework": framework,
            "timestamp": ts or meta.get("created_at", ""),
        })

    return entries


def _collect_cht_data_from_records() -> list[dict]:
    """
    Collect CHT code data from all user diagnosis records.
    Each entry: {code, category, framework, timestamp}
    """
    from .config import config

    user_data_dir = Path(config.ROOT_DIR) / ".user_data"
    entries = []

    if not user_data_dir.exists():
        return entries

    for user_dir in user_data_dir.iterdir():
        if not user_dir.is_dir() or user_dir.name.startswith("_"):
            continue
        profile_path = user_dir / "profile.json"
        if not profile_path.exists():
            continue
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            for rec in profile.get("records", []):
                code = rec.get("cht_code", "")
                if not code:
                    continue
                cat = code.split("-")[1] if len(code.split("-")) >= 2 else "UNK"
                entries.append({
                    "code": code,
                    "category": cat,
                    "framework": rec.get("framework", "unknown"),
                    "timestamp": rec.get("timestamp", ""),
                })
        except Exception:
            continue

    return entries


def analyze_trends(
    framework: str | None = None,
    category: str | None = None,
) -> str:
    """
    Analyze CHT code trends across knowledge base and diagnosis records.

    Returns Markdown report with:
      1. Category distribution heatmap
      2. Top codes by frequency
      3. Framework × Category cross-tabulation
      4. 7-day vs 30-day trend comparison
    """
    # Collect from both sources
    case_entries = _collect_cht_data_from_cases()
    record_entries = _collect_cht_data_from_records()
    all_entries = case_entries + record_entries

    # Apply filters
    if framework:
        all_entries = [e for e in all_entries if e["framework"].lower() == framework.lower()]
    if category:
        all_entries = [e for e in all_entries if e["category"].upper() == category.upper()]

    if not all_entries:
        msg = "No CHT code data available"
        if framework:
            msg += f" for framework `{framework}`"
        if category:
            msg += f" in category `{category}`"
        return f"# CHT Trend Analysis\n\n{msg}."

    total = len(all_entries)

    # ── 1. Category Distribution ──
    cat_counts: dict[str, int] = {}
    for e in all_entries:
        cat = e["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    sorted_cats = sorted(cat_counts.items(), key=lambda x: -x[1])

    # ── 2. Code Frequency ──
    code_counts: dict[str, int] = {}
    for e in all_entries:
        code = e["code"]
        code_counts[code] = code_counts.get(code, 0) + 1
    sorted_codes = sorted(code_counts.items(), key=lambda x: -x[1])

    # ── 3. Framework × Category ──
    fw_cat: dict[str, dict[str, int]] = {}
    for e in all_entries:
        fw = e["framework"]
        cat = e["category"]
        if fw not in fw_cat:
            fw_cat[fw] = {}
        fw_cat[fw][cat] = fw_cat[fw].get(cat, 0) + 1

    # ── 4. Time-based Trends ──
    now = time.time()
    seven_days = 7 * 24 * 3600
    thirty_days = 30 * 24 * 3600

    recent_7d: dict[str, int] = {}
    recent_30d: dict[str, int] = {}

    for e in all_entries:
        ts_str = e.get("timestamp", "")
        if not ts_str:
            continue
        try:
            import datetime
            ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            age = now - ts.timestamp()
            cat = e["category"]
            if age <= seven_days:
                recent_7d[cat] = recent_7d.get(cat, 0) + 1
            if age <= thirty_days:
                recent_30d[cat] = recent_30d.get(cat, 0) + 1
        except (ValueError, OSError):
            continue

    # ── Build Report ──
    parts = [
        "# CHT Trend Analysis",
        "# CHT 编码趋势分析\n",
    ]
    if framework:
        parts.append(f"**Framework Filter**: `{framework}`")
    if category:
        parts.append(f"**Category Filter**: `{category}`")
    parts.append(f"**Total Data Points**: {total} (Cases: {len(case_entries)}, Records: {len(record_entries)})\n")

    # Section 1: Category Heatmap
    parts.append("## Category Distribution\n")
    parts.append("| Category | CN | Count | % | Heatmap |")
    parts.append("|:---------|:---|------:|--:|:--------|")

    max_count = sorted_cats[0][1] if sorted_cats else 1
    for cat, count in sorted_cats:
        cat_names = CATEGORY_NAMES.get(cat, ("?", "?"))
        pct = round(count / total * 100, 1)
        bar_len = max(1, round(count / max_count * 20))
        bar = "\U0001f7e5" * bar_len
        parts.append(f"| `{cat}` | {cat_names[0]} | {count} | {pct}% | {bar} |")
    parts.append("")

    # Section 2: Top Codes
    parts.append("## Top Root Causes\n")
    parts.append("| Rank | Code | Name | Count |")
    parts.append("|:----:|:-----|:-----|------:|")
    for i, (code, count) in enumerate(sorted_codes[:15], 1):
        cht = CODE_MAP.get(code)
        name = f"{cht.name_cn}" if cht else code
        parts.append(f"| {i} | `{code}` | {name} | {count} |")
    parts.append("")

    # Section 3: Framework × Category Cross-tab
    if len(fw_cat) > 1:
        parts.append("## Framework × Category\n")
        all_cats_sorted = [c for c, _ in sorted_cats]
        header = "| Framework | " + " | ".join(all_cats_sorted) + " | Total |"
        sep = "|:----------|" + "|".join([":---:" for _ in all_cats_sorted]) + "|------:|"
        parts.append(header)
        parts.append(sep)

        sorted_fws = sorted(fw_cat.items(), key=lambda x: -sum(x[1].values()))
        for fw, cats in sorted_fws[:10]:
            cols = [str(cats.get(c, "")) for c in all_cats_sorted]
            fw_total = sum(cats.values())
            parts.append(f"| `{fw}` | " + " | ".join(cols) + f" | {fw_total} |")
        parts.append("")

    # Section 4: Trends
    if recent_7d or recent_30d:
        parts.append("## Trend Analysis (7d vs 30d)\n")
        parts.append("| Category | Last 7d | Last 30d | Trend |")
        parts.append("|:---------|--------:|---------:|:------|")

        all_trend_cats = set(list(recent_7d.keys()) + list(recent_30d.keys()))
        for cat in sorted(all_trend_cats):
            count_7d = recent_7d.get(cat, 0)
            count_30d = recent_30d.get(cat, 0)

            # Calculate trend
            if count_30d > 0:
                daily_7d = count_7d / 7
                daily_30d = count_30d / 30
                if daily_30d > 0:
                    ratio = daily_7d / daily_30d
                    if ratio > 1.5:
                        trend = "\u2B06\uFE0F Surging"
                    elif ratio > 1.1:
                        trend = "\u2197\uFE0F Rising"
                    elif ratio < 0.5:
                        trend = "\u2B07\uFE0F Declining"
                    elif ratio < 0.9:
                        trend = "\u2198\uFE0F Easing"
                    else:
                        trend = "\u27A1\uFE0F Stable"
                else:
                    trend = "\U0001F195 New"
            elif count_7d > 0:
                trend = "\U0001F195 New"
            else:
                trend = "\u27A1\uFE0F Stable"

            cat_names = CATEGORY_NAMES.get(cat, ("?", "?"))
            parts.append(f"| `{cat}` {cat_names[0]} | {count_7d} | {count_30d} | {trend} |")
        parts.append("")

        # Surge alerts
        surging = []
        for cat in all_trend_cats:
            count_7d = recent_7d.get(cat, 0)
            count_30d = recent_30d.get(cat, 0)
            if count_30d > 0:
                daily_7d = count_7d / 7
                daily_30d = count_30d / 30
                if daily_30d > 0 and daily_7d / daily_30d > 1.5 and count_7d >= 3:
                    cat_names = CATEGORY_NAMES.get(cat, ("?", "?"))
                    surging.append(f"- **{cat}** ({cat_names[0]}): 7d avg {daily_7d:.1f}/day vs 30d avg {daily_30d:.1f}/day")

        if surging:
            parts.append("### \U0001F6A8 Surge Alerts\n")
            parts.extend(surging)
            parts.append("")

    return "\n".join(parts)

