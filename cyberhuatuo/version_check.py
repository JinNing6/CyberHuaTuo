"""
赛博华佗 · 版本检查模块
CyberHuaTuo · Version Update Checker

在 MCP Server 启动时后台异步检查 PyPI 最新版本，
如果发现有更新，在用户首次调用工具时输出温和提示。
"""

import logging
import threading
from typing import Optional

logger = logging.getLogger("cyberhuatuo.version_check")

# 全局状态：更新提示信息（线程安全写入，主线程读取）
_update_notice: Optional[str] = None
_check_done = False


def _do_check(current_version: str) -> None:
    """后台线程：查询 PyPI 最新版本并对比"""
    global _update_notice, _check_done
    try:
        import urllib.request
        import json

        url = "https://pypi.org/pypi/cyberhuatuo/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        # 设置 3 秒超时，绝不阻塞启动
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        latest = data.get("info", {}).get("version", "")
        if not latest:
            return

        # 简单版本比较（支持 major.minor.patch 格式）
        from packaging.version import Version
        try:
            if Version(latest) > Version(current_version):
                summary = data.get("info", {}).get("summary", "")
                _update_notice = (
                    f"\n⚡ **赛博华佗有新版本可用！**\n"
                    f"   当前版本 Current: `v{current_version}` → 最新版本 Latest: `v{latest}`\n"
                    f"   升级命令 Upgrade: `pip install --upgrade cyberhuatuo`\n"
                )
        except Exception:
            # packaging 不可用时，回退到字符串比较
            if latest != current_version:
                _update_notice = (
                    f"\n⚡ **赛博华佗有新版本可用！**\n"
                    f"   当前版本 Current: `v{current_version}` → 最新版本 Latest: `v{latest}`\n"
                    f"   升级命令 Upgrade: `pip install --upgrade cyberhuatuo`\n"
                )
    except ImportError:
        # packaging 库不可用时的简化处理
        try:
            import urllib.request
            import json

            url = "https://pypi.org/pypi/cyberhuatuo/json"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            latest = data.get("info", {}).get("version", "")
            if latest and latest != current_version:
                _update_notice = (
                    f"\n⚡ **赛博华佗有新版本可用！**\n"
                    f"   当前版本 Current: `v{current_version}` → 最新版本 Latest: `v{latest}`\n"
                    f"   升级命令 Upgrade: `pip install --upgrade cyberhuatuo`\n"
                )
        except Exception:
            pass
    except Exception as e:
        # 任何网络/解析异常静默忽略，绝不影响正常功能
        logger.debug(f"版本检查失败（不影响功能）: {e}")
    finally:
        _check_done = True


def start_version_check() -> None:
    """启动后台版本检查（非阻塞，daemon 线程）"""
    try:
        from . import __version__
        current = __version__
    except (ImportError, AttributeError):
        current = "0.0.0"

    thread = threading.Thread(
        target=_do_check,
        args=(current,),
        daemon=True,  # 主进程退出时自动终止
        name="cyberhuatuo-version-check",
    )
    thread.start()


def get_update_notice() -> str:
    """获取更新提示（如果有）。只返回一次，之后清除。"""
    global _update_notice
    if _update_notice:
        notice = _update_notice
        _update_notice = None  # 只提示一次
        return notice
    return ""
