"""
CyberHuaTuo Standard Diagnosis Report Generator
Generates standardized, professional diagnosis reports with:
  - Unique Report ID
  - Structured diagnosis sections (Look/Listen/Diagnose/Prescribe)
  - Root cause CHT code classification
  - Confidence scoring
  - Brand signature
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from .searcher import SearchResult
from .taxonomy import CHTCode, classify_root_cause, format_cht_code


# ============================================================
# Report ID Generation
# ============================================================


def _generate_report_id() -> str:
    """
    Generate a unique diagnosis report ID.
    Format: CHT-DR-{YYYYMMDD}-{short_hash}
    Example: CHT-DR-20260313-a3f7
    """
    ts = time.strftime("%Y%m%d")
    # Use time-based hash for uniqueness
    raw = f"{time.time_ns()}"
    short_hash = hashlib.md5(raw.encode()).hexdigest()[:4]
    return f"CHT-DR-{ts}-{short_hash}"


# ============================================================
# Confidence Scoring
# ============================================================


@dataclass
class ConfidenceScore:
    """Diagnosis confidence assessment."""
    level: str   # HIGH / MEDIUM / LOW
    score: int   # 0-100
    reason: str  # Why this confidence level


def calculate_confidence(results: list[SearchResult]) -> ConfidenceScore:
    """
    Calculate diagnosis confidence based on search result quality.

    Factors:
      - Number of matching cases
      - Top relevance score
      - Source diversity (permanent vs ephemeral)
    """
    if not results:
        return ConfidenceScore(
            level="LOW",
            score=20,
            reason="No matching cases in knowledge base"
        )

    top_relevance = max(r.relevance for r in results)
    case_count = len(results)
    has_permanent = any(r.source == "permanent" for r in results)
    has_ephemeral = any(r.source == "ephemeral" for r in results)

    score = 0

    # Top relevance contributes 0-50 points
    score += min(int(top_relevance * 0.5), 50)

    # Case count contributes 0-25 points
    score += min(case_count * 5, 25)

    # Source diversity contributes 0-15 points
    if has_permanent:
        score += 10
    if has_ephemeral:
        score += 5

    # Relevance threshold bonus
    high_relevance_count = sum(1 for r in results if r.relevance >= 70)
    score += min(high_relevance_count * 3, 10)

    # Determine level
    if score >= 70:
        level = "HIGH"
        reason = f"{high_relevance_count} highly relevant case(s) found (top: {top_relevance:.0f}%)"
    elif score >= 40:
        level = "MEDIUM"
        reason = f"{case_count} related case(s), top relevance {top_relevance:.0f}%"
    else:
        level = "LOW"
        reason = f"Few relevant cases (top relevance: {top_relevance:.0f}%)"

    return ConfidenceScore(level=level, score=min(score, 100), reason=reason)


# ============================================================
# Report Formatting
# ============================================================

# Confidence level display mapping
_CONFIDENCE_DISPLAY = {
    "HIGH": ("HIGH", "precision strike / exact match found"),
    "MEDIUM": ("MEDIUM", "pattern match / related cases available"),
    "LOW": ("LOW", "exploratory / limited reference data"),
}


def format_standard_report(
    query: str,
    results: list[SearchResult],
    diagnosis_text: str | None = None,
    framework: str | None = None,
) -> str:
    """
    Generate a standardized CyberHuaTuo Diagnosis Report.

    Args:
        query: Original user query / error message
        results: Matched search results
        diagnosis_text: Optional LLM-generated diagnosis text
        framework: Detected framework name

    Returns:
        Formatted Markdown diagnosis report
    """
    report_id = _generate_report_id()
    confidence = calculate_confidence(results)

    # Auto-detect framework from results if not provided
    if not framework and results:
        for r in results:
            if r.framework and r.framework != "unknown":
                framework = r.framework
                break

    # Auto-classify root cause from query
    root_cause_code = classify_root_cause(query)

    # Build the report
    parts: list[str] = []

    # ---- Header ----
    parts.append(
        f"# CyberHuaTuo Diagnosis Report\n"
        f"**Report ID**: `{report_id}`\n"
    )

    # ---- Patient Info ----
    framework_display = framework.title() if framework else "Unknown"
    query_preview = query[:200] + ("..." if len(query) > 200 else "")

    parts.append(
        f"**Framework**: {framework_display}\n"
        f"**Complaint**: {query_preview}\n"
    )

    # ---- Diagnosis Sections ----

    # [LOOK] - Identify framework, version, error type
    parts.append("---\n")
    parts.append("## [LOOK] Identification\n")

    error_type = _detect_error_type(query)
    parts.append(
        f"- **Framework**: {framework_display}\n"
        f"- **Error Type**: {error_type}\n"
        f"- **CHT Code**: {format_cht_code(root_cause_code)}\n"
        f"- **Category**: {root_cause_code.category} "
        f"({root_cause_code.name_cn})\n"
    )

    # [LISTEN] - Categorize and assess severity
    parts.append("## [LISTEN] Category Assessment\n")

    top_severity = "UNKNOWN"
    if results:
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        top_result = max(results, key=lambda r: severity_map.get(r.severity, 0))
        top_severity = top_result.severity.upper()

    parts.append(
        f"- **Root Cause Category**: {root_cause_code.name_cn} / {root_cause_code.name_en}\n"
        f"- **Severity**: {top_severity}\n"
        f"- **Matched Cases**: {len(results)}\n"
    )

    # [DIAGNOSE] - Root cause analysis
    parts.append("## [DIAGNOSE] Root Cause Analysis\n")

    if diagnosis_text:
        parts.append(f"{diagnosis_text}\n")
    elif results:
        # Use top result's content as diagnosis basis
        top_result = max(results, key=lambda r: r.relevance)
        parts.append(
            f"Based on **{len(results)}** matched case(s), "
            f"the most relevant case is:\n\n"
            f"**{top_result.title}** (Relevance: {top_result.relevance:.0f}%)\n"
        )
        if top_result.content:
            # Extract a reasonable preview
            content_preview = top_result.content[:1500]
            parts.append(f"\n{content_preview}\n")
    else:
        parts.append(
            "No matching cases found in the knowledge base. "
            "Consider using `fetch_official_docs` for further reference.\n"
        )

    # [PRESCRIBE] - Not included if no LLM diagnosis
    # (The LLM diagnosis text already contains the prescription)

    # ---- Confidence Assessment ----
    parts.append("---\n")
    conf_label, conf_desc = _CONFIDENCE_DISPLAY.get(
        confidence.level, ("UNKNOWN", "")
    )
    parts.append(
        f"## Confidence Assessment\n\n"
        f"- **Confidence**: **{conf_label}** ({confidence.score}/100)\n"
        f"- **Basis**: {confidence.reason}\n"
        f"- **Mode**: {conf_desc}\n"
    )

    # ---- Matched Cases Summary ----
    if results:
        parts.append("## Matched Cases\n")
        parts.append("| # | Case | Framework | Relevance | Severity | Source |")
        parts.append("|:-:|:-----|:---------:|:---------:|:--------:|:------:|")
        for i, r in enumerate(results[:5], 1):
            source_badge = "Permanent" if r.source == "permanent" else "Ephemeral"
            title_short = r.title[:40] + ("..." if len(r.title) > 40 else "")
            parts.append(
                f"| {i} | {title_short} | {r.framework} | "
                f"{r.relevance:.0f}% | {r.severity} | {source_badge} |"
            )
        parts.append("")

    return "\n".join(parts)


def _detect_error_type(query: str) -> str:
    """Detect the general error type from the query text."""
    query_lower = query.lower()

    error_types = [
        ("ImportError", ["importerror", "modulenotfounderror", "no module named"]),
        ("TypeError", ["typeerror", "expected", "got type"]),
        ("ValueError", ["valueerror", "invalid value", "invalid literal"]),
        ("KeyError", ["keyerror", "key not found", "missing key"]),
        ("ConnectionError", ["connectionerror", "timeout", "connection refused"]),
        ("MemoryError", ["memoryerror", "out of memory", "oom", "cuda out of memory"]),
        ("RuntimeError", ["runtimeerror", "runtime error"]),
        ("AttributeError", ["attributeerror", "has no attribute"]),
        ("FileNotFoundError", ["filenotfounderror", "no such file", "file not found"]),
        ("PermissionError", ["permissionerror", "permission denied", "access denied"]),
        ("SyntaxError", ["syntaxerror", "syntax error", "invalid syntax"]),
        ("JSONDecodeError", ["json", "parse error", "decode error"]),
    ]

    for error_name, keywords in error_types:
        if any(kw in query_lower for kw in keywords):
            return error_name

    return "General Error"
