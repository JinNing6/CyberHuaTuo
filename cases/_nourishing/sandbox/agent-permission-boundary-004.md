---
id: "nourishing-sandbox-permission-boundary-004"
title: "Agent 权限边界管理 — 能力注册表与运行时守卫"
title_en: "Agent Permission Boundary — Capability Registry & Runtime Guard"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "sandbox"
  - "permission"
  - "capability"
  - "least-privilege"
  - "human-in-the-loop"
severity: "critical"
complexity: "complex"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-18"
updated_at: "2026-03-18"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
related_cases:
  - "nourishing-sandbox-best-practices-001"
  - "nourishing-sandbox-mcp-tool-security-005"
  - "nourishing-sandbox-zero-trust-network-006"
---

## 🧬 滋补概述
Nourishing Overview

AI Agent 最危险的安全问题不是代码执行，而是**权限失控**。当 Agent 拥有无限制的 Tool Calling 能力时，一个 Prompt 注入就可以让 Agent 删除数据库、泄露密钥、或发送恶意请求。本药方提供基于「能力注册表」的权限边界管理方案，确保 Agent 在**最小权限原则**下运行。

> ⚠️ **安全原则**：每个 Agent 的每次 Tool 调用都是一次「能力请求」（Capability Request），必须在运行时被校验和审计。

## 🏥 常见症状
Common Symptoms

- Agent 可以调用任意工具，无白名单限制
- 高危操作（删除、支付、发布）不需要人工确认
- Agent 的权限与人类用户的权限相同（无衰减）
- 多个 Agent 共享同一套权限，无角色隔离
- 工具调用缺少审计日志，无法追溯

## 🔬 权限风险分析
Permission Risk Analysis

| 风险类型 | 描述 | 影响级别 |
|:---|:---|:---|
| **无限能力** | Agent 可调用所有已注册工具 | 🔴 极高 |
| **权限继承** | Agent 继承用户的全部权限 | 🔴 极高 |
| **隐式提权** | 通过组合多个低权限工具实现高权限操作 | 🟡 高 |
| **无审批链** | 高危操作无 Human-in-the-Loop 环节 | 🔴 极高 |
| **审计空白** | 工具调用无结构化日志 | 🟠 中高 |

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：能力注册表（Capability Registry）✅ 核心必做

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Optional


class RiskLevel(Enum):
    """工具风险等级"""
    LOW = "low"           # 只读查询、搜索
    MEDIUM = "medium"     # 数据修改、文件写入
    HIGH = "high"         # 删除操作、外部API调用
    CRITICAL = "critical" # 支付、权限变更、数据导出


@dataclass
class ToolCapability:
    """工具能力描述"""
    name: str                          # 工具名称
    description: str                   # 工具描述
    risk_level: RiskLevel              # 风险等级
    requires_approval: bool = False    # 是否需要人工审批
    allowed_roles: list[str] = field(  # 允许调用的角色列表
        default_factory=lambda: ["admin"]
    )
    max_calls_per_minute: int = 60     # 速率限制
    argument_validators: dict = field( # 参数校验规则
        default_factory=dict
    )


class CapabilityRegistry:
    """
    能力注册表 — Agent 工具的白名单中枢

    所有工具必须先注册，未注册的工具调用将被拒绝。
    """

    def __init__(self):
        self._registry: dict[str, ToolCapability] = {}

    def register(self, capability: ToolCapability) -> None:
        """注册一个工具能力"""
        self._registry[capability.name] = capability

    def is_allowed(self, tool_name: str, role: str) -> tuple[bool, str]:
        """
        检查指定角色是否有权调用指定工具

        Returns:
            (is_allowed, reason)
        """
        if tool_name not in self._registry:
            return False, f"工具 '{tool_name}' 未在能力注册表中注册"

        cap = self._registry[tool_name]
        if role not in cap.allowed_roles:
            return False, (
                f"角色 '{role}' 无权调用 '{tool_name}'，"
                f"允许的角色: {cap.allowed_roles}"
            )

        return True, "允许"

    def get_capability(self, tool_name: str) -> Optional[ToolCapability]:
        return self._registry.get(tool_name)

    def list_capabilities(self, role: str) -> list[ToolCapability]:
        """列出指定角色可用的所有工具"""
        return [
            cap for cap in self._registry.values()
            if role in cap.allowed_roles
        ]


# ═══════════════════════════════════════════════════════════
# 使用示例：注册 Agent 工具
# ═══════════════════════════════════════════════════════════
registry = CapabilityRegistry()

# 低风险工具：搜索
registry.register(ToolCapability(
    name="search_knowledge_base",
    description="搜索知识库",
    risk_level=RiskLevel.LOW,
    allowed_roles=["admin", "agent", "viewer"],
))

# 中风险工具：写入
registry.register(ToolCapability(
    name="save_prescription",
    description="保存药方到知识库",
    risk_level=RiskLevel.MEDIUM,
    allowed_roles=["admin", "agent"],
))

# 高风险工具：删除（需审批）
registry.register(ToolCapability(
    name="delete_prescription",
    description="删除知识库药方",
    risk_level=RiskLevel.HIGH,
    requires_approval=True,
    allowed_roles=["admin"],
))
```

### 药方 2：运行时权限守卫（Runtime Permission Guard）✅ 推荐

```python
import time
import logging
from functools import wraps
from collections import defaultdict

logger = logging.getLogger("agent.security")


class PermissionDeniedError(Exception):
    """权限拒绝异常"""
    pass


class PermissionGuard:
    """
    运行时权限守卫 — 在每次 Tool 调用前进行权限校验

    功能：
    1. 白名单校验
    2. 角色匹配
    3. 速率限制
    4. 参数校验
    5. 审计日志
    """

    def __init__(self, registry: CapabilityRegistry):
        self._registry = registry
        self._call_counts: dict[str, list[float]] = defaultdict(list)

    def _check_rate_limit(
        self, tool_name: str, cap: ToolCapability,
    ) -> bool:
        """检查速率限制"""
        now = time.time()
        window = 60  # 1分钟窗口

        # 清理过期记录
        self._call_counts[tool_name] = [
            t for t in self._call_counts[tool_name]
            if now - t < window
        ]

        if len(self._call_counts[tool_name]) >= cap.max_calls_per_minute:
            return False

        self._call_counts[tool_name].append(now)
        return True

    def check_permission(
        self,
        tool_name: str,
        role: str,
        arguments: dict | None = None,
    ) -> tuple[bool, str]:
        """
        全方位权限校验

        Returns:
            (is_allowed, reason)
        """
        # 1. 白名单校验
        is_allowed, reason = self._registry.is_allowed(tool_name, role)
        if not is_allowed:
            logger.warning(
                f"🚫 权限拒绝: tool={tool_name} role={role} reason={reason}"
            )
            return False, reason

        cap = self._registry.get_capability(tool_name)

        # 2. 速率限制
        if not self._check_rate_limit(tool_name, cap):
            reason = f"工具 '{tool_name}' 调用频率超限（{cap.max_calls_per_minute}/min）"
            logger.warning(f"⏱️ 速率限制: {reason}")
            return False, reason

        # 3. 参数校验
        if arguments and cap.argument_validators:
            for key, validator in cap.argument_validators.items():
                if key in arguments:
                    try:
                        validator(arguments[key])
                    except (ValueError, TypeError) as e:
                        reason = f"参数校验失败: {key} — {e}"
                        return False, reason

        # 审计日志
        logger.info(
            f"✅ 权限通过: tool={tool_name} role={role} "
            f"risk={cap.risk_level.value}"
        )
        return True, "允许"


def require_permission(
    registry: CapabilityRegistry,
    role: str = "agent",
):
    """
    权限校验装饰器 — 装饰在 Tool 函数上

    使用方式：
        @require_permission(registry, role="agent")
        async def my_tool(query: str) -> str:
            ...
    """
    guard = PermissionGuard(registry)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tool_name = func.__name__
            is_allowed, reason = guard.check_permission(
                tool_name, role, kwargs,
            )
            if not is_allowed:
                raise PermissionDeniedError(
                    f"🚫 Agent 无权调用 '{tool_name}': {reason}"
                )

            cap = registry.get_capability(tool_name)
            if cap and cap.requires_approval:
                # 高危操作：需要人工审批
                approval = await request_human_approval(
                    tool_name=tool_name,
                    arguments=kwargs,
                    risk_level=cap.risk_level.value,
                )
                if not approval:
                    raise PermissionDeniedError(
                        f"🙅 人工审批拒绝: '{tool_name}'"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def request_human_approval(
    tool_name: str,
    arguments: dict,
    risk_level: str,
) -> bool:
    """
    请求人工审批 — Human-in-the-Loop

    在生产环境中，这可以是：
    - Slack/Discord 通知 + 按钮确认
    - Web Dashboard 审批队列
    - 命令行交互确认
    """
    print(f"\n{'='*50}")
    print(f"⚠️  高危操作审批请求")
    print(f"工具: {tool_name}")
    print(f"风险: {risk_level}")
    print(f"参数: {arguments}")
    print(f"{'='*50}")

    # 简化实现：命令行确认
    # 生产环境应替换为异步审批流
    response = input("是否批准？(y/n): ").strip().lower()
    return response == "y"
```

### 药方 3：按角色分配权限 — 最小权限实践

```python
# ═══════════════════════════════════════════════════════════
# 角色定义示例：不同 Agent 分配不同的工具子集
# ═══════════════════════════════════════════════════════════

ROLE_PERMISSIONS = {
    "reader": {
        "description": "只读查询 Agent",
        "tools": [
            "search_knowledge_base",
            "diagnose",  # 只读诊断
        ],
    },
    "contributor": {
        "description": "贡献者 Agent",
        "tools": [
            "search_knowledge_base",
            "diagnose",
            "save_prescription",    # 可以新增
            # 注意：没有 delete 权限
        ],
    },
    "admin": {
        "description": "管理员 Agent",
        "tools": [
            "search_knowledge_base",
            "diagnose",
            "save_prescription",
            "delete_prescription",  # 需审批
            "security_checkup",
        ],
    },
}


def setup_agent_permissions(
    registry: CapabilityRegistry,
    role: str,
) -> PermissionGuard:
    """
    根据角色快速配置 Agent 权限

    Usage:
        guard = setup_agent_permissions(registry, "contributor")
    """
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"未知角色: {role}")

    guard = PermissionGuard(registry)

    # 验证角色的工具都已注册
    role_config = ROLE_PERMISSIONS[role]
    for tool in role_config["tools"]:
        cap = registry.get_capability(tool)
        if cap is None:
            raise ValueError(
                f"角色 '{role}' 引用了未注册的工具: {tool}"
            )
        if role not in cap.allowed_roles:
            raise ValueError(
                f"角色 '{role}' 不在工具 '{tool}' 的允许列表中"
            )

    return guard
```

## ⚠️ 安全要点

1. **永远默认拒绝** — 未注册的工具一律禁止调用
2. **权限不可继承** — Agent 的权限必须独立于触发它的人类用户
3. **审批不可自动化** — `requires_approval=True` 的工具必须有真人确认
4. **日志不可关闭** — 所有权限校验结果必须记录到审计日志
5. **速率限制不可绕过** — 即使拥有权限，也需遵守调用频率限制

## 🔗 参考资料
References

- [OWASP LLM08 - Excessive Agency](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Anthropic: Building Safe AI Agents](https://docs.anthropic.com/en/docs/agents)
- [Google: Secure AI Agent Design](https://cloud.google.com/architecture/ai-agent-security)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
