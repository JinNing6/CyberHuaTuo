#!/usr/bin/env python3
"""
CyberHuaTuo Security Checkup — GitHub Action Entrypoint
赛博华佗安全体检 GitHub Action 入口脚本

流程:
  1. 读取环境变量（来自 action.yml inputs）
  2. 匹配并读取目标代码文件
  3. 根据是否有 API Key 选择扫描模式（LLM / 静态规则）
  4. 汇总各文件评分，生成总体报告
  5. 输出到 GITHUB_OUTPUT 和 GITHUB_STEP_SUMMARY
  6. 如果配置了 comment-on-pr,在 PR 下发表评论
  7. 如果分数低于 fail-on-score,以非零状态码退出
"""

from __future__ import annotations

import asyncio
import glob
import json
import os
import sys
from pathlib import Path

# 确保标准输出使用 UTF-8（处理 Windows GBK 环境下的 emoji 输出）
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 将 action/ 目录加入 sys.path 以导入 static_rules
ACTION_DIR = Path(__file__).parent
sys.path.insert(0, str(ACTION_DIR))

from static_rules import static_scan  # noqa: E402


# ═══════════════════════════════════════════════════════════
# 配置读取
# ═══════════════════════════════════════════════════════════

def get_input(name: str, default: str = "") -> str:
    """读取 GitHub Action 输入"""
    return os.environ.get(f"INPUT_{name.upper().replace('-', '_')}", default).strip()


def get_config() -> dict:
    """获取所有配置"""
    return {
        "api_key": get_input("api_key"),
        "provider": get_input("provider", "openai"),
        "model": get_input("model"),
        "scan_path": get_input("scan_path", "."),
        "file_pattern": get_input("file_pattern", "**/*.py"),
        "max_files": int(get_input("max_files", "10")),
        "fail_on_score": int(get_input("fail_on_score", "0")),
        "comment_on_pr": get_input("comment_on_pr", "true").lower() == "true",
        "github_token": get_input("github_token"),
    }


# ═══════════════════════════════════════════════════════════
# 文件扫描
# ═══════════════════════════════════════════════════════════

def collect_files(scan_path: str, file_pattern: str, max_files: int) -> list[Path]:
    """收集匹配的文件"""
    files = []
    patterns = [p.strip() for p in file_pattern.split(",")]

    for pattern in patterns:
        matched = glob.glob(
            os.path.join(scan_path, pattern),
            recursive=True,
        )
        for f in matched:
            fp = Path(f)
            if fp.is_file() and fp not in files:
                # 跳过常见无关目录
                parts = fp.parts
                skip_dirs = {
                    ".git", ".github", "__pycache__", "node_modules",
                    ".venv", "venv", ".tox", ".mypy_cache", ".ruff_cache",
                    "dist", "build", ".egg-info",
                }
                if any(part in skip_dirs for part in parts):
                    continue
                files.append(fp)

    # 按文件大小排序（优先扫描大文件，通常更重要）
    files.sort(key=lambda f: f.stat().st_size, reverse=True)
    return files[:max_files]


# ═══════════════════════════════════════════════════════════
# LLM 扫描（通过 litellm）
# ═══════════════════════════════════════════════════════════

CHECKUP_SYSTEM_PROMPT = """你是赛博华佗（CyberHuaTuo）的安全体检引擎，专精于 AI Agent 代码的六经脉安全审计。

请对代码进行以下六大维度的安全检查：

🛡️ 经脉一：沙箱隔离 — 代码执行是否有隔离保护？是否使用了危险的 eval()/exec()？
🔑 经脉二：密钥安全 — API Key 是否硬编码？是否通过安全方式管理密钥？
🧠 经脉三：Prompt 安全 — 是否有 Prompt 注入防御？用户输入是否做了消毒？
🔒 经脉四：输出安全 — LLM 输出是否在消费前做了验证？是否存在注入风险？
⏱️ 经脉五：韧性设计 — 是否有超时控制、重试、错误处理？
📊 经脉六：可观测性 — 是否有结构化日志、链路追踪、监控？

输出纯正 JSON（可被 json.loads 直接解析，不要 ```json 包裹）：
{
    "health_score": 65,
    "level": "🟡 需要调理",
    "dimensions": [
        {"name": "沙箱隔离", "emoji": "🛡️", "score": 30, "status": "❌ 危险", "findings": ["发现 xxx 问题"], "advice": "建议 xxx"},
        ...
    ],
    "top_issues": ["最紧急的问题1", "问题2", "问题3"],
    "summary": "总体评估描述"
}"""

CHECKUP_USER_TEMPLATE = """请对以下 AI Agent 代码进行六经脉安全体检：

文件：{filename}

```
{code}
```

输出 JSON 格式的体检报告。"""


async def llm_scan(
    code: str,
    filename: str,
    api_key: str,
    provider: str,
    model: str | None,
) -> dict:
    """使用 LLM 进行深度安全扫描"""
    try:
        import litellm

        # 确定模型
        resolved_model = model or ""
        if provider == "openai":
            resolved_model = resolved_model or "gpt-4o-mini"
        elif provider == "anthropic":
            resolved_model = resolved_model or "claude-3-5-sonnet-latest"
        elif provider == "deepseek":
            resolved_model = f"deepseek/{resolved_model or 'deepseek-chat'}"
        elif provider in ("google", "gemini"):
            resolved_model = f"gemini/{resolved_model or 'gemini-1.5-pro'}"
        elif provider == "groq":
            resolved_model = f"groq/{resolved_model or 'llama3-8b-8192'}"
        else:
            resolved_model = resolved_model or "gpt-4o-mini"

        messages = [
            {"role": "system", "content": CHECKUP_SYSTEM_PROMPT},
            {"role": "user", "content": CHECKUP_USER_TEMPLATE.format(
                filename=filename, code=code[:8000]  # 限 8000 字符防止 token 过大
            )},
        ]

        response = await litellm.acompletion(
            model=resolved_model,
            messages=messages,
            temperature=0.2,
            max_tokens=3000,
            api_key=api_key,
        )

        raw_content = response.choices[0].message.content.strip()

        # 清理 markdown 包裹
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        result = json.loads(raw_content.strip())
        result["scan_mode"] = "llm"
        return result

    except Exception as e:
        print(f"⚠️ LLM 扫描失败 ({filename}): {e}")
        print("🔄 降级到静态规则扫描...")
        result = static_scan(code)
        result["llm_error"] = str(e)
        return result


# ═══════════════════════════════════════════════════════════
# 报告生成
# ═══════════════════════════════════════════════════════════

def merge_reports(file_reports: list[dict]) -> dict:
    """合并多个文件的体检报告"""
    if not file_reports:
        return {
            "health_score": 100,
            "level": "🟢 强壮如虎",
            "dimensions": [],
            "top_issues": ["未扫描到目标文件"],
            "summary": "未找到匹配的代码文件进行扫描。",
            "files_scanned": 0,
        }

    if len(file_reports) == 1:
        report = file_reports[0]
        report["files_scanned"] = 1
        return report

    # 多文件：取各维度最低分（木桶原则）
    dim_names = ["沙箱隔离", "密钥安全", "Prompt 安全", "输出安全", "韧性设计", "可观测性"]
    dim_emojis = ["🛡️", "🔑", "🧠", "🔒", "⏱️", "📊"]

    merged_dims = []
    all_findings = []

    for i, dim_name in enumerate(dim_names):
        worst_score = 100
        all_dim_findings = []
        worst_advice = ""

        for report in file_reports:
            for dim in report.get("dimensions", []):
                if dim.get("name") == dim_name:
                    if dim.get("score", 100) < worst_score:
                        worst_score = dim["score"]
                        worst_advice = dim.get("advice", "")
                    all_dim_findings.extend(dim.get("findings", []))

        if worst_score >= 80:
            status = "✅ 通过"
        elif worst_score >= 50:
            status = "⚠️ 警告"
        else:
            status = "❌ 危险"

        # 去重 findings
        unique_findings = list(dict.fromkeys(all_dim_findings))

        merged_dims.append({
            "name": dim_name,
            "emoji": dim_emojis[i],
            "score": worst_score,
            "status": status,
            "findings": unique_findings[:5],  # 每维度最多5条
            "advice": worst_advice,
        })

        all_findings.extend(unique_findings)

    # 总分 = 各维度加权平均
    weights = [0.20, 0.25, 0.15, 0.15, 0.15, 0.10]
    scores = [d["score"] for d in merged_dims]
    health_score = int(sum(w * s for w, s in zip(weights, scores)))

    if health_score >= 90:
        level = "🟢 强壮如虎"
    elif health_score >= 70:
        level = "🔵 气血充沛"
    elif health_score >= 50:
        level = "🟡 需要调理"
    elif health_score >= 30:
        level = "🟠 体虚多病"
    else:
        level = "🔴 病入膏肓"

    scan_modes = set()
    for r in file_reports:
        scan_modes.add(r.get("scan_mode", "unknown"))

    return {
        "health_score": health_score,
        "level": level,
        "scan_mode": "/".join(sorted(scan_modes)),
        "dimensions": merged_dims,
        "top_issues": all_findings[:5],
        "summary": f"扫描了 {len(file_reports)} 个文件，总体健康评分 {health_score}/100（{level}）。",
        "files_scanned": len(file_reports),
    }


def generate_markdown_report(report: dict, file_details: list[dict]) -> str:
    """生成 Markdown 格式的体检报告"""
    score = report.get("health_score", 0)
    level = report.get("level", "未知")
    scan_mode = report.get("scan_mode", "unknown")

    # 评分进度条
    bar_filled = score // 5
    bar_empty = 20 - bar_filled
    progress_bar = "█" * bar_filled + "░" * bar_empty

    md = []
    md.append("## 🩺 CyberHuaTuo Security Checkup Report")
    md.append("")
    md.append(f"> **赛博华佗 · 六经脉安全体检**")
    md.append("")

    # 总体评分
    md.append("### 📊 总体评分")
    md.append("")
    md.append(f"| 项目 | 结果 |")
    md.append(f"|------|------|")
    md.append(f"| 健康评分 | **{score}/100** {level} |")
    md.append(f"| 评分条 | `{progress_bar}` |")
    md.append(f"| 扫描模式 | {'🧠 AI 深度分析' if 'llm' in scan_mode else '📋 静态规则扫描'} |")
    md.append(f"| 扫描文件数 | {report.get('files_scanned', 0)} |")
    md.append("")

    # 六经脉详情
    md.append("### 🔮 六经脉诊断详情")
    md.append("")
    md.append("| 经脉 | 评分 | 状态 |")
    md.append("|------|------|------|")

    for dim in report.get("dimensions", []):
        emoji = dim.get("emoji", "")
        name = dim.get("name", "")
        dim_score = dim.get("score", 0)
        status = dim.get("status", "")
        md.append(f"| {emoji} {name} | {dim_score}/100 | {status} |")

    md.append("")

    # 发现的问题
    all_findings_exist = False
    for dim in report.get("dimensions", []):
        if dim.get("findings"):
            all_findings_exist = True
            break

    if all_findings_exist:
        md.append("### ⚠️ 发现的问题")
        md.append("")
        for dim in report.get("dimensions", []):
            findings = dim.get("findings", [])
            if findings:
                md.append(f"**{dim.get('emoji', '')} {dim.get('name', '')}**")
                for finding in findings[:3]:
                    md.append(f"- {finding}")
                advice = dim.get("advice", "")
                if advice and "✅" not in advice:
                    md.append(f"  - 💊 **药方**: {advice}")
                md.append("")

    # Top Issues
    top_issues = report.get("top_issues", [])
    if top_issues and top_issues[0] != "未发现安全问题 🎉":
        md.append("### 🚨 最紧急的问题")
        md.append("")
        for i, issue in enumerate(top_issues[:3], 1):
            md.append(f"{i}. {issue}")
        md.append("")

    # 文件明细
    if file_details:
        md.append("<details>")
        md.append("<summary>📁 文件扫描明细</summary>")
        md.append("")
        md.append("| 文件 | 评分 | 模式 |")
        md.append("|------|------|------|")
        for fd in file_details:
            filename = fd.get("filename", "")
            file_score = fd.get("health_score", 0)
            mode = "🧠 AI" if fd.get("scan_mode") == "llm" else "📋 静态"
            md.append(f"| `{filename}` | {file_score}/100 | {mode} |")
        md.append("")
        md.append("</details>")
        md.append("")

    # 脚注
    md.append("---")
    md.append("")
    md.append(
        "*此报告由 [🩺 CyberHuaTuo 赛博华佗](https://github.com/JinNing6/CyberHuaTuo) 自动生成 "
        "| [安装此 Action](https://github.com/JinNing6/CyberHuaTuo/tree/main/action)*"
    )

    return "\n".join(md)


# ═══════════════════════════════════════════════════════════
# PR 评论
# ═══════════════════════════════════════════════════════════

def post_pr_comment(markdown_report: str, github_token: str) -> bool:
    """在 PR 下发表或更新体检报告评论"""
    import httpx

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name != "pull_request":
        print("ℹ️ 非 PR 事件，跳过评论")
        return False

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.exists(event_path):
        print("⚠️ 无法读取事件信息")
        return False

    with open(event_path) as f:
        event_data = json.load(f)

    pr_number = event_data.get("pull_request", {}).get("number")
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    if not pr_number or not repo:
        print("⚠️ 无法获取 PR 编号或仓库名")
        return False

    api_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # 查找是否已有赛博华佗的评论（更新而非重复发布）
    COMMENT_MARKER = "CyberHuaTuo Security Checkup Report"

    try:
        resp = httpx.get(api_url, headers=headers, timeout=30)
        if resp.status_code == 200:
            comments = resp.json()
            for comment in comments:
                if COMMENT_MARKER in comment.get("body", ""):
                    # 更新已有评论
                    update_url = f"https://api.github.com/repos/{repo}/issues/comments/{comment['id']}"
                    update_resp = httpx.patch(
                        update_url,
                        headers=headers,
                        json={"body": markdown_report},
                        timeout=30,
                    )
                    if update_resp.status_code == 200:
                        print(f"✅ 已更新 PR #{pr_number} 的体检报告评论")
                        return True

        # 创建新评论
        create_resp = httpx.post(
            api_url,
            headers=headers,
            json={"body": markdown_report},
            timeout=30,
        )
        if create_resp.status_code == 201:
            print(f"✅ 已在 PR #{pr_number} 发表体检报告评论")
            return True
        else:
            print(f"⚠️ PR 评论失败: {create_resp.status_code} {create_resp.text[:200]}")
            return False

    except Exception as e:
        print(f"⚠️ PR 评论异常: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

async def main():
    """入口"""
    print("🩺 CyberHuaTuo Security Checkup — 赛博华佗安全体检")
    print("═" * 50)

    config = get_config()

    # 1. 收集文件
    print(f"\n📂 扫描路径: {config['scan_path']}")
    print(f"🔍 匹配模式: {config['file_pattern']}")

    files = collect_files(
        config["scan_path"],
        config["file_pattern"],
        config["max_files"],
    )

    if not files:
        print("⚠️ 未找到匹配的代码文件")
        report = merge_reports([])
        _output_results(config, report, [], "")
        return

    print(f"📁 找到 {len(files)} 个文件待扫描\n")

    # 2. 逐文件扫描
    use_llm = bool(config["api_key"])
    scan_mode = "🧠 AI 深度分析" if use_llm else "📋 静态规则扫描"
    print(f"🔬 扫描模式: {scan_mode}\n")

    file_reports = []
    file_details = []

    for i, filepath in enumerate(files, 1):
        relative_path = str(filepath)
        print(f"  [{i}/{len(files)}] 扫描 {relative_path}...")

        try:
            code = filepath.read_text(encoding="utf-8", errors="ignore")

            if use_llm:
                result = await llm_scan(
                    code=code,
                    filename=relative_path,
                    api_key=config["api_key"],
                    provider=config["provider"],
                    model=config["model"] or None,
                )
            else:
                result = static_scan(code)

            file_reports.append(result)
            file_details.append({
                "filename": relative_path,
                "health_score": result.get("health_score", 0),
                "scan_mode": result.get("scan_mode", "unknown"),
            })

            score = result.get("health_score", 0)
            level = result.get("level", "")
            print(f"        → {score}/100 {level}")

        except Exception as e:
            print(f"        ⚠️ 扫描失败: {e}")

    # 3. 合并报告
    print(f"\n{'═' * 50}")
    merged_report = merge_reports(file_reports)

    total_score = merged_report["health_score"]
    total_level = merged_report["level"]
    print(f"\n🏥 总体健康评分: {total_score}/100 {total_level}")

    # 4. 生成 Markdown 报告
    markdown_report = generate_markdown_report(merged_report, file_details)

    # 5. 输出结果
    _output_results(config, merged_report, file_details, markdown_report)


def _output_results(
    config: dict,
    report: dict,
    file_details: list[dict],
    markdown_report: str,
):
    """输出到 GITHUB_OUTPUT / GITHUB_STEP_SUMMARY / PR 评论"""
    total_score = report.get("health_score", 0)

    # 写入 GITHUB_OUTPUT
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"health-score={total_score}\n")
            # JSON 报告使用 heredoc 格式写入（避免换行问题）
            report_json = json.dumps(report, ensure_ascii=False)
            f.write(f"report-json<<EOF\n{report_json}\nEOF\n")
        print("📤 已写入 GITHUB_OUTPUT")

    # 写入 GITHUB_STEP_SUMMARY
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file and markdown_report:
        with open(summary_file, "a") as f:
            f.write(markdown_report)
        print("📋 已写入 GITHUB_STEP_SUMMARY")

    # PR 评论
    if config.get("comment_on_pr") and config.get("github_token") and markdown_report:
        post_pr_comment(markdown_report, config["github_token"])

    # 检查是否需要失败
    fail_threshold = config.get("fail_on_score", 0)
    if fail_threshold > 0 and total_score < fail_threshold:
        print(f"\n❌ 健康评分 {total_score} 低于阈值 {fail_threshold}，Action 标记为失败")
        sys.exit(1)
    else:
        print(f"\n✅ 安全体检完成")


if __name__ == "__main__":
    asyncio.run(main())
