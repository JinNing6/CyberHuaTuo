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
        description="🩺 CyberHuaTuo 赛博华佗 - AI Agent 问题诊断知识库",
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
