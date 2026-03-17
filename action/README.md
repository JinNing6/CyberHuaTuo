# 🩺 CyberHuaTuo Security Checkup Action

**AI Agent 代码六经脉安全体检** — 每次 PR 自动审计，让赛博华佗成为你 CI/CD 的永久驻场医师。

[![GitHub Action](https://img.shields.io/badge/GitHub_Action-CyberHuaTuo-00D09C?logo=github-actions)](https://github.com/JinNing6/CyberHuaTuo)

## ✨ 功能

- 🛡️ **沙箱隔离** — 检测 `eval()`/`exec()` 等危险函数调用
- 🔑 **密钥安全** — 检测硬编码 API Key、Token、密码
- 🧠 **Prompt 安全** — 检测 Prompt 注入风险
- 🔒 **输出安全** — 检测 LLM 输出的注入风险
- ⏱️ **韧性设计** — 检测缺失的错误处理、超时、重试
- 📊 **可观测性** — 检测日志中的敏感信息泄露

## 🚀 快速开始

**3 步嵌入你的 CI/CD：**

### 第 1 步：添加 Workflow 文件

在你的项目中创建 `.github/workflows/cyberhuatuo-checkup.yml`：

```yaml
name: 🩺 CyberHuaTuo Security Checkup

on:
  pull_request:
    branches: [main]

jobs:
  checkup:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: JinNing6/CyberHuaTuo/action@v1
        with:
          api-key: ${{ secrets.OPENAI_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### 第 2 步：配置 API Key（可选）

在仓库 `Settings → Secrets and variables → Actions` 中添加：

| Secret 名称 | 说明 |
|-------------|-----|
| `OPENAI_API_KEY` | OpenAI API Key（推荐） |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（备选） |

> 💡 **不提供 API Key 也能用！** 系统会自动降级为静态规则扫描模式。

### 第 3 步：提交 PR，享受自动体检！

每次 PR 提交后，赛博华佗会自动：
1. 扫描变更的代码文件
2. 进行六经脉安全分析
3. 在 PR 下发表体检报告 👇

```
🩺 CyberHuaTuo Security Checkup Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 总体评分: 65/100 🟡 需要调理

🔮 六经脉诊断：
  🛡️ 沙箱隔离    80/100  ✅ 通过
  🔑 密钥安全    30/100  ❌ 危险 ← 发现硬编码 API Key
  🧠 Prompt 安全  70/100  ⚠️ 警告
  🔒 输出安全    85/100  ✅ 通过
  ⏱️ 韧性设计    55/100  ⚠️ 警告
  📊 可观测性    90/100  ✅ 通过

🚨 最紧急的问题:
  1. 发现疑似 OpenAI API Key (sk-...)
  2. HTTP 请求未设置 timeout
  3. 用户输入直接拼接进 Prompt
```

## ⚙️ 完整参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `api-key` | 否 | `""` | LLM API Key，不提供则使用静态规则扫描 |
| `provider` | 否 | `openai` | LLM 提供商: `openai` / `deepseek` / `gemini` / `anthropic` / `groq` |
| `model` | 否 | 自动选择 | LLM 模型名称 |
| `scan-path` | 否 | `.` | 扫描根路径（相对于仓库根目录） |
| `file-pattern` | 否 | `**/*.py` | 文件匹配模式（glob 格式，逗号分隔） |
| `max-files` | 否 | `10` | 最多扫描文件数 |
| `fail-on-score` | 否 | `0` | 低于此分数时 Action 标记为失败（0 = 永不失败） |
| `comment-on-pr` | 否 | `true` | 是否在 PR 下发表体检报告评论 |
| `github-token` | 否 | `${{ github.token }}` | GitHub Token（用于 PR 评论） |

## 📤 输出

| 输出 | 说明 |
|------|------|
| `health-score` | 总体健康评分 (0-100) |
| `report-json` | JSON 格式完整体检报告 |

### 使用输出值

```yaml
steps:
  - uses: JinNing6/CyberHuaTuo/action@v1
    id: checkup
    with:
      api-key: ${{ secrets.OPENAI_API_KEY }}
      github-token: ${{ secrets.GITHUB_TOKEN }}

  - name: 使用体检结果
    run: |
      echo "健康评分: ${{ steps.checkup.outputs.health-score }}"
      if [ "${{ steps.checkup.outputs.health-score }}" -lt 50 ]; then
        echo "⚠️ 安全评分过低，请修复后重试"
      fi
```

## 🔧 高级用法

### 仅扫描特定目录

```yaml
- uses: JinNing6/CyberHuaTuo/action@v1
  with:
    scan-path: src/agents
    file-pattern: "**/*.py,**/*.js"
    max-files: 20
```

### 设置失败阈值

```yaml
- uses: JinNing6/CyberHuaTuo/action@v1
  with:
    fail-on-score: 50  # 低于 50 分时 CI 失败
```

### 使用 DeepSeek（更经济）

```yaml
- uses: JinNing6/CyberHuaTuo/action@v1
  with:
    api-key: ${{ secrets.DEEPSEEK_API_KEY }}
    provider: deepseek
```

### 无 API Key 模式（纯静态规则扫描）

```yaml
- uses: JinNing6/CyberHuaTuo/action@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    # 不提供 api-key，自动使用静态规则扫描
```

## 🔐 安全与隐私

> [!IMPORTANT]
> 当使用 AI 深度分析模式时，你的代码内容会发送给 LLM 提供商（如 OpenAI）进行分析。
> 如果你的代码包含敏感信息，建议使用**静态规则扫描模式**（不提供 API Key 即可）。

- 代码仅在 CI 运行期间处理，不会被赛博华佗存储
- GitHub Token 仅用于 PR 评论，权限最小化
- 所有通信通过 HTTPS 加密

## 📊 两种扫描模式对比

| 特性 | 🧠 AI 深度分析 | 📋 静态规则扫描 |
|------|----------------|-----------------|
| 需要 API Key | ✅ 是 | ❌ 否 |
| 检测精度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 运行速度 | ~30 秒/文件 | ~1 秒/文件 |
| 代码发送给 LLM | ✅ 是 | ❌ 否 |
| 上下文理解 | ✅ 理解代码逻辑 | ❌ 仅模式匹配 |
| 建议质量 | ⭐⭐⭐⭐⭐ 精准药方 | ⭐⭐⭐ 通用建议 |

## 🔗 相关链接

- [CyberHuaTuo 主仓库](https://github.com/JinNing6/CyberHuaTuo)
- [MCP Server 文档](https://github.com/JinNing6/CyberHuaTuo/blob/main/README_MCP.md)
- [贡献指南](https://github.com/JinNing6/CyberHuaTuo/blob/main/CONTRIBUTING.md)

---

*🩺 赛博华佗——AI Agent 的永久驻场医师 | "拔掉就出血"*
