---
id: "nourishing-sandbox-best-practices-001"
title: "AI Agent 安全沙箱最佳实践总指南"
title_en: "Comprehensive Guide to Secure Sandbox for AI Agents"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "sandbox"
  - "security"
  - "best-practice"
  - "isolation"
severity: "high"
complexity: "complex"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: ""
related_cases:
  - "nourishing-sandbox-docker-isolation-002"
  - "nourishing-sandbox-restrictedpython-003"
---

## 🧬 滋补概述
Nourishing Overview

AI Agent 在运行过程中经常需要执行动态代码（如 Tool Calling、Code Interpreter），这带来了严重的安全风险。本指南提供了多种安全沙箱方案的全面对比，帮助开发者选择适合自己场景的隔离方案。

> ⚠️ **安全原则**：永远不要在无隔离的环境中执行 Agent 产出的代码。

## 🏥 常见症状
Common Symptoms

- Agent 执行的代码访问了宿主机的文件系统
- LLM 生成的代码中包含恶意系统调用
- Agent 工具链中存在 `eval()`/`exec()` 调用未受保护
- 外部用户输入直接拼接进代码执行上下文
- 沙箱逃逸（Container Escape）后数据泄漏

## 🔬 方案对比分析
Comparative Analysis

| 方案 | 隔离级别 | 性能开销 | 适用场景 | 安全等级 |
|:---|:---|:---|:---|:---|
| **RestrictedPython** | 语言级 | 极低 | 轻量级表达式求值 | ⚠️ 中 |
| **subprocess + seccomp** | 进程级 | 低 | 本地工具执行 | 🟡 中高 |
| **Docker Container** | 容器级 | 中 | 通用代码执行 | 🟢 高 |
| **gVisor (runsc)** | 内核级 | 中 | 高安全场景 | 🟢 很高 |
| **Firecracker MicroVM** | 虚拟机级 | 中高 | 云端多租户 | 🟢 极高 |
| **WebAssembly (WASM)** | 字节码级 | 低 | 跨平台轻量执行 | 🟢 高 |

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：分层防御策略（Defense in Depth） ✅ 推荐

不要依赖单一隔离机制，采用多层防御：

```
┌─────────────────────────────────────────┐
│  Layer 1: 输入校验 (Input Validation)    │
│  ↓ 过滤危险模式、长度限制、格式检查       │
├─────────────────────────────────────────┤
│  Layer 2: 语言限制 (RestrictedPython)    │
│  ↓ 白名单 builtins、禁止 import          │
├─────────────────────────────────────────┤
│  Layer 3: 进程隔离 (subprocess)          │
│  ↓ 独立进程、ulimit 资源限制             │
├─────────────────────────────────────────┤
│  Layer 4: 容器隔离 (Docker/gVisor)       │
│  ↓ 独立文件系统、网络隔离                │
├─────────────────────────────────────────┤
│  Layer 5: 监控与审计 (Monitoring)        │
│  ↓ 系统调用审计、异常检测                │
└─────────────────────────────────────────┘
```

### 药方 2：最小权限原则配置

```python
# ✅ 正确：使用临时目录 + 非 root 用户 + 超时控制
import subprocess
import tempfile
import os

def safe_execute(code: str, timeout: int = 10) -> str:
    """在受限环境中执行代码"""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "script.py")
        with open(script_path, "w") as f:
            f.write(code)

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tmpdir,
            env={
                "PATH": "/usr/bin:/bin",
                "HOME": tmpdir,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        return result.stdout if result.returncode == 0 else result.stderr
```

```python
# ❌ 危险：直接 exec() 用户代码
exec(user_submitted_code)  # 绝对不要这样做！

# ❌ 危险：使用 eval() 处理 LLM 输出
result = eval(llm_response)  # Prompt 注入可导致任意代码执行
```

### 药方 3：Docker 快速隔离模板

```dockerfile
# agent-sandbox/Dockerfile
FROM python:3.11-slim

# 创建非 root 用户
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox

# 只安装必要包
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 入口
COPY entrypoint.py .
CMD ["python", "entrypoint.py"]
```

```python
# 启动隔离容器执行代码
import docker

client = docker.from_env()
container = client.containers.run(
    "agent-sandbox:latest",
    command=f'python -c "{safe_code}"',
    mem_limit="256m",          # 内存限制
    cpu_period=100000,
    cpu_quota=50000,           # 50% CPU
    network_disabled=True,      # 禁用网络
    read_only=True,            # 只读文件系统
    remove=True,               # 自动清理
    timeout=30,                # 超时 30s
)
```

## 🔗 参考资料
References

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [RestrictedPython Documentation](https://restrictedpython.readthedocs.io/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Google gVisor](https://gvisor.dev/docs/)
- [AWS Firecracker](https://firecracker-microvm.github.io/)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
