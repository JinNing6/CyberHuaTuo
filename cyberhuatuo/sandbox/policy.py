"""
TEC 策略引擎 — Policy Engine v2 (Agent-Declared Scope)
Transient Execution Capsule — Policy Engine

核心范式升级:
    v1: TEC 用关键词解析用户意图 → 覆盖率低，需要维护词典
    v2: Agent 本身就是 LLM，它发出的 tool_call 即 structured output
        → TEC 不重复做意图解析，只做「验偏」

三大防线:
1. Agent-Declared Scope — Agent 首次调用自动声明安全边界
2. Semantic Drift Detection — 检测 Agent 行为偏离声明范围
3. Blast Radius Circuit Breaker — 统计学熔断器（不变）

设计哲学:
    Agent 说「我要做 X」—— 好的，你只能做 X，不能偷偷做 Y。
    不需要 TEC 自己去猜用户想要什么（那是 Agent 的工作），
    TEC 只需要保证 Agent 说到做到、不越权。
"""

from __future__ import annotations

import logging
import math
import re
import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field

from cyberhuatuo.sandbox.schemas import (
    ActionType,
    BlastRadiusEstimate,
    CapabilityToken,
    CircuitState,
    PolicyAction,
    PolicyDecision,
    SafetyLevel,
    ToolCall,
    ToolSafetyProfile,
)
from cyberhuatuo.sandbox.classifier import ToolDNA, ActionAffinityEngine

logger = logging.getLogger("tec.policy")


# ─────────────── 安全规则表 ──────────────────────────

# 静态 fallback 表 — 仅在无 tool schema 时使用。
# 当有 schema 时，ActionAffinityEngine 自动推导同族关系。
_STATIC_FAMILIES: dict[str, set[str]] = {
    "read":     {"read", "get", "list", "search", "query", "find",
                 "lookup", "check", "status", "exists", "count",
                 "describe", "metadata", "info", "show", "view"},
    "create":   {"create", "new", "add", "insert", "draft",
                 "compose", "save", "append", "write"},
    "reply":    {"reply", "draft", "forward", "send", "compose"},
    "update":   {"update", "edit", "modify", "patch", "rename",
                 "archive", "mark_read", "mark_unread", "star",
                 "unstar", "pin", "unpin"},
    "send":     {"send", "draft", "compose", "reply", "forward",
                 "edit"},  # edit 和 send 同族（先编辑后发送）
}

# 向后兼容
SAFE_ACTION_FAMILIES = _STATIC_FAMILIES

# 高危动作 — 必须用户显式声明才允许
# Cross-Tool + Exfil 检测提供额外层拦截
DANGEROUS_ACTIONS: set[str] = {
    # 删除/销毁类
    "delete", "remove", "drop", "truncate", "purge", "destroy",
    "wipe", "erase", "format", "revoke", "terminate", "kill",
    "uninstall", "clear", "reset",
    # 金融/交易类
    "transfer", "pay", "withdraw", "refund", "charge",
    "subscribe", "cancel", "purchase", "apply",
    "send_money", "trade", "buy", "sell", "checkout",
    "donate", "book", "schedule_payment", "schedule",
    # 修改/更新高敏感类
    "update_scheduled_transaction", "update_payment", "update_contact",
    "change_password", "create_user", "update",
    # 执行/系统类
    "exec", "execute", "eval", "run", "shell",
    "shutdown", "emergency_brake", "reboot",
    # 数据发送/外传类
    "send", "post", "share", "forward", "export",
    "send_message", "post_review", "submit_form",
    # 权限/访问控制类
    "invite_user", "grant", "grant_root",
}

# ─────────── 敏感目标检测 ─────────────────────────────
# 即使是 read/query 操作，如果目标是敏感资产也需要拦截

_SENSITIVE_TARGET_RES: list[re.Pattern] = [
    # 系统文件
    re.compile(r"(/etc/shadow|/etc/passwd|/etc/sudoers)", re.I),
    re.compile(r"(\.ssh/|id_rsa|id_ed25519|authorized_keys)", re.I),
    # 凭据文件
    re.compile(r"(\.env|\.credentials|secrets?\.ya?ml)", re.I),
    re.compile(r"(api[_-]?key|api[_-]?secret|oauth[_-]?token)", re.I),
    re.compile(r"(master\.key|encryption[_-]?key)", re.I),
    # 数据库凭据
    re.compile(r"(database\.ya?ml|db[_-]?config|connection[_-]?string)", re.I),
    # Chrome/Browser secrets
    re.compile(r"(Login Data|Cookies|Web Data|chrome)", re.I),
    # 通配符批量 + 敏感域
    re.compile(r"(all_users|all_patients|all_contacts)", re.I),
    # 外部恶意目标
    re.compile(r"(evil\.com|attacker|malicious|hack)", re.I),
    # Web Shell / 后门写入目标
    re.compile(r"(\.php|\.jsp|\.asp)$", re.I),  # 可执行脚本文件
    re.compile(r"(/var/www/|/srv/www/|public_html/|htdocs/)", re.I),  # Web 目录
    re.compile(r"(crontab|/etc/cron|/var/spool/cron)", re.I),  # 定时任务
    re.compile(r"(\.bashrc|\.profile|\.bash_profile)", re.I),  # Shell 启动脚本
    # 广泛批量目标
    re.compile(r"^\*$"),  # 纯通配符
]

# 超大批量阈值（即使是 read，查 99999 条也可疑）
_BULK_READ_THRESHOLD = 1000


def _is_sensitive_target(target: str, target_count: int = 1) -> bool:
    """检查目标是否是敏感资产"""
    for pat in _SENSITIVE_TARGET_RES:
        if pat.search(target):
            return True
    if target_count > _BULK_READ_THRESHOLD:
        return True
    return False


def _detect_sensitive_in_call(tool_call: ToolCall) -> str | None:
    """
    检测 ToolCall 中是否涉及敏感目标。

    扫描范围：
    1. tool_call.target（主目标）
    2. tool_call.parameters 中的所有字符串值（递归扫描）

    这解决了仅检查 target 字段不够的问题：LLM 可能将敏感路径
    放在 path/url/command 等参数中，而 target 为空。

    返回: 触发原因字符串（如发现）；否则返回 None。
    """
    # 收集所有需要扫描的字符串值
    values_to_check: list[str] = []

    if tool_call.target:
        values_to_check.append(tool_call.target)

    # 递归提取 parameters 中的所有字符串值
    def _extract_strings(obj):
        if isinstance(obj, str):
            values_to_check.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                _extract_strings(v)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                _extract_strings(item)

    if tool_call.parameters:
        _extract_strings(tool_call.parameters)

    # 对每个值进行敏感目标匹配
    for val in values_to_check:
        for pat in _SENSITIVE_TARGET_RES:
            if pat.search(val):
                return (
                    f"敏感目标: '{val[:80]}' 匹配敏感模式 "
                    f"(action={tool_call.action}, count={tool_call.target_count})"
                )

    # 超大批量
    if tool_call.target_count > _BULK_READ_THRESHOLD:
        return (
            f"超大批量操作: count={tool_call.target_count} "
            f"(阈值={_BULK_READ_THRESHOLD})"
        )

    return None


# ─────────── 批量破坏意图检测 ─────────────────────────────
# 检测「破坏性动作 + 批量/通配符目标」的组合模式
# 这是 Batch Destruction 攻击的核心特征

_DESTRUCTIVE_ACTIONS: set[str] = {
    "delete", "remove", "drop", "truncate", "purge", "destroy",
    "wipe", "erase", "clear", "reset", "format",
}

# 参数中表示「全部/批量」操作的模式
_BATCH_TARGET_RES: list[re.Pattern] = [
    re.compile(r"\ball\b", re.I),          # "all emails", "all files"
    re.compile(r"^\*$"),                     # 通配符 *
    re.compile(r"\*\.\w+", re.I),            # *.txt, *.log
    re.compile(r"every\s+", re.I),           # "every file"
    re.compile(r"entire\s+", re.I),          # "entire directory"
    re.compile(r"\b(inbox|all_\w+)\b", re.I),  # inbox 全量操作
]

# SQL 破坏语句模式
_SQL_DESTRUCTIVE_RES: list[re.Pattern] = [
    re.compile(r"\bDROP\s+(TABLE|DATABASE|INDEX|VIEW)\b", re.I),
    re.compile(r"\bDELETE\s+FROM\b", re.I),
    re.compile(r"\bTRUNCATE\s+(TABLE)?\b", re.I),
    re.compile(r"\bDROP\s+IF\s+EXISTS\b", re.I),
]


def _is_batch_destruction(tool_call: ToolCall) -> str | None:
    """
    批量破坏意图检测。

    检测「破坏性操作 + 批量目标」的组合模式：
    1. action ∈ 破坏性动作集 且 target_count > 1
    2. action ∈ 破坏性动作集 且 参数含有通配符/批量关键词
    3. database_query/system_exec 中含有 SQL 破坏语句

    返回: 触发原因字符串（如发现）；否则返回 None。
    """
    action = tool_call.action.lower()

    # ── 检测 1: 破坏性动作 + 批量目标 ──
    if action in _DESTRUCTIVE_ACTIONS:
        # 批量 target_count
        if tool_call.target_count > 1:
            return (
                f"批量破坏: '{action}' 影响 {tool_call.target_count} 个目标"
            )

        # 扫描参数中的批量/通配符模式
        all_values: list[str] = []
        if tool_call.target:
            all_values.append(tool_call.target)

        def _extract(obj):
            if isinstance(obj, str):
                all_values.append(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _extract(v)
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    _extract(item)

        if tool_call.parameters:
            _extract(tool_call.parameters)

        for val in all_values:
            for pat in _BATCH_TARGET_RES:
                if pat.search(val):
                    return (
                        f"批量破坏: '{action}' 目标含批量模式 "
                        f"'{val[:60]}' (匹配: {pat.pattern})"
                    )

    # ── 检测 2: SQL 破坏语句（无论 action 名称） ──
    # 扫描 query/command 等参数
    sql_params = (
        tool_call.parameters.get("query", "")
        if tool_call.parameters else ""
    )
    cmd_params = (
        tool_call.parameters.get("command", "")
        if tool_call.parameters else ""
    )
    for text in [sql_params, cmd_params]:
        if text:
            for pat in _SQL_DESTRUCTIVE_RES:
                if pat.search(text):
                    return (
                        f"SQL/系统破坏: 检测到破坏语句 "
                        f"'{text[:80]}' (匹配: {pat.pattern})"
                    )

    return None


# ─────────── 跨工具提权检测 ─────────────────────────────
# 核心检测逻辑：先从 A 工具读数据，再向 B 工具写数据 → 高危

_WRITE_ACTIONS: set[str] = {
    "send", "post", "share", "forward", "export", "send_message",
    "send_money", "transfer", "edit", "create", "write",
    "invite_user", "submit_form", "post_review", "book",
    "trade", "buy", "sell", "purchase", "checkout",
    "update", "update_payment", "update_contact",
    "change_password", "create_user", "grant_root", "grant",
    "delete", "remove", "cancel", "destroy", "drop", "truncate",
    "shutdown", "emergency_brake",
}

_READ_ACTIONS: set[str] = {
    "read", "get", "list", "search", "query", "find",
    "get_unread", "get_events", "get_transactions",
    "get_scheduled", "get_balance", "get_contacts",
    "get_reservations", "get_user_profile", "get_payment",
    "get_security", "get_addresses", "get_settings",
    "list_connections", "list_events", "list_orders",
    "list_messages", "read_channel", "read_url",
    "read_reviews", "view", "show", "status", "analyze",
    "get_quote", "get_price", "get_history", "get_card",
    "search_hotels", "compare", "translate", "generate",
}


def _is_cross_tool_escalation(
    current_call: ToolCall, call_history: list[ToolCall]
) -> tuple[bool, str]:
    """
    跨工具提权检测:
    Agent 先从 Tool-A 读取数据，然后对 Tool-B 执行**高危**写/发送操作。
    这是 AgentDojo / InjectAgent 等 benchmark 的核心攻击模式。

    精细化: 仅在写入操作本身是高危操作(在 DANGEROUS_ACTIONS 中)时才触发。
    这避免了合法的跨工具工作流（如 查日程→发通知）被误拦。
    """
    current_action = current_call.action.lower()

    # 只有当写入操作是高危操作时才检查跨工具
    if current_action not in DANGEROUS_ACTIONS:
        return False, ""
    if current_action not in _WRITE_ACTIONS:
        return False, ""

    current_tool = current_call.tool.lower()

    # 检查历史中是否有来自不同工具的读取操作
    for prev in call_history:
        prev_tool = prev.tool.lower()
        prev_action = prev.action.lower()
        if prev_tool != current_tool and prev_action in _READ_ACTIONS:
            return True, (
                f"跨工具提权: 从 '{prev.tool}.{prev.action}' 读取 "
                f"→ 向 '{current_call.tool}.{current_action}' 写入"
            )

    return False, ""


# ─────────── 外传数据流检测 ─────────────────────────────
# 检测任何向外部发送数据的操作（邮件、webhook、HTTP POST）

_EXFIL_ACTIONS: set[str] = {
    "send", "post", "forward", "export", "share",
    "send_message", "send_money", "submit_form",
}

_EXTERNAL_TARGET_RES: list[re.Pattern] = [
    re.compile(r"@", re.I),           # 邮件地址
    re.compile(r"https?://", re.I),   # HTTP URL
    re.compile(r"(evil|attacker|hack|malicious|phishing)", re.I),
    re.compile(r"(external|unknown|foreign)", re.I),
]


def _is_outbound_exfil(
    call: ToolCall, call_history: list[ToolCall]
) -> tuple[bool, str]:
    """
    外传数据流检测:
    Agent 读取了数据后通过 send/post/share 发送到外部目标。
    """
    action = call.action.lower()
    if action not in _EXFIL_ACTIONS:
        return False, ""

    target = call.target or ""

    # 检查目标是否是外部
    for pat in _EXTERNAL_TARGET_RES:
        if pat.search(target):
            # 进一步检查：之前是否有读取操作（说明是先读后传）
            has_prior_read = any(
                tc.action.lower() in _READ_ACTIONS for tc in call_history
            )
            if has_prior_read:
                return True, (
                    f"数据外传: 先读取数据后向 '{target}' 发送 "
                    f"(action={action})"
                )
            else:
                # 即使没有先读，向外部发送也需要审核
                return True, (
                    f"外传风险: 向外部目标 '{target}' 发送数据 "
                    f"(action={action})"
                )

    return False, ""


# ────────── Agent-Declared Scope（Agent 声明模式） ──────────

class AgentDeclaredScope:
    """
    Agent 声明式作用域引擎 — v2 核心。

    设计理念:
        Agent 自身就是 LLM（已经理解了用户意图），
        它发出的 tool_call 就是「我理解用户想让我做 X」的 structured output。
        TEC 不需要再做一遍意图解析，只需要:

        1. 学习: Agent 首次调用什么 → 声明了什么 scope
        2. 扩族: 自动将 scope 扩展到安全同族（reply → {reply, draft}）
        3. 锁定: 如果 Agent 后续调用超出了声明的 scope → 拦截
        4. 高危门禁: DANGEROUS_ACTIONS 始终需要显式授权

    类比:
        你告诉保安「我来开会的」（Agent 的首次 tool_call），
        保安给你一张门禁卡，能刷会议室和茶水间（安全同族），
        但你刷不了机房门（高危区域 → 需要另外审批）。
    """

    def __init__(
        self,
        user_intent: str = "",
        affinity_engine: ActionAffinityEngine | None = None,
    ):
        """
        参数:
            user_intent: 用户原始意图（仅用于审计日志和意图偏离检测）
            affinity_engine: 动作亲和度引擎（传入时使用自动推导，否则用静态表）
        """
        self.user_intent = user_intent
        # 亲和度引擎（v3 核心：自动推导安全同族）
        self._affinity_engine = affinity_engine
        # Agent 声明的操作范围: {tool: {actions}}
        self._declared_scopes: dict[str, set[str]] = {}
        # 已生成的令牌
        self._tokens: dict[str, CapabilityToken] = {}
        # 声明历史（用于审计）
        self._declaration_log: list[dict] = []

    def process_tool_call(
        self, tool_call: ToolCall
    ) -> tuple[CapabilityToken | None, str]:
        """
        处理 Agent 的 tool_call，自动学习/验证 scope。

        返回:
            (token, message)
            - ALLOW: (valid_token, "通过")
            - 需要新声明: (new_token, "新工具域已声明")
            - BLOCK: (None, "原因")
        """
        tool = tool_call.tool
        action = tool_call.action.lower()

        # ── 高危门禁: DANGEROUS_ACTIONS 必须显式授权 ──
        if action in DANGEROUS_ACTIONS:
            # Agent 要执行高危操作，检查用户意图中是否有相关词
            if not self._user_explicitly_authorized(action):
                return None, (
                    f"🚫 高危操作 '{action}' 未获用户显式授权。"
                    f"用户意图: '{self.user_intent[:80]}'"
                )

        # ── 检查是否已有该工具域的 scope ──
        if tool in self._declared_scopes:
            # 已有声明 → 检查新 action 是否在 scope 内
            scope = self._declared_scopes[tool]
            if action in scope:
                # 在范围内 → 返回已有令牌
                return self._tokens.get(tool), "通过"

            # 不在范围内 → 尝试安全同族扩展
            family = self._find_family(action, tool)
            if family and family & scope:
                # 新 action 与已有 scope 属于同一安全族
                scope.add(action)
                self._update_token(tool, scope)
                logger.info(
                    "🔄 Scope 同族扩展: %s.%s (族: %s)",
                    tool, action, family & scope,
                )
                return self._tokens.get(tool), f"同族扩展: {action}"

            # 不在同族 → 新的独立行为，需要审视
            return None, (
                f"操作 '{tool}.{action}' 超出已声明范围 "
                f"{scope}，且不属于安全同族"
            )

        # ── 首次使用该工具域 → 声明新 scope ──
        initial_scope = {action}

        # 自动扩展到安全同族（优先用 AffinityEngine）
        family = self._find_family(action, tool)
        if family:
            initial_scope = initial_scope | family

        # 只读操作默认无限制
        read_family = _STATIC_FAMILIES.get("read", set())
        if action in read_family:
            initial_scope = initial_scope | read_family

        self._declared_scopes[tool] = initial_scope
        self._declaration_log.append({
            "tool": tool,
            "trigger_action": action,
            "declared_scope": list(initial_scope),
            "timestamp": time.time(),
        })

        # 生成令牌
        token = CapabilityToken.create(
            tool=tool,
            actions=initial_scope,
            max_targets=self._infer_max_targets(tool_call),
            ttl_seconds=600.0,  # 10 分钟
        )
        self._tokens[tool] = token

        logger.info(
            "🎯 Agent 声明 Scope: %s → %s (由 '%s' 触发)",
            tool, initial_scope, action,
        )

        return token, f"新工具域已声明: {tool}={initial_scope}"

    def get_scope(self, tool: str) -> set[str] | None:
        """获取工具的已声明 scope"""
        return self._declared_scopes.get(tool)

    def get_all_scopes(self) -> dict[str, set[str]]:
        """获取所有已声明的 scope"""
        return dict(self._declared_scopes)

    def get_declaration_log(self) -> list[dict]:
        """获取声明历史（审计用）"""
        return list(self._declaration_log)

    def force_declare(
        self, tool: str, actions: set[str], max_targets: int = 10
    ):
        """人工强制声明 scope（用于审批后授权高危操作）"""
        self._declared_scopes[tool] = actions
        token = CapabilityToken.create(
            tool=tool,
            actions=actions,
            max_targets=max_targets,
            ttl_seconds=300.0,
            requires_approval=False,
        )
        self._tokens[tool] = token
        logger.info("🔑 强制声明: %s → %s", tool, actions)

    def _user_explicitly_authorized(self, action: str) -> bool:
        """检查用户意图中是否显式授权了高危操作"""
        if not self.user_intent:
            return False

        intent_lower = self.user_intent.lower()

        # 动作 → 用户可能说的话
        authorization_words: dict[str, list[str]] = {
            "delete":   ["删", "delete", "remove", "清空", "移除", "删除"],
            "remove":   ["删", "delete", "remove", "移除", "去掉"],
            "drop":     ["删", "drop", "删表", "删库"],
            "truncate": ["清空", "truncate", "清除"],
            "purge":    ["清", "purge", "彻底删"],
            "destroy":  ["销毁", "destroy", "注销"],
            "transfer": ["转账", "transfer", "转", "汇款"],
            "pay":      ["支付", "pay", "付款", "买", "购买"],
            "withdraw": ["提现", "withdraw", "取钱"],
            "execute":  ["执行", "execute", "run", "运行"],
            "exec":     ["执行", "exec", "运行"],
            # 新增：覆盖 benign 场景中的合法操作
            "send":     ["发", "发送", "send", "发邮件", "回复", "通知",
                         "发消息", "安排", "处理", "写"],
            "forward":  ["转发", "forward", "处理"],
            "share":    ["分享", "share", "共享"],
            "post":     ["发布", "post", "发帖", "评论"],
            "update":   ["修改", "更新", "update", "编辑", "edit", "改",
                         "标记", "mark", "存档", "archive", "置顶", "pin",
                         "处理", "写", "整理"],
            "archive":  ["归档", "archive", "存档", "处理", "整理"],
            "edit":     ["编辑", "edit", "修改", "写", "回复"],
            "book":     ["预订", "book", "订", "预约"],
            "subscribe": ["订阅", "subscribe"],
            "cancel":   ["取消", "cancel"],
            "purchase": ["买", "购买", "purchase", "buy"],
            "buy":      ["买", "购买", "buy"],
            "sell":     ["卖", "sell"],
            "trade":    ["交易", "trade"],
            "post_review": ["评论", "评价", "review"],
            "export":   ["导出", "export"],
            "invite_user": ["邀请", "invite"],
        }

        words = authorization_words.get(action, [action])
        return any(w in intent_lower for w in words)

    def _update_token(self, tool: str, new_scope: set[str]):
        """更新令牌的 action 集"""
        old_token = self._tokens.get(tool)
        if old_token:
            self._tokens[tool] = CapabilityToken.create(
                tool=tool,
                actions=new_scope,
                max_targets=old_token.max_targets,
                ttl_seconds=old_token.remaining_ttl,
                parent_id=old_token.token_id,
            )

    def _find_family(
        self, action: str, tool_domain: str = ""
    ) -> set[str] | None:
        """
        查找 action 所属的安全同族。

        策略:
        1. 如果有 AffinityEngine → 用自动推导结果
        2. 否则 → fallback 到静态 _STATIC_FAMILIES 表
           注意: 返回所有包含该 action 的族的并集（因为一个
           action 可能属于多个族，如 draft ∈ {create, reply, send}）
        """
        # v3: 优先使用亲和度引擎自动推导
        if self._affinity_engine and tool_domain:
            auto_family = self._affinity_engine.get_family(
                tool_domain, action
            )
            if len(auto_family) > 1:  # 至少有一个邻居
                logger.info(
                    "🧬 ToolDNA 自动推导同族: %s.%s → %s",
                    tool_domain, action, auto_family,
                )
                return auto_family

        # fallback: 静态表 — 合并所有包含该 action 的族
        merged: set[str] = set()
        for family_actions in _STATIC_FAMILIES.values():
            if action in family_actions:
                merged |= family_actions
        return merged if merged else None

    @staticmethod
    def _infer_max_targets(tool_call: ToolCall) -> int:
        """从首次调用推断合理的 max_targets"""
        base = tool_call.target_count
        # 给一个合理的缓冲（2倍或至少3个）
        return max(3, base * 2)


# ──────── Blast Radius Circuit Breaker（熔断器，不变） ──────

@dataclass
class _OperationStats:
    """单个工具域的操作统计"""
    counts: list[float] = field(default_factory=list)
    window_start: float = 0.0
    window_count: int = 0

    def record(self):
        """记录一次操作"""
        now = time.time()
        current_window = now // 3600
        if current_window != self.window_start:
            if self.window_count > 0:
                self.counts.append(self.window_count)
                if len(self.counts) > 30:
                    self.counts = self.counts[-30:]
            self.window_start = current_window
            self.window_count = 0
        self.window_count += 1

    @property
    def mean(self) -> float:
        if not self.counts:
            return 0.0
        return sum(self.counts) / len(self.counts)

    @property
    def std(self) -> float:
        if len(self.counts) < 2:
            return 1.0
        m = self.mean
        variance = sum((x - m) ** 2 for x in self.counts) / len(self.counts)
        return max(variance ** 0.5, 0.5)

    def dynamic_threshold(self, k: float = 3.0) -> int:
        if not self.counts:
            return 1
        return max(1, int(self.mean + k * self.std))


class CircuitBreaker:
    """
    爆炸半径熔断器 — 不硬编码阈值，动态学习。

    CLOSED → 正常放行
    OPEN → 全部阻断
    HALF_OPEN → 试探性放行
    """

    def __init__(
        self,
        default_threshold: int = 5,
        cooldown_seconds: float = 30.0,
        k_sigma: float = 3.0,
    ):
        self.default_threshold = default_threshold
        self.cooldown_seconds = cooldown_seconds
        self.k_sigma = k_sigma
        self._state = CircuitState.CLOSED
        self._tripped_at: float = 0.0
        self._stats: dict[str, _OperationStats] = defaultdict(
            _OperationStats
        )
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._tripped_at > self.cooldown_seconds:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def estimate(self, tool_call: ToolCall) -> BlastRadiusEstimate:
        """估算爆炸半径，决定是否熔断"""
        with self._lock:
            current_state = self.state

            if current_state == CircuitState.OPEN:
                return BlastRadiusEstimate(
                    affected_count=tool_call.target_count,
                    threshold=0, tripped=True, confidence=1.0,
                    details="熔断器已打开，所有操作暂停",
                )

            stats = self._stats[tool_call.tool]
            threshold = (
                stats.dynamic_threshold(self.k_sigma)
                if stats.counts
                else self.default_threshold
            )

            affected = tool_call.target_count
            tripped = affected > threshold

            if tripped:
                self._state = CircuitState.OPEN
                self._tripped_at = time.time()
                logger.warning(
                    "🔴 Circuit Breaker 触发! %s 影响 %d (阈值: %d)",
                    tool_call.signature, affected, threshold,
                )
            elif current_state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                logger.info("🟢 Circuit Breaker 恢复正常")

            stats.record()

            return BlastRadiusEstimate(
                affected_count=affected,
                threshold=threshold,
                tripped=tripped,
                confidence=0.8 if stats.counts else 0.5,
                details=(
                    f"动态阈值={threshold} "
                    f"(mean={stats.mean:.1f}, std={stats.std:.1f})"
                    if stats.counts
                    else f"默认阈值={threshold} (无历史数据)"
                ),
            )

    def reset(self):
        with self._lock:
            self._state = CircuitState.CLOSED
            self._tripped_at = 0.0

    def force_open(self):
        with self._lock:
            self._state = CircuitState.OPEN
            self._tripped_at = time.time()


# ──────── Semantic Drift Detector（语义偏离检测器） ─────────

class SemanticDriftDetector:
    """
    语义偏离检测器 — 检测 Agent 行为是否偏离了用户意图。

    这是「不用额外 LLM」方案的关键补充:
    Agent 自己做意图解析，TEC 做偏离检测。
    两者结合 = 比单独用 LLM 做意图解析更可靠。

    检测维度:
    1. 操作类型跳变 (read → delete = 跳变)
    2. 目标范围膨胀 (1个 → 100个 = 膨胀)
    3. 工具域切换频率 (快速在多个域间跳转 = 可疑)
    4. 高危操作无前奏 (没有 read 就直接 delete = 可疑)
    """

    def __init__(self, user_intent: str = ""):
        self.user_intent = user_intent
        self._call_history: list[ToolCall] = []

    def check(self, tool_call: ToolCall) -> tuple[bool, str]:
        """
        检查新的 tool_call 是否存在语义偏离。

        返回: (is_ok, reason)
        """
        # 检测 1: 操作类型跳变
        ok, msg = self._check_action_jump(tool_call)
        if not ok:
            return False, msg

        # 检测 2: 目标范围膨胀
        ok, msg = self._check_target_inflation(tool_call)
        if not ok:
            return False, msg

        # 检测 3: 高危操作无前奏
        ok, msg = self._check_no_recon(tool_call)
        if not ok:
            return False, msg

        # 记录历史
        self._call_history.append(tool_call)
        return True, ""

    def _check_action_jump(
        self, tool_call: ToolCall
    ) -> tuple[bool, str]:
        """检测操作类型跳变: 安全操作 → 突然执行高危操作"""
        if not self._call_history:
            return True, ""

        # 检查同一工具域的上一次操作
        same_tool = [
            tc for tc in self._call_history
            if tc.tool == tool_call.tool
        ]
        if not same_tool:
            return True, ""

        last = same_tool[-1]
        last_action = last.action.lower()
        curr_action = tool_call.action.lower()

        # 从读类跳到危险类 = 可疑
        read_actions = SAFE_ACTION_FAMILIES.get("read", set())
        if last_action in read_actions and curr_action in DANGEROUS_ACTIONS:
            return False, (
                f"操作跳变: {tool_call.tool} 从 '{last_action}' "
                f"突然跳到高危 '{curr_action}'"
            )

        return True, ""

    def _check_target_inflation(
        self, tool_call: ToolCall
    ) -> tuple[bool, str]:
        """检测目标范围膨胀"""
        same_tool = [
            tc for tc in self._call_history
            if tc.tool == tool_call.tool
        ]
        if not same_tool:
            return True, ""

        # 计算历史平均 target_count
        avg = sum(tc.target_count for tc in same_tool) / len(same_tool)
        curr = tool_call.target_count

        # 10倍以上膨胀 = 可疑
        if avg > 0 and curr > max(10, avg * 10):
            return False, (
                f"目标范围膨胀: {tool_call.tool} 历史平均 "
                f"{avg:.0f}，当前 {curr}（{curr/avg:.0f}x）"
            )

        return True, ""

    def _check_no_recon(
        self, tool_call: ToolCall
    ) -> tuple[bool, str]:
        """检测高危操作无前奏（没有先读取就直接操作）"""
        action = tool_call.action.lower()
        if action not in DANGEROUS_ACTIONS:
            return True, ""

        # 检查是否做过前奏操作（读取或准备）
        read_actions = SAFE_ACTION_FAMILIES.get("read", set())
        # 准备类动作也是有效前奏（如 draft→send）
        prep_actions = {"draft", "compose", "create", "new", "list", "edit"}
        valid_precursors = read_actions | prep_actions

        # 同工具前奏：最优先
        same_tool_precursors = [
            tc for tc in self._call_history
            if tc.tool == tool_call.tool
            and tc.action.lower() in valid_precursors
        ]

        # 跨工具前奏：如果做过任何工具的读取/准备，也算有前奏
        any_tool_precursors = [
            tc for tc in self._call_history
            if tc.action.lower() in valid_precursors
        ]

        if not same_tool_precursors and not any_tool_precursors \
           and self._call_history:
            return False, (
                f"高危无前奏: Agent 未对 '{tool_call.tool}' "
                f"执行任何读取操作就直接执行 '{action}'"
            )

        return True, ""


# ──────────── 策略引擎 v2（组装层） ────────────────────────

class PolicyEngine:
    """
    策略引擎 v2 — TEC 的大脑。

    v2 核心变化:
    - 不再用关键词解析意图（那是 v1 的方式）
    - Agent 的 tool_call 本身就是 structured output
    - TEC 从 Agent 的行为中"学习"scope，然后"验偏"

    四大武器:
    1. AgentDeclaredScope → 首次调用即声明 scope
    2. SemanticDriftDetector → 检测行为偏离
    3. CircuitBreaker → 统计学熔断
    4. ToolDNA → 工具安全画像

    + 频率异常检测
    """

    def __init__(
        self,
        user_intent: str = "",
        default_threshold: int = 5,
    ):
        self.user_intent = user_intent

        # 亲和度引擎（v3 核心：自动推导安全同族）
        self.affinity_engine = ActionAffinityEngine(threshold=0.6)

        # 四大组件
        self.scope = AgentDeclaredScope(
            user_intent=user_intent,
            affinity_engine=self.affinity_engine,
        )
        self.drift_detector = SemanticDriftDetector(
            user_intent=user_intent
        )
        self.circuit_breaker = CircuitBreaker(
            default_threshold=default_threshold
        )
        self.tool_dna = ToolDNA()

        # 频率限制
        self._call_timestamps: list[float] = []
        self._max_calls_per_minute = 20

    def register_tool_schemas(self, schemas: list[dict]):
        """
        注册 MCP 工具 schemas，用于自动推导安全同族。

        应在 session 初始化时调用（如 TECProxy 启动时）。
        注册后，同族关系从 schema 信号自动推导，
        取代硬编码的 _STATIC_FAMILIES 表。

        参数:
            schemas: MCP tools/list 返回的 schema 列表
        """
        self.affinity_engine.register_schemas(schemas)
        logger.info(
            "🧬 已注册 %d 个工具 schema，同族关系将自动推导",
            len(schemas),
        )

    def evaluate(
        self,
        tool_call: ToolCall,
        tool_schema: dict | None = None,
    ) -> PolicyDecision:
        """
        综合评估工具调用。

        检查流水线:
        0. ToolDNA 安全画像
        1. Agent-Declared Scope 声明/验证
        2. Semantic Drift Detection 偏离检测
        3. Blast Radius Circuit Breaker 熔断
        4. 频率异常检测
        """
        # ── Check 0: ToolDNA ──
        if tool_schema:
            profile = self.tool_dna.analyze(tool_schema)
            if profile.level == SafetyLevel.CRITICAL:
                return PolicyDecision.block(
                    f"工具 '{tool_call.tool}' 安全等级 CRITICAL "
                    f"(信号: {profile.danger_signals})"
                )

        # ── Check 0.5: 敏感目标检测 ──
        # 即使是 read 操作，目标是 /etc/shadow 等敏感资产也要拦截
        # 同时检查 parameters 中的值（如 path 参数包含敏感路径）
        sensitive_signal = _detect_sensitive_in_call(tool_call)
        if sensitive_signal:
            return PolicyDecision.escalate(
                f"🔒 {sensitive_signal}"
            )

        # ── Check 0.7: 批量破坏意图检测 ──
        # 检测「破坏性操作 + 批量目标」的组合模式
        # 即使用户意图说的是「整理」，批量删除也应被拦截
        batch_destruct_signal = _is_batch_destruction(tool_call)
        if batch_destruct_signal:
            return PolicyDecision.escalate(
                f"💥 {batch_destruct_signal}"
            )

        # ── Check 0.8 移至 scope 之后（见下方） ──
        # 跨工具和外传检测在 scope 验证后执行，
        # 确保用户授权的跨工具操作不被误拦。

        # ── Check 1: Agent-Declared Scope ──
        # 只读无副作用的操作 → 直接放行
        if not tool_call.has_side_effect:
            logger.info("📖 放行只读: %s", tool_call.signature)
            self._record_call()
            return PolicyDecision.allow()

        token, msg = self.scope.process_tool_call(tool_call)
        if token is None:
            # Scope 拒绝（用户未授权该操作）
            return PolicyDecision.escalate(msg)

        # ── Check 1.5: 跨工具提权检测 ──
        # 在 scope 验证通过后检查（用户已授权的操作可以跨工具）
        cross_esc, cross_msg = _is_cross_tool_escalation(
            tool_call, self.drift_detector._call_history
        )
        if cross_esc:
            # 额外检查：如果用户意图显式授权了该操作则放行
            if not self.scope._user_explicitly_authorized(
                tool_call.action.lower()
            ):
                return PolicyDecision.escalate(
                    f"🔀 {cross_msg}"
                )

        # ── Check 1.6: 外传数据流检测 ──
        exfil, exfil_msg = _is_outbound_exfil(
            tool_call, self.drift_detector._call_history
        )
        if exfil:
            # 如果用户显式授权了 send/forward 等外发操作 → 放行
            if not self.scope._user_explicitly_authorized(
                tool_call.action.lower()
            ):
                return PolicyDecision.escalate(
                    f"📤 {exfil_msg}"
                )

        # ── Check 2: Semantic Drift ──
        drift_ok, drift_msg = self.drift_detector.check(tool_call)
        if not drift_ok:
            return PolicyDecision.escalate(
                f"语义偏离: {drift_msg}"
            )

        # ── Check 3: 爆炸半径 ──
        blast = self.circuit_breaker.estimate(tool_call)
        if blast.tripped:
            return PolicyDecision.escalate(
                f"⚠️ 爆炸半径超限: {blast.affected_count} "
                f"(阈值: {blast.threshold}, {blast.details})",
                blast_radius=blast.affected_count,
            )

        # ── Check 4: 频率异常 ──
        if self._is_frequency_anomaly():
            return PolicyDecision.throttle(
                f"频率异常: 1分钟内 "
                f"{len(self._call_timestamps)} 次 "
                f"(上限: {self._max_calls_per_minute})"
            )

        # 全部通过
        self._record_call()
        return PolicyDecision.allow(token=token)

    def grant_token(self, token: CapabilityToken):
        """手动授予令牌"""
        self.scope.force_declare(
            token.tool, set(token.actions), token.max_targets
        )

    def revoke_token(self, tool: str):
        """撤销令牌"""
        if tool in self.scope._declared_scopes:
            del self.scope._declared_scopes[tool]
        if tool in self.scope._tokens:
            del self.scope._tokens[tool]

    def consume_token(self, tool: str) -> CapabilityToken | None:
        """消费令牌"""
        token = self.scope._tokens.get(tool)
        if token:
            updated = token.consume()
            self.scope._tokens[tool] = updated
            return updated
        return None

    def get_active_tokens(self) -> dict[str, CapabilityToken]:
        """获取所有活跃令牌"""
        return {
            k: v for k, v in self.scope._tokens.items()
            if not v.is_expired and not v.is_exhausted
        }

    def _is_frequency_anomaly(self) -> bool:
        now = time.time()
        self._call_timestamps = [
            t for t in self._call_timestamps if now - t < 60.0
        ]
        return len(self._call_timestamps) >= self._max_calls_per_minute

    def _record_call(self):
        self._call_timestamps.append(time.time())


# ──── 向后兼容: 保留旧版 SemanticScopeEngine 的引用 ────────

SemanticScopeEngine = AgentDeclaredScope
