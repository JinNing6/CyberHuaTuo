---
id: "nourishing-security-api-key-protection-001"
title: "API Key 保护三十六计"
title_en: "36 Strategies for API Key Protection in AI Agents"
framework: "_nourishing"
framework_version: "any"
language: "python"
tags:
  - "api-key"
  - "secrets"
  - "security"
  - "best-practice"
severity: "critical"
complexity: "simple"
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
  - "nourishing-security-prompt-injection-002"
---

## 🧬 滋补概述
Nourishing Overview

API Key 泄漏是 AI Agent 开发中最常见且最容易被忽视的安全问题。一个泄漏的 OpenAI API Key 可能在几小时内产生数千美元的费用。本药方提供了全面的 API Key 保护策略。

## 🏥 常见症状
Common Symptoms

- API Key 硬编码在源代码中并推送到 GitHub
- `.env` 文件未被 `.gitignore` 排除
- 日志中出现了明文 API Key
- Agent 调用链中 Key 通过不安全的方式传递
- 多人共享同一个 Key 无法追踪用量

## 💊 滋补药方
Nourishing Prescriptions

### 药方 1：环境变量 + dotenv ✅ 基础必做

```python
# ❌ 绝对不要这样做
OPENAI_API_KEY = "sk-abc123..."  # 硬编码 Key
client = OpenAI(api_key="sk-abc123...")

# ✅ 正确做法：使用环境变量
import os
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**确保 `.gitignore` 包含：**
```gitignore
.env
.env.local
.env.*.local
*.key
```

### 药方 2：Key 轮换与最小权限

```python
# 定期轮换 Key 的自动化脚本
import os
from datetime import datetime

def check_key_age():
    """检查 Key 创建时间，超过 90 天提醒轮换"""
    key_created = os.getenv("API_KEY_CREATED_AT", "")
    if key_created:
        created = datetime.fromisoformat(key_created)
        age_days = (datetime.now() - created).days
        if age_days > 90:
            print(f"⚠️ API Key 已使用 {age_days} 天，建议立即轮换！")
            return False
    return True
```

### 药方 3：日志脱敏

```python
import re
import logging

class KeyRedactingFilter(logging.Filter):
    """自动过滤日志中的 API Key"""
    PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', 'sk-***REDACTED***'),
        (r'key-[a-zA-Z0-9]{20,}', 'key-***REDACTED***'),
        (r'Bearer\s+[a-zA-Z0-9._-]+', 'Bearer ***REDACTED***'),
    ]

    def filter(self, record):
        msg = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg)
        record.msg = msg
        record.args = ()
        return True

# 使用
logger = logging.getLogger("agent")
logger.addFilter(KeyRedactingFilter())
```

### 药方 4：生产环境 Secrets 管理

| 方案 | 适用场景 | 成本 |
|:---|:---|:---|
| `.env` + dotenv | 本地开发 | 免费 |
| GitHub Secrets | CI/CD 流水线 | 免费 |
| AWS Secrets Manager | AWS 云端部署 | 按调用次数计费 |
| HashiCorp Vault | 企业级多环境 | 开源免费版可用 |
| 1Password CLI | 小团队协作 | 按席位计费 |

## 🔗 参考资料
References

- [OWASP Secrets Management Guide](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [git-secrets by AWS](https://github.com/awslabs/git-secrets)

---

> 🧬 本滋补药方由 [@CyberHuaTuo](https://github.com/CyberHuaTuo) 贡献 · 上医治未病，养生重于治疗
