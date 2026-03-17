"""
CyberHuaTuo Static Rules Engine — 无 LLM 的六经脉静态规则扫描
当用户未提供 API Key 时，使用正则匹配和 AST 分析进行基础安全检测。
"""

from __future__ import annotations

import re

# ═══════════════════════════════════════════════════════════
# 六经脉检测规则
# ═══════════════════════════════════════════════════════════

# 经脉一：沙箱隔离 — 检测危险函数调用
DANGEROUS_FUNCTIONS = [
    (r"\beval\s*\(", "使用了 eval()，存在代码注入风险"),
    (r"\bexec\s*\(", "使用了 exec()，存在代码注入风险"),
    (r"\bos\.system\s*\(", "使用了 os.system()，建议使用 subprocess 并设置 shell=False"),
    (r"\bos\.popen\s*\(", "使用了 os.popen()，存在命令注入风险"),
    (r"subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True", "subprocess 使用 shell=True，存在命令注入风险"),
    (r"__import__\s*\(", "使用了 __import__()，可能存在动态模块加载风险"),
    (r"\bcompile\s*\(.*\bexec\b", "使用了 compile() + exec 模式"),
]

# 经脉二：密钥安全 — 检测硬编码密钥
SECRET_PATTERNS = [
    (r"""(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"]""",
     "发现疑似硬编码 API Key"),
    (r"""['\"]sk-[A-Za-z0-9\-_]{20,}['\"]""", "发现疑似 OpenAI API Key (sk-...)"),
    (r"""['\"]AKIA[A-Z0-9]{12,}['\"]""", "发现疑似 AWS Access Key (AKIA...)"),
    (r"""['\"]ghp_[A-Za-z0-9]{36,}['\"]""", "发现疑似 GitHub Personal Access Token (ghp_...)"),
    (r"""['\"]ghs_[A-Za-z0-9]{36,}['\"]""", "发现疑似 GitHub Server Token (ghs_...)"),
    (r"""['\"]glpat-[A-Za-z0-9\-_]{20,}['\"]""", "发现疑似 GitLab Token (glpat-...)"),
    (r"""['\"]xoxb-[0-9]{10,}-[A-Za-z0-9]+['\"]""", "发现疑似 Slack Bot Token"),
    (r"""['\"]AIza[A-Za-z0-9_\-]{35}['\"]""", "发现疑似 Google API Key (AIza...)"),
    (r"""password\s*=\s*['\"][^'\"]{4,}['\"]""", "发现疑似硬编码密码"),
]

# 经脉三：Prompt 安全 — 检测 Prompt 注入风险
PROMPT_RISKS = [
    (r"""f['\"].*\{.*user.*input.*\}.*['\"]""", "用户输入直接拼接进 Prompt，存在 Prompt 注入风险"),
    (r"""\.format\(.*user.*\)""", "用户输入通过 .format() 拼入 Prompt"),
    (r"""system_prompt.*=.*\+.*input""", "System Prompt 与用户输入拼接"),
    (r"""\buser_message\b.*\bsystem\b.*\bcontent\b""", "用户消息可能影响系统提示词"),
]

# 经脉四：输出安全 — 检测未消毒的输出使用
OUTPUT_RISKS = [
    (r"""\.execute\s*\(.*\bf['\"]""", "LLM 输出可能直接用于 SQL 执行（SQL 注入风险）"),
    (r"""innerHTML\s*=.*response""", "LLM 输出直接设置 innerHTML（XSS 风险）"),
    (r"""os\.system\s*\(.*(?:response|output|result)""", "LLM 输出直接用于系统命令（命令注入风险）"),
    (r"""subprocess.*\(.*(?:response|output|result)""", "LLM 输出传入 subprocess（命令注入风险）"),
]

# 经脉五：韧性设计 — 检测缺失的错误处理
RESILIENCE_PATTERNS = [
    (r"""(?:await\s+)?(?:acompletion|completion|chat\.completions\.create)\s*\((?:(?!try).)*$""",
     "LLM 调用未包裹在 try/except 中"),
    (r"""requests\.(?:get|post|put|delete)\s*\((?:(?!timeout).)*\)""",
     "HTTP 请求未设置 timeout"),
    (r"""httpx\.(?:get|post|put|delete|AsyncClient)\s*\((?:(?!timeout).)*\)""",
     "httpx 请求未设置 timeout"),
    (r"""while\s+True\s*:(?:(?!break|return).)*$""",
     "存在无限循环且无退出条件"),
]

# 经脉六：可观测性 — 检测日志中的敏感信息泄露
OBSERVABILITY_RISKS = [
    (r"""(?:print|logging\.(?:info|debug|warning|error))\s*\(.*(?:api[_-]?key|secret|password|token)""",
     "日志/打印中可能泄露敏感信息"),
    (r"""print\s*\(.*(?:response|completion)\.choices""",
     "打印完整 LLM 响应对象，建议结构化日志"),
]


def _scan_with_rules(
    code: str,
    rules: list[tuple[str, str]],
) -> list[dict]:
    """用正则规则扫描代码，返回发现的问题列表"""
    findings = []
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        # 跳过注释行
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        for pattern, description in rules:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "line": i,
                    "description": description,
                    "matched_text": stripped[:120],
                })
    return findings


def static_scan(code: str) -> dict:
    """
    对代码进行六经脉静态规则扫描（无需 LLM）

    Args:
        code: 源代码内容

    Returns:
        兼容 security_checkup() 格式的体检报告 dict
    """
    # 逐经脉扫描
    sandbox_findings = _scan_with_rules(code, DANGEROUS_FUNCTIONS)
    secret_findings = _scan_with_rules(code, SECRET_PATTERNS)
    prompt_findings = _scan_with_rules(code, PROMPT_RISKS)
    output_findings = _scan_with_rules(code, OUTPUT_RISKS)
    resilience_findings = _scan_with_rules(code, RESILIENCE_PATTERNS)
    observability_findings = _scan_with_rules(code, OBSERVABILITY_RISKS)

    # 计算各维度分数 (100 - 每个发现扣15分，最低0)
    def calc_score(findings: list) -> int:
        return max(0, 100 - len(findings) * 15)

    sandbox_score = calc_score(sandbox_findings)
    secret_score = calc_score(secret_findings)
    prompt_score = calc_score(prompt_findings)
    output_score = calc_score(output_findings)
    resilience_score = calc_score(resilience_findings)
    observability_score = calc_score(observability_findings)

    # 总分 = 六维度加权平均
    # 密钥安全和沙箱隔离权重稍高
    weights = [0.20, 0.25, 0.15, 0.15, 0.15, 0.10]
    scores = [sandbox_score, secret_score, prompt_score,
              output_score, resilience_score, observability_score]
    health_score = int(sum(w * s for w, s in zip(weights, scores)))

    # 确定等级
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

    def _status(score: int) -> str:
        if score >= 80:
            return "✅ 通过"
        elif score >= 50:
            return "⚠️ 警告"
        else:
            return "❌ 危险"

    dimensions = [
        {
            "name": "沙箱隔离",
            "emoji": "🛡️",
            "score": sandbox_score,
            "status": _status(sandbox_score),
            "findings": [f["description"] for f in sandbox_findings],
            "details": sandbox_findings,
            "advice": "使用 subprocess 时设置 shell=False，避免 eval/exec，考虑使用 RestrictedPython 或 Docker 沙箱隔离。"
            if sandbox_findings else "未发现沙箱隔离问题 ✅",
        },
        {
            "name": "密钥安全",
            "emoji": "🔑",
            "score": secret_score,
            "status": _status(secret_score),
            "findings": [f["description"] for f in secret_findings],
            "details": secret_findings,
            "advice": "将 API Key 迁移到环境变量或 Secrets Manager，使用 python-dotenv 加载 .env 文件。"
            if secret_findings else "未发现硬编码密钥 ✅",
        },
        {
            "name": "Prompt 安全",
            "emoji": "🧠",
            "score": prompt_score,
            "status": _status(prompt_score),
            "findings": [f["description"] for f in prompt_findings],
            "details": prompt_findings,
            "advice": "使用参数化模板而非字符串拼接，对用户输入进行消毒和长度限制。"
            if prompt_findings else "未发现 Prompt 注入风险 ✅",
        },
        {
            "name": "输出安全",
            "emoji": "🔒",
            "score": output_score,
            "status": _status(output_score),
            "findings": [f["description"] for f in output_findings],
            "details": output_findings,
            "advice": "对 LLM 输出在消费前进行验证和消毒，避免直接用于 SQL/命令执行。"
            if output_findings else "未发现输出注入风险 ✅",
        },
        {
            "name": "韧性设计",
            "emoji": "⏱️",
            "score": resilience_score,
            "status": _status(resilience_score),
            "findings": [f["description"] for f in resilience_findings],
            "details": resilience_findings,
            "advice": "为 API 调用添加 try/except、timeout 和重试机制，避免无限循环。"
            if resilience_findings else "韧性设计良好 ✅",
        },
        {
            "name": "可观测性",
            "emoji": "📊",
            "score": observability_score,
            "status": _status(observability_score),
            "findings": [f["description"] for f in observability_findings],
            "details": observability_findings,
            "advice": "使用结构化日志（如 structlog），确保敏感信息不出现在日志中。"
            if observability_findings else "可观测性良好 ✅",
        },
    ]

    # 收集 Top Issues
    all_findings = []
    for dim in dimensions:
        for f in dim.get("findings", []):
            all_findings.append(f)
    top_issues = all_findings[:3] if all_findings else ["未发现安全问题 🎉"]

    return {
        "health_score": health_score,
        "level": level,
        "scan_mode": "static_rules",
        "dimensions": dimensions,
        "top_issues": top_issues,
        "summary": f"静态规则扫描完成，健康评分 {health_score}/100（{level}）。"
        f"共检测到 {len(all_findings)} 个潜在问题。"
        if all_findings
        else f"静态规则扫描完成，健康评分 {health_score}/100（{level}）。代码安全状况良好！",
    }
