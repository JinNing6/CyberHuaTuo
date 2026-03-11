"""
CyberHuaTuo 框架文档源注册表
全量框架到 Context7 Library ID 的映射，支持智能体直接检索最新官方技术文档
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FrameworkDoc:
    """框架文档源定义"""
    name: str                    # 显示名称
    key: str                     # 内部标识（小写连字符）
    context7_id: str             # Context7 Library ID（预映射）
    category: str                # 分类: agent / foundation / infrastructure
    language: str = "python"     # 主要语言: python / javascript / go / multi
    description: str = ""        # 简短描述
    tags: tuple[str, ...] = ()   # 关键词标签


# ===== 第一层：AI Agent 与 LLM 框架 =====
AGENT_FRAMEWORKS: list[FrameworkDoc] = [
    FrameworkDoc(
        name="LangChain",
        key="langchain",
        context7_id="/websites/langchain",
        category="agent",
        description="LLM 应用开发框架，支持链式调用和 Agent 架构",
        tags=("llm", "chain", "agent", "rag"),
    ),
    FrameworkDoc(
        name="LlamaIndex",
        key="llamaindex",
        context7_id="/run-llama/llama_index",
        category="agent",
        description="数据驱动的 LLM 应用框架，专注于 RAG",
        tags=("llm", "rag", "index", "retrieval"),
    ),
    FrameworkDoc(
        name="CrewAI",
        key="crewai",
        context7_id="/crewAIInc/crewAI",
        category="agent",
        description="多 Agent 协作编排框架",
        tags=("multi-agent", "crew", "orchestration"),
    ),
    FrameworkDoc(
        name="AutoGen",
        key="autogen",
        context7_id="/microsoft/autogen",
        category="agent",
        description="微软多 Agent 对话框架",
        tags=("multi-agent", "conversation", "microsoft"),
    ),
    FrameworkDoc(
        name="OpenAI SDK",
        key="openai-sdk",
        context7_id="/openai/openai-python",
        category="agent",
        description="OpenAI 官方 Python SDK",
        tags=("openai", "gpt", "api", "chat"),
    ),
    FrameworkDoc(
        name="OpenAI Agents",
        key="openai-agents",
        context7_id="/openai/openai-agents-python",
        category="agent",
        description="OpenAI 官方 Agent SDK",
        tags=("openai", "agent", "swarm"),
    ),
    FrameworkDoc(
        name="MCP (Model Context Protocol)",
        key="mcp",
        context7_id="/anthropics/anthropic-cookbook",
        category="agent",
        description="Anthropic 的模型上下文协议",
        tags=("mcp", "protocol", "anthropic", "tool-use"),
    ),
    FrameworkDoc(
        name="DSPy",
        key="dspy",
        context7_id="/stanfordnlp/dspy",
        category="agent",
        description="Stanford NLP 声明式 LLM 编程框架",
        tags=("declarative", "prompt", "optimization"),
    ),
    FrameworkDoc(
        name="Haystack",
        key="haystack",
        context7_id="/deepset-ai/haystack",
        category="agent",
        description="deepset 端到端 NLP/LLM 框架",
        tags=("pipeline", "rag", "nlp"),
    ),
    FrameworkDoc(
        name="Semantic Kernel",
        key="semantic-kernel",
        context7_id="/microsoft/semantic-kernel",
        category="agent",
        description="微软 AI 编排 SDK",
        tags=("microsoft", "orchestration", "plugin"),
    ),
    FrameworkDoc(
        name="PydanticAI",
        key="pydantic-ai",
        context7_id="/pydantic/pydantic-ai",
        category="agent",
        description="基于 Pydantic 的 AI Agent 框架",
        tags=("pydantic", "type-safe", "agent"),
    ),
    FrameworkDoc(
        name="LangFlow",
        key="langflow",
        context7_id="/langflow-ai/langflow",
        category="agent",
        description="可视化 LLM 应用构建器",
        tags=("visual", "low-code", "flow"),
    ),
    FrameworkDoc(
        name="LangGraph",
        key="langgraph",
        context7_id="/websites/langchain",
        category="agent",
        description="LangChain 图引擎，构建有状态 Agent",
        tags=("graph", "stateful", "agent"),
    ),
    FrameworkDoc(
        name="Agno",
        key="agno",
        context7_id="/agno-agi/agno",
        category="agent",
        description="轻量级 AGI Agent 框架",
        tags=("agi", "lightweight", "agent"),
    ),
    FrameworkDoc(
        name="Strands Agents",
        key="strands-agents",
        context7_id="/strands-agents/sdk-python",
        category="agent",
        description="AWS 开源 Agent SDK",
        tags=("aws", "agent", "sdk"),
    ),
    FrameworkDoc(
        name="Smolagents",
        key="smolagents",
        context7_id="/huggingface/smolagents",
        category="agent",
        description="HuggingFace 轻量 Agent 框架",
        tags=("huggingface", "lightweight", "agent"),
    ),
    FrameworkDoc(
        name="Anthropic SDK",
        key="anthropic-sdk",
        context7_id="/anthropics/anthropic-sdk-python",
        category="agent",
        description="Anthropic Claude 官方 Python SDK",
        tags=("anthropic", "claude", "api"),
    ),
    FrameworkDoc(
        name="Google GenAI",
        key="google-genai",
        context7_id="/googleapis/python-genai",
        category="agent",
        description="Google Gemini AI SDK",
        tags=("google", "gemini", "genai"),
    ),
    FrameworkDoc(
        name="LiteLLM",
        key="litellm",
        context7_id="/BerriAI/litellm",
        category="agent",
        description="统一 LLM API 调用层",
        tags=("proxy", "unified", "llm"),
    ),
]

# ===== 第二层：AI 基础框架与工具（Python/JS/Go 通用框架）=====
FOUNDATION_FRAMEWORKS: list[FrameworkDoc] = [
    FrameworkDoc(
        name="FastAPI",
        key="fastapi",
        context7_id="/fastapi/fastapi",
        category="foundation",
        description="现代高性能 Python Web 框架",
        tags=("web", "api", "async"),
    ),
    FrameworkDoc(
        name="Flask",
        key="flask",
        context7_id="/pallets/flask",
        category="foundation",
        description="轻量级 Python Web 框架",
        tags=("web", "micro", "wsgi"),
    ),
    FrameworkDoc(
        name="Django",
        key="django",
        context7_id="/django/django",
        category="foundation",
        description="全功能 Python Web 框架",
        tags=("web", "fullstack", "orm"),
    ),
    FrameworkDoc(
        name="Express.js",
        key="express",
        context7_id="/expressjs/express",
        category="foundation",
        language="javascript",
        description="Node.js 最流行的 Web 框架",
        tags=("web", "node", "middleware"),
    ),
    FrameworkDoc(
        name="Next.js",
        key="nextjs",
        context7_id="/vercel/next.js",
        category="foundation",
        language="javascript",
        description="React 全栈框架",
        tags=("react", "fullstack", "ssr"),
    ),
    FrameworkDoc(
        name="React",
        key="react",
        context7_id="/facebook/react",
        category="foundation",
        language="javascript",
        description="构建用户界面的 JavaScript 库",
        tags=("ui", "component", "frontend"),
    ),
    FrameworkDoc(
        name="Vue.js",
        key="vue",
        context7_id="/vuejs/core",
        category="foundation",
        language="javascript",
        description="渐进式 JavaScript 框架",
        tags=("ui", "frontend", "progressive"),
    ),
    FrameworkDoc(
        name="PyTorch",
        key="pytorch",
        context7_id="/pytorch/pytorch",
        category="foundation",
        description="深度学习框架",
        tags=("deep-learning", "ml", "tensor"),
    ),
    FrameworkDoc(
        name="Transformers",
        key="transformers",
        context7_id="/huggingface/transformers",
        category="foundation",
        description="HuggingFace Transformers 模型库",
        tags=("nlp", "ml", "pretrained"),
    ),
    FrameworkDoc(
        name="Pydantic",
        key="pydantic",
        context7_id="/pydantic/pydantic",
        category="foundation",
        description="数据验证和设置管理库",
        tags=("validation", "type-safe", "schema"),
    ),
    FrameworkDoc(
        name="scikit-learn",
        key="scikit-learn",
        context7_id="/scikit-learn/scikit-learn",
        category="foundation",
        description="机器学习库",
        tags=("ml", "classification", "regression"),
    ),
    FrameworkDoc(
        name="NumPy",
        key="numpy",
        context7_id="/numpy/numpy",
        category="foundation",
        description="科学计算基础库",
        tags=("array", "math", "scientific"),
    ),
    FrameworkDoc(
        name="Pandas",
        key="pandas",
        context7_id="/pandas-dev/pandas",
        category="foundation",
        description="数据分析与处理库",
        tags=("dataframe", "data", "analysis"),
    ),
]

# ===== 第三层：基础设施与 MLOps（数据库/部署/消息等）=====
INFRASTRUCTURE_FRAMEWORKS: list[FrameworkDoc] = [
    FrameworkDoc(
        name="Docker",
        key="docker",
        context7_id="/docker/docs",
        category="infrastructure",
        language="multi",
        description="容器化平台",
        tags=("container", "deployment", "devops"),
    ),
    FrameworkDoc(
        name="Kubernetes",
        key="kubernetes",
        context7_id="/kubernetes/website",
        category="infrastructure",
        language="multi",
        description="容器编排平台",
        tags=("orchestration", "container", "devops"),
    ),
    FrameworkDoc(
        name="Redis",
        key="redis",
        context7_id="/redis/redis",
        category="infrastructure",
        language="multi",
        description="内存数据存储",
        tags=("cache", "in-memory", "database"),
    ),
    FrameworkDoc(
        name="PostgreSQL",
        key="postgresql",
        context7_id="/postgres/postgres",
        category="infrastructure",
        language="multi",
        description="关系型数据库",
        tags=("sql", "database", "relational"),
    ),
    FrameworkDoc(
        name="MongoDB",
        key="mongodb",
        context7_id="/mongodb/docs",
        category="infrastructure",
        language="multi",
        description="文档型数据库",
        tags=("nosql", "document", "database"),
    ),
    FrameworkDoc(
        name="Elasticsearch",
        key="elasticsearch",
        context7_id="/elastic/elasticsearch",
        category="infrastructure",
        language="multi",
        description="分布式搜索引擎",
        tags=("search", "analytics", "fulltext"),
    ),
    FrameworkDoc(
        name="SQLAlchemy",
        key="sqlalchemy",
        context7_id="/sqlalchemy/sqlalchemy",
        category="infrastructure",
        description="Python SQL ORM 工具包",
        tags=("orm", "sql", "database"),
    ),
    FrameworkDoc(
        name="Celery",
        key="celery",
        context7_id="/celery/celery",
        category="infrastructure",
        description="分布式任务队列",
        tags=("async", "queue", "task"),
    ),
    FrameworkDoc(
        name="Prisma",
        key="prisma",
        context7_id="/prisma/prisma",
        category="infrastructure",
        language="javascript",
        description="下一代 ORM",
        tags=("orm", "typescript", "database"),
    ),
    FrameworkDoc(
        name="Supabase",
        key="supabase",
        context7_id="/supabase/supabase",
        category="infrastructure",
        language="multi",
        description="开源 Firebase 替代",
        tags=("baas", "postgres", "realtime"),
    ),
    FrameworkDoc(
        name="Firebase",
        key="firebase",
        context7_id="/firebase/firebase-admin-python",
        category="infrastructure",
        language="multi",
        description="Google 应用开发平台",
        tags=("baas", "google", "realtime"),
    ),
    FrameworkDoc(
        name="ChromaDB",
        key="chromadb",
        context7_id="/chroma-core/chroma",
        category="infrastructure",
        description="开源向量数据库",
        tags=("vector", "embedding", "database"),
    ),
]


# ===== 汇总注册表 =====

ALL_FRAMEWORKS: list[FrameworkDoc] = (
    AGENT_FRAMEWORKS + FOUNDATION_FRAMEWORKS + INFRASTRUCTURE_FRAMEWORKS
)

# 快速查找字典
_FRAMEWORK_BY_KEY: dict[str, FrameworkDoc] = {fw.key: fw for fw in ALL_FRAMEWORKS}
_FRAMEWORK_BY_C7ID: dict[str, FrameworkDoc] = {fw.context7_id: fw for fw in ALL_FRAMEWORKS}


def get_framework(key: str) -> FrameworkDoc | None:
    """根据 key 获取框架定义"""
    return _FRAMEWORK_BY_KEY.get(key)


def get_framework_by_context7_id(context7_id: str) -> FrameworkDoc | None:
    """根据 Context7 ID 获取框架定义"""
    return _FRAMEWORK_BY_C7ID.get(context7_id)


def get_all_framework_keys() -> list[str]:
    """获取所有框架 key 列表"""
    return [fw.key for fw in ALL_FRAMEWORKS]


def get_agent_framework_keys() -> list[str]:
    """获取 Agent 框架 key 列表（用于 contributor 模块）"""
    return [fw.key for fw in AGENT_FRAMEWORKS] + ["other"]


def get_frameworks_by_category(category: str) -> list[FrameworkDoc]:
    """按分类获取框架列表"""
    return [fw for fw in ALL_FRAMEWORKS if fw.category == category]


def search_frameworks(query: str) -> list[FrameworkDoc]:
    """根据关键词搜索匹配的框架"""
    query_lower = query.lower()
    results = []
    for fw in ALL_FRAMEWORKS:
        # 匹配 name、key、tags、description
        if (
            query_lower in fw.name.lower()
            or query_lower in fw.key
            or query_lower in fw.description.lower()
            or any(query_lower in tag for tag in fw.tags)
        ):
            results.append(fw)
    return results
