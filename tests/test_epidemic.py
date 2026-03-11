"""
🦠 CyberHuaTuo 测试 — 疫情通报模块
测试健康分数计算、异常检测、报告生成等核心逻辑
所有测试使用 mock 数据，不依赖外部 API
"""

import json
from dataclasses import field

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cyberhuatuo.epidemic_monitor import (
    FrameworkHealthData,
    CriticalIssue,
    EpidemicReport,
    EpidemicMonitor,
    generate_markdown_report,
    report_to_json,
)


# ===== 测试数据工厂 =====

def make_fw_data(**overrides) -> FrameworkHealthData:
    """创建测试用 FrameworkHealthData"""
    defaults = {
        "framework": "test-framework",
        "display_name": "test-org/test-repo",
        "owner": "test-org",
        "repo": "test-repo",
        "repo_url": "https://github.com/test-org/test-repo",
        "open_issues_count": 100,
        "closed_issues_count": 500,
        "new_issues_7d": 10,
        "new_issues_30d": 40,
        "closed_issues_7d": 12,
        "closed_issues_30d": 50,
        "bug_count": 15,
        "scanned_at": "2026-03-11T00:00:00+00:00",
    }
    defaults.update(overrides)
    return FrameworkHealthData(**defaults)


def make_report(**overrides) -> EpidemicReport:
    """创建测试用 EpidemicReport"""
    defaults = {
        "report_date": "2026-03-11",
        "generated_at": "2026-03-11T00:00:00+00:00",
        "framework_count": 2,
        "frameworks": [
            make_fw_data(framework="langchain", health_score=75),
            make_fw_data(framework="crewai", health_score=55),
        ],
        "total_open_issues": 200,
        "total_new_issues_7d": 20,
        "total_closed_issues_7d": 24,
        "avg_health_score": 65.0,
        "healthiest_frameworks": ["langchain"],
        "most_active_frameworks": ["langchain"],
        "needs_attention": ["crewai"],
    }
    defaults.update(overrides)
    return EpidemicReport(**defaults)


# ===== 健康分数计算测试 =====

class TestHealthScoreCalculation:
    """测试健康分数计算逻辑"""

    def setup_method(self):
        self.monitor = EpidemicMonitor(github_client=None)

    def test_healthy_framework(self):
        """关闭率高、bug 少的框架分数应高"""
        data = make_fw_data(
            open_issues_count=50,
            new_issues_7d=10,
            closed_issues_7d=15,
            bug_count=3,
            top_issues=[{"reactions": 25}, {"reactions": 30}],
        )
        score = self.monitor.calculate_health_score(data)
        assert score >= 70, f"健康框架分数应 >= 70, got {score}"

    def test_unhealthy_framework(self):
        """大量 bug、关闭率低的框架分数应低"""
        data = make_fw_data(
            open_issues_count=200,
            new_issues_7d=50,
            closed_issues_7d=5,
            bug_count=150,
            critical_issues=[CriticalIssue(i, f"Critical #{i}", f"url/{i}") for i in range(6)],
        )
        score = self.monitor.calculate_health_score(data)
        assert score < 50, f"不健康框架分数应 < 50, got {score}"

    def test_inactive_framework(self):
        """无活动的框架分数应为中性"""
        data = make_fw_data(
            open_issues_count=10,
            new_issues_7d=0,
            closed_issues_7d=0,
            bug_count=0,
        )
        score = self.monitor.calculate_health_score(data)
        assert 30 <= score <= 75, f"不活跃框架分数应在 30-75 之间, got {score}"

    def test_no_open_issues(self):
        """无开放 Issues 的框架应得高分"""
        data = make_fw_data(
            open_issues_count=0,
            new_issues_7d=0,
            closed_issues_7d=0,
            bug_count=0,
        )
        score = self.monitor.calculate_health_score(data)
        assert score >= 60, f"无 Issues 框架分数应 >= 60, got {score}"

    def test_score_bounds(self):
        """分数应在 0-100 之间"""
        # 极端高
        data_high = make_fw_data(
            open_issues_count=10,
            new_issues_7d=100,
            closed_issues_7d=200,
            bug_count=0,
            top_issues=[{"reactions": 50}],
        )
        score_high = self.monitor.calculate_health_score(data_high)
        assert 0 <= score_high <= 100, f"分数越界: {score_high}"

        # 极端低
        data_low = make_fw_data(
            open_issues_count=1000,
            new_issues_7d=100,
            closed_issues_7d=1,
            bug_count=900,
            critical_issues=[CriticalIssue(i, f"Issue #{i}", "") for i in range(10)],
        )
        score_low = self.monitor.calculate_health_score(data_low)
        assert 0 <= score_low <= 100, f"分数越界: {score_low}"


# ===== 趋势与异常检测测试 =====

class TestTrendAndAnomaly:
    """测试趋势计算和异常检测"""

    def setup_method(self):
        self.monitor = EpidemicMonitor(github_client=None)

    def test_improving_trend(self):
        """近期 issue 减少 → improving"""
        data = make_fw_data(
            new_issues_7d=5,
            new_issues_30d=60,
        )
        trend = self.monitor._calculate_trend(data)
        assert "improving" in trend

    def test_declining_trend(self):
        """近期 issue 激增 → declining"""
        data = make_fw_data(
            new_issues_7d=30,
            new_issues_30d=40,
        )
        trend = self.monitor._calculate_trend(data)
        assert "declining" in trend

    def test_stable_trend(self):
        """issue 数量稳定 → stable"""
        data = make_fw_data(
            new_issues_7d=10,
            new_issues_30d=45,
        )
        trend = self.monitor._calculate_trend(data)
        assert "stable" in trend

    def test_anomaly_high_new_issues(self):
        """新 Issue 激增应触发异常"""
        data = make_fw_data(new_issues_7d=80, closed_issues_7d=5)
        anomalies = self.monitor._detect_anomalies(data)
        assert len(anomalies) >= 1
        assert any("80" in a for a in anomalies)

    def test_anomaly_low_close_rate(self):
        """关闭率过低应触发异常"""
        data = make_fw_data(new_issues_7d=30, closed_issues_7d=3)
        anomalies = self.monitor._detect_anomalies(data)
        assert any("关闭率" in a for a in anomalies)

    def test_anomaly_many_critical(self):
        """多个 critical issues 应触发异常"""
        data = make_fw_data(
            critical_issues=[CriticalIssue(i, f"Bug #{i}", "") for i in range(6)]
        )
        anomalies = self.monitor._detect_anomalies(data)
        assert any("高影响" in a for a in anomalies)

    def test_no_anomalies(self):
        """健康框架应无异常"""
        data = make_fw_data(
            new_issues_7d=5,
            closed_issues_7d=8,
            bug_count=3,
            open_issues_count=50,
        )
        anomalies = self.monitor._detect_anomalies(data)
        assert len(anomalies) == 0


# ===== 报告生成测试 =====

class TestReportGeneration:
    """测试报告生成逻辑"""

    def test_markdown_report_has_sections(self):
        """Markdown 报告应包含所有必要章节"""
        report = make_report()
        md = generate_markdown_report(report)

        assert "疫情通报" in md
        assert "全局概览" in md
        assert "各框架详情" in md
        assert "langchain" in md
        assert "crewai" in md
        assert "2026-03-11" in md

    def test_markdown_report_has_stats(self):
        """Markdown 报告应包含统计数据"""
        report = make_report()
        md = generate_markdown_report(report)

        assert "200" in md  # total_open_issues
        assert "65" in md   # avg_health_score

    def test_json_roundtrip(self):
        """JSON 序列化/反序列化应保持数据完整"""
        report = make_report()
        json_data = report_to_json(report)

        # 能正确序列化
        json_str = json.dumps(json_data, ensure_ascii=False)
        parsed = json.loads(json_str)

        assert parsed["report_date"] == "2026-03-11"
        assert parsed["avg_health_score"] == 65.0
        assert parsed["framework_count"] == 2
        assert len(parsed["frameworks"]) == 2

    def test_json_framework_fields(self):
        """JSON 中每个框架应包含完整字段"""
        report = make_report()
        json_data = report_to_json(report)
        fw = json_data["frameworks"][0]

        required_fields = [
            "framework", "display_name", "owner", "repo",
            "open_issues_count", "new_issues_7d",
            "closed_issues_7d", "health_score", "trend",
            "anomalies", "scanned_at",
        ]

        for field_name in required_fields:
            assert field_name in fw, f"缺少字段: {field_name}"

    def test_empty_report(self):
        """空报告也应正常生成"""
        report = EpidemicReport(
            report_date="2026-03-11",
            generated_at="2026-03-11T00:00:00+00:00",
        )
        md = generate_markdown_report(report)
        assert "疫情通报" in md

        json_data = report_to_json(report)
        assert json_data["framework_count"] == 0


# ===== 边缘情况测试 =====

class TestEdgeCases:
    """边缘情况测试"""

    def test_zero_division_safety(self):
        """除零安全 — 各字段为 0 不应崩溃"""
        monitor = EpidemicMonitor(github_client=None)
        data = FrameworkHealthData(
            framework="zero",
            display_name="zero/zero",
            owner="zero",
            repo="zero",
        )
        # 所有值默认为 0
        score = monitor.calculate_health_score(data)
        assert score >= 0
        trend = monitor._calculate_trend(data)
        assert trend is not None
        anomalies = monitor._detect_anomalies(data)
        assert isinstance(anomalies, list)

    def test_critical_issue_serialization(self):
        """CriticalIssue 应正确序列化"""
        ci = CriticalIssue(
            number=123,
            title="Test Critical Issue 中文标题",
            url="https://github.com/test/test/issues/123",
            labels=["bug", "critical"],
            reactions=42,
        )
        report = make_report()
        report.frameworks[0].critical_issues = [ci]

        json_data = report_to_json(report)
        ci_data = json_data["frameworks"][0]["critical_issues"][0]

        assert ci_data["number"] == 123
        assert "中文" in ci_data["title"]
        assert ci_data["reactions"] == 42
