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
# 🏅 炼丹师称号体系（16 级）— 代理到 achievements 模块
# 已迁移到 achievements.py，此处保留兼容接口
# ============================================================


def calculate_title(contribution_count: int) -> tuple[str, str]:
    """
    根据贡献次数计算炼丹师称号（兼容接口）

    注意：新体系基于百分位而非固定阈值。此兼容函数
    使用简化的阈值映射来保持接口稳定。

    Returns:
        (emoji, title_text) — 如 ("⭐", "一星炼丹师 One-Star Alchemist")
    """
    # 简化映射：贡献数 → 近似称号
    _COMPAT_TIERS = [
        (50, "🩺", "华佗再世 Hua Tuo Reborn"),
        (30, "💎", "丹帝 Pill Emperor"),
        (20, "👑", "丹圣 Pill Saint"),
        (15, "⚡", "半圣 Half-Saint"),
        (10, "💜", "丹王 Pill King"),
        (7, "🏅", "小丹王 Junior Pill King"),
        (5, "🌟", "九星炼丹师 Nine-Star Alchemist"),
        (3, "⭐", "五星炼丹师 Five-Star Alchemist"),
        (1, "⭐", "一星炼丹师 One-Star Alchemist"),
    ]
    for threshold, emoji, title in _COMPAT_TIERS:
        if contribution_count >= threshold:
            return emoji, title
    return "🌱", "实习药童 Intern Apprentice"



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


def count_contributor_cases_by_framework(
    github_username: str,
    cases_dir: Path | None = None,
) -> dict[str, int]:
    """
    统计指定用户在各框架下的贡献数。

    Returns:
        dict[str, int] — 框架名→贡献数, e.g. {"langchain": 5, "pytorch": 3}
    """
    if cases_dir is None:
        cases_dir = config.CASES_DIR

    if not cases_dir.exists():
        return {}

    framework_counts: dict[str, int] = {}
    username_lower = github_username.lower()

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
            is_contributor = False
            if isinstance(contributors, list):
                for c in contributors:
                    gh = ""
                    if isinstance(c, dict):
                        gh = c.get("github", "")
                    elif isinstance(c, str):
                        gh = c
                    if gh.lower() == username_lower:
                        is_contributor = True
                        break

            if is_contributor:
                fw = meta.get("framework", "general")
                if isinstance(fw, str) and fw:
                    fw = fw.lower().strip()
                else:
                    fw = "general"
                framework_counts[fw] = framework_counts.get(fw, 0) + 1
        except Exception:
            continue

    return framework_counts


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

    async def create_prescription_issue(
        self,
        title: str,
        framework: str,
        prescription: str,
        symptom: str = "",
        error_message: str = "",
        root_cause: str = "",
        severity: str = "medium",
        complexity: str = "moderate",
        tags: list[str] | None = None,
        title_en: str = "",
        contributor_github: str = "anonymous",
    ) -> dict:
        """
        创建药方 Issue（瞬时药方层）
        Create a prescription Issue on GitHub (ephemeral prescription layer).

        任何拥有 GitHub 账号的用户都能在公开仓库上创建 Issue，
        无需仓库写权限。创建后即可被 MCP 搜索到。

        Any GitHub user can create an Issue on a public repo without
        write access. Once created, it is immediately searchable via MCP.
        """
        import json as _json

        # 构建结构化 Issue body（JSON + 人类可读摘要）
        structured_data = {
            "framework": framework,
            "title": title,
            "title_en": title_en,
            "symptom": symptom,
            "error_message": error_message,
            "root_cause": root_cause,
            "prescription": prescription,
            "severity": severity,
            "complexity": complexity,
            "tags": tags or [],
            "contributor_github": contributor_github,
        }

        # Issue body = 人类可读摘要 + 隐藏 JSON 块（供 CI 解析）
        body_parts = [
            f"## 💊 瞬时药方 Ephemeral Prescription\n",
            f"- **贡献者 Contributor**: @{contributor_github}",
            f"- **框架 Framework**: `{framework}`",
            f"- **严重性 Severity**: `{severity}`",
            f"- **复杂度 Complexity**: `{complexity}`\n",
        ]

        if symptom:
            body_parts.append(f"### 🏥 症状 Symptom\n\n{symptom}\n")
        if error_message:
            body_parts.append(f"### 🔍 错误信息 Error Message\n\n```\n{error_message}\n```\n")
        if root_cause:
            body_parts.append(f"### 🔬 根因分析 Root Cause\n\n{root_cause}\n")
        if prescription:
            body_parts.append(f"### 💊 药方 Prescription\n\n{prescription}\n")

        # 添加结构化 JSON（供 CI 自动晋升使用）
        body_parts.append(
            "---\n\n"
            "<details><summary>📋 Structured Data (for CI automation)</summary>\n\n"
            "```json\n"
            f"{_json.dumps(structured_data, ensure_ascii=False, indent=2)}\n"
            "```\n\n"
            "</details>\n\n"
            "*此 Issue 由 CyberHuaTuo MCP Server 自动创建 / "
            "Auto-created by CyberHuaTuo MCP Server*"
        )

        issue_body = "\n".join(body_parts)

        # 构建标签
        labels = ["prescription", f"framework:{framework}", f"severity:{severity}"]

        # Issue 标题
        issue_title = f"🩺 [{framework}] {title}"

        url = f"{self.API_BASE}/repos/{self.owner}/{self.repo}/issues"
        payload = {
            "title": issue_title,
            "body": issue_body,
            "labels": labels,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=self._headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "success": True,
                "method": "issue",
                "issue_number": data.get("number"),
                "issue_url": data.get("html_url", ""),
                "title": issue_title,
            }

        return {
            "success": False,
            "method": "issue",
            "status_code": resp.status_code,
            "error": resp.text[:500],
        }

    async def sync_prescription(
        self,
        relative_path: str,
        content: str,
        contributor_github: str = "anonymous",
        prescription_meta: dict | None = None,
    ) -> dict:
        """
        统一入口：自动选择推送策略（双层架构）
        Unified entry: auto-select sync strategy (dual-layer architecture).

        1. 先尝试直接推送（Owner/Collaborator）
        2. 推送失败（403/404）→ 创建 GitHub Issue（瞬时药方）

        Args:
            relative_path: cases/ 下的相对路径 / Relative path under cases/
            content: 文件内容 / File content
            contributor_github: 贡献者 GitHub 用户名 / Contributor GitHub username
            prescription_meta: 药方元数据（用于 Issue 创建） / Prescription metadata for Issue creation

        Returns:
            同步结果 dict / Sync result dict
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

        # 直推失败，创建 GitHub Issue（瞬时药方）
        if result.get("status_code") in (403, 404) and prescription_meta:
            logger.info("直推无权限，创建 GitHub Issue（瞬时药方模式）")
            return await self.create_prescription_issue(
                title=prescription_meta.get("title", ""),
                framework=prescription_meta.get("framework", "unknown"),
                prescription=prescription_meta.get("prescription", ""),
                symptom=prescription_meta.get("symptom", ""),
                error_message=prescription_meta.get("error_message", ""),
                root_cause=prescription_meta.get("root_cause", ""),
                severity=prescription_meta.get("severity", "medium"),
                complexity=prescription_meta.get("complexity", "moderate"),
                tags=prescription_meta.get("tags"),
                title_en=prescription_meta.get("title_en", ""),
                contributor_github=contributor_github,
            )

        # 无 prescription_meta 时回退到 Fork+PR（兼容老调用）
        if result.get("status_code") in (403, 404):
            logger.info("直推无权限，回退到 Fork + PR 模式")
            return await self.fork_and_pr(
                path=relative_path,
                content=content,
                message=commit_message,
                contributor_github=contributor_github,
            )

        return result


def get_global_ranking_stats(cases_dir: Path | None = None) -> dict[str, int]:
    """
    扫描 cases/ 目录，统计所有贡献者的贡献次数。
    返回 { "username_lower": count, ... }
    """
    if cases_dir is None:
        cases_dir = config.CASES_DIR

    if not cases_dir.exists():
        return {}

    stats = {}
    
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
                        gh_lower = gh.lower()
                        stats[gh_lower] = stats.get(gh_lower, 0) + 1
        except Exception:
            continue
            
    return stats


def get_contributor_summary(github_username: str) -> dict:
    """
    获取贡献者的完整统计摘要（兼容接口，代理到 achievements 模块）。

    Returns:
        dict 包含贡献次数、称号 emoji、称号名称、全球排行、总计炼丹师人数
    """
    from .achievements import get_cultivation_profile
    profile = get_cultivation_profile(github_username)
    return {
        "github": github_username,
        "contribution_count": profile["contribution_count"],
        "title_emoji": profile["title_emoji"],
        "title": f"{profile['title_cn']} {profile['title_en']}",
        "global_rank": profile["global_rank"],
        "global_total": profile["global_total"],
    }


def get_coronation_ascii(title_emoji: str, title: str, global_rank: int, global_total: int) -> str:
    """
    基于称号和全球排名生成加冕文案（兼容接口，代理到 achievements 模块）。
    """
    from .achievements import get_coronation_text
    
    percentile = 100.0
    if global_total > 1:
        percentile = round(((global_total - global_rank) / (global_total - 1)) * 100, 1)

    # 从 title 中提取中英文
    parts = title.split(" ", 1)
    title_cn = parts[0] if parts else title
    title_en = parts[1] if len(parts) > 1 else ""

    return get_coronation_text(
        emoji=title_emoji,
        title_cn=title_cn,
        title_en=title_en,
        rank=global_rank,
        total=global_total,
        percentile=percentile,
    )

