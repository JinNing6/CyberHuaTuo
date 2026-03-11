# 🤖 CyberHuaTuo GitHub Bot — 安装与使用指南
Installation & Usage Guide

> **让 CyberHuaTuo 赛博华佗守护你的仓库——每个新 Issue 都会自动收到药方推荐。**

## 🌟 功能概述
Feature Overview

| 功能 | 说明 |
|:----:|:----:|
| 🩺 **自动诊断** | 新 Issue 打开时自动匹配知识库中的药方 |
| 🤖 **@提及响应** | 在任意评论中 `@CyberHuaTuo` 触发定向诊断 |
| ⚡ **零配置** | 使用 GitHub Actions 内置 Token，无需额外 API Key |
| 🛡️ **防循环** | Bot 自动识别自身评论，不会陷入无限回复 |

## 🚀 快速安装（3 分钟）
Quick Setup

### 方式 1：直接在你的仓库使用（推荐）

只需将 CyberHuaTuo 的 Bot workflow 复制到你的仓库即可：

```bash
# 1. 在你的仓库根目录
mkdir -p .github/workflows

# 2. 下载 Bot workflow 文件
curl -o .github/workflows/bot-prescribe.yml \
  https://raw.githubusercontent.com/JinNing6/CyberHuaTuo/main/.github/workflows/bot-prescribe.yml

# 3. 克隆 CyberHuaTuo 药方库（作为 Git submodule）
git submodule add https://github.com/JinNing6/CyberHuaTuo.git cyberhuatuo-kb

# 4. 提交并推送
git add .
git commit -m "feat: 添加 CyberHuaTuo Bot 自动诊断"
git push
```

### 方式 2：Fork CyberHuaTuo 仓库

1. Fork [CyberHuaTuo](https://github.com/JinNing6/CyberHuaTuo) 仓库
2. Bot 会自动在你 Fork 的仓库中工作
3. 创建新 Issue 或评论 `@CyberHuaTuo` 即可测试

## 📋 工作原理
How It Works

```
┌─────────────────────────────────────────────────────┐
│                    GitHub Issue                      │
│                                                      │
│  触发事件                                            │
│  ├─ issues.opened     → 新 Issue 自动诊断           │
│  └─ issue_comment     → @CyberHuaTuo 定向响应       │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         GitHub Actions Workflow              │   │
│  │                                              │   │
│  │  1. 检出代码 (获取 cases/ 药方库)            │   │
│  │  2. 安装 Python + pyyaml                     │   │
│  │  3. 运行 bot_matcher.py                      │   │
│  │     ├─ 框架名检测                            │   │
│  │     ├─ 错误关键词匹配                        │   │
│  │     ├─ Tags 交叉匹配                         │   │
│  │     └─ 文本相似度计算                        │   │
│  │  4. 生成中医主题回复                         │   │
│  │  5. 通过 GitHub API 发表评论                 │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  💊 自动回复匹配的药方                              │
└─────────────────────────────────────────────────────┘
```

## ⚙️ 配置项
Configuration

在 `bot-prescribe.yml` 中可以调整以下环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BOT_MIN_SCORE` | `15` | 最低匹配分数阈值（0-100），低于此分数不回复 |
| `BOT_MAX_RESULTS` | `3` | 最大返回药方数量 |

## 🎯 使用示例
Usage Examples

### 示例 1：新 Issue 自动诊断

创建新 Issue:
```
标题: ImportError: cannot import name 'ChatOpenAI' from 'langchain'
正文: After upgrading to LangChain 0.3, my import statement broke...
```

Bot 自动回复：
> 🩺 赛博华佗 · 自动诊断
>
> 💊 药方 1：LangChain 0.3 升级后 ChatOpenAI 导入失败（相关度 92%）
>
> ⚡ 速效药：`pip install langchain-openai`

### 示例 2：@提及触发

在任意 Issue 评论中：
```
@CyberHuaTuo 我的 CrewAI agent 一直在无限循环
```

Bot 响应：
> 🩺 赛博华佗 · 自动诊断
>
> 💊 药方 1：CrewAI Agent 陷入无限循环（相关度 85%）

## 🏗️ 贡献飞轮
Contribution Flywheel

```
开发者看到 Bot 有用
        ↓
  贡献更多药方
        ↓
  Bot 更精准
        ↓
更多仓库安装 Bot
        ↓
更多开发者接触 CyberHuaTuo
        ↓
  (循环加速)
```

**如何贡献药方？**

1. Fork [CyberHuaTuo](https://github.com/JinNing6/CyberHuaTuo)
2. 在 `cases/<framework>/` 下添加新的 `.md` 药方文件
3. 提交 PR — CI 会自动校验格式
4. 你的药方将帮助全球开发者自动诊断问题 🌍

## 🛡️ 安全说明
Security Notes

- Bot 使用 GitHub Actions 内置的 `GITHUB_TOKEN`，权限仅限于读取代码和写入 Issue 评论
- 不调用任何外部 API（无 LLM、无第三方服务）
- 所有匹配逻辑在 CI runner 本地执行
- Bot 通过签名检测防止自身评论触发无限循环

---

*🩺 赛博华佗 — AI 生态的问题解决基础设施*
*CyberHuaTuo — Diagnostic Intelligence for AI Ecosystems*
