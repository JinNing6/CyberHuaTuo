# 🩺 CyberHuaTuo 本地 AI 搜索界面设计

> 本文档定义了 CyberHuaTuo 本地运行的 AI 诊断搜索界面的架构与功能。

## 设计理念

CyberHuaTuo 是一个 GitHub 开源知识库，但搜索体验应该是**智能的**。
开发者克隆仓库后，填入 API Key，一条命令启动本地诊断界面：

```bash
git clone https://github.com/[owner]/CyberHuaTuo.git
cd CyberHuaTuo
pip install -r requirements.txt
cp .env.example .env      # 填入 API Key
python -m cyberhuatuo serve
# → 🩺 访问 http://localhost:8000
```

## 系统架构

```
┌────────────────────────────────────────────────────────────────┐
│                     本地 Web UI（浏览器）                        │
│                                                                │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │  🔍 诊断搜索          │    │  👨‍⚕️ 我来开药方                │  │
│  │  粘贴报错 → AI 诊断   │    │  解决问题后 → 一键贡献药方    │  │
│  └──────────┬───────────┘    └──────────────┬───────────────┘  │
└─────────────┼───────────────────────────────┼──────────────────┘
              │ HTTP API                      │
┌─────────────┼───────────────────────────────┼──────────────────┐
│             ▼ 本地 Python 后端 (FastAPI)     ▼                  │
│                                                                │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ 📄 文件解析 │  │ 🧠 RAG 引擎  │  │ 📝 药方生成器           │  │
│  │ cases/*.md │→│ ChromaDB     │  │ 表单 → .md 文件        │  │
│  │ YAML+MD   │  │ 向量检索     │  │ + GitHub PR 集成       │  │
│  └────────────┘  └──────────────┘  └────────────────────────┘  │
│                         │                                      │
│                  ┌──────┴──────┐                                │
│                  │ 💊 LLM 诊断 │ ← 用户 API Key                 │
│                  │ 望闻问切引擎 │   (OpenAI/Anthropic/Ollama)     │
│                  └─────────────┘                                │
└────────────────────────────────────────────────────────────────┘
```

## 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| 后端 | **FastAPI** | 轻量、Python 原生、启动快 |
| 前端 | **内嵌 HTML**（Jinja2） | 零前端构建依赖，一条命令启动 |
| 向量数据库 | **ChromaDB** | 嵌入式、pip install 即可、无需额外服务 |
| Embedding | **OpenAI / 本地 sentence-transformers** | 有 Key 用云端，没 Key 用本地模型 |
| LLM | **LiteLLM** | 统一接入 OpenAI / Anthropic / Ollama 本地模型 |
| 配置 | **`.env` 文件** | Git 忽略，用户填入 API Key |

## 功能模块

### 模块 1：智能诊断搜索

#### 模式 A：纯向量检索（零成本）
```
用户粘贴报错 → 本地 Embedding → ChromaDB 向量匹配 → Top-K 病例列表
```
- 使用本地 `sentence-transformers` 模型，无需 API Key
- 返回语义最相关的病例列表

#### 模式 B：AI 望闻问切（需 API Key）
```
用户粘贴报错 → 向量检索 Top-K → LLM 重排 + 诊断分析 → 个性化药方推荐
```
- 望：自动解析堆栈，识别框架/版本/错误类型
- 闻：结合已知问题模式分析上下文
- 问：信息不足时智能追问（最多 3 个问题）
- 切：综合检索结果 + LLM 推理，给出排序药方

### 模块 2：便捷上传药方

开发者解决了问题后，通过 UI 一键贡献：

```
点击「👨‍⚕️ 我来开药方」
       │
       ▼
┌───────────── 表单 ─────────────┐
│  框架：[LangChain ▼]           │
│  标题：[_______________]       │
│  错误信息：[           ]       │
│  药方/解决步骤：[      ]       │
│  复杂度：[🟢 简单 ▼]           │
└────────────────────────────────┘
       │
       ▼
系统自动：
  1. 生成规范 YAML + Markdown 文件
  2. 分配唯一 ID、放入正确目录
  3. 本地校验格式
       │
       ├── 方式 A：保存到本地
       │   → cases/ 目录下生成 .md 文件
       │   → 用户自行 git push + 创建 PR
       │
       └── 方式 B：一键创建 GitHub PR
           → 自动 Fork + 创建分支 + 提交 + 打开 PR
```

**智能辅助**：
- AI 自动识别报错中的框架和版本，预填表单
- 提交前自动去重检查（是否已有类似病例）
- 根据复杂度自动加载对应模板

## 项目文件结构

```
CyberHuaTuo/
├── cases/                        # 📦 病例数据（核心）
├── schema/                       # 数据校验
├── tools/                        # CLI 工具
│
├── cyberhuatuo/                  # 🩺 本地搜索引擎（新增）
│   ├── __init__.py
│   ├── __main__.py               # python -m cyberhuatuo serve
│   ├── api.py                    # FastAPI 路由
│   ├── indexer.py                # 文件解析 + 向量索引构建
│   ├── searcher.py               # 向量检索引擎
│   ├── diagnosis.py              # LLM 望闻问切引擎
│   ├── contributor.py            # 药方生成 + GitHub PR 集成
│   ├── config.py                 # 配置管理
│   └── templates/                # 内嵌 HTML 页面
│       ├── index.html            # 诊断搜索页
│       └── contribute.html       # 贡献药方页
│
├── requirements.txt              # Python 依赖
├── .env.example                  # API Key 模板
├── .github/workflows/            # CI
└── README.md
```

---

*创建日期: 2026-03-10*
