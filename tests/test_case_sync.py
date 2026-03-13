"""
🩺 CyberHuaTuo 测试 — case_sync.py 药方库自动同步（高性能版）
测试 Git blob SHA 计算、冷却时间、树 SHA 快速检测、ETag 条件请求和后台线程
"""

import json
import sys
import time
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cyberhuatuo.case_sync import CaseSyncer, _git_blob_sha


# ============================================================
# 🔐 Git Blob SHA 计算测试
# ============================================================


class TestGitBlobSha:
    """测试 Git blob SHA 计算是否与 git hash-object 一致"""

    def test_empty_content(self):
        """空内容的 Git blob SHA 应该是已知值"""
        sha = _git_blob_sha(b"")
        assert sha == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"

    def test_hello_world(self):
        """'hello world' 的 blob SHA 应该与 git 一致"""
        sha = _git_blob_sha(b"hello world")
        assert sha == "95d09f2b10159347eece71399a7e2e907ea3df4f"

    def test_deterministic(self):
        """同一内容的 SHA 应该是确定性的"""
        content = b"test content for sha"
        sha1 = _git_blob_sha(content)
        sha2 = _git_blob_sha(content)
        assert sha1 == sha2

    def test_different_content_different_sha(self):
        """不同内容应产生不同的 SHA"""
        sha1 = _git_blob_sha(b"content A")
        sha2 = _git_blob_sha(b"content B")
        assert sha1 != sha2


# ============================================================
# ⏱️ 冷却时间测试
# ============================================================


class TestSyncCooldown:
    """测试同步冷却时间逻辑"""

    def test_first_run_needs_sync(self, tmp_path):
        """首次运行（无 .last_sync）应需要同步"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=30,
        )
        assert syncer.is_sync_needed() is True

    def test_recently_synced_no_need(self, tmp_path):
        """刚同步过应跳过"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=30,
        )
        last_sync_file = tmp_path / ".last_sync"
        last_sync_file.write_text(
            json.dumps({"last_sync": time.time()}), encoding="utf-8"
        )
        assert syncer.is_sync_needed() is False

    def test_expired_sync_needs_refresh(self, tmp_path):
        """超过冷却时间应需要同步"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=30,
        )
        last_sync_file = tmp_path / ".last_sync"
        last_sync_file.write_text(
            json.dumps({"last_sync": time.time() - 31 * 60}),
            encoding="utf-8",
        )
        assert syncer.is_sync_needed() is True

    def test_save_and_read_sync_time(self, tmp_path):
        """保存后应能正确读取同步时间"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=1,
        )
        syncer._save_state()
        assert syncer.is_sync_needed() is False


# ============================================================
# 📂 本地 SHA 计算测试
# ============================================================


class TestComputeLocalShas:
    """测试本地文件 SHA 计算"""

    def test_empty_directory(self, tmp_path):
        """空目录应返回空 dict"""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=cases_dir,
        )
        shas = syncer._compute_local_shas()
        assert shas == {}

    def test_single_file(self, tmp_path):
        """单个文件应正确计算 SHA"""
        cases_dir = tmp_path / "cases" / "langchain"
        cases_dir.mkdir(parents=True)

        content = b"---\nid: test\n---\n\n## test case\n"
        case_file = cases_dir / "test-001.md"
        case_file.write_bytes(content)

        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        shas = syncer._compute_local_shas()

        expected_path = "cases/langchain/test-001.md"
        assert expected_path in shas
        assert shas[expected_path] == _git_blob_sha(content)

    def test_skip_underscore_files(self, tmp_path):
        """以下划线开头的文件应跳过"""
        cases_dir = tmp_path / "cases" / "langchain"
        cases_dir.mkdir(parents=True)

        normal = cases_dir / "test-001.md"
        normal.write_bytes(b"test content")

        hidden = cases_dir / "_index.md"
        hidden.write_bytes(b"index content")

        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        shas = syncer._compute_local_shas()

        assert "cases/langchain/test-001.md" in shas
        assert "cases/langchain/_index.md" not in shas

    def test_nonexistent_directory(self, tmp_path):
        """不存在的目录应返回空 dict"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "nonexistent",
        )
        shas = syncer._compute_local_shas()
        assert shas == {}


# ============================================================
# ⚡ 树 SHA 快速检测测试
# ============================================================


class TestQuickCheck:
    """测试树 SHA + ETag 快速检测"""

    def test_tree_sha_unchanged_returns_false(self, tmp_path):
        """树 SHA 未变时应返回 False（无变化）"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._known_tree_sha = "abc123"

        # Mock GitHub API 返回相同的 tree SHA
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tree": [
                {"path": "cases", "type": "tree", "sha": "abc123"},
                {"path": "README.md", "type": "blob", "sha": "def456"},
            ]
        }).encode("utf-8")
        mock_resp.headers = {"ETag": '"etag-value"'}
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = syncer._quick_check_changed()
            assert result is False

    def test_tree_sha_changed_returns_true(self, tmp_path):
        """树 SHA 变化时应返回 True"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._known_tree_sha = "old_sha"

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tree": [
                {"path": "cases", "type": "tree", "sha": "new_sha"},
            ]
        }).encode("utf-8")
        mock_resp.headers = {"ETag": '"new-etag"'}
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = syncer._quick_check_changed()
            assert result is True
            assert syncer._known_tree_sha == "new_sha"

    def test_etag_304_returns_false(self, tmp_path):
        """ETag 304 响应应返回 False（无变化，不消耗配额）"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._etag = '"cached-etag"'

        http_error = urllib.request.HTTPError(
            url="https://api.github.com/...",
            code=304,
            msg="Not Modified",
            hdrs={},
            fp=None,
        )

        with patch("urllib.request.urlopen", side_effect=http_error):
            result = syncer._quick_check_changed()
            assert result is False

    def test_network_error_returns_none(self, tmp_path):
        """网络错误时应返回 None（回退到完整同步）"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )

        with patch(
            "urllib.request.urlopen",
            side_effect=Exception("Connection timeout"),
        ):
            result = syncer._quick_check_changed()
            assert result is None

    def test_etag_saved_from_response(self, tmp_path):
        """应保存响应中的 ETag 用于下次条件请求"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        assert syncer._etag is None

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tree": [
                {"path": "cases", "type": "tree", "sha": "first_sha"},
            ]
        }).encode("utf-8")
        mock_resp.headers = {"ETag": '"my-etag-123"'}
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            syncer._quick_check_changed()
            assert syncer._etag == '"my-etag-123"'


# ============================================================
# 🔄 增量同步检测测试
# ============================================================


class TestDoSync:
    """测试增量同步逻辑"""

    def test_quick_check_false_skips_full_sync(self, tmp_path):
        """快速检测无变化时应跳过完整同步"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._quick_check_changed = MagicMock(return_value=False)
        syncer._fetch_remote_tree = MagicMock()

        result = syncer._do_sync()
        assert result == 0
        syncer._fetch_remote_tree.assert_not_called()

    def test_quick_check_true_triggers_full_sync(self, tmp_path):
        """快速检测有变化时应执行完整同步"""
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir(parents=True)

        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=cases_dir,
        )
        syncer._quick_check_changed = MagicMock(return_value=True)
        syncer._fetch_remote_tree = MagicMock(
            return_value={"cases/new.md": "sha_new"}
        )
        syncer._download_files = MagicMock(return_value=1)

        result = syncer._do_sync()
        assert result == 1
        syncer._fetch_remote_tree.assert_called_once()

    def test_quick_check_none_falls_back_to_full(self, tmp_path):
        """快速检测失败（None）时应回退到完整同步"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._quick_check_changed = MagicMock(return_value=None)
        syncer._fetch_remote_tree = MagicMock(return_value={})

        result = syncer._do_sync()
        assert result == 0
        syncer._fetch_remote_tree.assert_called_once()


# ============================================================
# 🧵 后台线程测试
# ============================================================


class TestBackgroundSync:
    """测试后台线程行为"""

    def test_pending_update_consumed_on_check(self, tmp_path):
        """后台线程设置的 _pending_update 应被 check_and_sync 消费"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=999,  # 大冷却防止正常路径触发
        )
        # 模拟后台线程已检测到更新
        syncer._pending_update = True

        result = syncer.check_and_sync()
        assert result is True
        assert syncer._pending_update is False

    def test_pending_update_false_no_trigger(self, tmp_path):
        """无 pending update 且冷却未过时应返回 False"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=999,
        )
        syncer._pending_update = False
        # 模拟刚同步过
        last_sync_file = tmp_path / ".last_sync"
        last_sync_file.write_text(
            json.dumps({"last_sync": time.time()}), encoding="utf-8"
        )

        result = syncer.check_and_sync()
        assert result is False


# ============================================================
# 💾 状态持久化测试
# ============================================================


class TestStatePersistence:
    """测试同步状态的保存和恢复"""

    def test_save_and_load_tree_sha(self, tmp_path):
        """树 SHA 应能正确持久化和恢复"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        syncer._known_tree_sha = "persisted_sha_abc"
        syncer._etag = '"persisted-etag"'
        syncer._save_state()

        # 新实例应能恢复状态
        syncer2 = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
        )
        assert syncer2._known_tree_sha == "persisted_sha_abc"
        assert syncer2._etag == '"persisted-etag"'


# ============================================================
# 🛡️ 容错测试
# ============================================================


class TestSyncErrorHandling:
    """测试同步失败时的静默降级"""

    def test_check_and_sync_disabled(self, tmp_path):
        """CASE_SYNC_ENABLED=false 时应直接返回 False"""
        with patch("cyberhuatuo.case_sync.config") as mock_config:
            mock_config.CASE_SYNC_ENABLED = False
            mock_config.GITHUB_SYNC_OWNER = "test"
            mock_config.GITHUB_SYNC_REPO = "test"
            mock_config.GITHUB_SYNC_BRANCH = "main"
            mock_config.CASES_DIR = tmp_path / "cases"
            mock_config.ROOT_DIR = tmp_path
            mock_config.GITHUB_TOKEN = None
            mock_config.CASE_SYNC_INTERVAL_MINUTES = 5

            syncer = CaseSyncer(root_dir=tmp_path, cases_dir=tmp_path / "cases")
            result = syncer.check_and_sync()
            assert result is False

    def test_network_error_returns_false(self, tmp_path):
        """网络错误应静默返回 False"""
        syncer = CaseSyncer(
            root_dir=tmp_path,
            cases_dir=tmp_path / "cases",
            sync_interval_minutes=0,
        )

        syncer._do_sync = MagicMock(side_effect=Exception("Network Error"))

        result = syncer.check_and_sync()
        assert result is False
