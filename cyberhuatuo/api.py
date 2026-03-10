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
)
from .doc_fetcher import (
    smart_fetch, multi_framework_fetch, get_supported_frameworks_info,
    search_library, fetch_docs, DocSnippet,
)
from .doc_sources import ALL_FRAMEWORKS, search_frameworks


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
        print(f"📚 官方文档检索已启用（支持 {len(ALL_FRAMEWORKS)} 个框架）")
        if config.CONTEXT7_API_KEY:
            print(f"🔑 Context7 API Key 已配置（高速率模式）")
        else:
            print(f"💡 未配置 Context7 API Key（免费模式，有速率限制）")
    else:
        print(f"📚 官方文档检索未启用")
    print(f"📡 访问 http://{config.HOST}:{config.PORT}\n")
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title="CyberHuaTuo 赛博华佗",
    description="开源的 AI Agent 问题诊断知识库",
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
):
    """
    AI 望闻问切诊断 API
    基于 RAG 检索 + LLM 进行智能诊断
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

    # 再 LLM 诊断
    diagnosis_text = await diagnose(q, results)

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
    return {
        "library_id": library_id,
        "query": query,
        "total": len(snippets),
        "results": [
            {
                "title": s.title,
                "content": s.content,
                "source": s.source,
            }
            for s in snippets
        ],
    }
