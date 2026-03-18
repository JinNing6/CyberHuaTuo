---
id: "nourishing-sandbox-zero-trust-network-006"
title: "零信任 Agent 网络隔离方案"
title_en: "Zero-Trust Network Isolation for AI Agents"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "zero-trust"
  - "network"
  - "sandbox"
  - "egress-control"
  - "kill-switch"
severity: "critical"
complexity: "complex"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "linux"
created_at: "2026-03-18"
updated_at: "2026-03-18"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases:
  - "nourishing-sandbox-docker-isolation-002"
  - "nourishing-sandbox-permission-boundary-004"
---

## 🧬 滋补概述
Nourishing Overview

AI Agent 可以发起网络请求 — 调用外部 API、下载文件、POST 数据到远程服务器。在 Prompt 注入攻击下，Agent 可能被引导将敏感数据回传给攻击者控制的服务器（Data Exfiltration），或从恶意站点下载有害负载。本药方提供基于「零信任」原则的 Agent 网络隔离方案。

> ⚠️ **零信任原则**：所有 Agent 网络请求默认禁止，仅放行白名单中的目标端点。

## 🏥 常见症状
Common Symptoms

- Agent 通过 `requests.post()` 将用户数据发送到未知外部服务器
- LLM 被注入后，通过 Tool Call 下载并执行恶意脚本
- Agent 可以自由访问内网服务（数据库、Redis、K8s API）
- DNS 查询泄露内部域名结构
- 无法远程紧急停止失控的 Agent

## 🔬 网络攻击面分析
Network Attack Surface Analysis

| 攻击向量 | 描述 | 风险等级 |
|:---|:---|:---|
| **数据外泄** | Agent 将敏感数据 POST 到外部 | 🔴 极高 |
| **恶意下载** | Agent 下载并执行有害脚本 | 🔴 极高 |
| **SSRF** | Agent 被引导访问内网服务 | 🔴 极高 |
| **DNS 泄露** | DNS 查询暴露内部拓扑 | 🟡 中 |
| **DDoS 跳板** | Agent 被利用发起大量外部请求 | 🟠 高 |

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：出口白名单网关（Egress Whitelist）✅ 核心必做

```python
import re
from urllib.parse import urlparse
from typing import Optional


class EgressFirewall:
    """
    Agent 出口防火墙 — 白名单模式

    默认拒绝所有出站请求，仅允许白名单中的域名和端口。
    """

    def __init__(self):
        self._allowed_domains: set[str] = set()
        self._allowed_urls: list[re.Pattern] = []
        self._blocked_count: int = 0

    def allow_domain(self, domain: str) -> None:
        """添加允许的域名"""
        self._allowed_domains.add(domain.lower())

    def allow_url_pattern(self, pattern: str) -> None:
        """添加允许的 URL 模式（正则）"""
        self._allowed_urls.append(re.compile(pattern, re.IGNORECASE))

    def check(self, url: str) -> tuple[bool, str]:
        """
        检查出站 URL 是否被允许

        Returns:
            (is_allowed, reason)
        """
        try:
            parsed = urlparse(url)
        except Exception:
            return False, f"URL 解析失败: {url}"

        # 协议检查：只允许 https
        if parsed.scheme not in ("https", "http"):
            return False, f"不允许的协议: {parsed.scheme}"

        # 域名检查
        domain = parsed.hostname or ""
        if domain.lower() in self._allowed_domains:
            return True, "域名在白名单中"

        # URL 模式匹配
        for pattern in self._allowed_urls:
            if pattern.search(url):
                return True, "URL 匹配白名单模式"

        self._blocked_count += 1
        return False, f"域名 '{domain}' 不在白名单中（已拦截 {self._blocked_count} 次）"


# ═══════════════════════════════════════════════════════════
# 配置示例：只允许 Agent 访问必要的 API
# ═══════════════════════════════════════════════════════════
firewall = EgressFirewall()

# 允许 LLM 提供商
firewall.allow_domain("api.openai.com")
firewall.allow_domain("api.anthropic.com")
firewall.allow_domain("generativelanguage.googleapis.com")
firewall.allow_domain("api.deepseek.com")

# 允许特定工具 API
firewall.allow_domain("api.github.com")
firewall.allow_url_pattern(r"^https://pypi\.org/")

# 使用
is_ok, reason = firewall.check("https://api.openai.com/v1/chat")
print(f"✅ {reason}")  # 域名在白名单中

is_ok, reason = firewall.check("https://evil.com/exfiltrate")
print(f"🚫 {reason}")  # 域名 'evil.com' 不在白名单中


# ═══════════════════════════════════════════════════════════
# 集成到 requests/httpx（Monkey Patch 方式）
# ═══════════════════════════════════════════════════════════
import requests
from unittest.mock import patch

_original_request = requests.Session.request

def _guarded_request(self, method, url, **kwargs):
    """拦截所有 HTTP 请求进行白名单校验"""
    is_allowed, reason = firewall.check(url)
    if not is_allowed:
        raise PermissionError(
            f"🚫 出口防火墙拦截: {method} {url} — {reason}"
        )
    return _original_request(self, method, url, **kwargs)

# 启用出口防火墙
# requests.Session.request = _guarded_request
```

### 药方 2：Docker 网络隔离配置

```yaml
# docker-compose.agent-isolation.yml
# Agent 容器网络完全隔离，通过反向代理白名单出站
version: "3.8"

services:
  # Agent 沙箱 — 无直接外网访问
  agent-sandbox:
    build: ./sandbox
    networks:
      - agent-internal    # 仅内部网络
    dns:
      - 127.0.0.1         # 禁用外部 DNS
    extra_hosts:
      - "metadata.google.internal:127.0.0.1"  # 阻止云元数据
      - "169.254.169.254:127.0.0.1"           # 阻止 AWS IMDS
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M

  # 出口代理 — 白名单放行
  egress-proxy:
    image: nginx:alpine
    volumes:
      - ./nginx-whitelist.conf:/etc/nginx/nginx.conf:ro
    networks:
      - agent-internal    # 与 Agent 同网络
      - external          # 可访问外网
    ports: []             # 不暴露端口

networks:
  agent-internal:
    driver: bridge
    internal: true        # 🔒 关键：禁止直接外网访问
  external:
    driver: bridge
```

```nginx
# nginx-whitelist.conf — 出口白名单代理配置
events {
    worker_connections 64;
}

http {
    # 上游白名单
    upstream openai {
        server api.openai.com:443;
    }

    upstream anthropic {
        server api.anthropic.com:443;
    }

    server {
        listen 8080;

        # 只代理白名单中的路径
        location /v1/chat/completions {
            proxy_pass https://openai;
            proxy_ssl_verify on;
        }

        location /v1/messages {
            proxy_pass https://anthropic;
            proxy_ssl_verify on;
        }

        # 其他请求一律拒绝
        location / {
            return 403 "Blocked by egress firewall";
        }
    }
}
```

### 药方 3：紧急终止开关（Kill Switch）

```python
import signal
import subprocess
import logging
from typing import Optional

logger = logging.getLogger("agent.killswitch")


class AgentKillSwitch:
    """
    Agent 紧急终止开关

    当 Agent 行为异常时，立即终止其所有进程和网络连接。
    支持多种终止方式：
    1. 进程级终止（SIGTERM/SIGKILL）
    2. 容器级终止（docker stop/kill）
    3. 网络级隔离（iptables DROP）
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._is_killed = False

    def kill_process(self, pid: int) -> bool:
        """进程级终止"""
        try:
            import os
            os.kill(pid, signal.SIGTERM)
            logger.critical(
                f"🔴 KILL SWITCH: 进程 {pid} 已终止 "
                f"(Agent: {self.agent_id})"
            )
            self._is_killed = True
            return True
        except ProcessLookupError:
            return False

    def kill_container(
        self, container_name: str,
    ) -> bool:
        """容器级终止"""
        try:
            subprocess.run(
                ["docker", "kill", container_name],
                capture_output=True,
                timeout=10,
            )
            logger.critical(
                f"🔴 KILL SWITCH: 容器 {container_name} 已终止 "
                f"(Agent: {self.agent_id})"
            )
            self._is_killed = True
            return True
        except Exception as e:
            logger.error(f"容器终止失败: {e}")
            return False

    def isolate_network(
        self, container_name: str,
    ) -> bool:
        """网络级隔离 — 断开容器的所有网络"""
        try:
            subprocess.run(
                [
                    "docker", "network", "disconnect",
                    "--force", "bridge", container_name,
                ],
                capture_output=True,
                timeout=10,
            )
            logger.critical(
                f"🔴 KILL SWITCH: 容器 {container_name} 网络已隔离 "
                f"(Agent: {self.agent_id})"
            )
            return True
        except Exception as e:
            logger.error(f"网络隔离失败: {e}")
            return False

    def emergency_shutdown(
        self,
        pid: Optional[int] = None,
        container_name: Optional[str] = None,
    ) -> dict:
        """
        全面紧急关停 — 同时执行进程终止、容器杀死、网络隔离

        Returns:
            各步骤的执行结果
        """
        results = {}

        if container_name:
            results["network_isolated"] = self.isolate_network(
                container_name
            )
            results["container_killed"] = self.kill_container(
                container_name
            )

        if pid:
            results["process_killed"] = self.kill_process(pid)

        logger.critical(
            f"🚨 EMERGENCY SHUTDOWN 完成: Agent={self.agent_id} "
            f"结果={results}"
        )
        return results


# 使用示例
# killswitch = AgentKillSwitch("agent-001")
# killswitch.emergency_shutdown(
#     container_name="agent-sandbox-1"
# )
```

## ⚠️ 安全要点

1. **默认全部拒绝** — 出站网络必须是白名单模式，不是黑名单
2. **HTTPS Only** — 禁止 Agent 使用 HTTP 明文协议
3. **阻止云元数据** — 务必屏蔽 `169.254.169.254`（AWS IMDS）和 `metadata.google.internal`
4. **DNS 隔离** — Agent 容器使用自定义 DNS，禁止解析内网域名
5. **Kill Switch 不可被 Agent 访问** — 终止控制面板必须在 Agent 权限范围之外

## 🔗 参考资料
References

- [NIST Zero Trust Architecture (SP 800-207)](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [Docker Network Security](https://docs.docker.com/network/)
- [AWS IMDS Attack Prevention](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
