"""
CyberHuaTuo FastAPI 路由
提供 Web UI 和 API 接口
"""

from contextlib import asynccontextmanager

import chromadb
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import config
from .indexer import build_index, scan_cases
from .searcher import search_cases
from .diagnosis import diagnose
from .contributor import (
    CaseSubmission, FRAMEWORKS, SEVERITIES, COMPLEXITIES,
    generate_case_markdown, save_case_file, COMPLEXITY_EMOJI,
    smart_extract_contribution,
)
from .doc_fetcher import (
    smart_fetch, multi_framework_fetch, get_supported_frameworks_info,
    search_library, fetch_docs, DocSnippet,
)
from .doc_sources import ALL_FRAMEWORKS, search_frameworks
from .issue_miner import (
    IssueMiner, GitHubClient, get_all_target_repos,
    _issue_to_dict, _refined_to_dict,
)
from .nourishing import (
    security_checkup, get_nourishing_categories,
)
from .epidemic_monitor import (
    EpidemicMonitor, load_latest_report, list_report_history,
    report_to_json, save_report,
)


# 全局 ChromaDB 客户端
_chroma_client: chromadb.ClientAPI | None = None
_case_count: int = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时构建索引"""
    global _chroma_client, _case_count
    _chroma_client, _case_count = build_index()
    print(f"\n🩺 CyberHuaTuo 已启动！")
    print(f"📦 已加载 {_case_count} 个病例")
    if config.has_llm_key():
        providers = ", ".join(config.get_available_providers())
        print(f"🧠 AI 诊断已启用（{providers}）")
    else:
        print(f"💡 AI 诊断未启用（配置 .env 中的 API Key 可开启）")
    if config.CONTEXT7_ENABLED:
        print(f"\u00a0\u00a0📚 官方文档检索已启用（支持 {len(ALL_FRAMEWORKS)} 个框架）")
        if config.CONTEXT7_API_KEY:
            print(f"\u00a0\u00a0🔑 Context7 API Key 已配置（高速率模式）")
        else:
            print(f"\u00a0\u00a0💡 未配置 Context7 API Key（免费模式，有速率限制）")
    else:
        print(f"\u00a0\u00a0📚 官方文档检索未启用")
    if config.NOURISHING_ENABLED:
        print(f"\u00a0\u00a0🧬 滋补药方已启用（上医治未病）")
    if config.EPIDEMIC_ENABLED:
        print(f"\u00a0\u00a0🦠 疫情通报已启用（Agent 生态健康度监控）")
    print(f"\u00a0\u00a0📡 访问 http://{config.HOST}:{config.PORT}\n")
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title="CyberHuaTuo 赛博华佗",
    description="开源的 AI 问题诊断知识库",
    version="0.1.0",
    lifespan=lifespan,
)

# 模板引擎
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

# 静态文件
static_dir = config.STATIC_DIR
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ===== 页面路由 =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页 - 诊断搜索界面"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "case_count": _case_count,
        "has_llm": config.has_llm_key(),
        "providers": config.get_available_providers(),
        "frameworks": FRAMEWORKS,
        "severities": SEVERITIES,
        "complexities": COMPLEXITIES,
        "complexity_emoji": COMPLEXITY_EMOJI,
    })


@app.get("/contribute", response_class=HTMLResponse)
async def contribute_page(request: Request):
    """贡献药方页面"""
    return templates.TemplateResponse("contribute.html", {
        "request": request,
        "frameworks": FRAMEWORKS,
        "severities": SEVERITIES,
        "complexities": COMPLEXITIES,
        "complexity_emoji": COMPLEXITY_EMOJI,
    })


# ===== API 路由 =====

@app.get("/api/search")
async def api_search(
    q: str = Query(..., description="搜索查询"),
    framework: str | None = Query(None, description="框架过滤"),
    severity: str | None = Query(None, description="严重性过滤"),
    complexity: str | None = Query(None, description="复杂度过滤"),
    top_k: int = Query(5, ge=1, le=20, description="返回数量"),
):
    """
    向量搜索 API
    搜索知识库中匹配的病例
    """
    if not _chroma_client:
        return JSONResponse(
            status_code=503,
            content={"error": "索引未就绪，请稍后重试"}
        )

    results = search_cases(
        client=_chroma_client,
        query=q,
        framework=framework if framework != "all" else None,
        severity=severity if severity != "all" else None,
        complexity=complexity if complexity != "all" else None,
        top_k=top_k,
        include_content=True,
    )

    return {
        "query": q,
        "total": len(results),
        "results": [
            {
                "case_id": r.case_id,
                "title": r.title,
                "title_en": r.title_en,
                "framework": r.framework,
                "severity": r.severity,
                "complexity": r.complexity,
                "tags": r.tags,
                "filepath": r.filepath,
                "relevance": r.relevance,
                "content": r.content,
            }
            for r in results
        ],
    }


@app.post("/api/diagnose")
async def api_diagnose(
    q: str = Form(..., description="问题描述/报错信息"),
    framework: str | None = Form(None, description="框架过滤"),
    api_key: str | None = Form(None, description="用户自定义 API Key"),
    provider: str | None = Form(None, description="LLM 提供商"),
    model: str | None = Form(None, description="LLM 模型名称或接入点"),
):
    """
    AI 望闻问切诊断 API
    基于 RAG 检索 + LLM 进行智能诊断
    支持用户传入自己的 API Key 和 模型
    """
    if not _chroma_client:
        return JSONResponse(
            status_code=503,
            content={"error": "索引未就绪"}
        )

    # 先向量检索
    results = search_cases(
        client=_chroma_client,
        query=q,
        framework=framework if framework and framework != "all" else None,
        top_k=config.TOP_K,
        include_content=True,
    )

    # 再 LLM 诊断（支持用户自定义 API Key）
    diagnosis_text = await diagnose(
        q, results,
        user_api_key=api_key,
        user_provider=provider,
        user_model=model,
    )

    return {
        "query": q,
        "diagnosis": diagnosis_text,
        "matched_cases": [
            {
                "case_id": r.case_id,
                "title": r.title,
                "framework": r.framework,
                "relevance": r.relevance,
                "filepath": r.filepath,
            }
            for r in results
        ],
    }


@app.post("/api/contribute/smart")
async def api_contribute_smart(
    issue_text: str = Form(...),
    prescription: str = Form(...),
    framework: str = Form("auto"),
    source_url: str = Form(""),
    api_key: str | None = Form(None),
    provider: str | None = Form("openai")
):
    """
    极简版智能诊断提取 API
    """
    try:
        parsed_data = await smart_extract_contribution(
            issue_text=issue_text,
            prescription=prescription,
            framework_hint=framework,
            source_url=source_url,
            api_key=api_key,
            provider=provider
        )
        
        # Fallback values for required fields
        safe_data = {
            "framework": parsed_data.get("framework", "unknown"),
            "title": parsed_data.get("title", "未命名问题"),
            "symptom": parsed_data.get("symptom", issue_text),
            "prescription": parsed_data.get("prescription", prescription),
            "title_en": parsed_data.get("title_en", ""),
            "error_message": parsed_data.get("error_message", ""),
            "root_cause": parsed_data.get("root_cause", ""),
            "severity": parsed_data.get("severity", "medium"),
            "complexity": parsed_data.get("complexity", "moderate"),
            "tags": parsed_data.get("tags", []),
            "source_url": source_url,
            "contributor_github": "anonymous"
        }
        
        # Add values not strictly required by CaseSubmission
        parsed_data.update(safe_data)

        submission = CaseSubmission(
            framework=safe_data["framework"],
            title=safe_data["title"],
            symptom=safe_data["symptom"],
            prescription=safe_data["prescription"],
            title_en=safe_data["title_en"],
            error_message=safe_data["error_message"],
            root_cause=safe_data["root_cause"],
            severity=safe_data["severity"],
            complexity=safe_data["complexity"],
            tags=safe_data["tags"],
            source_url=safe_data["source_url"],
            contributor_github=safe_data["contributor_github"]
        )
        
        content = generate_case_markdown(submission)

        return {
            "action": "smart_extracted",
            "parsed_data": parsed_data,
            "content": content
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/contribute")
async def api_contribute(
    framework: str = Form(...),
    title: str = Form(...),
    title_en: str = Form(""),
    error_message: str = Form(""),
    symptom: str = Form(""),
    root_cause: str = Form(""),
    prescription: str = Form(""),
    severity: str = Form("medium"),
    complexity: str = Form("moderate"),
    tags: str = Form(""),
    framework_version: str = Form(""),
    contributor_github: str = Form("anonymous"),
    source_url: str = Form(""),
    action: str = Form("preview"),
):
    """
    贡献药方 API
    action: 'preview' 预览生成的文件 / 'save' 保存到本地
    """
    # 解析标签
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    submission = CaseSubmission(
        framework=framework,
        title=title,
        title_en=title_en,
        error_message=error_message,
        symptom=symptom,
        root_cause=root_cause,
        prescription=prescription,
        severity=severity,
        complexity=complexity,
        tags=tag_list,
        framework_version=framework_version,
        contributor_github=contributor_github,
        source_url=source_url,
    )

    if action == "preview":
        # 预览模式：返回生成的 Markdown 内容
        content = generate_case_markdown(submission)
        return {
            "action": "preview",
            "content": content,
        }
    elif action == "save":
        # 保存模式：写入 cases/ 目录
        result = save_case_file(submission)

        # 重建索引
        global _chroma_client, _case_count
        _chroma_client, _case_count = build_index(force_rebuild=True)

        return {
            "action": "saved",
            "case_id": result["case_id"],
            "filepath": result["filepath"],
            "message": f"✅ 病例已保存到 {result['filepath']}",
            "next_steps": [
                f"git add {result['filepath']}",
                f'git commit -m "feat: add case {result["case_id"]}"',
                "git push origin main",
                "在 GitHub 上创建 Pull Request",
            ],
        }

    return JSONResponse(
        status_code=400,
        content={"error": f"未知操作: {action}"}
    )


@app.post("/api/rebuild-index")
async def api_rebuild_index():
    """强制重建向量索引"""
    global _chroma_client, _case_count
    _chroma_client, _case_count = build_index(force_rebuild=True)
    return {
        "message": f"✅ 索引重建完成，共 {_case_count} 个病例",
        "case_count": _case_count,
    }


@app.get("/api/stats")
async def api_stats():
    """获取知识库统计信息"""
    cases = scan_cases()

    # 按框架统计
    framework_stats = {}
    complexity_stats = {"simple": 0, "moderate": 0, "complex": 0, "extreme": 0}

    for case in cases:
        fw = case["metadata"].get("framework", "unknown")
        cx = case["metadata"].get("complexity", "moderate")

        if fw not in framework_stats:
            framework_stats[fw] = 0
        framework_stats[fw] += 1

        if cx in complexity_stats:
            complexity_stats[cx] += 1

    return {
        "total_cases": len(cases),
        "by_framework": framework_stats,
        "by_complexity": complexity_stats,
    }


# ===== 官方文档检索 API =====

@app.get("/api/docs/frameworks")
async def api_docs_frameworks(
    category: str | None = Query(None, description="按分类过滤: agent/foundation/infrastructure"),
):
    """
    获取支持的框架列表
    返回所有已注册框架的名称、分类、Context7 Library ID 等信息
    """
    frameworks = get_supported_frameworks_info()
    if category:
        frameworks = [fw for fw in frameworks if fw["category"] == category]
    return {
        "total": len(frameworks),
        "doc_retrieval_enabled": config.CONTEXT7_ENABLED,
        "frameworks": frameworks,
    }


@app.get("/api/docs/search")
async def api_docs_search(
    q: str = Query(..., description="搜索查询"),
    framework: str | None = Query(None, description="指定框架（如 langchain、react）"),
    top_k: int = Query(5, ge=1, le=20, description="返回片段数量"),
):
    """
    搜索官方技术文档
    基于 Context7 REST API 检索最新官方文档片段
    """
    if not config.CONTEXT7_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"error": "官方文档检索未启用，请在 .env 中设置 CONTEXT7_ENABLED=true"}
        )

    if framework:
        # 指定框架：精确检索
        snippets = await smart_fetch(framework, q, top_k=top_k)
    else:
        # 未指定框架：跨框架智能检索
        snippets = await multi_framework_fetch(q, top_k_per_framework=top_k)

    return {
        "query": q,
        "framework": framework,
        "total": len(snippets),
        "results": [
            {
                "title": s.title,
                "content": s.content,
                "source": s.source,
                "framework": s.framework,
                "framework_name": s.framework_name,
            }
            for s in snippets
        ],
    }


@app.get("/api/docs/context")
async def api_docs_context(
    library_id: str = Query(..., description="Context7 Library ID（如 /facebook/react）"),
    query: str = Query(..., description="查询内容"),
):
    """
    直接获取指定框架的文档上下文
    使用 Context7 Library ID 精确检索官方文档
    """
    if not config.CONTEXT7_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"error": "官方文档检索未启用"}
        )

    snippets = await fetch_docs(library_id, query)

    snippets_data = [
        {
            "title": s.title,
            "content": s.content,
            "source": s.source,
        }
        for s in snippets
    ]

    return JSONResponse(content={
        "library_id": library_id,
        "query": query,
        "total": len(snippets_data),
        "results": snippets_data,
    })


# ===== 滋补药方 API =====

@app.get("/nourish", response_class=HTMLResponse)
async def nourish_page(request: Request):
    """滋补药方页面"""
    return templates.TemplateResponse("nourish.html", {
        "request": request,
        "has_llm": config.has_llm_key(),
        "providers": config.get_available_providers(),
        "nourishing_enabled": config.NOURISHING_ENABLED,
        "categories": get_nourishing_categories(),
    })


@app.get("/api/nourish/cases")
async def api_nourish_cases(
    category: str | None = Query(None, description="滋补分类: sandbox/security/performance"),
    top_k: int = Query(10, ge=1, le=50, description="返回数量"),
):
    """
    获取滋补药方列表
    从知识库中查询 case_type=nourishing 的药方
    """
    if not _chroma_client:
        return JSONResponse(
            status_code=503,
            content={"error": "索引未就绪"}
        )

    # 构建查询
    query = "安全沙箱 最佳实践 Agent 安全" if not category else f"{category} 安全 Agent"

    results = search_cases(
        client=_chroma_client,
        query=query,
        top_k=top_k,
        include_content=True,
    )

    # 过滤出滋补药方
    nourishing_results = [
        r for r in results
        if r.framework == "_nourishing" or (hasattr(r, 'case_type') and r.case_type == 'nourishing')
    ]

    return {
        "total": len(nourishing_results),
        "category": category,
        "results": [
            {
                "case_id": r.case_id,
                "title": r.title,
                "title_en": r.title_en,
                "framework": r.framework,
                "severity": r.severity,
                "complexity": r.complexity,
                "tags": r.tags,
                "filepath": r.filepath,
                "relevance": r.relevance,
                "content": r.content,
            }
            for r in nourishing_results
        ],
    }


@app.post("/api/nourish/checkup")
async def api_nourish_checkup(
    code: str = Form(..., description="Agent 代码"),
    api_key: str | None = Form(None, description="用户 API Key"),
    provider: str | None = Form(None, description="LLM 提供商"),
    model: str | None = Form(None, description="LLM 模型"),
):
    """
    AI 安全体检 API
    对用户提交的 Agent 代码进行六经脉安全分析
    """
    if not config.NOURISHING_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"error": "滋补药方功能未启用"}
        )

    result = await security_checkup(
        code=code,
        user_api_key=api_key,
        user_provider=provider,
        user_model=model,
    )

    return JSONResponse(content=result)


@app.get("/api/nourish/categories")
async def api_nourish_categories():
    """获取滋补药方分类列表"""
    return {
        "categories": get_nourishing_categories(),
        "nourishing_enabled": config.NOURISHING_ENABLED,
    }


# ===== GitHub Issues 淘金 API =====

# 全局 Miner 实例
_miner: IssueMiner | None = None


def _get_miner() -> IssueMiner:
    global _miner
    if _miner is None:
        _miner = IssueMiner()
    return _miner


@app.get("/mine")
async def mine_page(request: Request):
    """淘金操作页面"""
    return templates.TemplateResponse(
        "mine.html",
        {
            "request": request,
            "target_repos": get_all_target_repos(),
            "has_llm": config.has_llm_key(),
            "has_github_token": bool(config.GITHUB_TOKEN),
        },
    )


@app.get("/api/mine/repos")
async def api_mine_repos():
    """获取所有目标淘金仓库列表"""
    return JSONResponse(content={"repos": get_all_target_repos()})


@app.get("/api/mine/search")
async def api_mine_search(
    owner: str = Query(..., description="仓库所有者"),
    repo: str = Query(..., description="仓库名称"),
    framework: str = Query("", description="框架标识"),
    sort: str = Query("reactions-+1", description="排序方式"),
    min_reactions: int = Query(None, description="最低 reactions 数"),
    min_comments: int = Query(None, description="最低 comments 数"),
    limit: int = Query(10, ge=1, le=30, description="返回数量"),
):
    """
    搜索指定仓库的高频 Issues
    """
    miner = _get_miner()
    issues = await miner.search_hot_issues(
        owner=owner,
        repo=repo,
        framework=framework,
        sort=sort,
        min_reactions=min_reactions,
        min_comments=min_comments,
        limit=limit,
    )

    return JSONResponse(content={
        "owner": owner,
        "repo": repo,
        "total": len(issues),
        "issues": [_issue_to_dict(i) for i in issues],
        "rate_info": miner.github.get_rate_info(),
    })


@app.post("/api/mine/refine")
async def api_mine_refine(
    owner: str = Form(...),
    repo: str = Form(...),
    issue_number: int = Form(...),
    framework: str = Form(""),
    auto_save: bool = Form(False),
):
    """
    提炼单个 Issue 为标准病例格式
    获取 Issue 详情 + 评论 → LLM 提炼 → 可选保存
    """
    miner = _get_miner()
    result = await miner.mine_single(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        framework=framework,
        auto_save=auto_save,
    )
    return JSONResponse(content=result)


@app.post("/api/mine/batch")
async def api_mine_batch(
    owner: str = Form(...),
    repo: str = Form(...),
    framework: str = Form(""),
    sort: str = Form("reactions-+1"),
    limit: int = Form(5),
    auto_save: bool = Form(False),
):
    """
    批量淘金：搜索高频 Issues → 提炼 → 可选保存
    """
    miner = _get_miner()
    result = await miner.mine_repo(
        owner=owner,
        repo=repo,
        framework=framework,
        sort=sort,
        limit=limit,
        auto_save=auto_save,
    )
    return JSONResponse(content=result)


# ===== 疫情通报 API =====

_epidemic_monitor: EpidemicMonitor | None = None


def _get_epidemic_monitor() -> EpidemicMonitor:
    global _epidemic_monitor
    if _epidemic_monitor is None:
        _epidemic_monitor = EpidemicMonitor()
    return _epidemic_monitor


@app.get("/epidemic", response_class=HTMLResponse)
async def epidemic_page(request: Request):
    """疫情通报仪表盘页面"""
    latest_report = load_latest_report()
    history = list_report_history()
    return templates.TemplateResponse(
        "epidemic.html",
        {
            "request": request,
            "has_github_token": bool(config.GITHUB_TOKEN),
            "epidemic_enabled": config.EPIDEMIC_ENABLED,
            "latest_report": latest_report,
            "history": history,
        },
    )


@app.get("/api/epidemic/report")
async def api_epidemic_report():
    """获取最新疫情通报 JSON 报告"""
    report = load_latest_report()
    if not report:
        return JSONResponse(
            status_code=404,
            content={"error": "暂无疫情通报数据，请先执行一次扫描"},
        )
    return JSONResponse(content=report)


@app.post("/api/epidemic/scan")
async def api_epidemic_scan():
    """手动触发全量疫情扫描"""
    if not config.EPIDEMIC_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"error": "疫情通报功能未启用"},
        )

    monitor = _get_epidemic_monitor()
    report = await monitor.scan_all_frameworks()
    result = save_report(report)
    report_data = report_to_json(report)

    return JSONResponse(content={
        "message": f"✅ 疫情通报扫描完成，已扫描 {report.framework_count} 个框架",
        "avg_health_score": report.avg_health_score,
        "files": result,
        "report": report_data,
    })


@app.get("/api/epidemic/history")
async def api_epidemic_history():
    """获取历史报告列表"""
    history = list_report_history()
    return JSONResponse(content={
        "total": len(history),
        "reports": history,
    })


@app.get("/api/epidemic/framework/{name}")
async def api_epidemic_framework(name: str):
    """获取单框架详细健康数据"""
    # 优先从最新报告中查找
    report = load_latest_report()
    if report and "frameworks" in report:
        for fw in report["frameworks"]:
            if fw.get("framework") == name:
                return JSONResponse(content=fw)

    # 如果没有缓存数据，实时扫描
    if not config.EPIDEMIC_ENABLED:
        return JSONResponse(
            status_code=503,
            content={"error": "疫情通报功能未启用"},
        )

    monitor = _get_epidemic_monitor()
    result = await monitor.scan_single_framework(name)
    if not result:
        return JSONResponse(
            status_code=404,
            content={"error": f"未找到框架: {name}"},
        )

    return JSONResponse(content={
        "framework": result.framework,
        "display_name": result.display_name,
        "health_score": result.health_score,
        "trend": result.trend,
        "open_issues_count": result.open_issues_count,
        "new_issues_7d": result.new_issues_7d,
        "closed_issues_7d": result.closed_issues_7d,
        "bug_count": result.bug_count,
        "anomalies": result.anomalies,
        "scanned_at": result.scanned_at,
    })
