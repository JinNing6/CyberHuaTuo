"""
CyberHuaTuo GitHub Issues 淘金引擎
从 LangChain、CrewAI、AutoGen 等热门 AI Agent 项目的 Issues 中
搜索高频/高赞/高评论问题，利用 LLM 智能提炼为标准病例（药方）
"""

import asyncio
import json
import time
from dataclasses import dataclass, field

import httpx

from .config import config
from .contributor import CaseSubmission, generate_case_markdown, save_case_file

# ===== 目标仓库注册表 =====

@dataclass(frozen=True)
class TargetRepo:
    """目标淘金仓库"""
    owner: str
    repo: str
    framework: str
    description: str = ""


TARGET_REPOS: list[TargetRepo] = [
    TargetRepo("langchain-ai", "langchain", "langchain", "LLM 应用开发框架"),
    TargetRepo("crewAIInc", "crewAI", "crewai", "多 Agent 协作编排框架"),
    TargetRepo("microsoft", "autogen", "autogen", "微软多 Agent 对话框架"),
    TargetRepo("run-llama", "llama_index", "llamaindex", "数据驱动 RAG 框架"),
    TargetRepo("openai", "openai-python", "openai-sdk", "OpenAI 官方 Python SDK"),
    TargetRepo("stanfordnlp", "dspy", "dspy", "声明式 LLM 编程框架"),
    TargetRepo("deepset-ai", "haystack", "haystack", "端到端 NLP/LLM 框架"),
    TargetRepo("modelcontextprotocol", "python-sdk", "mcp", "Model Context Protocol SDK"),
    TargetRepo("pydantic", "pydantic-ai", "pydantic-ai", "基于 Pydantic 的 AI Agent 框架"),
    TargetRepo("langchain-ai", "langgraph", "langgraph", "LangChain 有状态 Agent 图引擎"),
]

# 快速查找字典
_REPO_BY_FRAMEWORK: dict[str, TargetRepo] = {r.framework: r for r in TARGET_REPOS}
_REPO_BY_KEY: dict[str, TargetRepo] = {f"{r.owner}/{r.repo}": r for r in TARGET_REPOS}


def get_target_repo(framework: str) -> TargetRepo | None:
    """根据框架 key 获取目标仓库"""
    return _REPO_BY_FRAMEWORK.get(framework)


def get_all_target_repos() -> list[dict[str, str]]:
    """获取所有目标仓库信息（用于 API/UI）"""
    return [
        {
            "owner": r.owner,
            "repo": r.repo,
            "framework": r.framework,
            "description": r.description,
            "full_name": f"{r.owner}/{r.repo}",
        }
        for r in TARGET_REPOS
    ]


# ===== Issue 数据结构 =====

@dataclass
class MinedIssue:
    """从 GitHub 挖掘到的 Issue"""
    number: int
    title: str
    body: str
    url: str
    owner: str
    repo: str
    framework: str
    state: str = "closed"
    labels: list[str] = field(default_factory=list)
    reactions_total: int = 0
    reactions_thumbs_up: int = 0
    comments_count: int = 0
    created_at: str = ""
    closed_at: str = ""
    top_comments: list[str] = field(default_factory=list)


@dataclass
class RefinedCase:
    """LLM 提炼后的标准病例"""
    title: str = ""
    title_en: str = ""
    error_message: str = ""
    symptom: str = ""
    root_cause: str = ""
    prescription: str = ""
    severity: str = "medium"
    complexity: str = "moderate"
    tags: list[str] = field(default_factory=list)
    source_url: str = ""
    framework: str = ""


# ===== GitHub API 客户端 =====

class GitHubClient:
    """GitHub REST API 客户端，内置速率限制处理"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token or config.GITHUB_TOKEN
        self._remaining: int = 5000
        self._reset_at: float = 0
        self._search_remaining: int = 30
        self._search_reset_at: float = 0

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _update_rate_limits(self, response: httpx.Response, is_search: bool = False):
        """从响应头更新速率限制信息"""
        if is_search:
            self._search_remaining = int(response.headers.get("x-ratelimit-remaining", 30))
            self._search_reset_at = float(response.headers.get("x-ratelimit-reset", 0))
        else:
            self._remaining = int(response.headers.get("x-ratelimit-remaining", 5000))
            self._reset_at = float(response.headers.get("x-ratelimit-reset", 0))

    async def _wait_if_limited(self, is_search: bool = False):
        """如果接近速率限制，等待重置"""
        remaining = self._search_remaining if is_search else self._remaining
        reset_at = self._search_reset_at if is_search else self._reset_at

        if remaining <= 1 and reset_at > 0:
            wait_seconds = max(0, reset_at - time.time()) + 1
            if wait_seconds > 0 and wait_seconds < 120:
                print(f"  ⏳ GitHub API 速率限制，等待 {wait_seconds:.0f}s ...")
                await asyncio.sleep(wait_seconds)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        is_search: bool = False,
        timeout: float = 30.0,
    ) -> dict | list | None:
        """发送 GitHub API 请求"""
        await self._wait_if_limited(is_search)

        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method, url,
                    params=params,
                    headers=self._headers(),
                )

                self._update_rate_limits(response, is_search)

                if response.status_code == 403:
                    retry_after = response.headers.get("retry-after")
                    if retry_after:
                        wait = int(retry_after)
                        print(f"  ⏳ 收到 403，等待 {wait}s 后重试 ...")
                        await asyncio.sleep(wait)
                        return await self._request(method, endpoint, params, is_search, timeout)
                    print(f"  ⚠️ GitHub API 403 Forbidden: {response.text[:200]}")
                    return None

                if response.status_code == 429:
                    retry_after = int(response.headers.get("retry-after", 60))
                    print(f"  ⏳ 收到 429 速率限制，等待 {retry_after}s ...")
                    await asyncio.sleep(retry_after)
                    return await self._request(method, endpoint, params, is_search, timeout)

                if response.status_code != 200:
                    print(f"  ⚠️ GitHub API 错误: HTTP {response.status_code}")
                    return None

                return response.json()

        except httpx.TimeoutException:
            print("  ⚠️ GitHub API 请求超时")
            return None
        except Exception as e:
            print(f"  ⚠️ GitHub API 请求失败: {e}")
            return None

    async def search_issues(
        self,
        owner: str,
        repo: str,
        sort: str = "reactions-+1",
        order: str = "desc",
        state: str = "closed",
        min_reactions: int | None = None,
        min_comments: int | None = None,
        labels: list[str] | None = None,
        per_page: int = 20,
        page: int = 1,
    ) -> dict | None:
        """
        搜索仓库的 Issues

        Args:
            owner: 仓库所有者
            repo: 仓库名
            sort: 排序方式 (reactions-+1 / comments / created / updated)
            order: 排序方向 (desc / asc)
            state: Issue 状态 (open / closed)
            min_reactions: 最低 reactions 数量
            min_comments: 最低 comments 数量
            labels: 标签过滤
            per_page: 每页数量
            page: 页码

        Returns:
            GitHub Search API 响应
        """
        # 构建查询字符串
        q_parts = [
            f"repo:{owner}/{repo}",
            "is:issue",
        ]

        if state:
            q_parts.append(f"is:{state}")

        if min_reactions is not None and min_reactions > 0:
            q_parts.append(f"reactions:>={min_reactions}")

        if min_comments is not None and min_comments > 0:
            q_parts.append(f"comments:>={min_comments}")

        if labels:
            for label in labels:
                q_parts.append(f'label:"{label}"')

        q = " ".join(q_parts)

        params = {
            "q": q,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }

        return await self._request("GET", "/search/issues", params=params, is_search=True)

    async def get_issue(self, owner: str, repo: str, number: int) -> dict | None:
        """获取单个 Issue 详情"""
        return await self._request("GET", f"/repos/{owner}/{repo}/issues/{number}")

    async def get_issue_comments(
        self,
        owner: str,
        repo: str,
        number: int,
        per_page: int = 10,
    ) -> list | None:
        """获取 Issue 的评论列表"""
        params = {
            "per_page": per_page,
            "sort": "created",
            "direction": "asc",
        }
        return await self._request("GET", f"/repos/{owner}/{repo}/issues/{number}/comments", params=params)

    def get_rate_info(self) -> dict:
        """获取当前速率限制信息"""
        return {
            "core_remaining": self._remaining,
            "search_remaining": self._search_remaining,
            "has_token": bool(self.token),
        }


# ===== 淘金引擎 =====

class IssueMiner:
    """GitHub Issues 淘金引擎"""

    def __init__(self, github_client: GitHubClient | None = None):
        self.github = github_client or GitHubClient()

    async def search_hot_issues(
        self,
        owner: str,
        repo: str,
        framework: str = "",
        sort: str = "reactions-+1",
        min_reactions: int | None = None,
        min_comments: int | None = None,
        limit: int = 10,
    ) -> list[MinedIssue]:
        """
        搜索仓库高频/高赞 Issues

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            framework: 框架标识
            sort: 排序方式
            min_reactions: 最低 reactions 数
            min_comments: 最低 comments 数
            limit: 返回数量上限

        Returns:
            MinedIssue 列表
        """
        min_reactions = min_reactions if min_reactions is not None else config.MINE_MIN_REACTIONS
        min_comments = min_comments if min_comments is not None else config.MINE_MIN_COMMENTS

        result = await self.github.search_issues(
            owner=owner,
            repo=repo,
            sort=sort,
            state="closed",
            min_reactions=min_reactions,
            min_comments=min_comments,
            per_page=min(limit, 30),
        )

        if not result or "items" not in result:
            return []

        issues = []
        for item in result["items"][:limit]:
            # 跳过 Pull Request
            if "pull_request" in item:
                continue

            reactions = item.get("reactions", {})
            reactions_total = reactions.get("total_count", 0) if isinstance(reactions, dict) else 0
            reactions_up = reactions.get("+1", 0) if isinstance(reactions, dict) else 0

            labels_list = [
                lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
                for lbl in item.get("labels", [])
            ]

            issues.append(MinedIssue(
                number=item.get("number", 0),
                title=item.get("title", ""),
                body=item.get("body", "") or "",
                url=item.get("html_url", ""),
                owner=owner,
                repo=repo,
                framework=framework,
                state=item.get("state", "closed"),
                labels=labels_list,
                reactions_total=reactions_total,
                reactions_thumbs_up=reactions_up,
                comments_count=item.get("comments", 0),
                created_at=item.get("created_at", ""),
                closed_at=item.get("closed_at", ""),
            ))

        return issues

    async def fetch_issue_with_comments(
        self,
        owner: str,
        repo: str,
        number: int,
        framework: str = "",
        max_comments: int = 8,
    ) -> MinedIssue | None:
        """
        获取 Issue 详情 + 精选评论

        Args:
            owner: 仓库所有者
            repo: 仓库名
            number: Issue 编号
            framework: 框架标识
            max_comments: 最多获取评论数

        Returns:
            包含评论的 MinedIssue
        """
        issue_data = await self.github.get_issue(owner, repo, number)
        if not issue_data:
            return None

        # 获取评论
        comments_data = await self.github.get_issue_comments(owner, repo, number, per_page=max_comments)
        top_comments = []
        if comments_data:
            for c in comments_data:
                body = c.get("body", "") or ""
                if len(body) > 30:  # 过滤太短的评论
                    # 截取前 1500 字符
                    top_comments.append(body[:1500])

        reactions = issue_data.get("reactions", {})
        reactions_total = reactions.get("total_count", 0) if isinstance(reactions, dict) else 0
        reactions_up = reactions.get("+1", 0) if isinstance(reactions, dict) else 0

        labels_list = [
            lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
            for lbl in issue_data.get("labels", [])
        ]

        return MinedIssue(
            number=issue_data.get("number", 0),
            title=issue_data.get("title", ""),
            body=(issue_data.get("body", "") or "")[:5000],
            url=issue_data.get("html_url", ""),
            owner=owner,
            repo=repo,
            framework=framework,
            state=issue_data.get("state", "closed"),
            labels=labels_list,
            reactions_total=reactions_total,
            reactions_thumbs_up=reactions_up,
            comments_count=issue_data.get("comments", 0),
            created_at=issue_data.get("created_at", ""),
            closed_at=issue_data.get("closed_at", ""),
            top_comments=top_comments,
        )

    async def refine_issue(self, issue: MinedIssue) -> RefinedCase | None:
        """
        用 LLM 将 Issue 提炼为标准病例格式

        Args:
            issue: 挖掘到的 Issue 数据

        Returns:
            提炼后的 RefinedCase，失败返回 None
        """
        if not config.has_llm_key():
            print("  ⚠️ 未配置 LLM API Key，无法提炼 Issue")
            return None

        # 构建提炼 Prompt
        comments_text = ""
        if issue.top_comments:
            comments_text = "\n\n---\n\n".join(
                f"### 评论 {i+1}\n{c}" for i, c in enumerate(issue.top_comments[:5])
            )

        prompt = f"""你是 CyberHuaTuo 药方提炼师。请将以下 GitHub Issue 提炼为标准病例格式。

## Issue 信息
- 标题: {issue.title}
- 仓库: {issue.owner}/{issue.repo}
- 框架: {issue.framework}
- 链接: {issue.url}
- Reactions: 👍 {issue.reactions_thumbs_up} / 总 {issue.reactions_total}
- 评论数: {issue.comments_count}
- 标签: {', '.join(issue.labels)}

## Issue 正文
{issue.body[:4000]}

## 精选评论（包含可能的解决方案）
{comments_text or "(无评论)"}

---

请提取并输出 **JSON 格式**（不要有 markdown 代码块包裹），包含以下字段：
- "title": 中文标题（精炼描述问题）
- "title_en": 英文标题
- "error_message": 关键报错信息（如果有，从 Issue 中提取原始错误消息）
- "symptom": 症状描述（用户遇到了什么问题，如何复现）
- "root_cause": 根因分析（为什么会出现这个问题）
- "prescription": 解决方案/药方（具体的修复步骤，代码示例用 markdown 代码块）
- "severity": "low" / "medium" / "high" / "critical"
- "complexity": "simple" / "moderate" / "complex" / "extreme"
- "tags": 标签列表（如 ["import-error", "breaking-change"]）

要求：
1. 药方要具体、可操作，最好有代码示例
2. 如果评论中有明确的解决方案，优先提取
3. tags 需要从这些类别中选择合适的: import-error, breaking-change, memory, performance, tool-calling, agent-behavior, authentication, configuration, retrieval, general
4. severity 根据影响范围判断：影响全部用户=critical，影响多数=high，影响部分=medium，边缘情况=low"""

        try:
            import litellm

            api_base = None
            model = config.DIAGNOSIS_MODEL
            if config.OLLAMA_BASE_URL and model.startswith("ollama/"):
                api_base = config.OLLAMA_BASE_URL

            response = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个精确的 JSON 数据提取机器人。只输出纯 JSON，不要有任何其他文字。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2000,
                api_base=api_base,
            )

            content = response.choices[0].message.content.strip()

            # 清理可能的 markdown 代码块包裹
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:])
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            data = json.loads(content)

            return RefinedCase(
                title=data.get("title", issue.title),
                title_en=data.get("title_en", issue.title),
                error_message=data.get("error_message", ""),
                symptom=data.get("symptom", ""),
                root_cause=data.get("root_cause", ""),
                prescription=data.get("prescription", ""),
                severity=data.get("severity", "medium"),
                complexity=data.get("complexity", "moderate"),
                tags=data.get("tags", []),
                source_url=issue.url,
                framework=issue.framework,
            )

        except json.JSONDecodeError as e:
            print(f"  ⚠️ LLM 输出解析失败: {e}")
            return None
        except ImportError:
            print("  ⚠️ 请安装 litellm: pip install litellm")
            return None
        except Exception as e:
            print(f"  ⚠️ LLM 调用失败: {e}")
            return None

    def save_refined_case(self, refined: RefinedCase) -> dict:
        """
        将提炼后的病例保存到 cases/ 目录

        Args:
            refined: 提炼后的 RefinedCase

        Returns:
            保存结果 dict
        """
        submission = CaseSubmission(
            framework=refined.framework,
            title=refined.title,
            title_en=refined.title_en,
            error_message=refined.error_message,
            symptom=refined.symptom,
            root_cause=refined.root_cause,
            prescription=refined.prescription,
            severity=refined.severity,
            complexity=refined.complexity,
            tags=refined.tags,
            source_url=refined.source_url,
            contributor_github="CyberHuaTuo-Miner",
        )

        return save_case_file(submission)

    def preview_refined_case(self, refined: RefinedCase) -> str:
        """
        预览提炼后的病例 markdown 内容（不保存）

        Args:
            refined: 提炼后的 RefinedCase

        Returns:
            Markdown 格式的病例内容
        """
        submission = CaseSubmission(
            framework=refined.framework,
            title=refined.title,
            title_en=refined.title_en,
            error_message=refined.error_message,
            symptom=refined.symptom,
            root_cause=refined.root_cause,
            prescription=refined.prescription,
            severity=refined.severity,
            complexity=refined.complexity,
            tags=refined.tags,
            source_url=refined.source_url,
            contributor_github="CyberHuaTuo-Miner",
        )

        return generate_case_markdown(submission)

    async def mine_single(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        framework: str = "",
        auto_save: bool = False,
    ) -> dict:
        """
        淘金单个 Issue：获取详情 → 提炼 → 可选保存

        Returns:
            结果 dict，包含 issue、refined、saved 字段
        """
        # 自动检测 framework
        if not framework:
            key = f"{owner}/{repo}"
            target = _REPO_BY_KEY.get(key)
            framework = target.framework if target else "other"

        # 获取 Issue + 评论
        print(f"  ⛏️ 获取 Issue #{issue_number} from {owner}/{repo} ...")
        issue = await self.fetch_issue_with_comments(owner, repo, issue_number, framework)
        if not issue:
            return {"error": f"无法获取 Issue #{issue_number}"}

        # LLM 提炼
        print(f"  🔬 提炼 Issue: {issue.title[:60]} ...")
        refined = await self.refine_issue(issue)
        if not refined:
            return {
                "issue": _issue_to_dict(issue),
                "error": "LLM 提炼失败",
            }

        result = {
            "issue": _issue_to_dict(issue),
            "refined": _refined_to_dict(refined),
            "preview": self.preview_refined_case(refined),
        }

        # 可选自动保存
        if auto_save:
            saved = self.save_refined_case(refined)
            result["saved"] = saved
            print(f"  💾 保存到: {saved['filepath']}")

        return result

    async def mine_repo(
        self,
        owner: str,
        repo: str,
        framework: str = "",
        sort: str = "reactions-+1",
        limit: int = 5,
        auto_save: bool = False,
    ) -> dict:
        """
        淘金整个仓库：搜索高频 Issues → 提炼 → 可选保存

        Returns:
            批量结果 dict
        """
        if not framework:
            key = f"{owner}/{repo}"
            target = _REPO_BY_KEY.get(key)
            framework = target.framework if target else "other"

        print(f"\n⛏️ 淘金 {owner}/{repo} (framework={framework}, limit={limit}) ...")

        issues = await self.search_hot_issues(
            owner=owner,
            repo=repo,
            framework=framework,
            sort=sort,
            limit=limit,
        )

        if not issues:
            return {"owner": owner, "repo": repo, "framework": framework, "results": [], "error": "未找到高频 Issues"}

        results = []
        for issue in issues:
            # 获取完整评论
            full_issue = await self.fetch_issue_with_comments(
                owner, repo, issue.number, framework, max_comments=5
            )
            if not full_issue:
                results.append({"issue_number": issue.number, "error": "获取详情失败"})
                continue

            # 提炼
            refined = await self.refine_issue(full_issue)
            if not refined:
                results.append({
                    "issue": _issue_to_dict(full_issue),
                    "error": "LLM 提炼失败",
                })
                continue

            entry = {
                "issue": _issue_to_dict(full_issue),
                "refined": _refined_to_dict(refined),
            }

            if auto_save:
                saved = self.save_refined_case(refined)
                entry["saved"] = saved
                print(f"  💾 #{full_issue.number} → {saved['filepath']}")

            results.append(entry)

            # 礼貌地间隔请求
            await asyncio.sleep(0.5)

        return {
            "owner": owner,
            "repo": repo,
            "framework": framework,
            "total_found": len(issues),
            "total_refined": len([r for r in results if "refined" in r]),
            "results": results,
        }


# ===== 序列化辅助函数 =====

def _issue_to_dict(issue: MinedIssue) -> dict:
    """将 MinedIssue 转为可 JSON 序列化的 dict"""
    return {
        "number": issue.number,
        "title": issue.title,
        "url": issue.url,
        "owner": issue.owner,
        "repo": issue.repo,
        "framework": issue.framework,
        "state": issue.state,
        "labels": issue.labels,
        "reactions_total": issue.reactions_total,
        "reactions_thumbs_up": issue.reactions_thumbs_up,
        "comments_count": issue.comments_count,
        "created_at": issue.created_at,
        "closed_at": issue.closed_at,
        "body_preview": issue.body[:300] if issue.body else "",
        "has_comments": len(issue.top_comments) > 0,
    }


def _refined_to_dict(refined: RefinedCase) -> dict:
    """将 RefinedCase 转为可 JSON 序列化的 dict"""
    return {
        "title": refined.title,
        "title_en": refined.title_en,
        "error_message": refined.error_message,
        "symptom": refined.symptom,
        "root_cause": refined.root_cause,
        "prescription": refined.prescription,
        "severity": refined.severity,
        "complexity": refined.complexity,
        "tags": refined.tags,
        "source_url": refined.source_url,
        "framework": refined.framework,
    }
