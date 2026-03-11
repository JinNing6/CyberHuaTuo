"""
CyberHuaTuo CLI 入口
python -m cyberhuatuo serve

双击 start.bat 或运行此模块即可启动应用
"""

import argparse
import sys
import threading
import time
import webbrowser


def _open_browser(url: str, delay: float = 1.5):
    """延迟后自动打开浏览器"""
    def _open():
        time.sleep(delay)
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main():
    parser = argparse.ArgumentParser(
        prog="cyberhuatuo",
        description="🩺 CyberHuaTuo 赛博华佗 - AI 问题诊断知识库",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动本地诊断搜索服务")
    serve_parser.add_argument("--host", default=None, help="绑定地址 (默认 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=None, help="端口号 (默认 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    serve_parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")

    # rebuild 命令
    subparsers.add_parser("rebuild", help="重建向量索引")

    # stats 命令
    subparsers.add_parser("stats", help="显示知识库统计")

    # mine 命令
    mine_parser = subparsers.add_parser("mine", help="GitHub Issues 淘金")
    mine_sub = mine_parser.add_subparsers(dest="mine_action", help="淘金操作")

    # mine search
    mine_search = mine_sub.add_parser("search", help="搜索高频 Issues")
    mine_search.add_argument("--repo", required=True, help="目标仓库 (如 langchain-ai/langchain)")
    mine_search.add_argument("--limit", type=int, default=10, help="返回数量")
    mine_search.add_argument("--min-reactions", type=int, default=None, help="最低 reactions 数")
    mine_search.add_argument("--min-comments", type=int, default=None, help="最低 comments 数")

    # mine batch
    mine_batch = mine_sub.add_parser("batch", help="批量淘金（搜索+提炼+保存）")
    mine_batch.add_argument("--repo", default=None, help="目标仓库 (如 langchain-ai/langchain)")
    mine_batch.add_argument("--all", action="store_true", dest="mine_all", help="全部目标仓库")
    mine_batch.add_argument("--limit", type=int, default=5, help="每仓库淘金数量")
    mine_batch.add_argument("--save", action="store_true", help="自动保存到 cases/")

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        from .config import config

        host = args.host or config.HOST
        port = args.port or config.PORT
        url = f"http://{host}:{port}"

        print("🩺 CyberHuaTuo 赛博华佗")
        print("=" * 40)
        print("望闻问切，药到病除。")
        print("Diagnose. Prescribe. Cure.")
        print("=" * 40)

        # 自动打开浏览器
        if not args.no_browser:
            _open_browser(url)

        uvicorn.run(
            "cyberhuatuo.api:app",
            host=host,
            port=port,
            reload=args.reload,
        )

    elif args.command == "rebuild":
        from .indexer import build_index
        build_index(force_rebuild=True)

    elif args.command == "stats":
        from .indexer import scan_cases
        cases = scan_cases()

        print(f"\n🩺 CyberHuaTuo 知识库统计")
        print("=" * 40)
        print(f"📦 总病例数: {len(cases)}")

        # 按框架统计
        fw_stats = {}
        for c in cases:
            fw = c["metadata"].get("framework", "unknown")
            fw_stats[fw] = fw_stats.get(fw, 0) + 1

        if fw_stats:
            print(f"\n📊 按框架统计:")
            for fw, count in sorted(fw_stats.items(), key=lambda x: -x[1]):
                print(f"  {fw}: {count}")

    elif args.command == "mine":
        import asyncio as _aio
        from .issue_miner import IssueMiner, TARGET_REPOS

        miner = IssueMiner()

        if args.mine_action == "search":
            # 解析 owner/repo
            parts = args.repo.split("/")
            if len(parts) != 2:
                print("⚠️ --repo 格式应为 owner/repo（如 langchain-ai/langchain）")
                sys.exit(1)
            owner, repo = parts

            print(f"\n⛏️ 搜索 {owner}/{repo} 的高频 Issues ...")
            issues = _aio.run(miner.search_hot_issues(
                owner=owner, repo=repo,
                min_reactions=args.min_reactions,
                min_comments=args.min_comments,
                limit=args.limit,
            ))

            if not issues:
                print("  未找到匹配的高频 Issues")
            else:
                print(f"  找到 {len(issues)} 个高频 Issues:\n")
                for i, iss in enumerate(issues, 1):
                    print(f"  {i}. [{iss.framework}] #{iss.number} {iss.title}")
                    print(f"     👍 {iss.reactions_thumbs_up}  💬 {iss.comments_count}  {iss.url}")

        elif args.mine_action == "batch":
            if args.mine_all:
                # 全量淘金
                print(f"\n⛏️ 全量淘金 {len(TARGET_REPOS)} 个仓库 (每仓库 {args.limit} 个) ...")
                for tr in TARGET_REPOS:
                    result = _aio.run(miner.mine_repo(
                        owner=tr.owner, repo=tr.repo,
                        framework=tr.framework, limit=args.limit,
                        auto_save=args.save,
                    ))
                    refined_count = result.get("total_refined", 0)
                    print(f"  ✅ {tr.owner}/{tr.repo}: 提炼 {refined_count} 个病例")
            elif args.repo:
                parts = args.repo.split("/")
                if len(parts) != 2:
                    print("⚠️ --repo 格式应为 owner/repo")
                    sys.exit(1)
                owner, repo = parts

                result = _aio.run(miner.mine_repo(
                    owner=owner, repo=repo,
                    limit=args.limit, auto_save=args.save,
                ))
                refined = result.get("total_refined", 0)
                print(f"\n  ✅ 提炼 {refined} 个病例")
                if args.save:
                    for r in result.get("results", []):
                        if "saved" in r:
                            print(f"  💾 {r['saved']['filepath']}")
            else:
                print("⚠️ 请指定 --repo 或 --all")

        else:
            mine_parser.print_help()

    else:
        # 没有子命令时默认启动 serve
        from .config import config
        import uvicorn

        host = config.HOST
        port = config.PORT
        url = f"http://{host}:{port}"

        print("🩺 CyberHuaTuo 赛博华佗")
        print("=" * 40)
        print("望闻问切，药到病除。")
        print("Diagnose. Prescribe. Cure.")
        print("=" * 40)

        _open_browser(url)

        uvicorn.run(
            "cyberhuatuo.api:app",
            host=host,
            port=port,
        )


if __name__ == "__main__":
    main()
