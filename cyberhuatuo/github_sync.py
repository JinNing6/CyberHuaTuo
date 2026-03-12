"""
CyberHuaTuo GitHub 同步模块
将药方自动推送到 GitHub 仓库，并追踪贡献者称号

支持两种策略：
  1. 直接推送（Owner / Collaborator）
  2. Fork + PR（外部贡献者）
"""

import base64
import logging
import re
from pathlib import Path

import httpx
import yaml

from .config import config

logger = logging.getLogger("cyberhuatuo.github_sync")

# ============================================================
# 🏅 名医堂称号体系（与 README.md 一致）
# ============================================================

TITLE_TIERS = [
    (20, "👑", "华佗再世 Hua Tuo Reborn"),
    (10, "🌟", "神医 Divine Doctor"),
    (5, "👨‍⚕️", "名医 Renowned Doctor"),
    (3, "⚕️", "主治医师 Attending Physician"),
    (1, "🏥", "坐堂医师 Resident Doctor"),
]


def calculate_title(contribution_count: int) -> tuple[str, str]:
    """
    根据贡献次数计算名医堂称号

    Returns:
        (emoji, title_text) — 如 ("⚕️", "主治医师 Attending Physician")
    """
    for threshold, emoji, title in TITLE_TIERS:
        if contribution_count >= threshold:
            return emoji, title
    return "🌱", "学徒 Apprentice"


def count_contributor_cases(
    github_username: str,
    cases_dir: Path | None = None,
) -> int:
    """
    扫描 cases/ 目录中所有 .md 文件的 YAML front matter，
    统计指定 GitHub 用户名作为 contributor 出现的次数。
    """
    if cases_dir is None:
        cases_dir = config.CASES_DIR

    if not cases_dir.exists():
        return 0

    count = 0
    username_lower = github_username.lower()

    for md_file in cases_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
            # 提取 YAML front matter
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
                    if gh.lower() == username_lower:
                        count += 1
                        break  # 同一个文件只计一次
        except Exception:
            continue

    return count


# ============================================================
# 🔄 GitHub API 同步客户端
# ============================================================


class GitHubSyncer:
    """GitHub 同步客户端 — 基于 httpx 调用 GitHub REST API"""

    API_BASE = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        owner: str | None = None,
        repo: str | None = None,
        branch: str | None = None,
    ):
        self.token = token or config.GITHUB_TOKEN
        self.owner = owner or config.GITHUB_SYNC_OWNER
        self.repo = repo or config.GITHUB_SYNC_REPO
        self.branch = branch or config.GITHUB_SYNC_BRANCH

    @property
    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def push_file(
        self,
        path: str,
        content: str,
        message: str,
        committer_name: str = "CyberHuaTuo Bot",
        committer_email: str = "bot@cyberhuatuo.dev",
    ) -> dict:
        """
        直接推送文件到仓库（需要 push 权限）

        Args:
            path: 仓库内文件路径 (如 cases/langchain/import-error/xxx.md)
            content: 文件内容（纯文本）
            message: commit message
            committer_name: 提交者名称
            committer_email: 提交者邮箱

        Returns:
            dict：包含 commit sha、html_url 等信息
        """
        url = f"{self.API_BASE}/repos/{self.owner}/{self.repo}/contents/{path}"

        # Base64 编码内容
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")

        # 先检查文件是否已存在（获取 sha 用于更新）
        sha = None
        async with httpx.AsyncClient(timeout=30) as client:
            check_resp = await client.get(url, headers=self._headers)
            if check_resp.status_code == 200:
                existing = check_resp.json()
                sha = existing.get("sha")

            # 构建请求体
            body: dict = {
                "message": message,
                "content": content_b64,
                "branch": self.branch,
                "committer": {
                    "name": committer_name,
                    "email": committer_email,
                },
            }
            if sha:
                body["sha"] = sha

            resp = await client.put(url, json=body, headers=self._headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            commit_info = data.get("commit", {})
            return {
                "success": True,
                "method": "direct_push",
                "commit_sha": commit_info.get("sha", "")[:7],
                "html_url": data.get("content", {}).get("html_url", ""),
                "message": message,
            }

        # 403 / 404 → 无推送权限
        if resp.status_code in (403, 404):
            return {
                "success": False,
                "method": "direct_push",
                "status_code": resp.status_code,
                "error": "No push access",
            }

        return {
            "success": False,
            "method": "direct_push",
            "status_code": resp.status_code,
            "error": resp.text[:500],
        }

    async def fork_and_pr(
        self,
        path: str,
        content: str,
        message: str,
        contributor_github: str = "anonymous",
    ) -> dict:
        """
        Fork 仓库 → 创建分支 → 提交文件 → 创建 PR

        Args:
            path: 仓库内文件路径
            content: 文件内容
            message: commit message
            contributor_github: 贡献者 GitHub 用户名

        Returns:
            dict：包含 PR url 等信息
        """
        async with httpx.AsyncClient(timeout=30) as client:
            # 1. Fork 仓库（如果已 fork，API 返回已存在的 fork）
            fork_url = f"{self.API_BASE}/repos/{self.owner}/{self.repo}/forks"
            fork_resp = await client.post(fork_url, headers=self._headers)

            if fork_resp.status_code not in (200, 202):
                return {
                    "success": False,
                    "method": "fork_pr",
                    "error": f"Fork failed: {fork_resp.status_code} {fork_resp.text[:300]}",
                }

            fork_data = fork_resp.json()
            fork_owner = fork_data.get("owner", {}).get("login", "")

            if not fork_owner:
                return {
                    "success": False,
                    "method": "fork_pr",
                    "error": "Cannot determine fork owner",
                }

            # 2. 获取 main 分支的最新 commit SHA
            ref_url = f"{self.API_BASE}/repos/{fork_owner}/{self.repo}/git/ref/heads/{self.branch}"
            ref_resp = await client.get(ref_url, headers=self._headers)

            if ref_resp.status_code != 200:
                return {
                    "success": False,
                    "method": "fork_pr",
                    "error": f"Cannot get branch ref: {ref_resp.status_code}",
                }

            base_sha = ref_resp.json()["object"]["sha"]

            # 3. 创建新分支
            branch_name = f"prescription/{path.replace('/', '-')}"
            # 截断避免分支名过长
            if len(branch_name) > 100:
                branch_name = branch_name[:100]

            create_ref_url = f"{self.API_BASE}/repos/{fork_owner}/{self.repo}/git/refs"
            create_ref_body = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
            branch_resp = await client.post(
                create_ref_url, json=create_ref_body, headers=self._headers
            )

            # 422 = 分支已存在，可以继续
            if branch_resp.status_code not in (200, 201, 422):
                return {
                    "success": False,
                    "method": "fork_pr",
                    "error": f"Cannot create branch: {branch_resp.status_code}",
                }

            # 4. 推送文件到 fork 的新分支
            content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
            file_url = f"{self.API_BASE}/repos/{fork_owner}/{self.repo}/contents/{path}"

            file_body: dict = {
                "message": message,
                "content": content_b64,
                "branch": branch_name,
            }
            file_resp = await client.put(file_url, json=file_body, headers=self._headers)

            if file_resp.status_code not in (200, 201):
                return {
                    "success": False,
                    "method": "fork_pr",
                    "error": f"Cannot push file: {file_resp.status_code}",
                }

            # 5. 创建 PR
            pr_url = f"{self.API_BASE}/repos/{self.owner}/{self.repo}/pulls"
            pr_body = {
                "title": f"🩺 药方贡献: {message}",
                "body": (
                    f"## 💊 新药方贡献\n\n"
                    f"- **贡献者**: @{contributor_github}\n"
                    f"- **文件路径**: `{path}`\n\n"
                    f"---\n\n"
                    f"*此 PR 由 CyberHuaTuo MCP Server 自动创建*"
                ),
                "head": f"{fork_owner}:{branch_name}",
                "base": self.branch,
            }
            pr_resp = await client.post(pr_url, json=pr_body, headers=self._headers)

            if pr_resp.status_code in (200, 201):
                pr_data = pr_resp.json()
                return {
                    "success": True,
                    "method": "fork_pr",
                    "pr_number": pr_data.get("number"),
                    "pr_url": pr_data.get("html_url", ""),
                    "message": message,
                }

            return {
                "success": False,
                "method": "fork_pr",
                "error": f"Cannot create PR: {pr_resp.status_code} {pr_resp.text[:300]}",
            }

    async def sync_prescription(
        self,
        relative_path: str,
        content: str,
        contributor_github: str = "anonymous",
    ) -> dict:
        """
        统一入口：自动选择推送策略

        1. 先尝试直接推送
        2. 推送失败（403/404）则自动 Fork + PR

        Args:
            relative_path: cases/ 下的相对路径
            content: 文件内容
            contributor_github: 贡献者 GitHub 用户名

        Returns:
            同步结果 dict
        """
        if not self.token:
            return {
                "success": False,
                "method": "none",
                "error": "未配置 GITHUB_TOKEN，无法同步到 GitHub",
            }

        commit_message = f"💊 新药方: {relative_path.split('/')[-1].replace('.md', '')}"

        # 尝试直接推送
        logger.info(f"尝试直接推送: {relative_path}")
        result = await self.push_file(
            path=relative_path,
            content=content,
            message=commit_message,
        )

        if result["success"]:
            logger.info(f"✅ 直接推送成功: {result.get('commit_sha')}")
            return result

        # 直推失败，尝试 Fork + PR
        if result.get("status_code") in (403, 404):
            logger.info("直推无权限，尝试 Fork + PR 模式")
            return await self.fork_and_pr(
                path=relative_path,
                content=content,
                message=commit_message,
                contributor_github=contributor_github,
            )

        return result


def get_contributor_summary(github_username: str) -> dict:
    """
    获取贡献者的完整统计摘要

    Returns:
        dict 包含贡献次数、称号 emoji、称号名称
    """
    count = count_contributor_cases(github_username)
    emoji, title = calculate_title(count)
    return {
        "github": github_username,
        "contribution_count": count,
        "title_emoji": emoji,
        "title": title,
    }
