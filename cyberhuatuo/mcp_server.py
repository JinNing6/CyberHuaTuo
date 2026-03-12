"""
CyberHuaTuo MCP Server — 赛博华佗 MCP 服务
让所有 AI Coding 工具都能调用「望闻问切」诊断能力

启动方式：
    python -m cyberhuatuo.mcp_server
    或通过 MCP 客户端配置自动启动（stdio 传输）
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from .config import config
from .doc_sources import (
    ALL_FRAMEWORKS,
    get_frameworks_by_category,
    search_frameworks,
)
from .indexer import build_index, scan_cases
from .searcher import SearchResult, search_cases, search_ephemeral_issues
from .contributor import CaseSubmission, save_case_file
from .github_sync import (
    GitHubSyncer,
    calculate_title,
    count_contributor_cases,
    get_contributor_summary,
)
from .banner import play_boot_animation

logger = logging.getLogger("cyberhuatuo.mcp")

# ============================================================
# 🩺 初始化 MCP Server
# ============================================================

mcp = FastMCP(
    "cyberhuatuo",
    instructions=(
        "赛博华佗（CyberHuaTuo）— AI 技术问题诊断知识库 MCP Server。"
        "提供望闻问切诊断、病例搜索、Agent 代码安全体检、"
        "官方文档检索、GitHub Issue 淘金等能力。"
    ),
)

# ===== ChromaDB 懒加载 =====
_chroma_client = None


def _get_chroma_client():
    """懒加载 ChromaDB 客户端，首次调用时构建索引"""
    global _chroma_client
    if _chroma_client is None:
        logger.info("🩺 首次加载，构建知识库索引...")
        _chroma_client, count = build_index()
        logger.info(f"✅ 索引就绪，共 {count} 个病例")
    return _chroma_client


# ============================================================
# 🔧 Tools — 六大诊断工具
# ============================================================


@mcp.tool()
async def diagnose(
    query: str,
    framework: str | None = None,
    top_k: int = 5,
) -> str:
    """
    🩺 望闻问切 AI 诊断
    Diagnose AI/Agent issues using CyberHuaTuo's knowledge base and LLM.

    输入你遇到的报错信息或问题描述，赛博华佗将根据知识库中的病例
    和最新官方文档，使用「望闻问切」方法给出精准诊断和药方。

    Paste your error message or problem description. CyberHuaTuo will
    diagnose it using its knowledge base of real-world cases and the
    latest official docs, then prescribe a targeted fix.

    Args:
        query: 报错信息或问题描述 / Error message or problem description
        framework: 按框架过滤（如 langchain, crewai） / Filter by framework
        top_k: 返回的参考病例数量，默认 5 / Number of reference cases, default 5
    """
    client = _get_chroma_client()

    # 1. 常驻药方：向量搜索
    results = search_cases(
        client=client,
        query=query,
        framework=framework,
        top_k=top_k,
        include_content=True,
    )

    # 2. 瞬时药方：GitHub Issues 搜索
    try:
        ephemeral = await search_ephemeral_issues(
            query=query, framework=framework, top_k=3,
        )
        results.extend(ephemeral)
    except Exception as e:
        logger.debug(f"瞬时药方搜索跳过: {e}")

    # 3. 尝试 LLM 诊断
    try:
        from .diagnosis import diagnose as llm_diagnose

        diagnosis_result = await llm_diagnose(query=query, results=results)
        return diagnosis_result
    except Exception as e:
        # LLM 不可用时回退到纯搜索结果
        logger.warning(f"LLM 诊断不可用，回退到纯搜索: {e}")
        return _format_search_results(query, results)


@mcp.tool()
async def search_knowledge_base(
    query: str,
    framework: str | None = None,
    severity: str | None = None,
    complexity: str | None = None,
    top_k: int = 5,
) -> str:
    """
    🔍 在赛博华佗知识库中搜索病例
    Search CyberHuaTuo's knowledge base for relevant cases.

    使用向量语义搜索匹配最相关的病例（药方），无需 LLM API Key 即可使用。
    返回病例标题、框架、严重性、相关度和完整内容。

    Perform semantic vector search across the case library (no LLM API Key required).
    Returns case title, framework, severity, relevance score, and full content.

    Args:
        query: 搜索查询（错误信息/问题描述） / Search query (error message / problem description)
        framework: 按框架过滤 / Filter by framework (e.g. langchain, pytorch)
        severity: 按严重性过滤 / Filter by severity (low / medium / high / critical)
        complexity: 按复杂度过滤 / Filter by complexity (simple / moderate / complex / extreme)
        top_k: 返回结果数量，默认 5 / Number of results, default 5
    """
    client = _get_chroma_client()

    # 常驻药方：ChromaDB 向量搜索
    results = search_cases(
        client=client,
        query=query,
        framework=framework,
        severity=severity,
        complexity=complexity,
        top_k=top_k,
        include_content=True,
    )

    # 瞬时药方：GitHub Issues 搜索
    try:
        ephemeral = await search_ephemeral_issues(
            query=query, framework=framework, severity=severity, top_k=3,
        )
        results.extend(ephemeral)
    except Exception as e:
        logger.debug(f"瞬时药方搜索跳过: {e}")

    return _format_search_results(query, results)


@mcp.tool()
async def security_checkup(code: str) -> str:
    """
    🛡️ AI Agent 代码安全体检
    Perform a security health check on AI agent code.

    对 AI Agent 代码进行六经脉安全体检，检测沙箱隔离、密钥安全、
    Prompt 安全、输出安全、韧性设计、可观测性等六大维度，
    输出健康评分和滋补建议。需要 LLM API Key。

    Run a Six-Meridian security audit covering sandbox isolation,
    secret management, prompt safety, output safety, resilience design,
    and observability. Outputs a health score and remediation advice.
    Requires an LLM API Key.

    Args:
        code: 要进行安全体检的代码内容 / The code to audit
    """
    try:
        from .nourishing import security_checkup as do_checkup

        result = await do_checkup(code=code)

        if "error" in result and result.get("health_score", 0) == -1:
            return f"⚠️ 安全体检失败: {result['error']}"

        # 格式化输出
        output_parts = [
            "# 🩺 赛博华佗安全体检报告",
            "",
            f"**健康评分**: {result.get('health_score', 'N/A')} / 100",
            f"**健康等级**: {result.get('level', 'N/A')}",
            "",
        ]

        # 各维度评分
        dimensions = result.get("dimensions", [])
        if dimensions:
            output_parts.append("## 六经脉评分")
            output_parts.append("")
            for dim in dimensions:
                emoji = dim.get("emoji", "📊")
                name = dim.get("name", "")
                score = dim.get("score", "N/A")
                status = dim.get("status", "")
                output_parts.append(f"- {emoji} **{name}**: {score}/100 ({status})")
                findings = dim.get("findings", [])
                for f in findings:
                    output_parts.append(f"  - {f}")
                advice = dim.get("advice", "")
                if advice:
                    output_parts.append(f"  - 💊 建议: {advice}")
            output_parts.append("")

        # 紧急问题
        top_issues = result.get("top_issues", [])
        if top_issues:
            output_parts.append("## ⚠️ 最紧急的问题")
            output_parts.append("")
            for i, issue in enumerate(top_issues, 1):
                output_parts.append(f"{i}. {issue}")
            output_parts.append("")

        # 总结
        summary = result.get("summary", "")
        if summary:
            output_parts.append(f"## 总结\n\n{summary}")

        return "\n".join(output_parts)

    except ImportError:
        return "⚠️ 请安装 litellm: `pip install litellm`"
    except Exception as e:
        return f"⚠️ 安全体检失败: {str(e)}"


@mcp.tool()
async def fetch_official_docs(
    framework: str,
    query: str,
    top_k: int = 5,
) -> str:
    """
    📚 获取框架最新官方技术文档
    Fetch latest official documentation for a framework via Context7.

    通过 Context7 API 获取指定框架的最新官方文档片段，
    支持 50+ 主流框架（LangChain、PyTorch、FastAPI、React 等）。

    Retrieve the latest official documentation snippets for a framework
    via the Context7 API. Supports 50+ mainstream frameworks including
    LangChain, PyTorch, FastAPI, React, and more.

    Args:
        framework: 框架标识 / Framework identifier (e.g. langchain, pytorch, fastapi)
        query: 查询的具体问题 / Specific question (e.g. "How to configure RAG pipeline")
        top_k: 返回文档片段数量，默认 5 / Number of doc snippets, default 5
    """
    try:
        from .doc_fetcher import smart_fetch

        snippets = await smart_fetch(
            framework_name=framework,
            query=query,
            top_k=top_k,
        )

        if not snippets:
            return f"未找到 {framework} 的相关官方文档。请检查框架名称是否正确，或使用 list_frameworks 查看支持的框架列表。"

        output_parts = [f"# 📚 {framework} 官方文档检索结果\n"]

        for i, s in enumerate(snippets, 1):
            output_parts.append(f"## 文档 {i}: {s.title}")
            if s.source:
                output_parts.append(f"*来源: {s.source}*\n")
            output_parts.append(s.content)
            output_parts.append("\n---\n")

        return "\n".join(output_parts)

    except Exception as e:
        return f"⚠️ 文档检索失败: {str(e)}"


@mcp.tool()
async def mine_github_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> str:
    """
    ⛏️ GitHub Issue 淘金提炼
    Mine and refine a GitHub Issue into a standardized case/prescription.

    从 GitHub Issue 中提取问题和解决方案，使用 LLM 将其提炼为
    CyberHuaTuo 标准病例格式（含症状、根因、药方）。
    需要 LLM API Key，可选配置 GITHUB_TOKEN 提升限额。

    Extract problems and solutions from a GitHub Issue and use an LLM
    to refine them into the CyberHuaTuo standard case format (symptoms,
    root cause, prescription). Requires an LLM API Key; optionally
    configure GITHUB_TOKEN for higher rate limits.

    Args:
        owner: 仓库所有者 / Repository owner (e.g. langchain-ai)
        repo: 仓库名称 / Repository name (e.g. langchain)
        issue_number: Issue 编号 / Issue number
    """
    try:
        from .issue_miner import IssueMiner

        miner = IssueMiner()
        result = await miner.mine_single(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            auto_save=False,
        )

        if "error" in result and "issue" not in result:
            return f"⚠️ {result['error']}"

        output_parts = ["# ⛏️ GitHub Issue 淘金结果\n"]

        # Issue 信息
        issue = result.get("issue", {})
        if issue:
            output_parts.append("## 原始 Issue")
            output_parts.append(f"- **标题**: {issue.get('title', 'N/A')}")
            output_parts.append(f"- **链接**: {issue.get('url', 'N/A')}")
            output_parts.append(f"- **👍 Reactions**: {issue.get('reactions_thumbs_up', 0)}")
            output_parts.append(f"- **💬 评论数**: {issue.get('comments_count', 0)}")
            output_parts.append(f"- **标签**: {', '.join(issue.get('labels', []))}")
            output_parts.append("")

        # 提炼结果
        refined = result.get("refined", {})
        if refined:
            output_parts.append("## 提炼后的病例")
            output_parts.append(f"- **标题**: {refined.get('title', 'N/A')}")
            output_parts.append(f"- **标题(EN)**: {refined.get('title_en', 'N/A')}")
            output_parts.append(f"- **严重性**: {refined.get('severity', 'N/A')}")
            output_parts.append(f"- **复杂度**: {refined.get('complexity', 'N/A')}")
            output_parts.append(f"- **标签**: {', '.join(refined.get('tags', []))}")
            output_parts.append("")

            if refined.get("symptom"):
                output_parts.append(f"### 🏥 症状\n{refined['symptom']}\n")
            if refined.get("error_message"):
                output_parts.append(f"### 🔍 错误信息\n```\n{refined['error_message']}\n```\n")
            if refined.get("root_cause"):
                output_parts.append(f"### 🔬 根因分析\n{refined['root_cause']}\n")
            if refined.get("prescription"):
                output_parts.append(f"### 💊 药方\n{refined['prescription']}\n")

        elif "error" in result:
            output_parts.append(f"\n⚠️ LLM 提炼失败: {result['error']}")

        return "\n".join(output_parts)

    except Exception as e:
        return f"⚠️ Issue 淘金失败: {str(e)}"


@mcp.tool()
async def save_prescription(
    title: str,
    prescription: str,
    framework: str,
    symptom: str = "",
    error_message: str = "",
    root_cause: str = "",
    severity: str = "medium",
    complexity: str = "moderate",
    tags: list[str] = None,
    title_en: str = "",
    framework_version: str = "",
    language: str = "python",
    contributor_github: str = "anonymous",
    source_url: str = "",
) -> str:
    """
    📥 保存贡献的药方（病例）到知识库
    Save a contributed prescription (case) to the CyberHuaTuo knowledge base.

    将新发现的问题和对应的解决方案保存为标准 Markdown 病例文件，
    保存后会自动分类并存入对应的知识库目录中。

    Save a newly discovered problem and its solution as a standard
    Markdown case file. The case is auto-categorized and stored in
    the corresponding knowledge base directory.

    Args:
        title: 问题标题，建议 20 字内 / Case title (keep under 20 chars)
        prescription: 详细修复方案 (Markdown) / Detailed fix (Markdown)
        framework: 框架标识 / Framework identifier (e.g. langchain, pytorch)
        symptom: 症状详细描述 / Detailed symptom description
        error_message: 纯报错日志或 Traceback / Raw error log or traceback
        root_cause: 根本原因分析 / Root cause analysis
        severity: 严重性 / Severity (low / medium / high / critical)
        complexity: 复杂度 / Complexity (simple / moderate / complex / extreme)
        tags: 标签数组 / Tag array
        title_en: 英文标题 / English title
        framework_version: 框架版本 / Framework version
        language: 编程语言 / Programming language (e.g. python, typescript)
        contributor_github: 贡献者 GitHub 用户名 / Contributor GitHub username
        source_url: 参考链接 / Reference URL
    """
    try:
        if tags is None:
            tags = []

        submission = CaseSubmission(
            title=title,
            prescription=prescription,
            framework=framework,
            symptom=symptom,
            error_message=error_message,
            root_cause=root_cause,
            severity=severity,
            complexity=complexity,
            tags=tags,
            title_en=title_en,
            framework_version=framework_version,
            language=language,
            contributor_github=contributor_github,
            source_url=source_url,
        )

        result = save_case_file(submission)

        # 获取现有的客户端判断是否需要强制触发一次重新索引
        global _chroma_client
        if _chroma_client is not None:
            _chroma_client = None
            logger.info("✅ 新药方已落盘，已清除 ChromaDB 实例缓存以便下次重载索引。")

        output_parts = [
            "✅ 药方保存成功！\n",
            f"- **病例 ID**: {result['case_id']}",
            f"- **保存路径**: {result['filepath']}",
        ]

        # GitHub 同步（双层架构：直推成功→常驻主任专家 / 直推失败→创建 Issue 临时医学实习生药方）
        sync_status = "⏭️ 未启用（GITHUB_SYNC_ENABLED=false 或未配置 GITHUB_TOKEN）"
        if config.GITHUB_SYNC_ENABLED and config.GITHUB_TOKEN:
            try:
                syncer = GitHubSyncer()
                content_preview = result.get("content_preview", "")
                # 读取完整文件内容
                abs_path = result.get("absolute_path", "")
                if abs_path:
                    from pathlib import Path

                    full_content = Path(abs_path).read_text(encoding="utf-8")
                else:
                    full_content = content_preview

                # 构建药方元数据（用于 Issue 创建）
                prescription_meta = {
                    "title": title,
                    "title_en": title_en,
                    "framework": framework,
                    "prescription": prescription,
                    "symptom": symptom,
                    "error_message": error_message,
                    "root_cause": root_cause,
                    "severity": severity,
                    "complexity": complexity,
                    "tags": tags,
                }

                sync_result = await _run_sync(
                    syncer, result["filepath"], full_content, contributor_github,
                    prescription_meta=prescription_meta,
                )

                if sync_result["success"]:
                    method = sync_result["method"]
                    if method == "direct_push":
                        commit_sha = sync_result.get("commit_sha", "")
                        sync_status = f"✅ 已推送到 {config.GITHUB_SYNC_OWNER}/{config.GITHUB_SYNC_REPO} (commit: {commit_sha})"
                    elif method == "issue":
                        issue_url = sync_result.get("issue_url", "")
                        sync_status = f"✅ 已创建瞬时药方 Issue: {issue_url}（CI 审核通过后自动晋升为常驻药方）"
                    elif method == "fork_pr":
                        pr_url = sync_result.get("pr_url", "")
                        sync_status = f"✅ 已创建 PR: {pr_url}"
                else:
                    sync_status = f"⚠️ 同步失败: {sync_result.get('error', '未知错误')}"
            except Exception as e:
                sync_status = f"⚠️ 同步异常: {str(e)}"
                logger.warning(f"GitHub 同步异常: {e}", exc_info=True)

        output_parts.append(f"- **GitHub 同步**: {sync_status}")

        # 贡献者称号
        if contributor_github and contributor_github != "anonymous":
            summary = get_contributor_summary(contributor_github)
            output_parts.append(
                f"- **贡献者称号**: {summary['title_emoji']} {summary['title']} "
                f"(累计 {summary['contribution_count']} 次贡献)"
            )

        output_parts.append(
            "\n💡 **温馨提示**: 系统缓存已标记过期，将在您下次诊断时自动重新构建最新知识库索引。"
        )

        return "\n".join(output_parts)

    except Exception as e:
        logger.error(f"保存药方失败: {e}", exc_info=True)
        return f"⚠️ 药方保存失败: {str(e)}"


@mcp.tool()
async def upload_prescription(
    title: str,
    prescription: str,
    framework: str,
    symptom: str = "",
    error_message: str = "",
    root_cause: str = "",
    severity: str = "medium",
    complexity: str = "moderate",
    tags: list[str] = None,
    title_en: str = "",
    framework_version: str = "",
    language: str = "python",
    contributor_github: str = "anonymous",
    source_url: str = "",
) -> str:
    """
    🌐 上传药方到 GitHub 知识库（必须配置 GITHUB_TOKEN）
    Upload a prescription directly to the CyberHuaTuo GitHub repository.

    与 save_prescription 类似，但此工具**强制要求**同步到 GitHub，
    适合外部贡献者通过 MCP 直接向社区贡献药方。
    自动创建 PR 并在返回中显示贡献者称号。
    需要在环境变量中配置 GITHUB_TOKEN。

    Similar to save_prescription, but **mandates** GitHub sync.
    Ideal for external contributors to submit prescriptions to the
    community via MCP. Automatically creates a PR and shows the
    contributor's Hall of Divine Doctors title.
    Requires GITHUB_TOKEN in environment variables.

    Args:
        title: 问题标题，建议 20 字内 / Case title (keep under 20 chars)
        prescription: 详细修复方案 (Markdown) / Detailed fix (Markdown)
        framework: 框架标识 / Framework identifier (e.g. langchain, pytorch)
        symptom: 症状详细描述 / Detailed symptom description
        error_message: 纯报错日志或 Traceback / Raw error log or traceback
        root_cause: 根本原因分析 / Root cause analysis
        severity: 严重性 / Severity (low / medium / high / critical)
        complexity: 复杂度 / Complexity (simple / moderate / complex / extreme)
        tags: 标签数组 / Tag array
        title_en: 英文标题 / English title
        framework_version: 框架版本 / Framework version
        language: 编程语言 / Programming language (e.g. python, typescript)
        contributor_github: 贡献者 GitHub 用户名 / Contributor GitHub username
        source_url: 参考链接 / Reference URL
    """
    if not config.GITHUB_TOKEN:
        return (
            "⚠️ 上传失败：未配置 GITHUB_TOKEN。\n\n"
            "请在环境变量或 `.env` 文件中配置：\n"
            "```\nGITHUB_TOKEN=ghp_your-token-here\n```\n\n"
            "💡 如果只想保存到本地，请使用 `save_prescription` 工具。"
        )

    # 保存到本地 + 同步到 GitHub（复用 save_prescription 逻辑）
    try:
        if tags is None:
            tags = []

        submission = CaseSubmission(
            title=title,
            prescription=prescription,
            framework=framework,
            symptom=symptom,
            error_message=error_message,
            root_cause=root_cause,
            severity=severity,
            complexity=complexity,
            tags=tags,
            title_en=title_en,
            framework_version=framework_version,
            language=language,
            contributor_github=contributor_github,
            source_url=source_url,
        )

        result = save_case_file(submission)

        # 清除缓存
        global _chroma_client
        if _chroma_client is not None:
            _chroma_client = None

        # 必须同步到 GitHub（双层架构）
        from pathlib import Path

        abs_path = result.get("absolute_path", "")
        full_content = Path(abs_path).read_text(encoding="utf-8") if abs_path else ""

        # 构建药方元数据
        prescription_meta = {
            "title": title,
            "title_en": title_en,
            "framework": framework,
            "prescription": prescription,
            "symptom": symptom,
            "error_message": error_message,
            "root_cause": root_cause,
            "severity": severity,
            "complexity": complexity,
            "tags": tags,
        }

        syncer = GitHubSyncer()
        sync_result = await _run_sync(
            syncer, result["filepath"], full_content, contributor_github,
            prescription_meta=prescription_meta,
        )

        output_parts = [
            "# 🌐 药方上传结果\n",
            f"- **病例 ID**: {result['case_id']}",
            f"- **本地路径**: {result['filepath']}",
        ]

        if sync_result["success"]:
            method = sync_result["method"]
            if method == "direct_push":
                commit_sha = sync_result.get("commit_sha", "")
                output_parts.append(
                    f"- **GitHub**: ✅ 已推送为常驻药方 (commit: {commit_sha})"
                )
            elif method == "issue":
                issue_url = sync_result.get("issue_url", "")
                output_parts.append(
                    f"- **GitHub**: ✅ 已创建瞬时药方 Issue: {issue_url}\n"
                    f"  CI 审核通过后将自动晋升为常驻药方"
                )
            elif method == "fork_pr":
                pr_url = sync_result.get("pr_url", "")
                output_parts.append(f"- **GitHub**: ✅ 已创建 PR: {pr_url}")
        else:
            output_parts.append(
                f"- **GitHub**: ⚠️ 同步失败: {sync_result.get('error', '未知错误')}"
            )

        # 贡献者称号
        if contributor_github and contributor_github != "anonymous":
            summary = get_contributor_summary(contributor_github)
            output_parts.append(
                f"\n### 🏅 名医堂称号\n"
                f"- **贡献者**: @{contributor_github}\n"
                f"- **称号**: {summary['title_emoji']} {summary['title']}\n"
                f"- **累计贡献**: {summary['contribution_count']} 次"
            )

        return "\n".join(output_parts)

    except Exception as e:
        logger.error(f"上传药方失败: {e}", exc_info=True)
        return f"⚠️ 上传药方失败: {str(e)}"


@mcp.tool()
def my_contribution_stats(
    github_username: str,
) -> str:
    """
    🏅 查询贡献者的名医堂称号和贡献统计
    Check a contributor's Hall of Divine Doctors title and contribution stats.

    查询指定 GitHub 用户在赛博华佗知识库中的贡献次数和当前称号。
    称号体系：学徒 → 坐堂医师 → 主治医师 → 名医 → 神医 → 华佗再世。

    Look up a GitHub user's contribution count and current title in the
    CyberHuaTuo knowledge base. Title ladder: Apprentice → Resident Doctor
    → Attending Physician → Renowned Doctor → Divine Doctor → Hua Tuo Reborn.

    Args:
        github_username: GitHub 用户名 / GitHub username
    """
    summary = get_contributor_summary(github_username)
    count = summary["contribution_count"]
    emoji = summary["title_emoji"]
    title = summary["title"]

    output_parts = [
        "# 🏅 名医堂 · 贡献者档案\n",
        f"**贡献者**: @{github_username}",
        f"**当前称号**: {emoji} {title}",
        f"**累计贡献**: {count} 个药方\n",
        "---\n",
        "### 📊 称号体系",
        "",
        "| 称号 | 条件 | 状态 |",
        "|:---:|:---:|:---:|",
    ]

    # 标记当前等级
    tiers_display = [
        (1, "🏥", "坐堂医师 Resident Doctor"),
        (3, "⚕️", "主治医师 Attending Physician"),
        (5, "👨‍⚕️", "名医 Renowned Doctor"),
        (10, "🌟", "神医 Divine Doctor"),
        (20, "👑", "华佗再世 Hua Tuo Reborn"),
    ]

    for threshold, tier_emoji, tier_title in tiers_display:
        if count >= threshold:
            status = "✅ 已达成"
        else:
            remaining = threshold - count
            status = f"🔒 还需 {remaining} 次贡献"
        output_parts.append(
            f"| {tier_emoji} {tier_title} | {threshold}+ 贡献 | {status} |"
        )

    output_parts.append(
        f"\n> 💊 通过 `save_prescription` 或 `upload_prescription` 贡献药方来提升你的称号！"
    )

    return "\n".join(output_parts)


@mcp.tool()
def list_frameworks(
    category: str | None = None,
    search: str | None = None,
) -> str:
    """
    📋 查询赛博华佗支持的框架列表
    List all supported frameworks in CyberHuaTuo's knowledge base.

    查看赛博华佗覆盖的所有框架和技术栈，支持按分类过滤或关键词搜索。
    分类包括: agent（AI Agent 框架）、foundation（基础框架）、infrastructure（基础设施）。

    Browse all frameworks and tech stacks covered by CyberHuaTuo.
    Supports category filtering and keyword search.
    Categories: agent (AI Agent frameworks), foundation (base frameworks),
    infrastructure (infra & MLOps).

    Args:
        category: 按分类过滤，不填返回全部 / Filter by category (agent / foundation / infrastructure), omit for all
        search: 关键词搜索 / Keyword search (e.g. "pytorch", "rag", "web")
    """
    if search:
        frameworks = search_frameworks(search)
    elif category:
        frameworks = get_frameworks_by_category(category)
    else:
        frameworks = ALL_FRAMEWORKS

    if not frameworks:
        return "未找到匹配的框架。"

    # 按 category 分组
    groups: dict[str, list] = {}
    for fw in frameworks:
        cat = fw.category
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(fw)

    category_names = {
        "agent": "🤖 AI Agent 与 LLM 框架",
        "foundation": "🏗️ AI 基础框架与工具",
        "infrastructure": "⚙️ 基础设施与 MLOps",
    }

    output_parts = ["# 📋 赛博华佗支持框架列表\n"]
    output_parts.append(f"共 **{len(frameworks)}** 个框架\n")

    for cat, fws in groups.items():
        output_parts.append(f"## {category_names.get(cat, cat)}\n")
        for fw in fws:
            tags_str = ", ".join(fw.tags) if fw.tags else ""
            output_parts.append(
                f"- **{fw.name}** (`{fw.key}`) — {fw.description}"
                + (f" [{tags_str}]" if tags_str else "")
            )
        output_parts.append("")

    return "\n".join(output_parts)


# ============================================================
# 📦 Resources — 知识库资源暴露
# ============================================================


@mcp.resource("cyberhuatuo://knowledge-base/stats")
def knowledge_base_stats() -> str:
    """
    📊 知识库统计信息
    Knowledge base statistics.

    返回病例总数、框架分布、严重性分布和病例类型分布。

    Returns total case count, framework distribution, severity
    distribution, and case type distribution.
    """
    cases = scan_cases()

    # 统计框架分布
    framework_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    case_type_counts: dict[str, int] = {}

    for case in cases:
        meta = case.get("metadata", {})
        fw = meta.get("framework", "unknown")
        sev = meta.get("severity", "unknown")
        ct = meta.get("case_type", "treatment")

        framework_counts[fw] = framework_counts.get(fw, 0) + 1
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        case_type_counts[ct] = case_type_counts.get(ct, 0) + 1

    stats = {
        "total_cases": len(cases),
        "framework_distribution": dict(sorted(framework_counts.items(), key=lambda x: -x[1])),
        "severity_distribution": severity_counts,
        "case_type_distribution": case_type_counts,
        "supported_frameworks_count": len(ALL_FRAMEWORKS),
    }

    return json.dumps(stats, ensure_ascii=False, indent=2)


@mcp.resource("cyberhuatuo://knowledge-base/schema")
def knowledge_base_schema() -> str:
    """
    📐 病例 Schema 定义
    Case schema definition (JSON Schema format).

    返回赛博华佗病例的标准 JSON Schema，用于校验和生成病例文件。

    Returns the standard JSON Schema for CyberHuaTuo cases,
    useful for validation and case file generation.
    """
    schema_path = config.SCHEMA_DIR / "case.schema.json"
    if schema_path.exists():
        return schema_path.read_text(encoding="utf-8")
    return json.dumps({"error": "Schema file not found"})


# ============================================================
# 💬 Prompts — 预定义交互模板
# ============================================================


@mcp.prompt()
def diagnose_error(error_message: str) -> str:
    """
    🩺 望闻问切诊断模式
    Enter diagnostic mode — paste your error message for analysis.

    粘贴报错信息，赛博华佗将自动搜索病例库并给出诊断药方。

    Paste your error message and CyberHuaTuo will automatically search
    its case library and deliver a diagnosis with prescription.
    """
    return (
        f"我遇到了以下 AI/Agent 相关的技术问题，请使用赛博华佗（CyberHuaTuo）进行望闻问切诊断：\n\n"
        f"```\n{error_message}\n```\n\n"
        f"请先使用 `search_knowledge_base` 搜索相关病例，"
        f"然后使用 `diagnose` 工具获取完整诊断和药方。"
        f"如果涉及特定框架，也请使用 `fetch_official_docs` 查阅最新官方文档。"
    )


@mcp.prompt()
def security_audit(code: str) -> str:
    """
    🛡️ Agent 安全体检模式
    Enter security audit mode — submit your agent code for health check.

    提交 Agent 代码，执行六经脉安全检测，获取健康评分和滋补建议。

    Submit your agent code for a Six-Meridian security audit.
    Receive a health score and remediation advice.
    """
    return (
        f"请对以下 AI Agent 代码进行赛博华佗安全体检，"
        f"使用 `security_checkup` 工具执行六经脉安全检测：\n\n"
        f"```\n{code}\n```\n\n"
        f"请给出健康评分、各维度分析和滋补建议。"
    )


@mcp.prompt()
def contribute_case(
    problem: str,
    solution: str,
    framework: str = "auto",
) -> str:
    """
    💊 贡献药方模式
    Enter contribution mode — submit a problem-solution pair as a new case.

    提交你解决过的问题和方案，赛博华佗将整理为标准病例格式并入库。

    Submit a problem you've solved along with the fix. CyberHuaTuo
    will format it as a standard case and add it to the knowledge base.
    """
    return (
        f"我想向赛博华佗知识库贡献一个新的病例/药方：\n\n"
        f"**问题描述**:\n{problem}\n\n"
        f"**解决方案**:\n{solution}\n\n"
        f"**框架**: {framework}\n\n"
        f"请帮我整理成标准的赛博华佗病例格式，包含：\n"
        f"- 中英文标题\n- 症状描述\n- 错误信息\n- 根因分析\n"
        f"- 完整药方（含代码示例）\n- 严重性和复杂度评估\n- 标签"
    )


# ============================================================
# 🔧 辅助函数
# ============================================================


async def _run_sync(
    syncer: GitHubSyncer,
    relative_path: str,
    content: str,
    contributor_github: str,
    prescription_meta: dict | None = None,
) -> dict:
    """执行 GitHub 同步的内部辅助函数（支持双层架构）"""
    return await syncer.sync_prescription(
        relative_path=relative_path,
        content=content,
        contributor_github=contributor_github,
        prescription_meta=prescription_meta,
    )


def _format_search_results(query: str, results: list[SearchResult]) -> str:
    """格式化搜索结果为 Markdown 文本（标注常驻/瞬时来源）"""
    if not results:
        return (
            f"在知识库中未找到与「{query}」相关的病例。\n\n"
            f"建议：\n"
            f"1. 尝试使用英文关键词搜索\n"
            f"2. 使用 `list_frameworks` 查看支持的框架\n"
            f"3. 使用 `fetch_official_docs` 查阅官方文档"
        )

    # 统计来源分布
    permanent_count = sum(1 for r in results if r.source == "常驻")
    ephemeral_count = sum(1 for r in results if r.source == "瞬时")

    output_parts = [
        "# 🔍 赛博华佗知识库搜索结果\n",
        f"查询: 「{query}」\n",
        f"找到 **{len(results)}** 个相关病例",
    ]
    if ephemeral_count > 0:
        output_parts[-1] += f"（📜 常驻 {permanent_count} + ⚡ 瞬时 {ephemeral_count}）"
    output_parts.append("\n")

    for i, r in enumerate(results, 1):
        source_badge = "📜" if r.source == "常驻" else "⚡"
        output_parts.append(f"## {source_badge} 病例 {i}: {r.title}")
        output_parts.append(f"- **来源**: {r.source}")
        output_parts.append(f"- **相关度**: {r.relevance}%")
        output_parts.append(f"- **框架**: {r.framework}")
        output_parts.append(f"- **严重性**: {r.severity}")
        output_parts.append(f"- **复杂度**: {r.complexity}")
        if r.tags:
            output_parts.append(f"- **标签**: {r.tags}")
        output_parts.append("")

        if r.content:
            # 截取内容，避免过长
            content_preview = r.content[:3000]
            if len(r.content) > 3000:
                content_preview += "\n\n... (内容已截断，完整内容请访问源文件)"
            output_parts.append(content_preview)

        output_parts.append("\n---\n")

    return "\n".join(output_parts)


# ============================================================
# 🚀 入口
# ============================================================


def main():
    """启动 CyberHuaTuo MCP Server"""
    # 播放赛博华佗启动动画
    try:
        cases = scan_cases()
        play_boot_animation(
            case_count=len(cases),
            framework_count=len(ALL_FRAMEWORKS),
            transport="stdio",
        )
    except Exception:
        pass  # 动画失败不影响启动

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
