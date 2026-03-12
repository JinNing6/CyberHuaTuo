"""
CyberHuaTuo 配置管理
从 .env 文件和环境变量中加载配置
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _discover_root_dir() -> Path:
    """
    智能发现项目根目录：
    1. 开发模式：__file__ 的父级父级目录（包含 cases/ 目录）
    2. uvx / pip install 模式：
       - 检查 site-packages 中 cyberhuatuo_data (data_files)
       - 回退到 GitHub API 拉取（运行时按需）
    """
    # 方式 1：开发模式（源码目录结构）
    dev_root = Path(__file__).parent.parent.resolve()
    if (dev_root / "cases").is_dir():
        return dev_root

    # 方式 2：uvx 安装模式 — 从 egg-info/源码中也可能保留了 cases/
    # uvx --from git+ 实际会克隆完整仓库再 pip install，
    # 如果用了 --editable 或者 setuptools include-package-data，cases 随仓库在
    # uv tool 的典型安装路径类似: ~/.local/share/uv/tools/cyberhuatuo/...
    # 但源码仓库会被完整解压，所以 dev_root 通常就是对的

    # 方式 3：回退 — 在用户 HOME 下创建缓存目录
    fallback_dir = Path.home() / ".cyberhuatuo"
    cases_dir = fallback_dir / "cases"
    if not cases_dir.exists():
        # 尝试从 GitHub 拉取 cases 目录
        try:
            _fetch_cases_from_github(fallback_dir)
        except Exception as e:
            print(f"⚠️ 无法从 GitHub 获取知识库: {e}", file=sys.stderr)
            cases_dir.mkdir(parents=True, exist_ok=True)

    return fallback_dir


def _fetch_cases_from_github(target_dir: Path) -> None:
    """从 GitHub 仓库下载 cases/ 目录到本地缓存"""
    import json
    import urllib.request

    repo = "JinNing6/CyberHuaTuo"
    branch = "main"
    api_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"

    print("🩺 首次运行，正在从 GitHub 获取赛博华佗知识库...")

    headers = {"Accept": "application/vnd.github+json"}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        tree_data = json.loads(resp.read().decode("utf-8"))

    # 筛选 cases/ 和 schema/ 目录下的文件
    files_to_download = []
    for item in tree_data.get("tree", []):
        path = item.get("path", "")
        if (path.startswith("cases/") or path.startswith("schema/")) and item.get("type") == "blob":
            files_to_download.append(path)

    downloaded = 0
    for file_path in files_to_download:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
        local_path = target_dir / file_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            req = urllib.request.Request(raw_url)
            if github_token:
                req.add_header("Authorization", f"Bearer {github_token}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                local_path.write_bytes(resp.read())
            downloaded += 1
        except Exception:
            pass  # 跳过单个文件失败

    print(f"✅ 已从 GitHub 下载 {downloaded} 个知识库文件到 {target_dir}")


# 项目根目录
ROOT_DIR = _discover_root_dir()

# 加载 .env 文件（开发模式下存在）
env_file = ROOT_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)



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

    # GitHub 同步配置（MCP 纯无后端模式使用）
    GITHUB_SYNC_ENABLED: bool = os.getenv("GITHUB_SYNC_ENABLED", "true").lower() == "true"
    GITHUB_SYNC_OWNER: str = os.getenv("GITHUB_SYNC_OWNER", "JinNing6")
    GITHUB_SYNC_REPO: str = os.getenv("GITHUB_SYNC_REPO", "CyberHuaTuo")
    GITHUB_SYNC_BRANCH: str = os.getenv("GITHUB_SYNC_BRANCH", "main")

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
