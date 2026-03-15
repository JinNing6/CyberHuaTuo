#!/usr/bin/env python3
"""
自动更新全球炼丹师排行榜脚本 (自动被 GitHub Action 触发)
扫描 cases/ 目录，将所有贡献者按百分位排名计算炼丹师称号，并覆盖更新 README.md 与 README_CN.md。
"""

import re
import sys
from pathlib import Path

import yaml

# ============================================================
# 🧬 炼丹师称号阶梯（16 级，基于全球排名百分位）
# ============================================================

# (percentile_threshold, emoji, title_cn, title_en)
# percentile = 超越了百分之几的贡献者
TITLE_TIERS = [
    (100.0, "🩺", "华佗再世", "Hua Tuo Reborn"),           # #1 全球第一
    (99.0,  "💎", "丹帝", "Pill Emperor"),                   # Top 1%
    (96.0,  "👑", "丹圣", "Pill Saint"),                     # Top 4%
    (92.0,  "⚡", "半圣", "Half-Saint"),                     # Top 8%
    (85.0,  "💜", "丹王", "Pill King"),                      # Top 15%
    (80.0,  "🏅", "小丹王", "Junior Pill King"),             # Top 20%
    (75.0,  "🌟", "九星炼丹师", "Nine-Star Alchemist"),      # Top 25%
    (70.0,  "🌟", "八星炼丹师", "Eight-Star Alchemist"),     # Top 30%
    (60.0,  "🌟", "七星炼丹师", "Seven-Star Alchemist"),     # Top 40%
    (50.0,  "🌟", "六星炼丹师", "Six-Star Alchemist"),       # Top 50%
    (40.0,  "⭐", "五星炼丹师", "Five-Star Alchemist"),      # Top 60%
    (30.0,  "⭐", "四星炼丹师", "Four-Star Alchemist"),      # Top 70%
    (20.0,  "⭐", "三星炼丹师", "Three-Star Alchemist"),     # Top 80%
    (10.0,  "⭐", "二星炼丹师", "Two-Star Alchemist"),       # Top 90%
    (0.0,   "⭐", "一星炼丹师", "One-Star Alchemist"),       # Top 100%
]

DEFAULT_TITLE = ("🌱", "实习药童", "Intern Apprentice")


def calculate_title(percentile: float, is_rank_one: bool = False, lang: str = "en") -> tuple[str, str]:
    """根据全球排名百分位计算炼丹师称号"""
    if is_rank_one:
        emoji, cn, en = TITLE_TIERS[0][1], TITLE_TIERS[0][2], TITLE_TIERS[0][3]
        return (emoji, f"{cn} {en}") if lang == "en" else (emoji, cn)

    for threshold, emoji, title_cn, title_en in TITLE_TIERS:
        if percentile >= threshold:
            return (emoji, f"{title_cn} {title_en}") if lang == "en" else (emoji, title_cn)

    return (DEFAULT_TITLE[0], f"{DEFAULT_TITLE[1]} {DEFAULT_TITLE[2]}") if lang == "en" else (DEFAULT_TITLE[0], DEFAULT_TITLE[1])


# ============================================================
# 🔍 扫描解析逻辑
# ============================================================

def scan_cases_dir(cases_dir: Path) -> dict[str, int]:
    stats = {}
    if not cases_dir.exists():
        return stats

    for md_file in cases_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
            match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
            if not match:
                continue
            meta = yaml.safe_load(match.group(1))
            if not isinstance(meta, dict):
                continue

            contributors = meta.get("contributors", [])
            if isinstance(contributors, list):
                for c in contributors:
                    gh = ""
                    if isinstance(c, dict):
                        gh = c.get("github", "")
                    elif isinstance(c, str):
                        gh = c
                    if gh:
                        # 不区分大小写
                        gh_lower = gh.lower()
                        # 保留原始大小写的用户名，用于展示
                        # 如果是第一次出现，存为一个带有原始用户名和计数的字典
                        if gh_lower not in stats:
                            stats[gh_lower] = {"username": gh, "count": 1}
                        else:
                            stats[gh_lower]["count"] += 1
        except Exception as e:
            print(f"Warning: Failed to parse {md_file}: {e}")

    return stats


def generate_markdown_table(stats_dict: dict, lang: str = "en") -> str:
    # 按照贡献数降序排列，同分再按照用户名排序
    sorted_stats = sorted(
        stats_dict.values(),
        key=lambda x: (-x["count"], x["username"].lower())
    )

    total = len(sorted_stats)

    if lang == "en":
        lines = [
            "| Rank | Avatar | Name | Title / 称号 | Contributions / 贡献 |",
            "|:----:|:------:|:----:|:------------:|:-------------------:|",
        ]
    else:
        lines = [
            "| 排名 | 头像 | 名称 | 称号 | 贡献 |",
            "|:----:|:----:|:----:|:----:|:----:|",
        ]

    for index, item in enumerate(sorted_stats):
        rank = index + 1
        # 前三名使用奖牌，其余使用数字名次
        if rank == 1:
            rank_str = "🥇"
        elif rank == 2:
            rank_str = "🥈"
        elif rank == 3:
            rank_str = "🥉"
        else:
            rank_str = f"{rank}"

        username = item["username"]
        count = item["count"]

        # 计算百分位（超越了百分之几的人）
        is_rank_one = (rank == 1)
        percentile = (100.0 if is_rank_one else 0.0) if total <= 1 else round((total - rank) / (total - 1) * 100, 1)

        emoji, title = calculate_title(percentile, is_rank_one=is_rank_one, lang=lang)

        avatar = f'<a href="https://github.com/{username}"><img src="https://github.com/{username}.png" width="50" height="50" style="border-radius:50%"/></a>'
        name_link = f'[@{username}](https://github.com/{username})'
        title_str = f"{emoji} {title}"

        contrib_str = str(count)

        lines.append(f"| {rank_str} | {avatar} | {name_link} | {title_str} | {contrib_str} |")

    return "\n".join(lines)


# ============================================================
# 📝 替换 README 逻辑
# ============================================================

def update_readme(file_path: Path, new_table: str):
    if not file_path.exists():
        print(f"Error: {file_path} does not exist.")
        return False

    content = file_path.read_text(encoding="utf-8")

    # 查找替换标志位
    pattern = r"(<!-- LEADERBOARD_START -->\n)(.*?)(\n<!-- LEADERBOARD_END -->)"

    if not re.search(pattern, content, flags=re.DOTALL):
         print(f"Error: Could not find LEADERBOARD flags in {file_path}")
         return False

    new_content = re.sub(
        pattern,
        rf"\g<1>{new_table}\g<3>",
        content,
        flags=re.DOTALL
    )

    file_path.write_text(new_content, encoding="utf-8")
    print(f"✅ Successfully updated leaderboard in {file_path}")
    return True


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    cases_dir = project_root / "cases"

    print("Scanning cases directory...")
    stats = scan_cases_dir(cases_dir)
    print(f"Found {len(stats)} contributors.")

    if not stats:
        print("No cases found, exiting.")
        sys.exit(0)

    print("\nGenerating English markdown table...")
    table_en = generate_markdown_table(stats, lang="en")
    print("\nGenerating Chinese markdown table...")
    table_cn = generate_markdown_table(stats, lang="cn")

    readme_en = project_root / "README.md"
    readme_cn = project_root / "README_CN.md"

    success_en = update_readme(readme_en, table_en)
    success_cn = update_readme(readme_cn, table_cn)

    if not (success_en and success_cn):
        sys.exit(1)
