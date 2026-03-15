"""
CyberHuaTuo Social Engagement & Growth Engine
Features:
  1. Weekly Digest -- summary of new prescriptions
  2. Prescription Evaluation -- citations, effectiveness, scoring, expiry
  3. Mentorship system -- senior alchemists review junior prescriptions
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from .config import config
from .indexer import scan_cases

logger = logging.getLogger("cyberhuatuo.social")



# ============================================================
# Weekly Digest
# ============================================================


def generate_weekly_digest() -> str:
    """
    Generate a weekly digest of new prescriptions in the knowledge base.
    Summarizes cases by framework and severity.
    """
    cases = scan_cases()
    now = time.time()
    seven_days = 7 * 24 * 3600

    # Filter recent cases (by file modification time as proxy)
    recent_cases = []
    for case in cases:
        filepath = case.get("filepath", "")
        if filepath:
            try:
                mtime = Path(filepath).stat().st_mtime
                if now - mtime <= seven_days:
                    recent_cases.append(case)
            except (OSError, FileNotFoundError):
                pass

    if not recent_cases:
        return (
            "# Weekly Digest\n\n"
            "**Period**: Last 7 days\n\n"
            "No new prescriptions this week.\n\n"
            "> Be the first to contribute! Use `save_prescription` to add a case."
        )

    # Aggregate stats
    fw_counts: dict[str, int] = {}
    sev_counts: dict[str, int] = {}
    titles: list[str] = []

    for case in recent_cases:
        meta = case.get("metadata", {})
        fw = meta.get("framework", "unknown")
        sev = meta.get("severity", "medium")
        title = meta.get("title", case.get("id", "Untitled"))
        fw_counts[fw] = fw_counts.get(fw, 0) + 1
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
        titles.append(f"- [{fw}] {title}")

    parts = [
        "# Weekly Digest\n",
        f"**Period**: Last 7 days\n"
        f"**New Prescriptions**: {len(recent_cases)}\n",
        "## By Framework\n",
    ]

    for fw, count in sorted(fw_counts.items(), key=lambda x: -x[1]):
        parts.append(f"- **{fw}**: {count} new")
    parts.append("")

    if sev_counts:
        parts.append("## By Severity\n")
        for sev in ["critical", "high", "medium", "low"]:
            if sev in sev_counts:
                parts.append(f"- **{sev}**: {sev_counts[sev]}")
        parts.append("")

    parts.append("## New Prescriptions\n")
    for title in titles[:20]:
        parts.append(title)

    parts.append(
        "\n---\n"
        "\n> Subscribe to frameworks to get personalized digests.\n"
        "> Use `subscribe_framework(action='subscribe', framework='langchain')` to start."
    )

    return "\n".join(parts)


# ============================================================
# Prescription Evaluation — 统一药方评价系统
# (Citations + Effectiveness + Score + Expiry)
# ============================================================

_EVAL_DIR = Path(config.ROOT_DIR) / ".user_data"


def _load_eval_data() -> dict:
    """Load unified prescription evaluation data."""
    path = _EVAL_DIR / "_prescription_eval.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"prescriptions": {}, "user_citation_totals": {}}


def _save_eval_data(data: dict) -> None:
    """Save evaluation data to disk."""
    _EVAL_DIR.mkdir(parents=True, exist_ok=True)
    path = _EVAL_DIR / "_prescription_eval.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _ensure_prescription_entry(data: dict, prescription_id: str) -> dict:
    """Ensure a prescription entry exists and return it."""
    if prescription_id not in data["prescriptions"]:
        data["prescriptions"][prescription_id] = {
            "contributor": "",
            "framework": "",
            "framework_version": "",
            "citations": [],
            "citation_count": 0,
            "feedbacks": [],
            "resolved_count": 0,
            "unresolved_count": 0,
            "cure_rate": 0.0,
            "overall_score": 0.0,
            "expired": False,
            "expire_note": "",
        }
    return data["prescriptions"][prescription_id]


# ---- Citation ----

def cite_prescription(
    prescription_id: str,
    cited_by: str,
    context: str = "",
) -> dict:
    """Record a citation for a prescription."""
    data = _load_eval_data()
    entry = _ensure_prescription_entry(data, prescription_id)

    existing_users = [c["by"] for c in entry["citations"]]
    if cited_by in existing_users:
        return {"status": "already_cited", "count": entry["citation_count"]}

    entry["citation_count"] += 1
    entry["citations"].append({
        "by": cited_by,
        "context": context[:200],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    contributor = entry.get("contributor", "")
    if contributor:
        data["user_citation_totals"][contributor] = (
            data["user_citation_totals"].get(contributor, 0) + 1
        )

    _recalculate_score(entry)
    _save_eval_data(data)
    return {"status": "cited", "count": entry["citation_count"]}


def register_prescription_contributor(
    prescription_id: str,
    contributor: str,
    framework: str = "",
    framework_version: str = "",
) -> None:
    """Register prescription metadata (called during save_prescription)."""
    data = _load_eval_data()
    entry = _ensure_prescription_entry(data, prescription_id)
    entry["contributor"] = contributor
    if framework:
        entry["framework"] = framework
    if framework_version:
        entry["framework_version"] = framework_version
    _save_eval_data(data)


# ---- Effectiveness Feedback ----

def submit_feedback(
    prescription_id: str,
    username: str,
    resolved: bool,
    comment: str = "",
) -> dict:
    """
    Submit effectiveness feedback for a prescription.
    resolved=True means it fixed the user's problem.
    """
    data = _load_eval_data()
    entry = _ensure_prescription_entry(data, prescription_id)

    # Prevent duplicate feedback
    existing = [f["by"] for f in entry["feedbacks"]]
    if username in existing:
        return {"status": "already_submitted"}

    entry["feedbacks"].append({
        "by": username,
        "resolved": resolved,
        "comment": comment[:300],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    if resolved:
        entry["resolved_count"] += 1
    else:
        entry["unresolved_count"] += 1

    total_fb = entry["resolved_count"] + entry["unresolved_count"]
    entry["cure_rate"] = round(entry["resolved_count"] / total_fb * 100, 1) if total_fb > 0 else 0.0

    _recalculate_score(entry)
    _save_eval_data(data)

    return {
        "status": "feedback_submitted",
        "resolved": resolved,
        "cure_rate": entry["cure_rate"],
        "overall_score": entry["overall_score"],
    }


# ---- Version Expiry ----

def mark_expired(
    prescription_id: str,
    reason: str = "Framework major version upgrade",
) -> dict:
    """Mark a prescription as expired (needs re-verification)."""
    data = _load_eval_data()
    entry = _ensure_prescription_entry(data, prescription_id)
    entry["expired"] = True
    entry["expire_note"] = reason
    _recalculate_score(entry)
    _save_eval_data(data)
    return {"status": "marked_expired", "prescription_id": prescription_id}


def mark_verified(prescription_id: str) -> dict:
    """Re-verify an expired prescription (confirmed still valid)."""
    data = _load_eval_data()
    entry = _ensure_prescription_entry(data, prescription_id)
    entry["expired"] = False
    entry["expire_note"] = ""
    _recalculate_score(entry)
    _save_eval_data(data)
    return {"status": "re_verified", "prescription_id": prescription_id}


# ---- Score Calculation ----

def _recalculate_score(entry: dict) -> None:
    """
    Calculate overall prescription score (0-100).
    Weighted formula:
      - Cure Rate (40%): resolved / total feedbacks
      - Citations (30%): log-scaled citation count
      - Feedback Count (20%): more feedback = more trusted
      - Freshness (10%): expired = penalty
    """
    import math

    # Cure Rate component (40 pts)
    cure_rate = entry.get("cure_rate", 0)
    cure_score = cure_rate / 100 * 40

    # Citation component (30 pts, logarithmic)
    citations = entry.get("citation_count", 0)
    cite_score = min(30, math.log2(citations + 1) * 10) if citations > 0 else 0

    # Feedback volume (20 pts)
    total_fb = entry.get("resolved_count", 0) + entry.get("unresolved_count", 0)
    if total_fb >= 10:
        fb_score = 20
    elif total_fb >= 5:
        fb_score = 15
    elif total_fb >= 2:
        fb_score = 10
    elif total_fb >= 1:
        fb_score = 5
    else:
        fb_score = 0

    # Freshness (10 pts)
    fresh_score = 0 if entry.get("expired") else 10

    entry["overall_score"] = round(cure_score + cite_score + fb_score + fresh_score, 1)


# ---- Report Generation ----

def get_prescription_eval(prescription_id: str | None = None) -> str:
    """Get evaluation report for one prescription or global leaderboard."""
    data = _load_eval_data()

    if prescription_id:
        entry = data["prescriptions"].get(prescription_id)
        if not entry:
            return f"No evaluation data for `{prescription_id}`."

        total_fb = entry["resolved_count"] + entry["unresolved_count"]
        expired_tag = " **[EXPIRED]**" if entry.get("expired") else ""

        parts = [
            f"# Prescription Evaluation: `{prescription_id}`{expired_tag}\n",
            f"**Contributor**: @{entry.get('contributor', 'unknown')}",
            f"**Framework**: {entry.get('framework', '?')} {entry.get('framework_version', '')}",
            f"**Overall Score**: **{entry['overall_score']}/100**\n",
            "## Metrics\n",
            "| Metric | Value |",
            "|:-------|:------|",
            f"| Citations | {entry['citation_count']} |",
            f"| Feedbacks | {total_fb} (Resolved: {entry['resolved_count']}, Unresolved: {entry['unresolved_count']}) |",
            f"| Cure Rate | {entry['cure_rate']}% |",
            f"| Status | {'Expired' if entry.get('expired') else 'Active'} |",
            "",
        ]

        if entry.get("expired") and entry.get("expire_note"):
            parts.append(f"> **Expire Reason**: {entry['expire_note']}\n")

        # Recent feedbacks
        feedbacks = entry.get("feedbacks", [])[-5:]
        if feedbacks:
            parts.append("## Recent Feedbacks\n")
            for fb in reversed(feedbacks):
                emoji = "\u2705" if fb["resolved"] else "\u274C"
                parts.append(f"- {emoji} @{fb['by']} ({fb['timestamp'][:10]})")
                if fb.get("comment"):
                    parts.append(f"  > {fb['comment'][:100]}")

        return "\n".join(parts)

    # Global leaderboard
    prescriptions = data.get("prescriptions", {})
    scored = [(pid, e) for pid, e in prescriptions.items() if e.get("overall_score", 0) > 0]
    scored.sort(key=lambda x: -x[1]["overall_score"])

    parts = [
        "# Prescription Quality Leaderboard\n",
        "| Rank | Prescription | Score | Cure Rate | Citations | Status |",
        "|:----:|:-------------|------:|----------:|----------:|:------:|",
    ]

    medals = ["\U0001F947", "\U0001F948", "\U0001F949"]
    for i, (pid, e) in enumerate(scored[:20], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        status = "\U0001F534 Expired" if e.get("expired") else "\U0001F7E2 Active"
        parts.append(
            f"| {medal} | `{pid[:35]}` | {e['overall_score']} | {e['cure_rate']}% | {e['citation_count']} | {status} |"
        )

    if not scored:
        parts.append("| — | No prescriptions evaluated yet | — | — | — | — |")

    # Contributor ranking by citations
    user_totals = data.get("user_citation_totals", {})
    if user_totals:
        sorted_users = sorted(user_totals.items(), key=lambda x: -x[1])
        parts.append("\n## Top Contributors by Citations\n")
        for i, (user, count) in enumerate(sorted_users[:10], 1):
            parts.append(f"{i}. @{user} — {count} citations")

    return "\n".join(parts)


def get_citation_stats(prescription_id: str | None = None) -> str:
    """Backward-compatible alias for get_prescription_eval."""
    return get_prescription_eval(prescription_id)


# ============================================================
# Mentorship System — 师徒系统
# ============================================================

_REVIEW_DIR = Path(config.ROOT_DIR) / ".user_data"


def _load_reviews() -> dict:
    """Load review data from disk."""
    path = _REVIEW_DIR / "_reviews.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"reviews": [], "mentor_stats": {}}


def _save_reviews(data: dict) -> None:
    """Save review data to disk."""
    _REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    path = _REVIEW_DIR / "_reviews.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def submit_review(
    reviewer: str,
    prescription_id: str,
    verdict: str,
    feedback: str = "",
) -> dict:
    """
    Submit a review of a prescription.

    Args:
        reviewer: GitHub username of the reviewing mentor
        prescription_id: ID of the prescription being reviewed
        verdict: approved / needs_revision / rejected
        feedback: Detailed feedback text

    Returns:
        Review result dict
    """
    if verdict not in ("approved", "needs_revision", "rejected"):
        return {"error": "verdict must be: approved, needs_revision, or rejected"}

    data = _load_reviews()

    review_entry = {
        "reviewer": reviewer,
        "prescription_id": prescription_id,
        "verdict": verdict,
        "feedback": feedback[:500],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    data["reviews"].append(review_entry)

    # Update mentor stats
    stats = data["mentor_stats"]
    if reviewer not in stats:
        stats[reviewer] = {"total_reviews": 0, "approved": 0, "needs_revision": 0, "rejected": 0}
    stats[reviewer]["total_reviews"] += 1
    stats[reviewer][verdict] = stats[reviewer].get(verdict, 0) + 1

    _save_reviews(data)

    return {
        "status": "review_submitted",
        "verdict": verdict,
        "reviewer": reviewer,
        "prescription_id": prescription_id,
    }


def get_mentor_profile(username: str) -> str:
    """Get a mentor's review profile."""
    data = _load_reviews()
    stats = data["mentor_stats"].get(username)

    if not stats:
        return (
            f"# Mentor Profile: @{username}\n\n"
            "No reviews yet. Start reviewing prescriptions to build your mentor profile!\n\n"
            "> Use `mentorship(action='review', ...)` to review a prescription."
        )

    total = stats["total_reviews"]
    parts = [
        f"# Mentor Profile: @{username}\n",
        f"**Total Reviews**: {total}",
        f"**Approved**: {stats.get('approved', 0)}",
        f"**Needs Revision**: {stats.get('needs_revision', 0)}",
        f"**Rejected**: {stats.get('rejected', 0)}\n",
    ]

    # Mentor title based on review count
    if total >= 50:
        title = "Grand Master Mentor (大宗师)"
    elif total >= 30:
        title = "Senior Mentor (导师)"
    elif total >= 15:
        title = "Mentor (师父)"
    elif total >= 5:
        title = "Reviewer (点评师)"
    else:
        title = "Apprentice Reviewer (学徒)"

    parts.append(f"**Mentor Title**: {title}\n")

    # Recent reviews
    user_reviews = [r for r in data["reviews"] if r["reviewer"] == username][-5:]
    if user_reviews:
        parts.append("## Recent Reviews\n")
        for r in reversed(user_reviews):
            verdict_emoji = {"approved": "✅", "needs_revision": "🔧", "rejected": "❌"}.get(r["verdict"], "?")
            parts.append(
                f"- {verdict_emoji} `{r['prescription_id']}` — {r['verdict']} ({r['timestamp'][:10]})"
            )
            if r.get("feedback"):
                parts.append(f"  > {r['feedback'][:100]}")

    return "\n".join(parts)


def get_mentor_leaderboard() -> str:
    """Generate the mentor leaderboard."""
    data = _load_reviews()
    stats = data.get("mentor_stats", {})

    if not stats:
        return (
            "# Mentor Leaderboard\n\n"
            "No mentors yet. Be the first!\n\n"
            "> High-level alchemists can review prescriptions from junior contributors.\n"
            "> Use `mentorship(action='review', ...)` to start your mentor journey."
        )

    sorted_mentors = sorted(stats.items(), key=lambda x: -x[1]["total_reviews"])

    parts = [
        "# Mentor Leaderboard\n",
        "| Rank | Mentor | Reviews | Approved | Title |",
        "|:----:|:-------|:-------:|:--------:|:------|",
    ]

    medals = ["🥇", "🥈", "🥉"]
    for i, (user, s) in enumerate(sorted_mentors[:20], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        total = s["total_reviews"]
        if total >= 50:
            title = "Grand Master"
        elif total >= 30:
            title = "Senior Mentor"
        elif total >= 15:
            title = "Mentor"
        elif total >= 5:
            title = "Reviewer"
        else:
            title = "Apprentice"
        parts.append(f"| {medal} | @{user} | {total} | {s.get('approved', 0)} | {title} |")

    return "\n".join(parts)


def get_pending_reviews(framework: str | None = None) -> str:
    """List prescriptions that need review (cases without reviews)."""
    cases = scan_cases()
    data = _load_reviews()
    reviewed_ids = {r["prescription_id"] for r in data["reviews"]}

    pending = []
    for case in cases:
        meta = case.get("metadata", {})
        case_id = case.get("id", "")
        if case_id in reviewed_ids:
            continue
        fw = meta.get("framework", "unknown")
        if framework and fw.lower() != framework.lower():
            continue
        pending.append({
            "id": case_id,
            "framework": fw,
            "title": meta.get("title", case_id),
            "severity": meta.get("severity", "medium"),
            "contributor": meta.get("contributor_github", "anonymous"),
        })

    if not pending:
        msg = "No pending prescriptions to review"
        if framework:
            msg += f" for **{framework}**"
        return f"# Pending Reviews\n\n{msg}."

    parts = [
        f"# Pending Reviews ({len(pending)} prescriptions)\n",
    ]
    if framework:
        parts.append(f"**Filtered by**: {framework}\n")

    parts.append("| Prescription | Framework | Severity | Contributor |")
    parts.append("|:-------------|:---------:|:--------:|:-----------|")
    for p in pending[:20]:
        parts.append(
            f"| `{p['id'][:40]}` | {p['framework']} | {p['severity']} | @{p['contributor']} |"
        )

    parts.append(
        "\n> Use `mentorship(action='review', prescription_id='...', verdict='approved', feedback='...')` to review."
    )
    return "\n".join(parts)

