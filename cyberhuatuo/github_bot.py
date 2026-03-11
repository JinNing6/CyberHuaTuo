"""
🤖 CyberHuaTuo GitHub Bot — 入口脚本
被 GitHub Actions workflow 调用，自动在 Issue 中回复匹配的药方

用法：
    python -m cyberhuatuo.github_bot \\
        --event-type "issues" \\
        --event-path "/path/to/event.json"

环境变量：
    GITHUB_TOKEN      — GitHub Actions 自动提供
    GITHUB_REPOSITORY — 格式 "owner/repo"
    BOT_MIN_SCORE     — 最低匹配分数（默认 15）
    BOT_MAX_RESULTS   — 最大返回药方数（默认 3）
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 项目根目录（github_bot.py 在 cyberhuatuo/ 下）
ROOT_DIR = Path(__file__).parent.parent.resolve()


def _github_api_request(method: str, url: str, token: str, data: dict | None = None) -> dict:
    """
    使用 urllib 发送 GitHub API 请求（避免依赖 httpx/requests）
    """
    import urllib.error
    import urllib.request

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    if body:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ GitHub API 错误 {e.code}: {error_body}", file=sys.stderr)
        raise


def _post_comment(token: str, repo: str, issue_number: int, body: str) -> bool:
    """在 Issue 上发表评论"""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    try:
        _github_api_request("POST", url, token, {"body": body})
        print(f"✅ 已发表评论到 Issue #{issue_number}")
        return True
    except Exception as e:
        print(f"❌ 发表评论失败: {e}", file=sys.stderr)
        return False


def _add_label(token: str, repo: str, issue_number: int, label: str) -> bool:
    """为 Issue 添加标签"""
    # 先确保标签存在（标签可能已存在，忽略错误）
    import contextlib
    label_url = f"https://api.github.com/repos/{repo}/labels"
    with contextlib.suppress(Exception):
        _github_api_request("POST", label_url, token, {
            "name": label,
            "color": "00D09C",
            "description": "CyberHuaTuo Bot 已处理",
        })

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    try:
        _github_api_request("POST", url, token, {"labels": [label]})
        return True
    except Exception:
        return False


def _get_issue_labels(token: str, repo: str, issue_number: int) -> list[str]:
    """获取 Issue 的当前标签"""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    try:
        labels = _github_api_request("GET", url, token)
        return [label["name"] for label in labels]
    except Exception:
        return []


def _is_bot_comment(comment_body: str) -> bool:
    """检查评论是否是 Bot 自身的评论（防止无限循环）"""
    bot_signatures = [
        "🩺 赛博华佗 · 自动诊断",
        "CyberHuaTuo · Auto Diagnosis",
        "此回复由 [CyberHuaTuo 赛博华佗]",
    ]
    return any(sig in comment_body for sig in bot_signatures)


def _detect_mention(text: str) -> bool:
    """检测文本中是否包含 @CyberHuaTuo 提及"""
    import re
    # 匹配 @CyberHuaTuo（不区分大小写）
    return bool(re.search(r"@cyber\s*hua\s*tuo", text, re.IGNORECASE))


def handle_issue_opened(event: dict, token: str, repo: str) -> None:
    """处理新 Issue 打开事件"""
    issue = event.get("issue", {})
    issue_number = issue.get("number")
    issue_title = issue.get("title", "")
    issue_body = issue.get("body", "")
    issue.get("user", {}).get("login", "")

    if not issue_number:
        print("⚠️ 无法获取 Issue 编号", file=sys.stderr)
        return

    print(f"🩺 处理新 Issue #{issue_number}: {issue_title}")

    # 检查是否已处理
    labels = _get_issue_labels(token, repo, issue_number)
    if "bot:diagnosed" in labels:
        print(f"⏭️ Issue #{issue_number} 已被 Bot 诊断过，跳过")
        return

    # 加载药方库
    from .bot_matcher import format_bot_reply, load_prescriptions, match_prescriptions

    cases_dir = ROOT_DIR / "cases"
    prescriptions = load_prescriptions(cases_dir)
    print(f"📚 已加载 {len(prescriptions)} 个药方")

    if not prescriptions:
        print("⚠️ 药方库为空，跳过")
        return

    # 匹配
    min_score = float(os.getenv("BOT_MIN_SCORE", "15"))
    max_results = int(os.getenv("BOT_MAX_RESULTS", "3"))

    matches = match_prescriptions(
        issue_title=issue_title,
        issue_body=issue_body,
        prescriptions=prescriptions,
        top_k=max_results,
        min_score=min_score,
    )

    print(f"🔍 找到 {len(matches)} 个匹配药方")

    if not matches:
        print("ℹ️ 未找到匹配药方，不回复")
        return

    # 生成回复
    repo_url = f"https://github.com/{repo}"
    reply = format_bot_reply(matches, trigger_type="auto", repo_url=repo_url)

    if reply:
        _post_comment(token, repo, issue_number, reply)
        _add_label(token, repo, issue_number, "bot:diagnosed")


def handle_issue_comment(event: dict, token: str, repo: str) -> None:
    """处理 Issue 评论事件（@CyberHuaTuo 提及触发）"""
    comment = event.get("comment", {})
    comment_body = comment.get("body", "")
    comment.get("user", {}).get("login", "")

    issue = event.get("issue", {})
    issue_number = issue.get("number")
    issue_title = issue.get("title", "")
    issue_body = issue.get("body", "")

    if not issue_number:
        print("⚠️ 无法获取 Issue 编号", file=sys.stderr)
        return

    # 防止响应 Bot 自身的评论
    if _is_bot_comment(comment_body):
        print("⏭️ 跳过 Bot 自身的评论")
        return

    # 检查是否提到 @CyberHuaTuo
    if not _detect_mention(comment_body):
        print("⏭️ 评论中未提到 @CyberHuaTuo，跳过")
        return

    print(f"🩺 收到 @CyberHuaTuo 提及，处理 Issue #{issue_number}")

    # 加载药方库
    from .bot_matcher import format_bot_reply, load_prescriptions, match_prescriptions

    cases_dir = ROOT_DIR / "cases"
    prescriptions = load_prescriptions(cases_dir)
    print(f"📚 已加载 {len(prescriptions)} 个药方")

    # 将评论内容 + Issue 标题/正文合并作为查询
    query_title = issue_title
    query_body = f"{comment_body}\n\n---\n\n{issue_body}"

    # 匹配
    min_score = float(os.getenv("BOT_MIN_SCORE", "15"))
    max_results = int(os.getenv("BOT_MAX_RESULTS", "3"))

    matches = match_prescriptions(
        issue_title=query_title,
        issue_body=query_body,
        prescriptions=prescriptions,
        top_k=max_results,
        min_score=min_score,
    )

    print(f"🔍 找到 {len(matches)} 个匹配药方")

    # 生成回复（即使没有匹配也回复，因为是被 @提及的）
    repo_url = f"https://github.com/{repo}"
    reply = format_bot_reply(matches, trigger_type="mention", repo_url=repo_url)

    if reply:
        _post_comment(token, repo, issue_number, reply)


def main() -> None:
    """Bot 主入口"""
    parser = argparse.ArgumentParser(description="CyberHuaTuo GitHub Bot")
    parser.add_argument(
        "--event-type",
        required=True,
        choices=["issues", "issue_comment"],
        help="GitHub 事件类型",
    )
    parser.add_argument(
        "--event-path",
        required=True,
        help="GitHub 事件 JSON 文件路径",
    )
    args = parser.parse_args()

    # 读取环境变量
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ 未设置 GITHUB_TOKEN 环境变量", file=sys.stderr)
        sys.exit(1)

    repo = os.getenv("GITHUB_REPOSITORY")
    if not repo:
        print("❌ 未设置 GITHUB_REPOSITORY 环境变量", file=sys.stderr)
        sys.exit(1)

    # 读取事件数据
    event_path = Path(args.event_path)
    if not event_path.exists():
        print(f"❌ 事件文件不存在: {event_path}", file=sys.stderr)
        sys.exit(1)

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    print("🤖 CyberHuaTuo Bot 启动")
    print(f"📋 事件类型: {args.event_type}")
    print(f"📦 仓库: {repo}")

    # 分发事件
    if args.event_type == "issues":
        handle_issue_opened(event, token, repo)
    elif args.event_type == "issue_comment":
        handle_issue_comment(event, token, repo)
    else:
        print(f"⚠️ 不支持的事件类型: {args.event_type}", file=sys.stderr)

    print("🤖 CyberHuaTuo Bot 执行完毕")


if __name__ == "__main__":
    main()
