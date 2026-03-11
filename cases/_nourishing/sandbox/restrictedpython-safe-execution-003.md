---
id: "nourishing-sandbox-restrictedpython-003"
title: "RestrictedPython 轻量级安全执行方案"
title_en: "Lightweight Safe Execution with RestrictedPython"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "restrictedpython"
  - "sandbox"
  - "lightweight"
  - "safe-execution"
severity: "medium"
complexity: "moderate"
case_type: "nourishing"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-11"
updated_at: "2026-03-11"
contributors:
  - github: "CyberHuaTuo"
source_url: "https://restrictedpython.readthedocs.io/"
related_cases:
  - "nourishing-sandbox-best-practices-001"
---

## 🧬 滋补概述
Nourishing Overview

RestrictedPython 是一个 Python 语言级别的沙箱方案，通过限制可用的语言特性和内置函数来提供安全执行环境。适合轻量级的表达式求值和简单计算场景，但不适合用作唯一的安全屏障。

## 🏥 适用症状
Target Symptoms

- Agent 需要执行简单的数学计算或数据处理
- 需要在不启动 Docker 的情况下快速验证 LLM 输出的表达式
- 作为多层安全策略中的第一道防线

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：基础安全执行 ✅ 推荐

```python
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from RestrictedPython.Eval import default_guarded_getattr
from RestrictedPython.Guards import guarded_unpack_sequence, safer_getattr


def safe_eval(expression: str, variables: dict = None) -> any:
    """
    在受限环境中安全执行 Python 表达式

    允许：基础数学运算、字符串操作、列表推导
    禁止：文件 I/O、网络、import、exec、eval、__builtins__
    """
    # 编译受限代码
    byte_code = compile_restricted(
        f"result = {expression}",
        filename="<agent-eval>",
        mode="exec",
    )

    # 构建安全的全局命名空间
    restricted_globals = safe_globals.copy()
    restricted_globals["_getattr_"] = default_guarded_getattr
    restricted_globals["_getiter_"] = iter
    restricted_globals["_getitem_"] = default_guarded_getattr

    # 注入用户变量（如有）
    restricted_locals = variables or {}

    # 执行
    exec(byte_code, restricted_globals, restricted_locals)

    return restricted_locals.get("result")


# ✅ 安全使用示例
result = safe_eval("sum([x**2 for x in range(10)])")
print(result)  # 285

result = safe_eval("a + b * 2", {"a": 10, "b": 5})
print(result)  # 20

# ❌ 以下会被阻止
# safe_eval("__import__('os').system('rm -rf /')")     # 禁止 import
# safe_eval("open('/etc/passwd').read()")               # 禁止文件操作
# safe_eval("eval('malicious_code')")                   # 禁止 eval
```

### 药方 2：带超时的安全执行

```python
import signal
import threading
from functools import wraps


class ExecutionTimeout(Exception):
    pass


def with_timeout(seconds: int = 5):
    """超时装饰器，防止无限循环"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [ExecutionTimeout(f"执行超时（{seconds}s）")]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator


@with_timeout(seconds=5)
def safe_eval_with_timeout(expression: str) -> any:
    return safe_eval(expression)


# 使用
try:
    result = safe_eval_with_timeout("sum(range(1000000))")
    print(result)
except ExecutionTimeout:
    print("⏰ 代码执行超时！")
```

## ⚠️ 重要限制

> **RestrictedPython 不是银弹！** 由于 Python 语言高度动态的特性，语言级沙箱存在已知的逃逸手法。

1. **不要单独依赖 RestrictedPython** — 应搭配进程/容器级隔离使用
2. **Python 的 introspection 能力** 使得完全封堵所有逃逸路径非常困难
3. **无资源限制** — RestrictedPython 不限制 CPU/内存，需配合 `ulimit` 或容器限制
4. **建议使用场景**：作为多层防御的第一道过滤，而非最后一道防线

## 🔗 参考资料
References

- [RestrictedPython Documentation](https://restrictedpython.readthedocs.io/)
- [RestrictedPython GitHub](https://github.com/zopefoundation/RestrictedPython)
- [Python Security Guide - Sandboxing](https://python-security.readthedocs.io/)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
