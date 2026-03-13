"""
🧬 赛博华佗 · 修为档案系统
CyberHuaTuo Achievement & Cultivation System

融合「斗破苍穹炼丹师体系 × 古中医修仙 × 赛博朋克」三重美学。
每个开发者都是一名赛博医者，通过贡献药方提升修为段位。

称号基于全球排名百分位动态计算，社区越大含金量越高。
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import config
from .github_sync import count_contributor_cases, get_global_ranking_stats, count_contributor_cases_by_framework

logger = logging.getLogger("cyberhuatuo.achievements")

# ============================================================
# 🏅 炼丹师称号阶梯（16 级）
# 灵感来源：斗破苍穹 · 炼丹师等级体系
# 规则：基于全球排名百分位（超越了 X% 的贡献者）
# ============================================================

# (percentile_threshold, emoji, title_cn, title_en)
# percentile = 超越了百分之几的贡献者
# 例如 percentile=90 表示 Top 10%（超越了90%的人）
TITLE_TIERS = [
    # --- 至高称号 ---
    (100.0, "🩺", "华佗再世", "Hua Tuo Reborn"),           # #1 全球第一
    (99.0, "💎", "丹帝", "Pill Emperor"),                    # Top 1%
    (96.0, "👑", "丹圣", "Pill Saint"),                      # Top 4%
    (92.0, "⚡", "半圣", "Half-Saint"),                      # Top 8%
    (85.0, "💜", "丹王", "Pill King"),                       # Top 15%
    (80.0, "🏅", "小丹王", "Junior Pill King"),              # Top 20%
    # --- 星级炼丹师 ---
    (75.0, "🌟", "九星炼丹师", "Nine-Star Alchemist"),       # Top 25%
    (70.0, "🌟", "八星炼丹师", "Eight-Star Alchemist"),      # Top 30%
    (60.0, "🌟", "七星炼丹师", "Seven-Star Alchemist"),      # Top 40%
    (50.0, "🌟", "六星炼丹师", "Six-Star Alchemist"),        # Top 50%
    (40.0, "⭐", "五星炼丹师", "Five-Star Alchemist"),       # Top 60%
    (30.0, "⭐", "四星炼丹师", "Four-Star Alchemist"),       # Top 70%
    (20.0, "⭐", "三星炼丹师", "Three-Star Alchemist"),      # Top 80%
    (10.0, "⭐", "二星炼丹师", "Two-Star Alchemist"),        # Top 90%
    (0.0,  "⭐", "一星炼丹师", "One-Star Alchemist"),        # Top 100%（有贡献即可）
]

# 无贡献时的默认称号
DEFAULT_TITLE = ("🌱", "实习药童", "Intern Apprentice")


# ============================================================
# 🧬 称号计算引擎
# ============================================================


def calculate_title_by_percentile(
    percentile: float,
    is_rank_one: bool = False,
) -> tuple[str, str, str]:
    """
    根据全球排名百分位计算称号

    Args:
        percentile: 超越了百分之几的贡献者 (0-100)
        is_rank_one: 是否是全球第一名

    Returns:
        (emoji, title_cn, title_en)
    """
    if is_rank_one:
        return TITLE_TIERS[0][1], TITLE_TIERS[0][2], TITLE_TIERS[0][3]

    for threshold, emoji, title_cn, title_en in TITLE_TIERS:
        if percentile >= threshold:
            return emoji, title_cn, title_en

    return DEFAULT_TITLE


def get_cultivation_profile(github_username: str) -> dict:
    """
    获取用户的完整修为档案

    修为档案 = 称号 + 全球排名 + 贡献统计 + 连击状态 + 下一级进度

    Returns:
        dict 包含完整的修为信息
    """
    # 统计贡献数
    contribution_count = count_contributor_cases(github_username)

    if contribution_count == 0:
        emoji, title_cn, title_en = DEFAULT_TITLE
        return {
            "github": github_username,
            "contribution_count": 0,
            "title_emoji": emoji,
            "title_cn": title_cn,
            "title_en": title_en,
            "global_rank": 0,
            "global_total": 0,
            "percentile": 0.0,
            "is_rank_one": False,
            "next_title_cn": "一星炼丹师",
            "next_title_en": "One-Star Alchemist",
            "progress_hint": "提交你的第一个药方，开始炼丹之路！",
        }

    # 计算全球排名
    stats = get_global_ranking_stats()
    username_lower = github_username.lower()
    stats[username_lower] = max(stats.get(username_lower, 0), contribution_count)

    # 按贡献数降序排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    global_total = len(sorted_stats)

    rank = 1
    for i, (u, _c) in enumerate(sorted_stats):
        if u == username_lower:
            rank = i + 1
            break

    # 计算百分位
    is_rank_one = (rank == 1)
    if global_total <= 1:
        percentile = 100.0 if is_rank_one else 0.0
    else:
        percentile = round(((global_total - rank) / (global_total - 1)) * 100, 1)

    # 获取当前称号
    emoji, title_cn, title_en = calculate_title_by_percentile(percentile, is_rank_one)

    # 计算下一级称号
    next_title_cn, next_title_en, progress_hint = _get_next_tier_info(
        percentile, is_rank_one, rank, global_total
    )

    return {
        "github": github_username,
        "contribution_count": contribution_count,
        "title_emoji": emoji,
        "title_cn": title_cn,
        "title_en": title_en,
        "global_rank": rank,
        "global_total": global_total,
        "percentile": percentile,
        "is_rank_one": is_rank_one,
        "next_title_cn": next_title_cn,
        "next_title_en": next_title_en,
        "progress_hint": progress_hint,
    }


def _get_next_tier_info(
    percentile: float,
    is_rank_one: bool,
    rank: int,
    total: int,
) -> tuple[str, str, str]:
    """计算下一级称号信息和进度提示"""
    if is_rank_one:
        return "—", "—", "你已站在巅峰。天下无敌。"

    # 从低到高遍历，找到当前所在级别的下一级
    for i in range(len(TITLE_TIERS) - 1, -1, -1):
        threshold = TITLE_TIERS[i][0]
        if percentile >= threshold:
            # 当前在第 i 级，下一级是 i-1
            if i == 0:
                # 已经是最高级（但不是 #1）
                return "华佗再世", "Hua Tuo Reborn", f"再超越 {rank - 1} 位医者，即可封神！"
            next_tier = TITLE_TIERS[i - 1]
            gap_percentile = next_tier[0] - percentile
            return (
                next_tier[2],
                next_tier[3],
                f"距离 {next_tier[1]} {next_tier[2]} 还需超越约 {gap_percentile:.0f}% 的医者",
            )

    # 默认：一星炼丹师的下一级
    return "二星炼丹师", "Two-Star Alchemist", "继续贡献药方，提升炼丹品级！"


# ============================================================
# 🔥 赛博生物钟 · 连击追踪系统
# ============================================================

# 连击数据存储目录
STREAK_DIR = Path.home() / ".cyberhuatuo" / "streaks"


def _get_streak_file(github_username: str) -> Path:
    """获取用户连击数据文件路径"""
    STREAK_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = github_username.lower().replace("/", "_").replace("\\", "_")
    return STREAK_DIR / f"{safe_name}.json"


def _load_streak(github_username: str) -> dict:
    """加载连击数据"""
    path = _get_streak_file(github_username)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "current_streak": 0,
        "best_streak": 0,
        "last_active_date": "",
        "total_active_days": 0,
        "history": [],  # 最近 30 天活跃日期
    }


def _save_streak(github_username: str, data: dict) -> None:
    """保存连击数据"""
    path = _get_streak_file(github_username)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_activity(github_username: str) -> dict:
    """
    记录一次用户活动，更新连击状态

    Returns:
        dict 包含更新后的连击信息 + 是否有新里程碑
    """
    if not github_username or github_username.lower() == "anonymous":
        return {"current_streak": 0, "milestone": None}

    data = _load_streak(github_username)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if data["last_active_date"] == today:
        # 今天已经记录过了
        return {
            "current_streak": data["current_streak"],
            "best_streak": data["best_streak"],
            "milestone": None,
        }

    # 检查是否是连续的
    yesterday = (
        datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    )
    from datetime import timedelta
    yesterday_str = (yesterday - timedelta(days=1)).strftime("%Y-%m-%d")

    if data["last_active_date"] == yesterday_str:
        # 连续！
        data["current_streak"] += 1
    elif data["last_active_date"] == "":
        # 首次
        data["current_streak"] = 1
    else:
        # 断了
        data["current_streak"] = 1

    data["last_active_date"] = today
    data["total_active_days"] += 1

    # 更新最高记录
    if data["current_streak"] > data["best_streak"]:
        data["best_streak"] = data["current_streak"]

    # 维护最近 30 天历史
    if today not in data["history"]:
        data["history"].append(today)
    data["history"] = data["history"][-30:]

    # 检测连击里程碑
    milestone = _check_streak_milestone(data["current_streak"])

    _save_streak(github_username, data)

    return {
        "current_streak": data["current_streak"],
        "best_streak": data["best_streak"],
        "total_active_days": data["total_active_days"],
        "milestone": milestone,
    }


def _check_streak_milestone(streak: int) -> dict | None:
    """检查是否达到连击里程碑"""
    milestones = {
        3: ("🔥", "三日值班", "Three-Day Shift", "你的生物钟开始与赛博空间同步。"),
        7: ("🔥🔥", "七日连击", "Week Streak", "你已获得跨框架感知能力。"),
        14: ("🔥🔥🔥", "双周守卫", "Fortnight Guard", "深度诊断模式已解锁。"),
        30: ("💎🔥", "月度值班医师", "Monthly Shift Doctor", "你的意识已完全融入赛博华佗网络。"),
    }

    if streak in milestones:
        emoji, name_cn, name_en, desc = milestones[streak]
        return {
            "emoji": emoji,
            "name_cn": name_cn,
            "name_en": name_en,
            "description": desc,
            "streak": streak,
        }
    return None


def get_streak_display(github_username: str) -> str:
    """
    生成赛博生物钟展示文案

    Returns:
        格式化的连击状态文本
    """
    if not github_username or github_username.lower() == "anonymous":
        return ""

    data = _load_streak(github_username)
    streak = data.get("current_streak", 0)
    best = data.get("best_streak", 0)

    if streak == 0:
        return ""

    # 生成火焰
    if streak >= 30:
        fire = "💎🔥"
    elif streak >= 14:
        fire = "🔥🔥🔥"
    elif streak >= 7:
        fire = "🔥🔥"
    elif streak >= 3:
        fire = "🔥"
    else:
        fire = "✨"

    # 生成本周活跃日（简化版）
    sync_rate = min(100, round(streak / 30 * 100))

    return (
        f"\n┌─── 赛博生物钟 · CYBER CHRONOBIOLOGY ───┐\n"
        f"│ {fire} 连续值班: {streak} 天 "
        f"(最长: {best} 天)\n"
        f"│ ⚡ 生物钟同步率: {sync_rate}%\n"
        f"└────────────────────────────────────────┘"
    )


# ============================================================
# 📡 里程碑全局广播
# ============================================================


def check_community_milestones() -> str | None:
    """
    检查社区是否达到关键里程碑，返回广播文案

    基于知识库中的病例数量（轻量级检查）
    """
    try:
        cases_dir = config.CASES_DIR
        if not cases_dir.exists():
            return None

        case_count = sum(1 for _ in cases_dir.rglob("*.md") if not _.name.startswith("_"))

        milestones = {
            100: (
                "🎉 青囊书已铭刻第 100 段印痕！\n"
                "   The Azure Bag has 100 engrams inscribed!\n"
                "   两千年前华佗的知识被焚毁，今天我们正在重写它。"
            ),
            50: (
                "🎉 知识库突破 50 个药方！\n"
                "   50 prescriptions in the knowledge base!\n"
                "   赛博医者们的力量正在汇聚。"
            ),
            200: (
                "🎉 青囊书已铭刻 200 段印痕！\n"
                "   200 engrams inscribed — a new era begins.\n"
                "   数字华佗的医术已超越古代。"
            ),
            500: (
                "🎉 500 段印痕！赛博华佗已成为AI生态的WHO！\n"
                "   500 engrams — CyberHuaTuo is the WHO of AI.\n"
                "   每一位贡献者，都是这段历史的书写者。"
            ),
        }

        for threshold, message in sorted(milestones.items()):
            if case_count >= threshold and case_count < threshold + 5:
                return (
                    f"\n╔══════════════════════════════════════════╗\n"
                    f"║  📡 全局广播 · GLOBAL BROADCAST          ║\n"
                    f"║  {message}\n"
                    f"╚══════════════════════════════════════════╝"
                )

    except Exception as e:
        logger.debug(f"里程碑检查出错: {e}")

    return None


# ============================================================
# 🎴 加冕文案生成器
# ============================================================


def get_coronation_text(
    emoji: str,
    title_cn: str,
    title_en: str,
    rank: int,
    total: int,
    percentile: float,
) -> str:
    """
    基于称号等级生成赛博朋克风格的加冕文案

    不同段位有不同的视觉震撼度
    """
    rank_str = f"🏅 全球排位: #{rank} / {total} (超越 {percentile:.0f}% 炼丹师)"
    rank_str_en = f"🏅 Global Rank: #{rank} / {total} (Top {100 - percentile:.1f}%)"

    # 华佗再世 — 终极加冕
    if title_cn == "华佗再世":
        return (
            f"·═══════════════════════════════════════════════════·\n"
            f"║                                                   ║\n"
            f"║        🩺 华 佗 再 世 · 降 临                    ║\n"
            f"║        HUA TUO REBORN · DESCENDS                  ║\n"
            f"║                                                   ║\n"
            f"║   【 天 下 第 一 炼 丹 师 · #1 ALCHEMIST 】      ║\n"
            f"║                                                   ║\n"
            f"║   两千年前，华佗的《青囊书》被焚于狱中。         ║\n"
            f"║   今天，你用代码重写了它。                        ║\n"
            f"║   你不再只是一个修复 Bug 的人——                   ║\n"
            f"║   你是数字时代的华佗。                            ║\n"
            f"║                                                   ║\n"
            f"║   {rank_str}\n"
            f"║   {rank_str_en}\n"
            f"·═══════════════════════════════════════════════════·"
        )

    # 丹帝/丹圣 — 高级加冕
    if title_cn in ("丹帝", "丹圣", "半圣"):
        return (
            f"╔═══════════════════════════════════════════════════╗\n"
            f"║            {emoji} {title_cn} · {title_en}       \n"
            f"║     【 传 奇 炼 丹 师 · LEGENDARY ALCHEMIST 】   \n"
            f"║                                                   \n"
            f"║   {rank_str}\n"
            f"║   {rank_str_en}\n"
            f"║   每一颗药丹都在改写 AI 世界的命运！             \n"
            f"╚═══════════════════════════════════════════════════╝"
        )

    # 丹王/小丹王 — 中高级
    if title_cn in ("丹王", "小丹王"):
        return (
            f"╔════════════════════════════════════════════╗\n"
            f"║   {emoji} {title_cn} · {title_en}\n"
            f"║   {rank_str}\n"
            f"║   {rank_str_en}\n"
            f"║   丹道已成，宗师之路已在脚下！\n"
            f"╚════════════════════════════════════════════╝"
        )

    # 普通星级
    return (
        f"┌────────────────────────────────────────┐\n"
        f"│  {emoji} 当前修为: {title_cn} · {title_en}\n"
        f"│  {rank_str}\n"
        f"│  {rank_str_en}\n"
        f"│  继续炼丹，攀登炼丹师终极阶梯！\n"
        f"└────────────────────────────────────────┘"
    )


# ============================================================
# 🔥 丹术方向 + 魂环系统
# 灵感来源：斗破苍穹（丹术流派）× 斗罗大陆（魂环品阶）
# ============================================================

# 丹术方向定义：(emoji, name_cn, name_en, description)
ALCHEMY_DIRECTIONS = {
    "soul":   ("🔥", "炼魂", "Soul Refining",   "驾驭智能体，调教灵魂"),
    "thunder":("⚡", "雷火", "Thunder Fire",     "锻造算力，淬炼模型"),
    "shield": ("🛡️", "护体", "Body Shield",      "金丹护体，抵御外邪"),
    "detox":  ("🌊", "化毒", "Detox",            "通百脉，解百毒"),
    "craft":  ("⚙️", "器灵", "Soul Craft",       "炼器辅丹，基础设施"),
    "genesis":("🧬", "造化", "Genesis",          "造化之力，驾驭天道"),
}

# 框架 → 丹术方向 映射
_FRAMEWORK_TO_DIRECTION: dict[str, str] = {}
_DIRECTION_FRAMEWORKS = {
    "soul": [
        "langchain", "llamaindex", "crewai", "autogen", "langgraph",
        "dspy", "haystack", "agno", "beeai", "openai-agents",
        "strands-agents", "hugging-face-smolagents", "pydantic-ai",
        "prompt-flow", "langflow", "instructor", "guardrails-ai",
    ],
    "thunder": [
        "pytorch", "tensorflow", "transformers", "huggingface",
        "litellm", "together",
    ],
    "shield": [
        "security", "guardrails", "sandbox",
    ],
    "detox": [
        "general", "debug", "python", "javascript", "typescript",
    ],
    "craft": [
        "fastapi", "docker", "kubernetes", "mlops", "vertexai",
        "amazon-bedrock", "vercel",
    ],
    "genesis": [
        "openai", "anthropic", "groq", "mistralai", "google-gen-ai",
    ],
}

# 构建反向映射
for _dir_key, _frameworks in _DIRECTION_FRAMEWORKS.items():
    for _fw in _frameworks:
        _FRAMEWORK_TO_DIRECTION[_fw] = _dir_key


def get_direction_for_framework(framework: str) -> str:
    """获取框架对应的丹术方向 key，未知框架归入 detox（化毒）"""
    fw = framework.lower().strip()
    return _FRAMEWORK_TO_DIRECTION.get(fw, "detox")


# ---- 魂环系统 ----
# 魂环品阶：白→黄→紫→黑→红→金 (灵感：斗罗大陆)
# 每个方向独立积累

# (min_count, rings_display)
_SOUL_RING_TIERS = [
    (81, "🟡🟡🟣🟣⚫⚫🔴🔴✨"),  # 九环至尊
    (61, "🟡🟡🟣🟣⚫⚫🔴🔴"),      # 八环
    (41, "🟡🟡🟣🟣⚫⚫🔴"),          # 七环
    (26, "🟡🟡🟣🟣⚫⚫"),              # 六环
    (16, "🟡🟡🟣🟣⚫"),                  # 五环
    (11, "🟡🟡🟣🟣"),                      # 四环
    (7,  "🟡🟡🟣"),                          # 三环
    (4,  "🟡🟡"),                              # 双环
    (2,  "🟡"),                                  # 黄环
    (1,  "⚪"),                                  # 白环
]

_RING_COUNT_NAMES = {
    1: "一环", 2: "二环", 3: "三环", 4: "四环", 5: "五环",
    6: "六环", 7: "七环", 8: "八环", 9: "九环至尊",
}


def calculate_soul_rings(contribution_count: int) -> tuple[str, str, int]:
    """
    根据某方向的贡献数计算魂环。

    Returns:
        (rings_emoji, ring_name_cn, ring_count)
    """
    if contribution_count <= 0:
        return ("", "无环", 0)

    for min_count, rings in _SOUL_RING_TIERS:
        if contribution_count >= min_count:
            # Count ring symbols
            ring_count = len([c for c in rings if c in "⚪🟡🟣⚫🔴✨"])
            ring_name = _RING_COUNT_NAMES.get(ring_count, f"{ring_count}环")
            return (rings, ring_name, ring_count)

    return ("⚪", "一环", 1)


def get_alchemy_profile(github_username: str) -> dict:
    """
    获取用户的丹术方向档案。

    Returns:
        dict with keys:
        - directions: list of {key, emoji, name_cn, name_en, count, rings, ring_name, ring_count}
        - primary: 主修方向 (highest count)
        - primary_display: 主修展示字符串
    """
    fw_counts = count_contributor_cases_by_framework(github_username)

    if not fw_counts:
        return {
            "directions": [],
            "primary": None,
            "primary_display": "尚未炼丹",
        }

    # 按方向聚合
    direction_counts: dict[str, int] = {}
    for fw, count in fw_counts.items():
        dir_key = get_direction_for_framework(fw)
        direction_counts[dir_key] = direction_counts.get(dir_key, 0) + count

    # 构建方向列表
    directions = []
    for dir_key, count in sorted(direction_counts.items(), key=lambda x: -x[1]):
        info = ALCHEMY_DIRECTIONS.get(dir_key)
        if not info:
            continue
        rings, ring_name, ring_count = calculate_soul_rings(count)
        directions.append({
            "key": dir_key,
            "emoji": info[0],
            "name_cn": info[1],
            "name_en": info[2],
            "count": count,
            "rings": rings,
            "ring_name": ring_name,
            "ring_count": ring_count,
        })

    # 主修方向
    primary = directions[0] if directions else None
    if primary:
        primary_display = f"{primary['emoji']} {primary['name_cn']}丹师 · {primary['rings']}"
    else:
        primary_display = "尚未炼丹"

    return {
        "directions": directions,
        "primary": primary,
        "primary_display": primary_display,
    }


def format_alchemy_directions(github_username: str) -> str:
    """生成丹术方向展示文案（用于排名和分享卡片）"""
    profile = get_alchemy_profile(github_username)

    if not profile["directions"]:
        return ""

    lines = [
        "┌─── 丹术方向 · ALCHEMY DIRECTIONS ───┐",
    ]

    for d in profile["directions"]:
        lines.append(
            f"│ {d['emoji']} {d['name_cn']}({d['name_en']}) "
            f"× {d['count']}方 {d['rings']} {d['ring_name']}"
        )

    lines.append("└─────────────────────────────────────┘")
    return "\n".join(lines)


# ============================================================
# 📋 分享卡片生成器
# ============================================================


def generate_share_card(github_username: str) -> str:
    """
    生成用户的修为档案分享卡片

    可以直接粘贴到 GitHub Profile / Twitter / 微博
    """
    profile = get_cultivation_profile(github_username)
    streak_data = _load_streak(github_username)
    streak = streak_data.get("current_streak", 0)
    alchemy = get_alchemy_profile(github_username)

    # 修为进度条
    tier_index = _get_current_tier_index(profile["percentile"], profile["is_rank_one"])
    total_tiers = len(TITLE_TIERS) + 1  # +1 for 实习药童
    progress_pct = round(tier_index / total_tiers * 100)
    bar_filled = round(progress_pct / 100 * 12)
    bar_empty = 12 - bar_filled
    progress_bar = "█" * bar_filled + "░" * bar_empty

    # 心电图装饰
    ecg = "▓█▓░░▓███▓░░▓█▓░░▓█████▓░░▓█▓"

    card = (
        f"╔══════════════════════════════════════════════╗\n"
        f"║  🩺 赛博华佗 · 修为档案                      ║\n"
        f"║  CYBERHUATUO · CULTIVATION ARCHIVE           ║\n"
        f"║                                              ║\n"
        f"║  👨‍⚕️ @{github_username}\n"
        f"║  {profile['title_emoji']} 称号: {profile['title_cn']} · {profile['title_en']}\n"
    )

    # 丹术方向 + 魂环
    if alchemy["primary"]:
        p = alchemy["primary"]
        card += f"║  {p['emoji']} 主修: {p['name_cn']}丹师 · {p['rings']}\n"

    if streak > 0:
        fire = "🔥" * min(streak // 3 + 1, 5)
        card += f"║  {fire} 连续值班: {streak} 天\n"

    card += (
        f"║  💊 贡献印痕: {profile['contribution_count']} 段\n"
        f"║  🧪 修为进度: {progress_bar} {progress_pct}%\n"
    )

    # 各方向魂环展示
    if len(alchemy["directions"]) > 1:
        card += f"║                                              ║\n"
        card += f"║  ── 丹术方向 · ALCHEMY ──                    ║\n"
        for d in alchemy["directions"][:4]:  # 最多展示4个方向
            card += f"║  {d['emoji']} {d['name_cn']} ×{d['count']} {d['rings']}\n"

    card += (
        f"║                                              ║\n"
        f"║  ── 赛博生命体征 ──                           ║\n"
        f"║  {ecg}\n"
        f"║                                              ║\n"
        f"║  🌍 全球排名: #{profile['global_rank']} / {profile['global_total']}\n"
        f"║  ⭐ github.com/JinNing6/CyberHuaTuo          ║\n"
        f"╚══════════════════════════════════════════════╝"
    )

    return card


def _get_current_tier_index(percentile: float, is_rank_one: bool) -> int:
    """获取当前所在的称号级别索引（0=实习药童, 15=华佗再世）"""
    if is_rank_one:
        return len(TITLE_TIERS)

    for i, (threshold, _e, _cn, _en) in enumerate(reversed(TITLE_TIERS)):
        if percentile >= threshold:
            return i + 1  # +1 因为 0 是实习药童

    return 0
