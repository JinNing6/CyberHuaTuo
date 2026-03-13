#!/usr/bin/env python3
"""
自动更新全球 AI 医师排行榜脚本 (自动被 GitHub Action 触发)
扫描 cases/ 目录，将所有贡献者的贡献进行打分、排序，并覆盖更新 README.md 与 README_CN.md。
"""

import re
import sys
from pathlib import Path
import yaml

# ============================================================
# 🎖️ 积分与称号体系配置
# ============================================================

TITLE_TIERS = [
    (20, "👑", "华佗再世", "Hua Tuo Reborn"),
    (10, "🌟", "神医", "Divine Doctor"),
    (5, "👨‍⚕️", "名医", "Renowned Doctor"),
    (3, "⚕️", "主治医师", "Attending Physician"),
    (1, "🏥", "坐堂医师", "Resident Doctor"),
]

def calculate_title(contribution_count: int, lang: str = "en") -> tuple[str, str]:
    for threshold, emoji, title_cn, title_en in TITLE_TIERS:
        if contribution_count >= threshold:
            if lang == "en":
                return emoji, f"{title_cn} {title_en}"
            return emoji, title_cn
    if lang == "en":
        return "🌱", "学徒 Apprentice"
    return "🌱", "学徒"


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
        emoji, title = calculate_title(count, lang=lang)
        
        avatar = f'<a href="https://github.com/{username}"><img src="https://github.com/{username}.png" width="50" height="50" style="border-radius:50%"/></a>'
        name_link = f'[@{username}](https://github.com/{username})'
        title_str = f"{emoji} {title}"
        
        # 对于 JinNing6，保持 Creator & Lead 的描述，其他使用数字贡献
        if username.lower() == "jinning6" and rank == 1:
             contrib_str = "Creator & Lead" if lang == "en" else "创建者 & 主导"
        else:
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
