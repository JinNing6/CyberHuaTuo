"""
CyberHuaTuo 疫情通报引擎 — Agent 生态健康度监控

实时监控主流 Agent 框架 GitHub Issues，
自动生成多维度"框架健康度报告"。
对标 Cloudflare 年度互联网报告 / npm 年度包统计。
"""

import asyncio
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import config
from .issue_miner import GitHubClient, TARGET_REPOS, TargetRepo


# ===== 数据结构 =====

@dataclass
class CriticalIssue:
    """高危 Issue 摘要"""
    number: int
    title: str
    url: str
    labels: list[str] = field(default_factory=list)
    reactions: int = 0
    created_at: str = ""


@dataclass
class FrameworkHealthData:
    """单框架健康度全景数据"""
    framework: str
    display_name: str
    owner: str
    repo: str
    repo_url: str = ""

    # 基础指标
    open_issues_count: int = 0
    closed_issues_count: int = 0

    # 时域活跃度
    new_issues_7d: int = 0
    new_issues_30d: int = 0
    closed_issues_7d: int = 0
    closed_issues_30d: int = 0

    # 质量指标
    avg_close_time_hours: float = 0.0
    critical_issues: list[CriticalIssue] = field(default_factory=list)
    bug_count: int = 0

    # 社区参与
    top_issues: list[dict] = field(default_factory=list)
    label_distribution: dict[str, int] = field(default_factory=dict)

    # 综合评估
    health_score: float = 0.0
    trend: str = "→ stable"  # ↑ improving / → stable / ↓ declining
    anomalies: list[str] = field(default_factory=list)

    # 元数据
    scanned_at: str = ""
    scan_error: str = ""


@dataclass
class EpidemicReport:
    """疫情通报完整报告"""
    report_date: str
    generated_at: str
    framework_count: int = 0
    frameworks: list[FrameworkHealthData] = field(default_factory=list)

    # 全局统计
    total_open_issues: int = 0
    total_new_issues_7d: int = 0
    total_closed_issues_7d: int = 0
    avg_health_score: float = 0.0

    # 排行榜
    healthiest_frameworks: list[str] = field(default_factory=list)
    most_active_frameworks: list[str] = field(default_factory=list)
    needs_attention: list[str] = field(default_factory=list)

    # 全局告警
    global_anomalies: list[str] = field(default_factory=list)


# ===== 核心监控引擎 =====

class EpidemicMonitor:
    """Agent 生态疫情监控引擎"""

    def __init__(self, github_client: GitHubClient | None = None):
        self.github = github_client or GitHubClient()

    async def scan_repo_health(
        self,
        target: TargetRepo,
    ) -> FrameworkHealthData:
        """
        采集单个仓库多维度健康指标

        通过 GitHub Search API 获取以下数据：
          1. 当前开放 Issues 数
          2. 近 7/30 天新增 Issues
          3. 近 7 天关闭 Issues
          4. bug 标签 Issues
          5. critical/breaking-change Issues
          6. 高反应热门 Issues (reactions > 5)

        Args:
            target: 目标仓库信息

        Returns:
            FrameworkHealthData 包含完整健康数据
        """
        data = FrameworkHealthData(
            framework=target.framework,
            display_name=f"{target.owner}/{target.repo}",
            owner=target.owner,
            repo=target.repo,
            repo_url=f"https://github.com/{target.owner}/{target.repo}",
            scanned_at=datetime.now(timezone.utc).isoformat(),
        )

        now = datetime.now(timezone.utc)
        date_7d = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        date_30d = (now - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            # ── 1. 当前开放 Issues ──
            open_result = await self.github.search_issues(
                owner=target.owner, repo=target.repo,
                state="open", sort="created", per_page=1,
            )
            if open_result and "total_count" in open_result:
                data.open_issues_count = open_result["total_count"]

            # 速率控制间隔
            await asyncio.sleep(2.5)

            # ── 2. 近 7 天新增 Issues ──
            new_7d = await self._search_count(
                target.owner, target.repo,
                extra_qualifiers=[f"created:>{date_7d}"],
                state="",
            )
            data.new_issues_7d = new_7d

            await asyncio.sleep(2.5)

            # ── 3. 近 30 天新增 Issues ──
            new_30d = await self._search_count(
                target.owner, target.repo,
                extra_qualifiers=[f"created:>{date_30d}"],
                state="",
            )
            data.new_issues_30d = new_30d

            await asyncio.sleep(2.5)

            # ── 4. 近 7 天关闭 Issues ──
            closed_7d = await self._search_count(
                target.owner, target.repo,
                extra_qualifiers=[f"closed:>{date_7d}"],
                state="closed",
            )
            data.closed_issues_7d = closed_7d

            await asyncio.sleep(2.5)

            # ── 5. 近 30 天关闭 Issues ──
            closed_30d = await self._search_count(
                target.owner, target.repo,
                extra_qualifiers=[f"closed:>{date_30d}"],
                state="closed",
            )
            data.closed_issues_30d = closed_30d

            await asyncio.sleep(2.5)

            # ── 6. Bug 标签 Issues ──
            bug_result = await self._search_count(
                target.owner, target.repo,
                extra_qualifiers=['label:bug'],
                state="open",
            )
            data.bug_count = bug_result

            await asyncio.sleep(2.5)

            # ── 7. Critical / Breaking Change Issues ──
            critical_result = await self.github.search_issues(
                owner=target.owner, repo=target.repo,
                state="open", sort="reactions-+1", per_page=10,
                labels=["bug"],
            )
            if critical_result and "items" in critical_result:
                for item in critical_result["items"][:5]:
                    if "pull_request" in item:
                        continue
                    reactions = item.get("reactions", {})
                    total_reactions = reactions.get("total_count", 0) if isinstance(reactions, dict) else 0
                    labels_list = [
                        lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
                        for lbl in item.get("labels", [])
                    ]
                    data.critical_issues.append(CriticalIssue(
                        number=item.get("number", 0),
                        title=item.get("title", ""),
                        url=item.get("html_url", ""),
                        labels=labels_list,
                        reactions=total_reactions,
                        created_at=item.get("created_at", ""),
                    ))

            await asyncio.sleep(2.5)

            # ── 8. 热门 Issues (by reactions) ──
            hot_result = await self.github.search_issues(
                owner=target.owner, repo=target.repo,
                state="open", sort="reactions-+1", per_page=5,
                min_reactions=3,
            )
            if hot_result and "items" in hot_result:
                for item in hot_result["items"]:
                    if "pull_request" in item:
                        continue
                    reactions = item.get("reactions", {})
                    data.top_issues.append({
                        "number": item.get("number", 0),
                        "title": item.get("title", ""),
                        "url": item.get("html_url", ""),
                        "reactions": reactions.get("total_count", 0) if isinstance(reactions, dict) else 0,
                        "comments": item.get("comments", 0),
                    })

            # ── 计算健康分数 ──
            data.health_score = self.calculate_health_score(data)
            data.trend = self._calculate_trend(data)
            data.anomalies = self._detect_anomalies(data)

        except Exception as e:
            data.scan_error = str(e)
            print(f"  ⚠️ 扫描 {target.owner}/{target.repo} 出错: {e}")

        return data

    async def _search_count(
        self,
        owner: str,
        repo: str,
        extra_qualifiers: list[str] | None = None,
        state: str = "open",
    ) -> int:
        """通过 Search API 获取匹配数量（仅返回 total_count）"""
        import httpx
        import time

        await self.github._wait_if_limited(is_search=True)

        q_parts = [f"repo:{owner}/{repo}", "is:issue"]
        if state:
            q_parts.append(f"is:{state}")
        if extra_qualifiers:
            q_parts.extend(extra_qualifiers)

        q = " ".join(q_parts)
        params = {"q": q, "per_page": 1}
        url = f"{self.github.BASE_URL}/search/issues"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.github._headers(),
                )
                self.github._update_rate_limits(response, is_search=True)

                if response.status_code == 200:
                    data = response.json()
                    return data.get("total_count", 0)
                elif response.status_code == 403:
                    retry_after = response.headers.get("retry-after")
                    if retry_after:
                        wait = int(retry_after)
                        print(f"  ⏳ Search API 403，等待 {wait}s ...")
                        await asyncio.sleep(wait)
                        return await self._search_count(owner, repo, extra_qualifiers, state)
                    return 0
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", 60))
                    print(f"  ⏳ Search API 429，等待 {retry_after}s ...")
                    await asyncio.sleep(retry_after)
                    return await self._search_count(owner, repo, extra_qualifiers, state)
                else:
                    print(f"  ⚠️ Search API 错误: HTTP {response.status_code}")
                    return 0

        except Exception as e:
            print(f"  ⚠️ Search API 请求失败: {e}")
            return 0

    def calculate_health_score(self, data: FrameworkHealthData) -> float:
        """
        加权计算框架健康分数 (0-100)

        评分维度：
          1. 关闭率 (30 分) — closed_7d / new_7d
          2. Bug 密度 (25 分) — bug_count / open_issues 反向
          3. 活跃度 (20 分) — 近期关闭数量
          4. 稳定性 (15 分) — critical issues 数量反向
          5. 社区参与 (10 分) — 热门 issues 反应度
        """
        score = 0.0

        # 1. 关闭效率 (30 分)
        if data.new_issues_7d > 0:
            close_ratio = min(data.closed_issues_7d / data.new_issues_7d, 2.0)
            score += close_ratio * 15  # 最高 30
        elif data.closed_issues_7d > 0:
            score += 30  # 没新 Issue 但有在关旧的 → 满分
        else:
            score += 15  # 无活动 → 中性

        # 2. Bug 密度 (25 分) — bug 占比越低越好
        if data.open_issues_count > 0:
            bug_ratio = data.bug_count / data.open_issues_count
            bug_score = max(0, 25 * (1 - bug_ratio * 2))
            score += bug_score
        else:
            score += 25

        # 3. 活跃度 (20 分) — 关不关 Issue 都算活跃
        activity = data.closed_issues_7d + data.new_issues_7d
        if activity > 50:
            score += 20
        elif activity > 20:
            score += 15
        elif activity > 5:
            score += 10
        else:
            score += 5

        # 4. 稳定性 (15 分) — critical issues 越少越好
        critical_count = len(data.critical_issues)
        if critical_count == 0:
            score += 15
        elif critical_count <= 2:
            score += 10
        elif critical_count <= 5:
            score += 5
        # > 5 个 critical → 0 分

        # 5. 社区参与 (10 分)
        if data.top_issues:
            avg_reactions = sum(i.get("reactions", 0) for i in data.top_issues) / len(data.top_issues)
            if avg_reactions > 20:
                score += 10
            elif avg_reactions > 10:
                score += 7
            elif avg_reactions > 3:
                score += 5
            else:
                score += 3
        else:
            score += 5

        return round(min(score, 100), 1)

    def _calculate_trend(self, data: FrameworkHealthData) -> str:
        """推算趋势方向"""
        if data.new_issues_30d == 0:
            return "→ stable"

        # 近 7 天 vs 近 30 天的日均
        daily_7d = data.new_issues_7d / 7
        daily_30d = data.new_issues_30d / 30

        if daily_30d == 0:
            return "→ stable"

        ratio = daily_7d / daily_30d

        if ratio > 1.5:
            return "↓ declining"  # 新 Issue 激增 → 可能有问题
        elif ratio < 0.7:
            return "↑ improving"  # 新 Issue 减少 → 趋于稳定
        else:
            return "→ stable"

    def _detect_anomalies(self, data: FrameworkHealthData) -> list[str]:
        """检测异常情况"""
        anomalies = []

        # 新 Issue 激增
        if data.new_issues_7d > 50:
            anomalies.append(f"⚠️ 本周新增 {data.new_issues_7d} 个 Issues，高于常规水平")

        # 关闭率过低
        if data.new_issues_7d > 10 and data.closed_issues_7d < data.new_issues_7d * 0.3:
            anomalies.append(f"⚠️ 关闭率偏低：本周新增 {data.new_issues_7d}，仅关闭 {data.closed_issues_7d}")

        # Critical issues 多
        if len(data.critical_issues) >= 5:
            anomalies.append(f"🔴 存在 {len(data.critical_issues)} 个高影响 Bug Issues")

        # Bug 占比高
        if data.open_issues_count > 0 and data.bug_count / data.open_issues_count > 0.4:
            pct = round(data.bug_count / data.open_issues_count * 100)
            anomalies.append(f"🐛 Bug 类 Issue 占比达 {pct}%")

        return anomalies

    async def scan_all_frameworks(
        self,
        targets: list[TargetRepo] | None = None,
    ) -> EpidemicReport:
        """
        并发扫描所有目标仓库，生成疫情通报报告

        GitHub Search API 限制: 认证用户 30 请求/分钟
        每仓库约 8 次搜索 → 10 仓库需分批串行

        Args:
            targets: 指定仓库列表，默认 TARGET_REPOS 全部

        Returns:
            EpidemicReport 完整报告
        """
        targets = targets or TARGET_REPOS
        now = datetime.now(timezone.utc)

        report = EpidemicReport(
            report_date=now.strftime("%Y-%m-%d"),
            generated_at=now.isoformat(),
            framework_count=len(targets),
        )

        print(f"\n🦠 疫情通报扫描启动（{len(targets)} 个框架）...")
        print(f"  ⏰ {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  📡 GitHub Token: {'✅ 已配置' if self.github.token else '❌ 未配置'}\n")

        # 串行扫描（受 Search API 速率限制）
        for i, target in enumerate(targets, 1):
            print(f"  [{i}/{len(targets)}] 扫描 {target.owner}/{target.repo} ({target.framework}) ...")
            health = await self.scan_repo_health(target)
            report.frameworks.append(health)

            if health.scan_error:
                print(f"    ❌ 扫描出错: {health.scan_error}")
            else:
                emoji = "🟢" if health.health_score >= 70 else "🟡" if health.health_score >= 40 else "🔴"
                print(f"    {emoji} 健康分数: {health.health_score} | 开放 Issues: {health.open_issues_count} | 本周新增: {health.new_issues_7d}")

            # 仓库间多等一会儿，避免触发 secondary rate limit
            if i < len(targets):
                await asyncio.sleep(5)

        # 计算全局统计
        valid = [f for f in report.frameworks if not f.scan_error]

        report.total_open_issues = sum(f.open_issues_count for f in valid)
        report.total_new_issues_7d = sum(f.new_issues_7d for f in valid)
        report.total_closed_issues_7d = sum(f.closed_issues_7d for f in valid)

        if valid:
            report.avg_health_score = round(
                sum(f.health_score for f in valid) / len(valid), 1
            )

        # 排行榜
        sorted_by_health = sorted(valid, key=lambda f: f.health_score, reverse=True)
        report.healthiest_frameworks = [f.framework for f in sorted_by_health[:3]]

        sorted_by_activity = sorted(valid, key=lambda f: f.closed_issues_7d, reverse=True)
        report.most_active_frameworks = [f.framework for f in sorted_by_activity[:3]]

        low_health = [f for f in valid if f.health_score < 50]
        report.needs_attention = [f.framework for f in low_health]

        # 全局异常汇总
        for fw in valid:
            for anomaly in fw.anomalies:
                report.global_anomalies.append(f"[{fw.framework}] {anomaly}")

        print(f"\n✅ 疫情通报扫描完成！平均健康分数: {report.avg_health_score}")

        return report

    async def scan_single_framework(self, framework: str) -> FrameworkHealthData | None:
        """扫描单个框架的健康数据"""
        from .issue_miner import _REPO_BY_FRAMEWORK
        target = _REPO_BY_FRAMEWORK.get(framework)
        if not target:
            return None
        return await self.scan_repo_health(target)


# ===== 报告生成器 =====

def generate_markdown_report(report: EpidemicReport) -> str:
    """生成 Markdown 格式的疫情通报"""
    lines = [
        f"# 🦠 Agent 生态疫情通报",
        f"# Agent Ecosystem Epidemic Report",
        f"",
        f"> **报告日期**: {report.report_date}",
        f"> **生成时间**: {report.generated_at}",
        f"> **监控框架**: {report.framework_count} 个主流 Agent 框架",
        f"",
        f"---",
        f"",
        f"## 📊 全局概览 / Global Overview",
        f"",
        f"| 指标 Metric | 数值 Value |",
        f"|:---|:---|",
        f"| 📈 监控框架数 Frameworks | **{report.framework_count}** |",
        f"| 🔓 总开放 Issues Total Open | **{report.total_open_issues:,}** |",
        f"| 📥 本周新增 New (7d) | **{report.total_new_issues_7d:,}** |",
        f"| ✅ 本周关闭 Closed (7d) | **{report.total_closed_issues_7d:,}** |",
        f"| 💚 平均健康分 Avg Score | **{report.avg_health_score}/100** |",
        f"",
    ]

    # 排行榜
    if report.healthiest_frameworks:
        lines.extend([
            f"### 🏆 健康度排行 / Health Ranking",
            f"",
        ])
        for i, fw in enumerate(report.healthiest_frameworks, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            lines.append(f"{medal} **{fw}**")
        lines.append("")

    if report.needs_attention:
        lines.extend([
            f"### ⚠️ 需要关注 / Needs Attention",
            f"",
        ])
        for fw in report.needs_attention:
            lines.append(f"- 🔴 **{fw}**")
        lines.append("")

    # 全局异常
    if report.global_anomalies:
        lines.extend([
            f"### 🚨 异常告警 / Anomaly Alerts",
            f"",
        ])
        for anomaly in report.global_anomalies:
            lines.append(f"- {anomaly}")
        lines.append("")

    lines.extend([
        f"---",
        f"",
        f"## 📋 各框架详情 / Framework Details",
        f"",
    ])

    # 各框架详细报告
    for fw_data in sorted(report.frameworks, key=lambda f: f.health_score, reverse=True):
        score = fw_data.health_score
        if score >= 80:
            health_emoji = "🟢"
        elif score >= 60:
            health_emoji = "🟡"
        elif score >= 40:
            health_emoji = "🟠"
        else:
            health_emoji = "🔴"

        lines.extend([
            f"### {health_emoji} {fw_data.display_name}",
            f"**框架**: `{fw_data.framework}` | **健康分数 Health Score**: **{score}/100** | **趋势 Trend**: {fw_data.trend}",
            f"",
            f"| 指标 | 数值 |",
            f"|:---|:---|",
            f"| 开放 Issues Open | {fw_data.open_issues_count:,} |",
            f"| 本周新增 New (7d) | {fw_data.new_issues_7d} |",
            f"| 本月新增 New (30d) | {fw_data.new_issues_30d} |",
            f"| 本周关闭 Closed (7d) | {fw_data.closed_issues_7d} |",
            f"| 本月关闭 Closed (30d) | {fw_data.closed_issues_30d} |",
            f"| Bug 类 Issues | {fw_data.bug_count} |",
            f"",
        ])

        if fw_data.anomalies:
            lines.append(f"**异常告警 Anomalies**:")
            for a in fw_data.anomalies:
                lines.append(f"- {a}")
            lines.append("")

        if fw_data.top_issues:
            lines.append(f"**🔥 热门 Issues / Hot Issues**:")
            for issue in fw_data.top_issues[:3]:
                lines.append(
                    f"- [{issue['title'][:80]}]({issue['url']}) "
                    f"(👍 {issue['reactions']} / 💬 {issue['comments']})"
                )
            lines.append("")

        if fw_data.critical_issues:
            lines.append(f"**🚨 高危 Issues / Critical Issues**:")
            for ci in fw_data.critical_issues[:3]:
                lines.append(
                    f"- [{ci.title[:80]}]({ci.url}) "
                    f"(👍 {ci.reactions})"
                )
            lines.append("")

        if fw_data.scan_error:
            lines.append(f"⚠️ 扫描错误: `{fw_data.scan_error}`")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    lines.extend([
        f"",
        f"---",
        f"",
        f"*🩺 由 [CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成*",
        f"*📡 数据来源: GitHub REST API | 更新频率: 每日*",
        f"*🦠 掌握 Agent 生态脉搏，定义框架健康标准*",
    ])

    return "\n".join(lines)


def report_to_json(report: EpidemicReport) -> dict:
    """将报告转为 JSON 可序列化的 dict"""
    def _critical_to_dict(ci: CriticalIssue) -> dict:
        return {
            "number": ci.number,
            "title": ci.title,
            "url": ci.url,
            "labels": ci.labels,
            "reactions": ci.reactions,
            "created_at": ci.created_at,
        }

    def _fw_to_dict(fw: FrameworkHealthData) -> dict:
        return {
            "framework": fw.framework,
            "display_name": fw.display_name,
            "owner": fw.owner,
            "repo": fw.repo,
            "repo_url": fw.repo_url,
            "open_issues_count": fw.open_issues_count,
            "closed_issues_count": fw.closed_issues_count,
            "new_issues_7d": fw.new_issues_7d,
            "new_issues_30d": fw.new_issues_30d,
            "closed_issues_7d": fw.closed_issues_7d,
            "closed_issues_30d": fw.closed_issues_30d,
            "avg_close_time_hours": fw.avg_close_time_hours,
            "critical_issues": [_critical_to_dict(ci) for ci in fw.critical_issues],
            "bug_count": fw.bug_count,
            "top_issues": fw.top_issues,
            "label_distribution": fw.label_distribution,
            "health_score": fw.health_score,
            "trend": fw.trend,
            "anomalies": fw.anomalies,
            "scanned_at": fw.scanned_at,
            "scan_error": fw.scan_error,
        }

    return {
        "report_date": report.report_date,
        "generated_at": report.generated_at,
        "framework_count": report.framework_count,
        "total_open_issues": report.total_open_issues,
        "total_new_issues_7d": report.total_new_issues_7d,
        "total_closed_issues_7d": report.total_closed_issues_7d,
        "avg_health_score": report.avg_health_score,
        "healthiest_frameworks": report.healthiest_frameworks,
        "most_active_frameworks": report.most_active_frameworks,
        "needs_attention": report.needs_attention,
        "global_anomalies": report.global_anomalies,
        "frameworks": [_fw_to_dict(fw) for fw in report.frameworks],
    }


def save_report(report: EpidemicReport) -> dict:
    """
    保存报告到文件系统

    输出：
      - EPIDEMIC_REPORT.md (项目根目录)
      - reports/epidemic/YYYY-MM-DD.json (JSON 存档)

    Returns:
        保存结果 dict
    """
    result = {}

    # Markdown 报告 → 项目根目录
    md_content = generate_markdown_report(report)
    md_path = config.ROOT_DIR / "EPIDEMIC_REPORT.md"
    md_path.write_text(md_content, encoding="utf-8")
    result["markdown_path"] = str(md_path)

    # JSON 存档 → reports/epidemic/
    report_dir = config.EPIDEMIC_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    json_filename = f"{report.report_date}.json"
    json_path = report_dir / json_filename
    json_data = report_to_json(report)
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    result["json_path"] = str(json_path)

    print(f"  📄 Markdown 报告: {md_path}")
    print(f"  📊 JSON 存档:    {json_path}")

    return result


def load_latest_report() -> dict | None:
    """加载最新的 JSON 报告"""
    report_dir = config.EPIDEMIC_REPORT_DIR
    if not report_dir.exists():
        return None

    json_files = sorted(report_dir.glob("*.json"), reverse=True)
    if not json_files:
        return None

    try:
        return json.loads(json_files[0].read_text(encoding="utf-8"))
    except Exception:
        return None


def list_report_history() -> list[dict]:
    """列出所有历史报告"""
    report_dir = config.EPIDEMIC_REPORT_DIR
    if not report_dir.exists():
        return []

    reports = []
    for json_file in sorted(report_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            reports.append({
                "date": data.get("report_date", json_file.stem),
                "generated_at": data.get("generated_at", ""),
                "framework_count": data.get("framework_count", 0),
                "avg_health_score": data.get("avg_health_score", 0),
                "total_open_issues": data.get("total_open_issues", 0),
                "filename": json_file.name,
            })
        except Exception:
            continue

    return reports


# ===== CLI 入口 =====

async def _cli_main():
    """命令行生成疫情报告"""
    monitor = EpidemicMonitor()
    report = await monitor.scan_all_frameworks()
    result = save_report(report)
    print(f"\n🦠 疫情通报生成完成！")
    print(f"  📄 {result['markdown_path']}")
    print(f"  📊 {result['json_path']}")


if __name__ == "__main__":
    asyncio.run(_cli_main())
