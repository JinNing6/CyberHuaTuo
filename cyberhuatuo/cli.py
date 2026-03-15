"""
CyberHuaTuo CLI — 赛博华佗命令行界面
让开发者直接在终端使用「望闻问切」诊断能力

使用方式：
    python -m cyberhuatuo diagnose "你的报错信息"
    python -m cyberhuatuo search "CUDA out of memory"
    python -m cyberhuatuo stats
    python -m cyberhuatuo --help
"""

import argparse
import asyncio
import os
import sys
import threading
import time
import webbrowser

# Windows 环境下强制使用 UTF-8 编码
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


# ============================================================
# 🎨 终端输出辅助
# ============================================================

def _print_header(title: str):
    """打印赛博华佗 CLI 头部"""
    print()
    print("🩺 CyberHuaTuo 赛博华佗 · CLI")
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)
    print()


def _print_result(text: str):
    """打印工具结果（去除 MCP 品牌签名尾部）"""
    # 去除品牌签名部分
    marker = "\n\n---\n\n**"
    idx = text.rfind(marker)
    if idx > 0:
        text = text[:idx]
    print(text)


def _run_async(coro):
    """在 CLI 中同步运行异步函数"""
    return asyncio.run(coro)


def _open_browser(url: str, delay: float = 1.5):
    """延迟后自动打开浏览器"""
    def _open():
        time.sleep(delay)
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


# ============================================================
# 🧩 懒加载辅助（避免 import 时触发 ChromaDB 等重量级初始化）
# ============================================================

_chroma_client = None


def _get_chroma():
    """懒加载 ChromaDB 客户端"""
    global _chroma_client
    if _chroma_client is None:
        from .indexer import build_index
        _chroma_client, count = build_index()
        print(f"✅ 知识库索引就绪，共 {count} 个病例")
    return _chroma_client


# ============================================================
# 📋 子命令实现
# ============================================================


def cmd_diagnose(args):
    """🩺 望闻问切诊断"""
    _print_header("望闻问切 · AI 诊断")
    client = _get_chroma()

    from .report import _generate_report_id, calculate_confidence, format_standard_report
    from .searcher import search_cases
    from .taxonomy import classify_root_cause

    results = search_cases(
        client=client,
        query=args.query,
        framework=args.framework,
        top_k=args.top_k,
        include_content=True,
    )

    # 尝试瞬时药方搜索
    try:
        from .searcher import search_ephemeral_issues
        ephemeral = _run_async(search_ephemeral_issues(
            query=args.query, framework=args.framework, top_k=3,
        ))
        results.extend(ephemeral)
    except Exception:
        pass

    # LLM 诊断
    _generate_report_id()
    classify_root_cause(args.query)
    calculate_confidence(results)

    try:
        from .diagnosis import diagnose as llm_diagnose
        diagnosis_text = _run_async(llm_diagnose(query=args.query, results=results))
        report = format_standard_report(
            query=args.query, results=results,
            diagnosis_text=diagnosis_text, framework=args.framework,
        )
    except Exception:
        report = format_standard_report(
            query=args.query, results=results, framework=args.framework,
        )

    _print_result(report)


def cmd_search(args):
    """🔍 搜索知识库"""
    _print_header("知识库搜索")
    client = _get_chroma()

    from .searcher import search_cases

    results = search_cases(
        client=client,
        query=args.query,
        framework=args.framework,
        severity=args.severity,
        top_k=args.top_k,
        include_content=True,
    )

    # 瞬时药方
    try:
        from .searcher import search_ephemeral_issues
        ephemeral = _run_async(search_ephemeral_issues(
            query=args.query, framework=args.framework,
            severity=args.severity, top_k=3,
        ))
        results.extend(ephemeral)
    except Exception:
        pass

    if not results:
        print(f"❌ 未找到与「{args.query}」相关的病例。")
        print("建议：使用英文关键词，或尝试 `cyberhuatuo frameworks` 查看支持的框架")
        return

    print(f"找到 {len(results)} 个相关病例：\n")
    for i, r in enumerate(results, 1):
        src = "📜" if r.source == "常驻" else "⚡"
        print(f"{src} [{i}] {r.title}")
        print(f"    框架: {r.framework} | 严重性: {r.severity} | 相关度: {r.relevance}%")
        if r.content:
            preview = r.content[:300].replace("\n", " ")
            print(f"    摘要: {preview}...")
        print()


def cmd_checkup(args):
    """🛡️ 安全体检"""
    _print_header("AI Agent 安全体检")

    code = args.code
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"❌ 无法读取文件: {e}")
            sys.exit(1)

    if not code:
        print("❌ 请提供代码内容（--code）或代码文件路径（--file）")
        sys.exit(1)

    try:
        from .nourishing import security_checkup as do_checkup
        result = _run_async(do_checkup(code=code))
        if "error" in result and result.get("health_score", 0) == -1:
            print(f"⚠️ 安全体检失败（需要 LLM API Key）: {result.get('error', '')}")
        else:
            print(f"健康评分: {result.get('health_score', 'N/A')} / 100")
            print(f"健康等级: {result.get('level', 'N/A')}")
            for dim in result.get("dimensions", []):
                print(f"  {dim.get('emoji', '')} {dim.get('name', '')}: {dim.get('score', 'N/A')}/100")
    except ImportError:
        print("⚠️ 安全体检需要 LLM API Key，请在 .env 中配置")
    except Exception as e:
        print(f"⚠️ 安全体检异常: {e}")


def cmd_docs(args):
    """📚 获取官方文档"""
    _print_header(f"官方文档检索: {args.framework}")

    try:
        from .doc_fetcher import smart_fetch
        snippets = _run_async(smart_fetch(
            framework_name=args.framework,
            query=args.query,
            top_k=args.top_k,
        ))
        if not snippets:
            print(f"❌ 未找到 {args.framework} 的相关文档")
            return
        for i, s in enumerate(snippets, 1):
            print(f"\n--- 文档 {i}: {s.title} ---")
            if s.source:
                print(f"来源: {s.source}")
            print(s.content)
    except Exception as e:
        print(f"⚠️ 文档检索失败: {e}")


def cmd_save(args):
    """📥 保存药方到本地"""
    _print_header("保存药方")

    from .contributor import CaseSubmission, save_case_file

    tags = args.tags.split(",") if args.tags else []
    submission = CaseSubmission(
        title=args.title,
        prescription=args.prescription,
        framework=args.framework,
        symptom=args.symptom or "",
        error_message=args.error_message or "",
        root_cause=args.root_cause or "",
        severity=args.severity,
        complexity=args.complexity,
        tags=tags,
        title_en=args.title_en or "",
        framework_version=args.framework_version or "",
        language=args.language,
        contributor_github=args.contributor or "anonymous",
        source_url=args.source_url or "",
    )

    try:
        result = save_case_file(submission)
        print("✅ 药方保存成功！")
        print(f"  病例 ID: {result['case_id']}")
        print(f"  保存路径: {result['filepath']}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        sys.exit(1)


def cmd_upload(args):
    """🌐 上传药方到 GitHub"""
    _print_header("上传药方到 GitHub")

    from .config import config
    if not config.GITHUB_TOKEN:
        print("❌ 上传失败：未配置 GITHUB_TOKEN。")
        print("请在环境变量或 .env 文件中配置：")
        print("  GITHUB_TOKEN=ghp_your-token-here")
        print("\n💡 如果只想保存到本地，请使用 `cyberhuatuo save`")
        sys.exit(1)

    from .contributor import CaseSubmission, save_case_file
    from .github_sync import GitHubSyncer

    tags = args.tags.split(",") if args.tags else []
    submission = CaseSubmission(
        title=args.title,
        prescription=args.prescription,
        framework=args.framework,
        symptom=args.symptom or "",
        error_message=args.error_message or "",
        root_cause=args.root_cause or "",
        severity=args.severity,
        complexity=args.complexity,
        tags=tags,
        title_en=args.title_en or "",
        framework_version=args.framework_version or "",
        language=args.language,
        contributor_github=args.contributor or "anonymous",
        source_url=args.source_url or "",
    )

    try:
        result = save_case_file(submission)
        print(f"✅ 药方本地保存成功: {result['case_id']}")

        # 同步到 GitHub
        from pathlib import Path
        abs_path = result.get("absolute_path", "")
        full_content = Path(abs_path).read_text(encoding="utf-8") if abs_path else ""

        prescription_meta = {
            "title": args.title, "framework": args.framework,
            "prescription": args.prescription, "severity": args.severity,
        }

        syncer = GitHubSyncer()
        sync_result = syncer.sync_prescription(
            relative_path=result["filepath"],
            content=full_content,
            contributor_github=args.contributor or "anonymous",
            prescription_meta=prescription_meta,
        )

        if sync_result.get("success"):
            method = sync_result.get("method", "")
            if method == "direct_push":
                print(f"🌐 GitHub: ✅ 已推送为常驻药方 (commit: {sync_result.get('commit_sha', '')[:8]})")
            elif method == "issue":
                print(f"🌐 GitHub: ✅ 已创建瞬时药方 Issue: {sync_result.get('issue_url', '')}")
            elif method == "fork_pr":
                print(f"🌐 GitHub: ✅ 已创建 PR: {sync_result.get('pr_url', '')}")
            else:
                print(f"🌐 GitHub: ✅ 同步成功 ({method})")
        else:
            print(f"🌐 GitHub: ⚠️ 同步失败: {sync_result.get('error', '未知错误')}")

        # 显示贡献者修为
        contributor = args.contributor or "anonymous"
        if contributor != "anonymous":
            from .achievements import get_cultivation_profile, record_activity
            record_activity(contributor)
            profile = get_cultivation_profile(contributor)
            print("\n🧬 修为结算:")
            print(f"  炼丹师: @{contributor}")
            print(f"  称号: {profile['title_emoji']} {profile['title_cn']}")
            print(f"  累计药方: {profile['contribution_count']} 段")

    except Exception as e:
        print(f"❌ 上传失败: {e}")
        sys.exit(1)


def cmd_ranking(args):
    """🏆 查看个人排名（带科幻动画）"""
    from .achievements import (
        get_alchemy_profile,
        get_cultivation_profile,
        get_streak_display,
        record_activity,
    )
    from .cli_effects import (
        _supports_color,
        animate_ranking_scan,
        render_alchemy_hud,
        render_soul_rings,
    )

    record_activity(args.username)
    profile = get_cultivation_profile(args.username)
    alchemy = get_alchemy_profile(args.username)

    has_color = _supports_color()

    if has_color:
        # ── 科幻动画模式 ──
        # 1. 全息扫描 + 排名面板
        animate_ranking_scan(args.username, profile)

        # 2. 魂环全息投影
        if alchemy["directions"]:
            render_soul_rings(alchemy["directions"])

        # 3. 丹术方向 HUD 面板
        if alchemy["directions"]:
            render_alchemy_hud(alchemy["directions"], username=args.username)
    else:
        # ── 纯文本模式 ──
        _print_header("全球炼丹师排名")
        print(f"炼丹师: @{args.username}")
        print(f"修  为: {profile['title_emoji']} {profile['title_cn']} · {profile['title_en']}")
        print(f"印  痕: {profile['contribution_count']} 段药方")
        print(f"全球排位: #{profile['global_rank']} / {profile['global_total']}")
        print(f"超越百分比: {profile['percentile']:.0f}%")
        if alchemy["primary"]:
            p = alchemy["primary"]
            print(f"丹术方向: {p['emoji']} {p['name_cn']}丹师 · {p['rings']}")

    streak = get_streak_display(args.username)
    if streak:
        print(f"\n{streak}")


def cmd_leaderboard(args):
    """🏆 全球封神榜（带揭榜动画）"""
    from .achievements import calculate_title_by_percentile
    from .cli_effects import animate_leaderboard
    from .github_sync import get_global_ranking_stats

    stats = get_global_ranking_stats()
    if not stats:
        _print_header("全球封神榜")
        print("封神榜尚未开启，等待第一位炼丹师的降临！")
        return

    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    total = len(sorted_stats)
    display = min(args.top_n, total)

    # 使用科幻揭榜动画
    animate_leaderboard(
        sorted_stats=sorted_stats,
        total=total,
        display_count=display,
        calculate_title_fn=calculate_title_by_percentile,
    )


def cmd_card(args):
    """📋 生成分享卡片（带生成动画）"""
    from .achievements import generate_share_card, record_activity
    from .cli_effects import animate_card_generation

    record_activity(args.username)

    # 播放生成过程动画
    animate_card_generation(args.username)

    card = generate_share_card(args.username)
    print("\n📋 修为档案卡片（可复制分享）：\n")
    print(card)


def cmd_frameworks(args):
    """📋 支持框架列表"""
    _print_header("支持框架列表")

    from .doc_sources import ALL_FRAMEWORKS, get_frameworks_by_category, search_frameworks

    if args.search:
        frameworks = search_frameworks(args.search)
    elif args.category:
        frameworks = get_frameworks_by_category(args.category)
    else:
        frameworks = ALL_FRAMEWORKS

    if not frameworks:
        print("未找到匹配的框架。")
        return

    groups: dict[str, list] = {}
    for fw in frameworks:
        groups.setdefault(fw.category, []).append(fw)

    cat_names = {
        "agent": "🤖 AI Agent 与 LLM 框架",
        "foundation": "🏗️ AI 基础框架与工具",
        "infrastructure": "⚙️ 基础设施与 MLOps",
    }

    print(f"共 {len(frameworks)} 个框架\n")
    for cat, fws in groups.items():
        print(f"\n{cat_names.get(cat, cat)}")
        for fw in fws:
            print(f"  • {fw.name} ({fw.key}) — {fw.description}")


def cmd_taxonomy(args):
    """🧬 CHT 编码系统"""
    from .taxonomy import (
        CATEGORY_NAMES,
        CODE_MAP,
        classify_multi,
        get_taxonomy_table,
    )

    if args.action == "list":
        _print_header("CHT 根因编码系统")
        print(f"10 个分类, {len(CODE_MAP) - 1} 个编码\n")
        for cat_key, (cn, en) in CATEGORY_NAMES.items():
            if cat_key == "UNK":
                continue
            print(f"  {cat_key}: {cn} / {en}")
        print(f"\n{get_taxonomy_table()}")

    elif args.action == "lookup":
        if not args.code:
            print("❌ 请提供 CHT 编码（如 CHT-CFG-001）")
            sys.exit(1)
        cht = CODE_MAP.get(args.code.upper())
        if not cht:
            print(f"❌ 编码 `{args.code}` 未找到，使用 `taxonomy list` 查看全部。")
            sys.exit(1)
        print(f"\n{cht.code}")
        print(f"  分类: {cht.category}")
        print(f"  中文: {cht.name_cn}")
        print(f"  英文: {cht.name_en}")
        print(f"  描述: {cht.description_cn}")
        print(f"  关键词: {', '.join(cht.keywords)}")

    elif args.action == "classify":
        if not args.text:
            print("❌ 请提供要分类的文本（--text）")
            sys.exit(1)
        matches = classify_multi(args.text, top_k=3)
        if not matches:
            print("未找到匹配的编码。")
            return
        print(f"\n输入: {args.text[:200]}\n")
        for i, (cht, score) in enumerate(matches, 1):
            marker = " ← 最佳匹配" if i == 1 else ""
            print(f"  [{i}] {cht.code} — {cht.name_cn} / {cht.name_en} (得分: {score}){marker}")


def cmd_trends(args):
    """📈 CHT 趋势分析"""
    _print_header("CHT 编码趋势分析")
    from .taxonomy import analyze_trends
    result = analyze_trends(args.framework, args.category)
    _print_result(result)


def cmd_record(args):
    """📋 诊疗档案"""
    from .medical_record import get_follow_up_candidates, get_profile_summary, mark_resolved

    user = args.username or os.getenv("GITHUB_USERNAME", os.getenv("USER", "anonymous"))

    if args.action == "view":
        _print_header(f"诊疗档案: @{user}")
        _print_result(get_profile_summary(user))
    elif args.action == "resolve":
        if not args.record_id:
            print("❌ 请提供 record_id（如 CHT-DR-20260313-a3f7）")
            sys.exit(1)
        ok = mark_resolved(user, args.record_id, args.note or "")
        print(f"✅ 已标记 {args.record_id} 为已解决" if ok else f"❌ 未找到记录 {args.record_id}")
    elif args.action == "followup":
        candidates = get_follow_up_candidates(user)
        if not candidates:
            print("✅ 无待跟进记录。")
            return
        print(f"📋 待跟进记录 ({len(candidates)} 项)：\n")
        for rec in candidates:
            print(f"  • {rec['record_id']} [{rec['framework']}] {rec['query'][:60]}...")


def cmd_subscribe(args):
    """📬 框架订阅"""
    from .medical_record import (
        check_new_prescriptions,
        get_subscriptions,
        subscribe_framework_for_user,
        unsubscribe_framework_for_user,
    )

    user = args.username or os.getenv("GITHUB_USERNAME", os.getenv("USER", "anonymous"))

    if args.action == "subscribe":
        if not args.framework:
            print("❌ 请指定框架名（如 langchain）")
            sys.exit(1)
        ok = subscribe_framework_for_user(user, args.framework)
        print(f"✅ 已订阅 {args.framework}" if ok else f"已订阅过 {args.framework}")
    elif args.action == "unsubscribe":
        if not args.framework:
            print("❌ 请指定要取消订阅的框架")
            sys.exit(1)
        ok = unsubscribe_framework_for_user(user, args.framework)
        print(f"✅ 已取消订阅 {args.framework}" if ok else f"未订阅 {args.framework}")
    elif args.action == "list":
        subs = get_subscriptions(user)
        print(f"当前订阅: {', '.join(subs)}" if subs else "暂无订阅。")
    elif args.action == "check":
        cases = check_new_prescriptions(user)
        if not cases:
            print("✅ 订阅框架无新药方。")
        else:
            print(f"📬 {len(cases)} 个新药方：")
            for c in cases:
                print(f"  • [{c['framework']}] {c['title']} ({c['severity']})")


def cmd_digest(args):
    """📊 周刊摘要"""
    _print_header("本周药方摘要")
    from .social import generate_weekly_digest
    _print_result(generate_weekly_digest())


def cmd_epidemic(args):
    """🦠 疫情预警"""
    from .epidemic_monitor import EpidemicMonitor, generate_markdown_report, load_latest_report, save_report

    if args.action == "check":
        latest = load_latest_report()
        if not latest:
            print("暂无疫情报告。使用 `cyberhuatuo epidemic --action generate` 生成。")
            return
        print(f"报告日期: {latest.get('report_date', '?')}")
        for fw in latest.get("frameworks", [])[:10]:
            score = fw.get("health_score", 0)
            emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🟠" if score >= 40 else "🔴"
            print(f"  {emoji} {fw.get('framework', '?')}: {score}/100")
    elif args.action == "scan":
        if not args.framework:
            print("❌ 请指定框架（--framework）")
            sys.exit(1)
        monitor = EpidemicMonitor()
        fw_data = _run_async(monitor.scan_single_framework(args.framework))
        if not fw_data:
            print(f"❌ 框架 {args.framework} 未在监测列表")
            return
        print(f"{args.framework}: {fw_data.health_score}/100 趋势: {fw_data.trend}")
        print(f"  Open Issues: {fw_data.open_issues_count:,}")
        print(f"  新增(7d): {fw_data.new_issues_7d} | 关闭(7d): {fw_data.closed_issues_7d}")
    elif args.action == "report":
        latest = load_latest_report()
        if not latest:
            print("暂无报告。")
            return
        _print_result(
            f"日期: {latest.get('report_date', '?')}\n"
            f"框架数: {latest.get('framework_count', 0)}\n"
            f"平均健康: {latest.get('avg_health_score', 0)}/100"
        )
    elif args.action == "generate":
        print("🔬 正在生成疫情报告（约需 2 分钟）...")
        monitor = EpidemicMonitor()
        report = _run_async(monitor.scan_all_frameworks())
        save_report(report)
        md = generate_markdown_report(report)
        _print_result(md)
        print("\n✅ 报告已生成并保存。")


def cmd_serve(args):
    """🚀 启动 Web 服务"""
    import uvicorn

    from .config import config

    host = args.host or config.HOST
    port = args.port or config.PORT
    url = f"http://{host}:{port}"

    _print_header("Web 诊断服务")
    if not args.no_browser:
        _open_browser(url)

    uvicorn.run("cyberhuatuo.api:app", host=host, port=port, reload=args.reload)


def cmd_rebuild(args):
    """🔄 重建索引"""
    _print_header("重建向量索引")
    from .indexer import build_index
    client, count = build_index(force_rebuild=True)
    print(f"✅ 索引重建完成，共 {count} 个病例")


def cmd_stats(args):
    """📦 知识库统计"""
    _print_header("知识库统计")
    from .indexer import scan_cases

    cases = scan_cases()
    print(f"📦 总病例数: {len(cases)}")

    fw_stats: dict[str, int] = {}
    for c in cases:
        fw = c["metadata"].get("framework", "unknown")
        fw_stats[fw] = fw_stats.get(fw, 0) + 1

    if fw_stats:
        print("\n📊 按框架统计:")
        for fw, count in sorted(fw_stats.items(), key=lambda x: -x[1]):
            print(f"  {fw}: {count}")


def cmd_mine(args):
    """⛏️ GitHub Issues 淘金"""
    from .issue_miner import TARGET_REPOS, IssueMiner
    miner = IssueMiner()

    if args.mine_action == "search":
        parts = args.repo.split("/")
        if len(parts) != 2:
            print("❌ --repo 格式应为 owner/repo")
            sys.exit(1)
        owner, repo = parts
        print(f"\n⛏️ 搜索 {owner}/{repo} 的高频 Issues ...")
        issues = _run_async(miner.search_hot_issues(
            owner=owner, repo=repo,
            min_reactions=args.min_reactions,
            min_comments=args.min_comments,
            limit=args.limit,
        ))
        if not issues:
            print("  未找到匹配的高频 Issues")
        else:
            for i, iss in enumerate(issues, 1):
                print(f"  {i}. [{iss.framework}] #{iss.number} {iss.title}")
                print(f"     👍 {iss.reactions_thumbs_up}  💬 {iss.comments_count}")

    elif args.mine_action == "batch":
        if args.mine_all:
            print(f"\n⛏️ 全量淘金 {len(TARGET_REPOS)} 个仓库 ...")
            for tr in TARGET_REPOS:
                result = _run_async(miner.mine_repo(
                    owner=tr.owner, repo=tr.repo,
                    framework=tr.framework, limit=args.limit,
                    auto_save=args.save,
                ))
                print(f"  ✅ {tr.owner}/{tr.repo}: 提炼 {result.get('total_refined', 0)} 个")
        elif args.repo:
            parts = args.repo.split("/")
            if len(parts) != 2:
                print("❌ --repo 格式应为 owner/repo")
                sys.exit(1)
            owner, repo = parts
            result = _run_async(miner.mine_repo(
                owner=owner, repo=repo,
                limit=args.limit, auto_save=args.save,
            ))
            print(f"  ✅ 提炼 {result.get('total_refined', 0)} 个病例")
        else:
            print("❌ 请指定 --repo 或 --all")
    else:
        print("请使用 mine search 或 mine batch 子命令")


# ============================================================
# 🏗️ 参数解析器构建
# ============================================================


def _build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器"""
    parser = argparse.ArgumentParser(
        prog="cyberhuatuo",
        description="🩺 CyberHuaTuo 赛博华佗 — AI 问题诊断知识库 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  cyberhuatuo diagnose \"ImportError: cannot import name 'ChatOpenAI'\"\n"
            "  cyberhuatuo search \"CUDA out of memory\" --framework pytorch\n"
            "  cyberhuatuo stats\n"
            "  cyberhuatuo frameworks --search langchain\n"
            "  cyberhuatuo serve --port 8080\n"
            "\n"
            "MCP 模式:\n"
            "  cyberhuatuo-mcp    # 启动 MCP Server (stdio 传输)\n"
        ),
    )

    subs = parser.add_subparsers(dest="command", help="可用命令")

    # --- diagnose ---
    p = subs.add_parser("diagnose", help="🩺 望闻问切 AI 诊断")
    p.add_argument("query", help="报错信息、Traceback 或问题描述")
    p.add_argument("--framework", "-f", default=None, help="按框架过滤")
    p.add_argument("--top-k", "-k", type=int, default=5, help="返回病例数量")
    p.set_defaults(func=cmd_diagnose)

    # --- search ---
    p = subs.add_parser("search", help="🔍 搜索知识库")
    p.add_argument("query", help="搜索查询")
    p.add_argument("--framework", "-f", default=None, help="按框架过滤")
    p.add_argument("--severity", "-s", default=None, choices=["low", "medium", "high", "critical"])
    p.add_argument("--top-k", "-k", type=int, default=5)
    p.set_defaults(func=cmd_search)

    # --- checkup ---
    p = subs.add_parser("checkup", help="🛡️ AI Agent 安全体检")
    p.add_argument("--code", default=None, help="代码内容")
    p.add_argument("--file", default=None, help="代码文件路径")
    p.set_defaults(func=cmd_checkup)

    # --- docs ---
    p = subs.add_parser("docs", help="📚 获取官方文档")
    p.add_argument("framework", help="框架名（如 langchain, pytorch）")
    p.add_argument("query", help="查询问题")
    p.add_argument("--top-k", "-k", type=int, default=5)
    p.set_defaults(func=cmd_docs)

    # --- save ---
    p = subs.add_parser("save", help="📥 保存药方到本地")
    p.add_argument("--title", required=True, help="问题标题")
    p.add_argument("--prescription", required=True, help="修复方案")
    p.add_argument("--framework", required=True, help="框架标识")
    p.add_argument("--symptom", default=None)
    p.add_argument("--error-message", default=None)
    p.add_argument("--root-cause", default=None)
    p.add_argument("--severity", default="medium", choices=["low", "medium", "high", "critical"])
    p.add_argument("--complexity", default="moderate", choices=["simple", "moderate", "complex", "extreme"])
    p.add_argument("--tags", default=None, help="逗号分隔的标签")
    p.add_argument("--title-en", default=None)
    p.add_argument("--framework-version", default=None)
    p.add_argument("--language", default="python")
    p.add_argument("--contributor", default="anonymous")
    p.add_argument("--source-url", default=None)
    p.set_defaults(func=cmd_save)

    # --- upload ---
    p = subs.add_parser("upload", help="🌐 上传药方到 GitHub（需配置 GITHUB_TOKEN）")
    p.add_argument("--title", required=True, help="问题标题")
    p.add_argument("--prescription", required=True, help="修复方案")
    p.add_argument("--framework", required=True, help="框架标识")
    p.add_argument("--symptom", default=None)
    p.add_argument("--error-message", default=None)
    p.add_argument("--root-cause", default=None)
    p.add_argument("--severity", default="medium", choices=["low", "medium", "high", "critical"])
    p.add_argument("--complexity", default="moderate", choices=["simple", "moderate", "complex", "extreme"])
    p.add_argument("--tags", default=None, help="逗号分隔的标签")
    p.add_argument("--title-en", default=None)
    p.add_argument("--framework-version", default=None)
    p.add_argument("--language", default="python")
    p.add_argument("--contributor", default="anonymous")
    p.add_argument("--source-url", default=None)
    p.set_defaults(func=cmd_upload)

    # --- ranking ---
    p = subs.add_parser("ranking", help="🏆 查看个人排名")
    p.add_argument("username", help="GitHub 用户名")
    p.set_defaults(func=cmd_ranking)

    # --- leaderboard ---
    p = subs.add_parser("leaderboard", help="🏆 全球封神榜")
    p.add_argument("--top-n", "-n", type=int, default=10, help="显示前 N 名")
    p.set_defaults(func=cmd_leaderboard)

    # --- card ---
    p = subs.add_parser("card", help="📋 生成分享卡片")
    p.add_argument("username", help="GitHub 用户名")
    p.set_defaults(func=cmd_card)

    # --- frameworks ---
    p = subs.add_parser("frameworks", help="📋 支持框架列表")
    p.add_argument("--category", "-c", default=None, choices=["agent", "foundation", "infrastructure"])
    p.add_argument("--search", "-s", default=None, help="关键词搜索")
    p.set_defaults(func=cmd_frameworks)

    # --- taxonomy ---
    p = subs.add_parser("taxonomy", help="🧬 CHT 根因编码系统")
    p.add_argument("action", choices=["list", "lookup", "classify"], help="操作类型")
    p.add_argument("--code", default=None, help="CHT 编码（lookup 时使用）")
    p.add_argument("--text", default=None, help="要分类的文本（classify 时使用）")
    p.set_defaults(func=cmd_taxonomy)

    # --- trends ---
    p = subs.add_parser("trends", help="📈 CHT 趋势分析")
    p.add_argument("--framework", "-f", default=None)
    p.add_argument("--category", "-c", default=None)
    p.set_defaults(func=cmd_trends)

    # --- record ---
    p = subs.add_parser("record", help="📋 诊疗档案")
    p.add_argument("action", nargs="?", default="view", choices=["view", "resolve", "followup"])
    p.add_argument("--username", "-u", default=None)
    p.add_argument("--record-id", default=None)
    p.add_argument("--note", default=None)
    p.set_defaults(func=cmd_record)

    # --- subscribe ---
    p = subs.add_parser("subscribe", help="📬 框架订阅管理")
    p.add_argument("action", nargs="?", default="list", choices=["subscribe", "unsubscribe", "list", "check"])
    p.add_argument("--framework", "-f", default=None)
    p.add_argument("--username", "-u", default=None)
    p.set_defaults(func=cmd_subscribe)

    # --- digest ---
    p = subs.add_parser("digest", help="📊 本周药方摘要")
    p.set_defaults(func=cmd_digest)

    # --- epidemic ---
    p = subs.add_parser("epidemic", help="🦠 疫情预警")
    p.add_argument("--action", "-a", default="check", choices=["check", "scan", "report", "generate"])
    p.add_argument("--framework", "-f", default=None)
    p.set_defaults(func=cmd_epidemic)

    # --- serve ---
    p = subs.add_parser("serve", help="🚀 启动 Web 诊断服务")
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--reload", action="store_true", help="开发模式")
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_serve)

    # --- rebuild ---
    p = subs.add_parser("rebuild", help="🔄 重建向量索引")
    p.set_defaults(func=cmd_rebuild)

    # --- stats ---
    p = subs.add_parser("stats", help="📦 知识库统计")
    p.set_defaults(func=cmd_stats)

    # --- mine ---
    p = subs.add_parser("mine", help="⛏️ GitHub Issues 淘金")
    mine_sub = p.add_subparsers(dest="mine_action", help="淘金操作")

    ms = mine_sub.add_parser("search", help="搜索高频 Issues")
    ms.add_argument("--repo", required=True, help="owner/repo")
    ms.add_argument("--limit", type=int, default=10)
    ms.add_argument("--min-reactions", type=int, default=None)
    ms.add_argument("--min-comments", type=int, default=None)

    mb = mine_sub.add_parser("batch", help="批量淘金")
    mb.add_argument("--repo", default=None)
    mb.add_argument("--all", action="store_true", dest="mine_all")
    mb.add_argument("--limit", type=int, default=5)
    mb.add_argument("--save", action="store_true")

    p.set_defaults(func=cmd_mine)

    return parser


# ============================================================
# 🚀 主入口
# ============================================================


def main():
    """CyberHuaTuo CLI 主入口"""
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        # 没有子命令时显示帮助
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
