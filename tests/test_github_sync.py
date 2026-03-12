"""
🩺 CyberHuaTuo 测试 — GitHub 同步 & 贡献榜
测试 github_sync.py 的称号计算、贡献统计和 API 调用逻辑
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ===== 导入被测模块 =====
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cyberhuatuo.github_sync import (
    GitHubSyncer,
    calculate_title,
    count_contributor_cases,
    get_contributor_summary,
)


# ============================================================
# 🏅 称号计算测试
# ============================================================


class TestCalculateTitle:
    """测试贡献次数 → 名医堂称号的映射"""

    def test_zero_contributions(self):
        emoji, title = calculate_title(0)
        assert emoji == "🌱"
        assert "学徒" in title

    def test_one_contribution_resident(self):
        emoji, title = calculate_title(1)
        assert emoji == "🏥"
        assert "坐堂医师" in title

    def test_two_contributions_still_resident(self):
        emoji, title = calculate_title(2)
        assert emoji == "🏥"
        assert "坐堂医师" in title

    def test_three_contributions_attending(self):
        emoji, title = calculate_title(3)
        assert emoji == "⚕️"
        assert "主治医师" in title

    def test_five_contributions_renowned(self):
        emoji, title = calculate_title(5)
        assert emoji == "👨‍⚕️"
        assert "名医" in title

    def test_ten_contributions_divine(self):
        emoji, title = calculate_title(10)
        assert emoji == "🌟"
        assert "神医" in title

    def test_twenty_contributions_reborn(self):
        emoji, title = calculate_title(20)
        assert emoji == "👑"
        assert "华佗再世" in title

    def test_hundred_contributions_still_reborn(self):
        """超过 20 次应保持最高称号"""
        emoji, title = calculate_title(100)
        assert emoji == "👑"
        assert "华佗再世" in title


# ============================================================
# 📊 贡献统计测试
# ============================================================


class TestCountContributorCases:
    """测试扫描 cases/ 目录统计贡献者"""

    def test_empty_directory(self, tmp_path):
        """空目录应返回 0"""
        count = count_contributor_cases("testuser", cases_dir=tmp_path)
        assert count == 0

    def test_nonexistent_directory(self, tmp_path):
        """不存在的目录应返回 0"""
        non_existent = tmp_path / "nonexistent"
        count = count_contributor_cases("testuser", cases_dir=non_existent)
        assert count == 0

    def test_single_contributor(self, tmp_path):
        """单个贡献者的文件应正确计数"""
        case_dir = tmp_path / "langchain" / "general"
        case_dir.mkdir(parents=True)

        for i in range(3):
            case_file = case_dir / f"case-{i:03d}.md"
            case_file.write_text(
                f'---\nid: "case-{i:03d}"\ncontributors:\n  - github: "alice"\n---\n\n## body\n',
                encoding="utf-8",
            )

        count = count_contributor_cases("alice", cases_dir=tmp_path)
        assert count == 3

    def test_case_insensitive_username(self, tmp_path):
        """用户名匹配应不区分大小写"""
        case_dir = tmp_path / "pytorch"
        case_dir.mkdir(parents=True)

        case_file = case_dir / "case-001.md"
        case_file.write_text(
            '---\nid: "case-001"\ncontributors:\n  - github: "Alice"\n---\n\n## body\n',
            encoding="utf-8",
        )

        count = count_contributor_cases("alice", cases_dir=tmp_path)
        assert count == 1

    def test_multiple_contributors_per_file(self, tmp_path):
        """多个贡献者的文件只计数一次"""
        case_dir = tmp_path / "crewai"
        case_dir.mkdir(parents=True)

        case_file = case_dir / "case-001.md"
        case_file.write_text(
            '---\nid: "case-001"\ncontributors:\n  - github: "alice"\n  - github: "bob"\n---\n\n## body\n',
            encoding="utf-8",
        )

        count_alice = count_contributor_cases("alice", cases_dir=tmp_path)
        count_bob = count_contributor_cases("bob", cases_dir=tmp_path)
        assert count_alice == 1
        assert count_bob == 1

    def test_different_user_not_counted(self, tmp_path):
        """不同用户不应被计入"""
        case_dir = tmp_path / "fastapi"
        case_dir.mkdir(parents=True)

        case_file = case_dir / "case-001.md"
        case_file.write_text(
            '---\nid: "case-001"\ncontributors:\n  - github: "alice"\n---\n\n## body\n',
            encoding="utf-8",
        )

        count = count_contributor_cases("bob", cases_dir=tmp_path)
        assert count == 0

    def test_skip_underscore_files(self, tmp_path):
        """以下划线开头的文件应跳过"""
        case_dir = tmp_path / "langchain"
        case_dir.mkdir(parents=True)

        # 正常文件
        normal = case_dir / "case-001.md"
        normal.write_text(
            '---\nid: "case-001"\ncontributors:\n  - github: "alice"\n---\n\n## body\n',
            encoding="utf-8",
        )

        # 下划线文件（应跳过）
        hidden = case_dir / "_index.md"
        hidden.write_text(
            '---\nid: "_index"\ncontributors:\n  - github: "alice"\n---\n\n## body\n',
            encoding="utf-8",
        )

        count = count_contributor_cases("alice", cases_dir=tmp_path)
        assert count == 1  # 只计正常文件


# ============================================================
# 🔄 同步策略测试
# ============================================================


class TestGitHubSyncer:
    """测试 GitHubSyncer 同步逻辑"""

    def test_sync_without_token_returns_error(self):
        """无 token 时应返回错误"""
        syncer = GitHubSyncer(token=None)
        syncer.token = None  # 确保清空

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            syncer.sync_prescription(
                relative_path="cases/test/case.md",
                content="test content",
                contributor_github="testuser",
            )
        )

        assert result["success"] is False
        assert "GITHUB_TOKEN" in result["error"]


class TestGetContributorSummary:
    """测试贡献者摘要生成"""

    def test_summary_structure(self, tmp_path):
        """摘要应包含所有必要字段"""
        with patch("cyberhuatuo.github_sync.config") as mock_config:
            mock_config.CASES_DIR = tmp_path

            summary = get_contributor_summary("nonexistent_user")

            assert "github" in summary
            assert "contribution_count" in summary
            assert "title_emoji" in summary
            assert "title" in summary
            assert summary["github"] == "nonexistent_user"
            assert summary["contribution_count"] == 0
            assert summary["title_emoji"] == "🌱"


# ============================================================
# 📋 Issue 创建测试（瞬时药方层）
# ============================================================


class TestCreatePrescriptionIssue:
    """测试 GitHubSyncer.create_prescription_issue 方法"""

    def test_issue_body_contains_structured_json(self):
        """Issue body 应包含结构化 JSON 数据块"""
        syncer = GitHubSyncer(token="test-token")

        import asyncio
        import json

        # Mock httpx 响应
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "number": 42,
                "html_url": "https://github.com/test/repo/issues/42",
            }

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = asyncio.get_event_loop().run_until_complete(
                syncer.create_prescription_issue(
                    title="测试药方",
                    framework="langchain",
                    prescription="安装最新版本",
                    symptom="导入报错",
                    severity="high",
                    contributor_github="testuser",
                )
            )

            assert result["success"] is True
            assert result["method"] == "issue"
            assert result["issue_number"] == 42

            # 检查发送的请求 payload
            call_args = mock_client.post.call_args
            payload = call_args.kwargs.get("json") or call_args[1].get("json")
            assert "🩺 [langchain] 测试药方" == payload["title"]
            assert "prescription" in payload["labels"]
            assert "framework:langchain" in payload["labels"]
            assert "severity:high" in payload["labels"]

    def test_issue_title_format(self):
        """Issue 标题应遵循 🩺 [framework] 标题 格式"""
        syncer = GitHubSyncer(token="test-token")

        import asyncio

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "number": 1,
                "html_url": "https://github.com/test/issues/1",
            }

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = asyncio.get_event_loop().run_until_complete(
                syncer.create_prescription_issue(
                    title="RAG内存泄漏修复",
                    framework="pytorch",
                    prescription="修复方案详情",
                )
            )

            assert result["success"] is True
            assert result["title"] == "🩺 [pytorch] RAG内存泄漏修复"

    def test_issue_creation_failure(self):
        """API 返回非 2xx 时应报告失败"""
        syncer = GitHubSyncer(token="test-token")

        import asyncio

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 422
            mock_resp.text = "Validation Failed"

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = asyncio.get_event_loop().run_until_complete(
                syncer.create_prescription_issue(
                    title="测试",
                    framework="test",
                    prescription="药方",
                )
            )

            assert result["success"] is False
            assert result["method"] == "issue"
            assert "Validation Failed" in result["error"]


# ============================================================
# 🔄 降级策略测试（双层架构）
# ============================================================


class TestSyncPrescriptionStrategies:
    """测试 sync_prescription 的降级路径：直推 → Issue → Fork+PR"""

    def test_direct_push_success_skips_issue(self):
        """直推成功时不应创建 Issue"""
        syncer = GitHubSyncer(token="test-token")
        syncer.push_file = AsyncMock(return_value={
            "success": True,
            "method": "direct_push",
            "commit_sha": "abc123",
        })
        syncer.create_prescription_issue = AsyncMock()

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            syncer.sync_prescription(
                relative_path="cases/test/case.md",
                content="test content",
                contributor_github="testuser",
                prescription_meta={"title": "test", "framework": "test", "prescription": "fix"},
            )
        )

        assert result["success"] is True
        assert result["method"] == "direct_push"
        syncer.create_prescription_issue.assert_not_called()

    def test_push_403_with_meta_creates_issue(self):
        """直推 403 且有 prescription_meta 时应创建 Issue"""
        syncer = GitHubSyncer(token="test-token")
        syncer.push_file = AsyncMock(return_value={
            "success": False,
            "status_code": 403,
            "method": "direct_push",
        })
        syncer.create_prescription_issue = AsyncMock(return_value={
            "success": True,
            "method": "issue",
            "issue_number": 99,
            "issue_url": "https://github.com/test/issues/99",
        })
        syncer.fork_and_pr = AsyncMock()

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            syncer.sync_prescription(
                relative_path="cases/test/case.md",
                content="test content",
                contributor_github="testuser",
                prescription_meta={"title": "测试", "framework": "langchain", "prescription": "修复方案"},
            )
        )

        assert result["success"] is True
        assert result["method"] == "issue"
        syncer.create_prescription_issue.assert_called_once()
        syncer.fork_and_pr.assert_not_called()

    def test_push_403_without_meta_falls_back_to_fork_pr(self):
        """直推 403 且无 prescription_meta 时应回退到 Fork+PR"""
        syncer = GitHubSyncer(token="test-token")
        syncer.push_file = AsyncMock(return_value={
            "success": False,
            "status_code": 404,
            "method": "direct_push",
        })
        syncer.create_prescription_issue = AsyncMock()
        syncer.fork_and_pr = AsyncMock(return_value={
            "success": True,
            "method": "fork_pr",
            "pr_url": "https://github.com/test/pr/1",
        })

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            syncer.sync_prescription(
                relative_path="cases/test/case.md",
                content="test content",
                contributor_github="testuser",
                prescription_meta=None,
            )
        )

        assert result["success"] is True
        assert result["method"] == "fork_pr"
        syncer.create_prescription_issue.assert_not_called()
        syncer.fork_and_pr.assert_called_once()

