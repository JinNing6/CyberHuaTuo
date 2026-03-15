"""
CyberHuaTuo Personal Medical Record System
Tracks individual user diagnosis history for retention loop:
  diagnose -> record -> follow-up reminder -> return

Storage: Local JSON files under {ROOT_DIR}/.user_data/{username}/
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import config
from .taxonomy import CHTCode

logger = logging.getLogger("cyberhuatuo.medical_record")

# User data directory
_USER_DATA_DIR = Path(config.ROOT_DIR) / ".user_data"


@dataclass
class DiagnosisRecord:
    """A single diagnosis record."""
    record_id: str          # CHT-DR-YYYYMMDD-hash
    timestamp: str          # ISO 8601
    query: str              # Original error/problem description
    framework: str          # Detected framework
    cht_code: str           # Root cause CHT code
    cht_name: str           # Root cause name
    confidence: str         # HIGH / MEDIUM / LOW
    confidence_score: int   # 0-100
    matched_cases: int      # Number of matched cases
    top_relevance: float    # Top case relevance
    resolved: bool = False  # Whether the user marked it resolved
    resolution_note: str = ""  # User's resolution note


@dataclass
class UserMedicalProfile:
    """Aggregated medical profile for a user."""
    username: str
    total_diagnoses: int = 0
    total_resolved: int = 0
    records: list[dict] = field(default_factory=list)
    framework_stats: dict[str, int] = field(default_factory=dict)
    cht_code_stats: dict[str, int] = field(default_factory=dict)
    subscriptions: list[str] = field(default_factory=list)
    last_visit: str = ""


def _get_user_dir(username: str) -> Path:
    """Get or create user data directory."""
    user_dir = _USER_DATA_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _load_profile(username: str) -> UserMedicalProfile:
    """Load user medical profile from disk."""
    user_dir = _get_user_dir(username)
    profile_path = user_dir / "profile.json"
    if profile_path.exists():
        try:
            data = json.loads(profile_path.read_text(encoding="utf-8"))
            return UserMedicalProfile(**data)
        except Exception as e:
            logger.warning(f"Failed to load profile for {username}: {e}")
    return UserMedicalProfile(username=username)


def _save_profile(profile: UserMedicalProfile) -> None:
    """Save user medical profile to disk."""
    user_dir = _get_user_dir(profile.username)
    profile_path = user_dir / "profile.json"
    data = {
        "username": profile.username,
        "total_diagnoses": profile.total_diagnoses,
        "total_resolved": profile.total_resolved,
        "records": profile.records,
        "framework_stats": profile.framework_stats,
        "cht_code_stats": profile.cht_code_stats,
        "subscriptions": profile.subscriptions,
        "last_visit": profile.last_visit,
    }
    profile_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ============================================================
# Core API
# ============================================================


def save_diagnosis_record(
    username: str,
    record_id: str,
    query: str,
    framework: str,
    cht_code: CHTCode,
    confidence_level: str,
    confidence_score: int,
    matched_cases: int,
    top_relevance: float,
) -> DiagnosisRecord:
    """
    Save a new diagnosis record to user's medical history.

    Called automatically after each `diagnose` tool invocation.
    """
    record = DiagnosisRecord(
        record_id=record_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        query=query[:500],  # Truncate long queries
        framework=framework or "unknown",
        cht_code=cht_code.code,
        cht_name=f"{cht_code.name_cn} / {cht_code.name_en}",
        confidence=confidence_level,
        confidence_score=confidence_score,
        matched_cases=matched_cases,
        top_relevance=top_relevance,
    )

    profile = _load_profile(username)
    profile.total_diagnoses += 1
    profile.last_visit = record.timestamp
    profile.records.append(asdict(record))

    # Update stats
    fw = record.framework
    profile.framework_stats[fw] = profile.framework_stats.get(fw, 0) + 1
    code = record.cht_code
    profile.cht_code_stats[code] = profile.cht_code_stats.get(code, 0) + 1

    # Keep only last 100 records in profile (older ones in archive)
    if len(profile.records) > 100:
        _archive_old_records(username, profile.records[:-100])
        profile.records = profile.records[-100:]

    _save_profile(profile)
    return record


def mark_resolved(username: str, record_id: str, note: str = "") -> bool:
    """Mark a diagnosis record as resolved."""
    profile = _load_profile(username)
    for rec in profile.records:
        if rec.get("record_id") == record_id:
            rec["resolved"] = True
            rec["resolution_note"] = note
            profile.total_resolved += 1
            _save_profile(profile)
            return True
    return False


def get_follow_up_candidates(username: str) -> list[dict]:
    """
    Get unresolved diagnosis records for follow-up reminders.
    Returns records from the last 7 days that haven't been resolved.
    """
    profile = _load_profile(username)
    candidates = []
    cutoff = time.time() - 7 * 24 * 3600  # 7 days ago

    for rec in reversed(profile.records):
        if rec.get("resolved"):
            continue
        ts_str = rec.get("timestamp", "")
        try:
            import datetime
            ts = datetime.datetime.fromisoformat(ts_str)
            if ts.timestamp() >= cutoff:
                candidates.append(rec)
        except (ValueError, OSError):
            candidates.append(rec)  # Include if timestamp unparseable

    return candidates[:5]  # Return at most 5


def get_profile_summary(username: str) -> str:
    """Generate a formatted medical profile summary."""
    profile = _load_profile(username)

    if profile.total_diagnoses == 0:
        return (
            f"# Medical Record: @{username}\n\n"
            "No diagnosis records yet.\n"
            "Use `diagnose` to start building your medical history."
        )

    # Resolution rate
    resolution_rate = 0
    if profile.total_diagnoses > 0:
        resolution_rate = (profile.total_resolved / profile.total_diagnoses) * 100

    parts = [
        f"# Medical Record: @{username}\n",
        f"**Total Diagnoses**: {profile.total_diagnoses}",
        f"**Resolved**: {profile.total_resolved} ({resolution_rate:.0f}%)",
        f"**Last Visit**: {profile.last_visit or 'N/A'}\n",
    ]

    # Framework statistics
    if profile.framework_stats:
        parts.append("## Framework Breakdown\n")
        sorted_fw = sorted(profile.framework_stats.items(), key=lambda x: -x[1])
        for fw, count in sorted_fw[:10]:
            bar = "=" * min(count, 20)
            parts.append(f"- **{fw}**: {count} {bar}")
        parts.append("")

    # CHT code statistics
    if profile.cht_code_stats:
        parts.append("## Common Root Causes (CHT Codes)\n")
        sorted_codes = sorted(profile.cht_code_stats.items(), key=lambda x: -x[1])
        for code, count in sorted_codes[:10]:
            from .taxonomy import CODE_MAP
            cht = CODE_MAP.get(code)
            label = f"{cht.name_cn} / {cht.name_en}" if cht else code
            parts.append(f"- `{code}` {label}: **{count}**")
        parts.append("")

    # Follow-up candidates
    followups = get_follow_up_candidates(username)
    if followups:
        parts.append("## Pending Follow-ups\n")
        for rec in followups:
            parts.append(
                f"- `{rec['record_id']}` [{rec['framework']}] "
                f"{rec['query'][:80]}..."
            )
        parts.append(
            "\n> Use `my_medical_record(action='resolve', record_id='...')` "
            "to mark as resolved."
        )

    # Recent records
    recent = profile.records[-5:]
    if recent:
        parts.append("\n## Recent Diagnoses\n")
        parts.append("| Date | Framework | CHT Code | Confidence | Resolved |")
        parts.append("|:-----|:---------:|:--------:|:----------:|:--------:|")
        for rec in reversed(recent):
            date = rec.get("timestamp", "")[:10]
            resolved = "Y" if rec.get("resolved") else "N"
            parts.append(
                f"| {date} | {rec.get('framework', '')} | "
                f"`{rec.get('cht_code', '')}` | "
                f"{rec.get('confidence', '')} | {resolved} |"
            )

    return "\n".join(parts)


def _archive_old_records(username: str, records: list[dict]) -> None:
    """Archive older records to a separate file."""
    user_dir = _get_user_dir(username)
    archive_path = user_dir / "archive.jsonl"
    with open(archive_path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ============================================================
# Subscription Management
# ============================================================


def subscribe_framework_for_user(username: str, framework: str) -> bool:
    """Subscribe a user to a framework for updates."""
    profile = _load_profile(username)
    fw = framework.lower()
    if fw not in profile.subscriptions:
        profile.subscriptions.append(fw)
        _save_profile(profile)
        return True
    return False  # Already subscribed


def unsubscribe_framework_for_user(username: str, framework: str) -> bool:
    """Unsubscribe a user from a framework."""
    profile = _load_profile(username)
    fw = framework.lower()
    if fw in profile.subscriptions:
        profile.subscriptions.remove(fw)
        _save_profile(profile)
        return True
    return False  # Not subscribed


def get_subscriptions(username: str) -> list[str]:
    """Get user's framework subscriptions."""
    profile = _load_profile(username)
    return profile.subscriptions


def check_new_prescriptions(username: str) -> list[dict]:
    """
    Check for new prescriptions in subscribed frameworks since last visit.
    Returns a list of new case summaries.
    """
    profile = _load_profile(username)
    if not profile.subscriptions or not profile.last_visit:
        return []

    from .indexer import scan_cases
    cases = scan_cases()
    new_cases = []

    for case in cases:
        meta = case.get("metadata", {})
        fw = meta.get("framework", "").lower()
        if fw not in profile.subscriptions:
            continue
        # Check if case is newer than last visit
        case_date = meta.get("created_at", meta.get("date", ""))
        if case_date > profile.last_visit:
            new_cases.append({
                "title": meta.get("title", case.get("id", "")),
                "framework": fw,
                "severity": meta.get("severity", "medium"),
                "date": case_date,
            })

    return new_cases[:20]
