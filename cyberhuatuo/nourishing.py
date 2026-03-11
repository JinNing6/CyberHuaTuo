"""
CyberHuaTuo 滋补药方引擎
AI 安全体检 + 健康评分 + 滋补方案推荐
"""

import json
from .config import config


# ===== 安全体检 System Prompt =====

CHECKUP_SYSTEM_PROMPT = """你是赛博华佗（CyberHuaTuo）的「养生堂」主治医师，专精于 AI Agent 代码的安全体检和健康评估。

你的职责不是修复 Bug（那是「急诊科」的事），而是：
1. 对用户提交的 Agent 代码进行全面的「安全体检」
2. 检测潜在的安全风险和不良实践
3. 给出健康评分和滋补建议（预防性优化方案）

你需要检查以下六大维度：

🛡️ **经脉一：沙箱隔离**
- 代码执行是否有隔离保护（subprocess、Docker、RestrictedPython）？
- 是否使用了危险的 exec()/eval() 而无保护？
- Agent 工具是否有权限边界？

🔑 **经脉二：密钥安全**
- API Key 是否硬编码在代码中？
- 密钥是否通过安全方式（环境变量/Secrets Manager）管理？
- 日志中是否可能泄漏密钥？

🧠 **经脉三：Prompt 安全**
- 是否有 Prompt 注入防御机制？
- System Prompt 是否有防泄漏措施？
- 用户输入是否在嵌入 Prompt 前做了消毒？

🔒 **经脉四：输出安全**
- LLM 输出是否在消费前做了验证/消毒？
- 是否存在 XSS/SQL注入/命令注入风险？
- Agent 动作是否有人工确认环节（Human-in-the-Loop）？

⏱️ **经脉五：韧性设计**
- 是否有超时控制和重试机制？
- 错误处理是否完善（try/except）？
- 是否有限流/速率控制？

📊 **经脉六：可观测性**
- 是否有结构化日志记录？
- 是否有链路追踪（tracing）？
- 是否有监控和告警？

回答规范：
- 输出 JSON 格式，包含 health_score (0-100)、level、dimensions (六大维度的评分和建议)、summary
- health_score 评分标准：
  - 90-100: 🟢 强壮如虎（安全实践完善）
  - 70-89: 🔵 气血充沛（基本安全，有改进空间）
  - 50-69: 🟡 需要调理（存在明显安全隐患）
  - 30-49: 🟠 体虚多病（多处安全漏洞）
  - 0-29: 🔴 病入膏肓（严重安全风险）
- 每个维度给出 0-100 的分数和具体问题描述
- 给出 top3 最紧急的滋补建议（按优先级排序）

确保输出纯正 JSON，可以被 json.loads 直接解析！不要包含 ```json 等 Markdown 包裹！"""


CHECKUP_USER_TEMPLATE = """请对以下 AI Agent 代码进行安全体检：

```
{code}
```

请进行全面的六经脉安全体检，输出 JSON 格式的体检报告。JSON 结构如下：
{{
    "health_score": 65,
    "level": "🟡 需要调理",
    "dimensions": [
        {{"name": "沙箱隔离", "emoji": "🛡️", "score": 30, "status": "危", "findings": ["发现 xxx 问题"], "advice": "建议 xxx"}},
        ...
    ],
    "top_issues": ["最紧急的问题1", "问题2", "问题3"],
    "summary": "总体评估描述"
}}"""


def _score_to_level(score: int) -> str:
    """将分数转换为健康等级"""
    if score >= 90:
        return "🟢 强壮如虎"
    elif score >= 70:
        return "🔵 气血充沛"
    elif score >= 50:
        return "🟡 需要调理"
    elif score >= 30:
        return "🟠 体虚多病"
    else:
        return "🔴 病入膏肓"


async def security_checkup(
    code: str,
    user_api_key: str | None = None,
    user_provider: str | None = None,
    user_model: str | None = None,
) -> dict:
    """
    对用户提交的 Agent 代码进行安全体检

    Args:
        code: 用户提交的代码
        user_api_key: 用户自定义 API Key
        user_provider: 用户选择的 LLM 提供商
        user_model: 用户传入的模型名称

    Returns:
        体检报告 dict
    """
    import os

    # 检查是否有可用的 LLM Key
    has_key = config.has_llm_key() or bool(user_api_key)
    if not has_key:
        return {
            "error": "未配置 LLM API Key，无法进行 AI 安全体检。请在开发者设置中配置 API Key。",
            "health_score": -1,
        }

    # 构建消息
    messages = [
        {"role": "system", "content": CHECKUP_SYSTEM_PROMPT},
        {"role": "user", "content": CHECKUP_USER_TEMPLATE.format(code=code)},
    ]

    try:
        import litellm

        # 确定模型和 API Key（复用 diagnosis.py 的类似逻辑）
        api_base = None
        api_key = None
        model = config.DIAGNOSIS_MODEL

        if user_api_key:
            api_key = user_api_key
            provider = (user_provider or "openai").lower()
            if provider == "anthropic":
                model = user_model or "claude-3-5-sonnet-latest"
            elif provider == "openai":
                model = user_model or "gpt-4o-mini"
            elif provider == "deepseek":
                model = "deepseek/" + (user_model or "deepseek-chat")
            elif provider == "kimi":
                model = "openai/" + (user_model or "moonshot-v1-8k")
                api_base = "https://api.moonshot.cn/v1"
            elif provider == "doubao":
                model = "openai/" + (user_model or "ep-xxxx")
                api_base = "https://ark.cn-beijing.volces.com/api/v3"
            elif provider == "minimax":
                model = "openai/" + (user_model or "abab6.5s-chat")
                api_base = "https://api.minimax.chat/v1"
            elif provider == "groq":
                model = "groq/" + (user_model or "llama3-8b-8192")
            elif provider == "google" or provider == "gemini":
                model = "gemini/" + (user_model or "gemini-1.5-pro")
            elif provider == "cohere":
                model = "cohere/" + (user_model or "command-r-plus")
            else:
                model = user_model or config.DIAGNOSIS_MODEL
        else:
            # 使用服务端配置（简化版）
            if os.getenv("DEEPSEEK_API_KEY") and "deepseek" in model.lower():
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not model.startswith("deepseek/"):
                    model = f"deepseek/{model}"
            elif os.getenv("GEMINI_API_KEY") and ("gemini" in model.lower() or "google" in model.lower()):
                api_key = os.getenv("GEMINI_API_KEY")
                if not model.startswith("gemini/"):
                    model = f"gemini/{model}"
            elif config.OLLAMA_BASE_URL and model.startswith("ollama/"):
                api_base = config.OLLAMA_BASE_URL

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=3000,
            api_base=api_base,
            api_key=api_key,
        )

        raw_content = response.choices[0].message.content.strip()

        # 清理可能的 markdown 包裹
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        result = json.loads(raw_content.strip())

        # 确保有必要字段
        if "health_score" not in result:
            result["health_score"] = 50
        if "level" not in result:
            result["level"] = _score_to_level(result["health_score"])

        return result

    except json.JSONDecodeError:
        # LLM 没返回合法 JSON，返回原始文本
        return {
            "health_score": -1,
            "level": "⚠️ 解析失败",
            "raw_response": raw_content if 'raw_content' in dir() else "无响应",
            "error": "AI 返回的体检报告格式异常，请重试。",
        }
    except ImportError:
        return {
            "health_score": -1,
            "error": "请安装 litellm: pip install litellm",
        }
    except Exception as e:
        return {
            "health_score": -1,
            "error": f"安全体检失败: {str(e)}",
        }


def get_nourishing_categories() -> list[dict]:
    """获取滋补药方分类列表"""
    categories = [
        {
            "key": "sandbox",
            "name": "🛡️ 安全沙箱",
            "name_en": "Security Sandbox",
            "description": "Agent 代码安全执行与隔离方案",
        },
        {
            "key": "security",
            "name": "🔒 安全加固",
            "name_en": "Security Hardening",
            "description": "API Key 保护、Prompt 注入防御、输出消毒",
        },
        {
            "key": "performance",
            "name": "⚡ 性能调理",
            "name_en": "Performance Tuning",
            "description": "Token 节省、缓存策略、并发优化",
        },
    ]
    return categories
