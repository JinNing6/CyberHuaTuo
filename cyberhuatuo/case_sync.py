"""
CyberHuaTuo 药方库自动同步模块（高性能版）
Case Sync — Near-realtime prescription sync from GitHub repository

三层优化架构：
  1. 树 SHA 快速检测 — 一次轻量 API 调用判断 cases/ 是否有变化
  2. ETag 条件请求 — 304 响应不消耗请求配额，高频检查零开销
  3. 后台守护线程 — 主动轮询，用户搜索时数据已是最新

Three-layer optimization:
  1. Tree SHA quick-check — one lightweight API call to detect changes
  2. ETag conditional requests — 304 responses are free (no rate limit cost)
  3. Background daemon thread — proactive polling, data ready when user searches
"""

import hashlib
import json
import logging
import threading
import time
import urllib.request
from pathlib import Path

from .config import config

logger = logging.getLogger("cyberhuatuo.case_sync")

# 上次同步时间文件
_LAST_SYNC_FILE = ".last_sync"


def _git_blob_sha(content: bytes) -> str:
    """
    计算与 Git blob 对象一致的 SHA-1 哈希值。
    Compute the SHA-1 hash consistent with a Git blob object.

    Git blob SHA = SHA1("blob <size>\\0<content>")
    """
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


class CaseSyncer:
    """
    药方库增量同步器（高性能版）

    使用树 SHA + ETag 实现极低开销的变更检测，
    通过后台线程实现接近实时的同步。
    """

    def __init__(
        self,
        owner: str | None = None,
        repo: str | None = None,
        branch: str | None = None,
        cases_dir: Path | None = None,
        root_dir: Path | None = None,
        token: str | None = None,
        sync_interval_minutes: int | None = None,
    ):
        self.owner = owner or config.GITHUB_SYNC_OWNER
        self.repo = repo or config.GITHUB_SYNC_REPO
        self.branch = branch or config.GITHUB_SYNC_BRANCH
        self.cases_dir = cases_dir or config.CASES_DIR
        self.root_dir = root_dir or config.ROOT_DIR
        self.token = token or config.GITHUB_TOKEN
        self.sync_interval = (
            sync_interval_minutes
            if sync_interval_minutes is not None
            else config.CASE_SYNC_INTERVAL_MINUTES
        ) * 60  # 转换为秒

        self._last_sync_path = self.root_dir / _LAST_SYNC_FILE

        # ETag 缓存（内存中）
        self._etag: str | None = None

        # 上次已知的 cases/ 树 SHA（内存 + 持久化）
        self._known_tree_sha: str | None = None

        # 后台线程同步结果回调标志
        self._pending_update = False
        self._lock = threading.Lock()

        # 从磁盘恢复状态
        self._load_state()

    # ============================================================
    # 📦 状态持久化
    # ============================================================

    def _load_state(self) -> None:
        """从磁盘恢复上次同步状态"""
        try:
            if self._last_sync_path.exists():
                data = json.loads(
                    self._last_sync_path.read_text(encoding="utf-8")
                )
                self._known_tree_sha = data.get("tree_sha")
                self._etag = data.get("etag")
        except Exception:
            pass

    def _get_last_sync_time(self) -> float:
        """读取上次同步的 Unix 时间戳"""
        try:
            if self._last_sync_path.exists():
                data = json.loads(
                    self._last_sync_path.read_text(encoding="utf-8")
                )
                return float(data.get("last_sync", 0))
        except Exception:
            pass
        return 0.0

    def _save_state(self) -> None:
        """保存同步状态到磁盘"""
        try:
            data = {
                "last_sync": time.time(),
                "tree_sha": self._known_tree_sha,
                "etag": self._etag,
            }
            self._last_sync_path.write_text(
                json.dumps(data), encoding="utf-8"
            )
        except Exception as e:
            logger.debug(f"保存同步状态失败: {e}")

    # ============================================================
    # ⏱️ 冷却检测
    # ============================================================

    def is_sync_needed(self) -> bool:
        """检查是否需要同步（冷却时间已过）"""
        elapsed = time.time() - self._get_last_sync_time()
        return elapsed >= self.sync_interval

    # ============================================================
    # 🔄 主入口
    # ============================================================

    def check_and_sync(self) -> bool:
        """
        检查并执行增量同步。

        Returns:
            True 如果有文件被更新，False 如果无更新或已跳过
        """
        if not config.CASE_SYNC_ENABLED:
            return False

        # 检查后台线程是否已准备好更新
        with self._lock:
            if self._pending_update:
                self._pending_update = False
                return True

        if not self.is_sync_needed():
            return False

        logger.info("🔄 药方库同步检查中...")

        try:
            updated = self._do_sync()
            self._save_state()

            if updated:
                logger.info(f"✅ 药方库同步完成，新增/更新了 {updated} 个文件")
            else:
                logger.debug("✅ 药方库已是最新")

            return updated > 0

        except Exception as e:
            logger.warning(f"⚠️ 药方库同步失败（不影响现有功能）: {e}")
            self._save_state()
            return False

    # ============================================================
    # 🚀 快速检测路径（树 SHA + ETag）
    # ============================================================

    def _quick_check_changed(self) -> bool | None:
        """
        快速检测 cases/ 目录是否有变化。

        使用两层优化：
          1. ETag 条件请求 — 304 表示无变化（不消耗配额）
          2. 树 SHA 对比 — 比较 cases/ 目录的树 SHA

        Returns:
            True  = 有变化，需要完整同步
            False = 无变化，跳过
            None  = 检测失败，回退到完整同步
        """
        url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
            f"/git/trees/{self.branch}"
        )

        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        # ETag 条件请求
        if self._etag:
            headers["If-None-Match"] = self._etag

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                # 保存新 ETag
                new_etag = resp.headers.get("ETag")
                if new_etag:
                    self._etag = new_etag

                data = json.loads(resp.read().decode("utf-8"))

                # 在顶层树中找 cases/ 目录
                for item in data.get("tree", []):
                    if item.get("path") == "cases" and item.get("type") == "tree":
                        remote_tree_sha = item.get("sha", "")

                        if self._known_tree_sha == remote_tree_sha:
                            logger.debug("⚡ 树 SHA 未变，跳过同步")
                            return False

                        # SHA 变了，记录新 SHA
                        self._known_tree_sha = remote_tree_sha
                        return True

                # 未找到 cases/ 目录
                return None

        except urllib.request.HTTPError as e:
            if e.code == 304:
                # 304 Not Modified — ETag 命中，无变化
                logger.debug("⚡ ETag 304 命中，跳过同步")
                return False
            logger.debug(f"快速检测 HTTP 错误: {e.code}")
            return None
        except Exception as e:
            logger.debug(f"快速检测失败: {e}")
            return None

    # ============================================================
    # 🔄 完整同步
    # ============================================================

    def _do_sync(self) -> int:
        """
        执行同步逻辑：
        1. 快速检测是否有变化
        2. 有变化时获取完整文件树并下载差异

        Returns:
            更新的文件数量
        """
        # 第 1 层：快速检测
        changed = self._quick_check_changed()
        if changed is False:
            return 0

        # 第 2 层：完整增量同步
        remote_files = self._fetch_remote_tree()
        if not remote_files:
            return 0

        local_shas = self._compute_local_shas()

        files_to_download = []
        for remote_path, remote_sha in remote_files.items():
            local_sha = local_shas.get(remote_path)
            if local_sha != remote_sha:
                files_to_download.append(remote_path)

        if not files_to_download:
            return 0

        downloaded = self._download_files(files_to_download)
        return downloaded

    def _fetch_remote_tree(self) -> dict[str, str]:
        """
        通过 GitHub Git Trees API 获取 cases/ 目录的文件-SHA 映射。

        Returns:
            dict: { "cases/langchain/xxx.md": "sha1_hash", ... }
        """
        url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
            f"/git/trees/{self.branch}?recursive=1"
        )

        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.warning(f"获取远程文件树失败: {e}")
            return {}

        result = {}
        for item in data.get("tree", []):
            path = item.get("path", "")
            item_type = item.get("type", "")
            sha = item.get("sha", "")

            if (
                item_type == "blob"
                and path.startswith("cases/")
                and path.endswith(".md")
                and not path.split("/")[-1].startswith("_")
            ):
                result[path] = sha

        return result

    def _compute_local_shas(self) -> dict[str, str]:
        """
        计算本地 cases/ 目录下所有 .md 文件的 Git blob SHA。
        """
        result = {}

        if not self.cases_dir.exists():
            return result

        for md_file in self.cases_dir.rglob("*.md"):
            if md_file.name.startswith("_"):
                continue

            try:
                content = md_file.read_bytes()
                sha = _git_blob_sha(content)
                rel_path = md_file.relative_to(self.root_dir).as_posix()
                result[rel_path] = sha
            except Exception:
                continue

        return result

    def _download_files(self, file_paths: list[str]) -> int:
        """从 GitHub raw 下载指定文件到本地 cases/ 目录。"""
        downloaded = 0

        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        for file_path in file_paths:
            raw_url = (
                f"https://raw.githubusercontent.com/{self.owner}/{self.repo}"
                f"/{self.branch}/{file_path}"
            )

            local_path = self.root_dir / file_path
            local_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                req = urllib.request.Request(raw_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    local_path.write_bytes(resp.read())
                downloaded += 1
                logger.debug(f"  📥 下载: {file_path}")
            except Exception as e:
                logger.debug(f"  ⚠️ 下载失败 {file_path}: {e}")

        return downloaded

    # ============================================================
    # 🧵 后台线程轮询
    # ============================================================

    def start_background_sync(self) -> None:
        """
        启动后台守护线程，定期检查并同步药方库。

        线程特征：
        - daemon=True，主进程退出时自动终止
        - 首次启动延迟 30 秒（避免与 MCP 初始化竞争）
        - 此后每 sync_interval 秒检查一次
        - 同步成功后标记 _pending_update，由主线程消费
        """
        thread = threading.Thread(
            target=self._background_loop,
            daemon=True,
            name="cyberhuatuo-case-sync",
        )
        thread.start()
        logger.info(
            f"🧵 药方库后台同步已启动 "
            f"(间隔 {self.sync_interval // 60} 分钟)"
        )

    def _background_loop(self) -> None:
        """后台同步循环"""
        # 首次启动延迟，让 MCP Server 初始化完成
        time.sleep(30)

        while True:
            try:
                updated = self._do_sync()
                self._save_state()

                if updated > 0:
                    with self._lock:
                        self._pending_update = True
                    logger.info(
                        f"🧵 后台同步发现 {updated} 个新药方，"
                        "将在下次搜索时重建索引"
                    )
            except Exception as e:
                logger.debug(f"后台同步异常: {e}")

            time.sleep(self.sync_interval)
