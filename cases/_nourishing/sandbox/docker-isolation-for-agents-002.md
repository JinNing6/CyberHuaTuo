---
id: "nourishing-sandbox-docker-isolation-002"
title: "Docker 隔离方案 — AI Agent 安全执行环境"
title_en: "Docker Isolation for Secure AI Agent Code Execution"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "docker"
  - "sandbox"
  - "container"
  - "isolation"
severity: "high"
complexity: "moderate"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "linux"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases:
  - "nourishing-sandbox-best-practices-001"
---

## 🧬 滋补概述
Nourishing Overview

Docker 容器提供了操作系统级别的隔离，是 AI Agent 执行用户代码或 LLM 生成代码时最实用的安全沙箱方案之一。本药方提供了一套生产就绪的 Docker 隔离模板和最佳实践。

## 🏥 适用症状
Target Symptoms

- Agent 需要运行用户提交的 Python/Shell 脚本
- Code Interpreter 类功能需要安全执行环境
- Tool Calling 链中涉及代码生成与执行
- 需要防止 Agent 访问宿主机敏感文件和网络

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：最小化安全镜像 ✅ 推荐

```dockerfile
# Dockerfile.sandbox
FROM python:3.11-slim AS sandbox

# 安全配置：非 root 用户
RUN groupadd -r sandbox && useradd -r -g sandbox -d /home/sandbox -s /bin/bash sandbox

# 最小化安装（仅安装必要包）
RUN pip install --no-cache-dir numpy pandas requests 2>/dev/null || true

# 创建工作目录
RUN mkdir -p /workspace && chown sandbox:sandbox /workspace

# 切换到非 root 用户
USER sandbox
WORKDIR /workspace

# 默认入口
ENTRYPOINT ["python"]
```

### 药方 2：Python SDK 安全调用封装

```python
import docker
import tempfile
import os
from typing import Optional


class AgentSandbox:
    """AI Agent 安全代码执行沙箱"""

    def __init__(
        self,
        image: str = "python:3.11-slim",
        mem_limit: str = "256m",
        cpu_quota: int = 50000,
        timeout: int = 30,
        network_enabled: bool = False,
    ):
        self.client = docker.from_env()
        self.image = image
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.timeout = timeout
        self.network_enabled = network_enabled

    def execute(self, code: str, stdin: str = "") -> dict:
        """
        在隔离容器中执行 Python 代码

        Returns:
            {"stdout": str, "stderr": str, "exit_code": int, "timed_out": bool}
        """
        try:
            container = self.client.containers.run(
                self.image,
                command=["python", "-c", code],
                mem_limit=self.mem_limit,
                cpu_period=100000,
                cpu_quota=self.cpu_quota,
                network_disabled=not self.network_enabled,
                read_only=True,
                remove=False,          # 先不删，需要获取日志
                detach=True,
                tmpfs={"/tmp": "size=64m"},  # 只允许写入 /tmp
                security_opt=["no-new-privileges"],
                stdin_open=bool(stdin),
            )

            # 等待执行完成
            result = container.wait(timeout=self.timeout)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            exit_code = result.get("StatusCode", -1)

            container.remove(force=True)

            return {
                "stdout": logs,
                "stderr": "",
                "exit_code": exit_code,
                "timed_out": False,
            }

        except docker.errors.ContainerError as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": e.exit_status,
                "timed_out": False,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"沙箱执行异常: {str(e)}",
                "exit_code": -1,
                "timed_out": "timeout" in str(e).lower(),
            }


# 使用示例
sandbox = AgentSandbox(
    mem_limit="128m",
    timeout=10,
    network_enabled=False,
)

result = sandbox.execute("""
import sys
print(f"Python {sys.version}")
print("Hello from sandbox!")
# 尝试访问文件系统将失败（只读）
# open('/etc/passwd').read()  # PermissionError
""")

print(result["stdout"])
```

### 药方 3：Docker Compose 多容器安全编排

```yaml
# docker-compose.sandbox.yml
version: "3.8"

services:
  agent-sandbox:
    build:
      context: .
      dockerfile: Dockerfile.sandbox
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
        reservations:
          memory: 64M
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:size=64m
    networks:
      - sandbox-net

networks:
  sandbox-net:
    driver: bridge
    internal: true  # 禁止外部网络访问
```

## ⚠️ 安全注意事项

1. **永远不要** 挂载宿主机敏感目录（如 `/`, `/home`, `/etc`）
2. **永远不要** 以 `--privileged` 模式运行沙箱容器
3. **始终设置** 内存和 CPU 限制防止资源耗尽攻击
4. **定期更新** 基础镜像修补已知安全漏洞
5. **考虑 gVisor**：对于高安全场景，使用 `--runtime=runsc`

## 🔗 参考资料
References

- [Docker Security Documentation](https://docs.docker.com/engine/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
