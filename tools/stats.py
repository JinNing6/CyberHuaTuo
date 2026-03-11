#!/usr/bin/env python3
"""
CyberHuaTuo 疫情统计报告生成器
扫描 cases/ 目录，生成 EPIDEMIC_REPORT.md

用法:
    python tools/stats.py
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

try:
    import yaml
except ImportError:
    print("❌ 请安装 pyyaml: pip install pyyaml")
    sys.exit(1)


ROOT = Path(__file__).parent.parent.resolve()
CASES_DIR = ROOT / "cases"
REPORT_PATH = ROOT / "EPIDEMIC_REPORT.md"


def parse_front_matter(filepath: Path) -> dict | None:
    """解析 YAML front matter"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        return yaml.safe_load(parts[1].strip())
    except yaml.YAMLError:
        return None


def generate_report():
    """生成疫情通报"""
    case_files = sorted(CASES_DIR.rglob("*.md"))
    case_files = [f for f in case_files if f.name != "_index.md"]

    # 统计数据
    frameworks = Counter()
    severities = Counter()
    complexities = Counter()
    tags_counter = Counter()
    contributors = Counter()
    recent_cases = []
    nourishing_count = 0

    for fp in case_files:
        meta = parse_front_matter(fp)
        if not meta:
            continue

        fw = meta.get("framework", "unknown")
        if fw == "_nourishing":
            nourishing_count += 1
        else:
            frameworks[fw] += 1

        severities[meta.get("severity", "unknown")] += 1
        complexities[meta.get("complexity", "unknown")] += 1

        for tag in meta.get("tags", []):
            tags_counter[tag] += 1

        for c in meta.get("contributors", []):
            gh = c.get("github", "unknown")
            contributors[gh] += 1

        recent_cases.append({
            "title": meta.get("title", ""),
            "framework": fw,
            "severity": meta.get("severity", ""),
            "created_at": meta.get("created_at", ""),
            "id": meta.get("id", ""),
        })

    # 按创建日期排序
    recent_cases.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(case_files)
    diagnostic_total = total - nourishing_count

    # 框架健康度评分（病例越多 = 越多人踩坑 = 越需要关注）
    severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 5}

    # 生成报告
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("# 🏥 疫情通报 Epidemic Report")
    lines.append("")
    lines.append(f"> 🕐 最后更新: {now} · 自动生成 by `tools/stats.py`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 生态总览")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 📋 总病例数 | **{total}** |")
    lines.append(f"| 🩺 诊断病例 | **{diagnostic_total}** |")
    lines.append(f"| 🧬 滋补药方 | **{nourishing_count}** |")
    lines.append(f"| 🔧 覆盖框架 | **{len(frameworks)}** |")
    lines.append(f"| 👥 贡献者 | **{len(contributors)}** |")
    lines.append("")

    # 各框架病例统计
    lines.append("## 🔧 各框架病例数")
    lines.append("")
    lines.append("| 框架 | 病例数 | 占比 |")
    lines.append("|------|--------|------|")
    for fw, count in frameworks.most_common():
        pct = f"{count / diagnostic_total * 100:.0f}%" if diagnostic_total > 0 else "0%"
        lines.append(f"| {fw} | {count} | {pct} |")
    lines.append("")

    # 严重程度分布
    lines.append("## ⚠️ 严重程度分布")
    lines.append("")
    sv_order = ["critical", "high", "medium", "low"]
    sv_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for sv in sv_order:
        count = severities.get(sv, 0)
        bar = "█" * count
        lines.append(f"- {sv_emoji.get(sv, '⚪')} **{sv}**: {count} {bar}")
    lines.append("")

    # 复杂度分布
    lines.append("## 🧩 复杂度分布")
    lines.append("")
    cx_order = ["simple", "moderate", "complex", "extreme"]
    for cx in cx_order:
        count = complexities.get(cx, 0)
        bar = "▓" * count
        lines.append(f"- **{cx}**: {count} {bar}")
    lines.append("")

    # 热门标签
    lines.append("## 🏷️ 热门标签 Top 10")
    lines.append("")
    for tag, count in tags_counter.most_common(10):
        lines.append(f"- `{tag}` ({count})")
    lines.append("")

    # 贡献者 Hall of Fame
    lines.append("## 🏆 贡献者 Hall of Fame")
    lines.append("")
    lines.append("| 排名 | 贡献者 | 药方数 |")
    lines.append("|------|--------|--------|")
    for i, (gh, count) in enumerate(contributors.most_common(10), 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
        lines.append(f"| {medal} | [@{gh}](https://github.com/{gh}) | {count} |")
    lines.append("")

    # 最近病例
    lines.append("## 📝 最新收录")
    lines.append("")
    for case in recent_cases[:10]:
        sv = case["severity"]
        sv_badge = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(sv, "⚪")
        fw = case["framework"]
        lines.append(f"- {sv_badge} **[{fw}]** {case['title']} (`{case['id']}`)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报告由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*")

    report = "\n".join(lines)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"✅ 报告已生成: {REPORT_PATH}")
    print(f"   📋 总计 {total} 个病例 · {len(frameworks)} 个框架 · {len(contributors)} 个贡献者")


if __name__ == "__main__":
    generate_report()
