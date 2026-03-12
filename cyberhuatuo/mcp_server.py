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
from .searcher import SearchResult, search_cases
from .contributor import CaseSubmission, save_case_file
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

    Args:
        query: 报错信息或问题描述（Error message or problem description）
        framework: 可选，按框架过滤（如 langchain, crewai, openai-sdk）
        top_k: 返回的参考病例数量，默认 5
    """
    client = _get_chroma_client()

    # 1. 向量搜索相关病例
    results = search_cases(
        client=client,
        query=query,
        framework=framework,
        top_k=top_k,
        include_content=True,
    )

    # 2. 尝试 LLM 诊断
    try:
        from .diagnosis import diagnose as llm_diagnose

        diagnosis_result = await llm_diagnose(query=query, results=results)
        return diagnosis_result
    except Exception as e:
        # LLM 不可用时回退到纯搜索结果
        logger.warning(f"LLM 诊断不可用，回退到纯搜索: {e}")
        return _format_search_results(query, results)


@mcp.tool()
def search_knowledge_base(
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

    Args:
        query: 搜索查询（错误信息/问题描述）
        framework: 按框架过滤（如 langchain, crewai, openai-sdk, pytorch）
        severity: 按严重性过滤（low / medium / high / critical）
        complexity: 按复杂度过滤（simple / moderate / complex / extreme）
        top_k: 返回结果数量，默认 5
    """
    client = _get_chroma_client()

    results = search_cases(
        client=client,
        query=query,
        framework=framework,
        severity=severity,
        complexity=complexity,
        top_k=top_k,
        include_content=True,
    )

    return _format_search_results(query, results)


@mcp.tool()
async def security_checkup(code: str) -> str:
    """
    🛡️ AI Agent 代码安全体检
    Perform a security health check on AI agent code.

    对 AI Agent 代码进行六经脉安全体检，检测沙箱隔离、密钥安全、
    Prompt 安全、输出安全、韧性设计、可观测性等六大维度，
    输出健康评分和滋补建议。需要 LLM API Key。

    Args:
        code: 要进行安全体检的代码内容
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

    Args:
        framework: 框架标识（如 langchain, pytorch, fastapi, react, openai-sdk）
        query: 要查询的具体问题（如 "如何配置 RAG pipeline"）
        top_k: 返回文档片段数量，默认 5
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

    Args:
        owner: 仓库所有者（如 langchain-ai）
        repo: 仓库名称（如 langchain）
        issue_number: Issue 编号
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
def save_prescription(
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

    Args:
        title: 问题标题 (中文为主，建议 20 字内)
        prescription: 详细修复方案 (Markdown 格式)
        framework: 框架标识 (如 langchain, pytorch)
        symptom: 症状详细描述
        error_message: 纯报错日志或 Traceback
        root_cause: 根本原因分析
        severity: 严重性 (low / medium / high / critical)
        complexity: 复杂度 (simple / moderate / complex / extreme)
        tags: 标签数组 (英文或中文标签)
        title_en: 英文问题标题
        framework_version: 框架版本
        language: 编程语言 (如 python, typescript)
        contributor_github: 贡献者的 Github 用户名
        source_url: 参考链接
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
             # 由于当前版本不支持增量添加单个 Case 到 ChromaDB
             # 此处简单的将全局变量重置，以便下次查询时重新加载整个 cases 目录
             # (此为一种简单的懒加载重置策略进行缓存失效)
             _chroma_client = None
             logger.info("✅ 新药方已落盘，已清除 ChromaDB 实例缓存以便下次重载索引。")

        return (
            f"✅ 药方保存成功！\n\n"
            f"- **病例 ID**: {result['case_id']}\n"
            f"- **保存路径**: {result['filepath']}\n"
            f"- **温馨提示**: 系统缓存已标记过期，将在您下次诊断时自动重新构建最新知识库索引。"
        )

    except Exception as e:
        logger.error(f"保存药方失败: {e}", exc_info=True)
        return f"⚠️ 药方保存失败: {str(e)}"


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

    Args:
        category: 按分类过滤（agent / foundation / infrastructure），不填返回全部
        search: 关键词搜索（如 "pytorch"、"rag"、"web"）
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
    知识库统计信息
    Knowledge base statistics including case count and framework distribution.
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
    病例 Schema 定义
    Case schema definition (JSON Schema format).
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


def _format_search_results(query: str, results: list[SearchResult]) -> str:
    """格式化搜索结果为 Markdown 文本"""
    if not results:
        return (
            f"在知识库中未找到与「{query}」相关的病例。\n\n"
            f"建议：\n"
            f"1. 尝试使用英文关键词搜索\n"
            f"2. 使用 `list_frameworks` 查看支持的框架\n"
            f"3. 使用 `fetch_official_docs` 查阅官方文档"
        )

    output_parts = [
        "# 🔍 赛博华佗知识库搜索结果\n",
        f"查询: 「{query}」\n",
        f"找到 **{len(results)}** 个相关病例：\n",
    ]

    for i, r in enumerate(results, 1):
        output_parts.append(f"## 病例 {i}: {r.title}")
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
