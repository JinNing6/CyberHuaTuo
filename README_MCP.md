# 🩺 CyberHuaTuo MCP Server

> 让所有 AI Coding 工具都能调用赛博华佗的「望闻问切」诊断能力
> Make CyberHuaTuo available in every AI coding tool

## 什么是 MCP？

**MCP (Model Context Protocol)** 是由 Anthropic 发起的开放协议，让 AI 助手能够连接外部工具和数据源。支持 MCP 的工具包括：

- **Claude Desktop** (Anthropic)
- **Cursor** (AI 代码编辑器)
- **Windsurf** (Codeium)
- **VS Code + GitHub Copilot**
- **Gemini CLI** (Google)
- **Continue** (开源 AI 编程助手)
- 以及更多...

## 快速开始

### ⚡ 方式一：一行直连（推荐！）

> **前提**：安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)（Python 包管理工具）

在任意 AI 工具（Claude Desktop / Cursor / VS Code / Gemini CLI）中添加：

```json
{
  "mcpServers": {
    "cyberhuatuo": {
      "command": "uvx",
      "args": ["cyberhuatuo"]
    }
  }
}
```

> `uvx` 自动从 PyPI 安装并运行，无需手动操作。与 Anthropic 官方 MCP Server 相同的标准方式。

---

### 🚀 方式二：GitHub 直连（获取最新开发版）

如果想使用 GitHub 上的最新代码（可能包含尚未发布到 PyPI 的新功能）：

#### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "cyberhuatuo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JinNing6/CyberHuaTuo", "cyberhuatuo-mcp"]
    }
  }
}
```

#### Cursor

在 Cursor 设置中添加 MCP Server：

```json
{
  "mcpServers": {
    "cyberhuatuo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JinNing6/CyberHuaTuo", "cyberhuatuo-mcp"]
    }
  }
}
```

#### VS Code (Copilot Chat)

在 `.vscode/settings.json` 中添加：

```json
{
  "mcp": {
    "servers": {
      "cyberhuatuo": {
        "command": "uvx",
        "args": ["--from", "git+https://github.com/JinNing6/CyberHuaTuo", "cyberhuatuo-mcp"]
      }
    }
  }
}
```

#### Gemini CLI

在 `~/.gemini/settings.json` 中添加：

```json
{
  "mcpServers": {
    "cyberhuatuo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JinNing6/CyberHuaTuo", "cyberhuatuo-mcp"]
    }
  }
}
```

> **工作原理**：
> `uvx` 会自动从 GitHub 仓库下载代码 → 安装依赖 → 启动 MCP Server。
> 首次运行时会自动从 GitHub 获取最新的知识库数据。
> 无需手动 clone 或 pip install。

---

### 方式三：本地安装（开发者 / 离线使用）

如果你需要修改代码或离线使用：

```bash
# 1. 克隆仓库
git clone https://github.com/JinNing6/CyberHuaTuo.git
cd CyberHuaTuo

# 2. 安装依赖
pip install -r requirements.txt
```

然后在 AI 工具中配置：

```json
{
  "mcpServers": {
    "cyberhuatuo": {
      "command": "python",
      "args": ["-m", "cyberhuatuo.mcp_server"],
      "cwd": "/path/to/CyberHuaTuo"
    }
  }
}
```

> **提示**: 将 `/path/to/CyberHuaTuo` 替换为你的实际项目路径。

### 3. 开始使用

配置完成后，在 AI 助手中直接提问即可：

- *"帮我诊断这个 LangChain 报错: ImportError: cannot import name 'ChatOpenAI' from 'langchain'"*
- *"搜索一下 CrewAI 相关的已知问题"*
- *"对这段 Agent 代码做安全体检"*

## 🌐 品牌矩阵 (Brand Matrix)

为了保护开源生态并提供全球化的无缝使用体验，CyberHuaTuo 团队在 PyPI 上建立了一系列涵盖东西方古代医学神祗的**官方别名包（Alias Packages）**。

您可以执行、安装以下**任意一个**名字，它们都会自动包含并重定向至最核心的 `cyberhuatuo` 引擎：

*   **东方建安神医 (核心)**：`cyberhuatuo`, `openhuatuo`
*   **希罗神话系**：`cyber-asclepius`, `open-asclepius`, `cyber-panacea`, `open-panacea`
*   **人类医学先驱**：`cyber-hippocrates`, `open-hippocrates`, `cyber-galen`, `open-galen`
*   **古老文明极客**：`cyber-imhotep`, `open-imhotep`, `cyber-avicenna`, `open-avicenna`

无论您身处何种文化语境，执行 `uvx <上述任意名字>` 即可直接唤醒赛博神医为你诊断代码。

---

## 可用工具 (Tools)

### 🩺 `diagnose` — 望闻问切 AI 诊断

使用知识库 + LLM 对报错信息进行「望闻问切」诊断，给出药方。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 报错信息或问题描述 |
| `framework` | string | ❌ | 按框架过滤 |
| `top_k` | int | ❌ | 参考病例数量（默认 5） |

### 🔍 `search_knowledge_base` — 向量语义搜索

在病例知识库中进行向量语义搜索，无需 LLM API Key。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 搜索查询 |
| `framework` | string | ❌ | 按框架过滤 |
| `severity` | string | ❌ | 按严重性过滤（low/medium/high/critical） |
| `complexity` | string | ❌ | 按复杂度过滤（simple/moderate/complex/extreme） |
| `top_k` | int | ❌ | 返回数量（默认 5） |

### 🛡️ `security_checkup` — Agent 代码安全体检

六经脉安全检测：沙箱隔离、密钥安全、Prompt 安全、输出安全、韧性设计、可观测性。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | string | ✅ | 要检测的代码 |

### 📚 `fetch_official_docs` — 获取官方文档

通过 Context7 获取 50+ 框架的最新官方文档（LangChain、PyTorch、FastAPI 等）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `framework` | string | ✅ | 框架标识（如 langchain, pytorch） |
| `query` | string | ✅ | 查询内容 |
| `top_k` | int | ❌ | 文档片段数量（默认 5） |

### ⛏️ `mine_github_issue` — GitHub Issue 淘金

从 GitHub Issue 中提取问题和解决方案，提炼为标准病例格式。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `owner` | string | ✅ | 仓库所有者 |
| `repo` | string | ✅ | 仓库名称 |
| `issue_number` | int | ✅ | Issue 编号 |

### 📋 `list_frameworks` — 查询支持框架

列出赛博华佗覆盖的所有框架和技术栈。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | ❌ | 按分类过滤（agent/foundation/infrastructure） |
| `search` | string | ❌ | 关键词搜索 |

### 📥 `save_prescription` — 保存贡献药方（本地 + 自动同步 GitHub）

保存药方到本地知识库。如果配置了 `GITHUB_TOKEN` 且 `GITHUB_SYNC_ENABLED=true`，会自动推送到 GitHub 仓库。保存后会自动分配 ID、重载缓存索引，并返回**贡献者名医堂称号**。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 标题（建议以中文为主，20字以内） |
| `prescription` | string | ✅ | 详细修复方案 (能解决问题的代码/思路等) |
| `framework` | string | ✅ | 框架表示 (如 `langchain`, `fastapi`) |
| `symptom` | string | ❌ | 针对症状的详细描述 |
| `error_message`| string | ❌ | 极简报错或 Traceback 会有助于之后被匹配 |
| `root_cause` | string | ❌ | 根本原因分析解释 |
| `severity` | string | ❌ | 严重性 (`low`/`medium`/`high`/`critical`) |
| `complexity` | string | ❌ | 复杂性等级 (`simple`/`moderate`/`complex`/`extreme`) |
| `tags` | array | ❌ | 自定义标签集 |
| `title_en` | string | ❌ | 对应的英文标题 |
| `contributor_github` | string | ❌ | 贡献者 GitHub 用户名（用于名医堂称号追踪） |

### 🌐 `upload_prescription` — 上传药方到 GitHub（必须配置 GITHUB_TOKEN）

与 `save_prescription` 参数完全相同，但**强制要求**同步到 GitHub 仓库。适合外部贡献者通过 MCP 直接向社区贡献药方。无 `GITHUB_TOKEN` 时会返回配置引导。

支持两种同步策略（自动选择）：
- **直接推送**：如果你是仓库 Owner/Collaborator
- **Fork + PR**：外部贡献者自动 Fork 并创建 PR

### 🏅 `my_contribution_stats` — 查询名医堂称号

查询指定 GitHub 用户在赛博华佗知识库中的贡献次数和当前称号。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `github_username` | string | ✅ | GitHub 用户名 |

**称号体系**：

| 称号 | 条件 |
|:---:|:---:|
| 🏥 坐堂医师 Resident Doctor | 1+ 贡献 |
| ⚕️ 主治医师 Attending Physician | 3+ 贡献 |
| 👨‍⚕️ 名医 Renowned Doctor | 5+ 贡献 |
| 🌟 神医 Divine Doctor | 10+ 贡献 |
| 👑 华佗再世 Hua Tuo Reborn | 20+ 贡献 |



## 资源 (Resources)

| URI | 描述 |
|-----|------|
| `cyberhuatuo://knowledge-base/stats` | 知识库统计（病例数、框架分布） |
| `cyberhuatuo://knowledge-base/schema` | 病例 JSON Schema |

---

## 提示词模板 (Prompts)

| 名称 | 描述 | 参数 |
|------|------|------|
| `diagnose-error` | 望闻问切诊断模式 | `error_message` |
| `security-audit` | Agent 安全体检模式 | `code` |
| `contribute-case` | 贡献药方模式 | `problem`, `solution`, `framework?` |

---

## 环境配置

MCP Server 会自动读取项目根目录的 `.env` 文件配置。最小配置只需：

```bash
# .env  — 最小配置（纯搜索模式，无需 API Key）
CONTEXT7_ENABLED=true
```

如需使用 `diagnose` 和 `security_checkup` 等 LLM 功能，需配置至少一个 LLM API Key：

```bash
# 选一个即可
OPENAI_API_KEY=sk-your-key
# 或
DEEPSEEK_API_KEY=sk-your-key
# 或
GEMINI_API_KEY=AIzaSy-your-key
```

完整配置选项请参考 [`.env.example`](.env.example)。

---

## 协议

Apache-2.0 License
