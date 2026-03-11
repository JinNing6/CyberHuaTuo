"""
CyberHuaTuo 配置管理
从 .env 文件和环境变量中加载配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.resolve()

# 加载 .env 文件
load_dotenv(ROOT_DIR / ".env")


class Config:
    """CyberHuaTuo 配置"""

    # 项目路径
    ROOT_DIR: Path = ROOT_DIR
    CASES_DIR: Path = ROOT_DIR / "cases"
    SCHEMA_DIR: Path = ROOT_DIR / "schema"
    TEMPLATES_DIR: Path = Path(__file__).parent / "templates"
    STATIC_DIR: Path = Path(__file__).parent / "static"

    # 向量数据库
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(ROOT_DIR / ".chroma_db"))
    COLLECTION_NAME: str = "cyberhuatuo_cases"

    # LLM 配置
    DIAGNOSIS_MODEL: str = os.getenv("DIAGNOSIS_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str | None = os.getenv("EMBEDDING_MODEL", None)

    # Ollama
    OLLAMA_BASE_URL: str | None = os.getenv("OLLAMA_BASE_URL", None)

    # 服务配置
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # 检索配置
    TOP_K: int = 5                    # 默认返回 Top-K 病例
    MAX_DIAGNOSIS_QUESTIONS: int = 3  # 望闻问切最多追问次数

    # Context7 官方文档检索配置
    CONTEXT7_ENABLED: bool = os.getenv("CONTEXT7_ENABLED", "true").lower() == "true"
    CONTEXT7_API_KEY: str | None = os.getenv("CONTEXT7_API_KEY", None)
    CONTEXT7_BASE_URL: str = os.getenv("CONTEXT7_BASE_URL", "https://context7.com/api/v2")

    # GitHub Issues 淘金配置
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN", None)
    MINE_DEFAULT_LIMIT: int = int(os.getenv("MINE_DEFAULT_LIMIT", "10"))
    MINE_MIN_REACTIONS: int = int(os.getenv("MINE_MIN_REACTIONS", "3"))
    MINE_MIN_COMMENTS: int = int(os.getenv("MINE_MIN_COMMENTS", "2"))

    # 滋补药方配置
    NOURISHING_ENABLED: bool = os.getenv("NOURISHING_ENABLED", "true").lower() == "true"

    # 疫情通报配置
    EPIDEMIC_ENABLED: bool = os.getenv("EPIDEMIC_ENABLED", "true").lower() == "true"
    EPIDEMIC_REPORT_DIR: Path = ROOT_DIR / "reports" / "epidemic"

    @classmethod
    def has_llm_key(cls) -> bool:
        """检查是否配置了 LLM API Key"""
        return any([
            os.getenv("OPENAI_API_KEY"),
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("DEEPSEEK_API_KEY"),
            os.getenv("KIMI_API_KEY"),
            os.getenv("DOUBAO_API_KEY"),
            os.getenv("MINIMAX_API_KEY"),
            os.getenv("GROQ_API_KEY"),
            os.getenv("GEMINI_API_KEY"),
            os.getenv("COHERE_API_KEY"),
            cls.OLLAMA_BASE_URL,
        ])

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """返回已配置的 LLM 提供商列表"""
        providers = []
        if os.getenv("OPENAI_API_KEY"):
            providers.append("OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append("Anthropic")
        if os.getenv("DEEPSEEK_API_KEY"):
            providers.append("DeepSeek")
        if os.getenv("KIMI_API_KEY"):
            providers.append("Kimi")
        if os.getenv("DOUBAO_API_KEY"):
            providers.append("Doubao")
        if os.getenv("MINIMAX_API_KEY"):
            providers.append("MiniMax")
        if os.getenv("GROQ_API_KEY"):
            providers.append("Groq")
        if os.getenv("GEMINI_API_KEY"):
            providers.append("Google")
        if os.getenv("COHERE_API_KEY"):
            providers.append("Cohere")
        if cls.OLLAMA_BASE_URL:
            providers.append("Ollama")
        return providers


config = Config()
