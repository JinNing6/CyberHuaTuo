# 🩺 贡献指南 Contributing Guide

感谢你对 CyberHuaTuo（赛博华佗）的关注！每一份贡献都是为 AI 开发者社区开出的一剂良药。

Thank you for your interest in CyberHuaTuo! Every contribution is a prescription that heals the AI developer community.

---

## 🤝 贡献方式 Ways to Contribute

### 💊 贡献药方（病例） Submit a Prescription

这是最有价值的贡献方式。如果你解决过一个 AI Agent 框架的问题，请把你的经验分享出来。

This is the most valuable way to contribute. If you've solved an AI Agent framework issue, share your experience.

**方式一：通过 GitHub Issue 提交**

1. 点击 [💊 贡献药方](https://github.com/JinNing6/CyberHuaTuo/issues/new?template=prescription.yml)
2. 填写 Issue 模板中的信息
3. 维护者会将其转化为标准病例文件入库

**方式二：通过 Pull Request 提交**

1. Fork 本仓库
2. 在 `cases/<framework>/<category>/` 目录下创建病例文件
3. 运行本地校验：`python tools/validate.py`
4. 提交 PR

### 🛠️ 改进引擎 Improve the Engine

帮助改进诊断引擎、搜索算法、前端 UI 等：

1. Fork & Clone 本仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 启动开发服务器：`python -m cyberhuatuo serve --reload`
4. 修改代码并提交 PR

### 🐛 报告问题 Report a Bug

发现了 Bug？请通过 [Issue](https://github.com/JinNing6/CyberHuaTuo/issues/new?template=bug_report.yml) 提交。

### 💡 提出建议 Suggest a Feature

有好的想法？请在 [Discussions](https://github.com/JinNing6/CyberHuaTuo/discussions) 中讨论。

---

## 📋 病例文件格式 Case File Format

所有病例文件采用 **YAML Front Matter + Markdown Body** 格式：

```markdown
---
id: "langchain-import-chatmodel-001"
title: "LangChain 0.3 升级后 ChatOpenAI 导入失败"
title_en: "ChatOpenAI import error after upgrading to LangChain 0.3"
framework: "langchain"
framework_version: ">=0.3.0"
language: "python"
tags:
  - "import-error"
  - "breaking-change"
severity: "medium"        # low / medium / high / critical
complexity: "simple"      # simple / moderate / complex / extreme
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-10"
updated_at: "2026-03-10"
contributors:
  - github: "your-username"
source_url: ""
related_cases: []
---

## 🏥 症状描述
Symptom Description

（描述问题现象）

## 🔍 错误信息
Error Message

（粘贴报错信息）

## 🔬 根因分析
Root Cause Analysis

（解释为什么会出现这个问题）

## 💊 药方
Prescriptions

### 药方 1：推荐方案 ✅ 推荐

（具体的解决步骤和代码示例）

## 🔗 参考资料
References

- [链接](url)
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 格式：`<framework>-<category>-<name>-<number>`，如 `langchain-import-chatmodel-001` |
| `title` | ✅ | 中文标题 |
| `title_en` | ✅ | 英文标题 |
| `framework` | ✅ | 框架名（见下方枚举值） |
| `severity` | ✅ | `low` / `medium` / `high` / `critical` |
| `complexity` | ✅ | `simple` / `moderate` / `complex` / `extreme` |
| `tags` | ✅ | 标签列表 |
| `created_at` | ✅ | 创建日期 |
| `contributors` | ✅ | 贡献者 GitHub 用户名列表 |

### framework 枚举值

`langchain` · `llamaindex` · `crewai` · `autogen` · `openai-sdk` · `mcp` · `dspy` · `haystack` · `semantic-kernel` · `pydantic-ai` · `langgraph` · `other`

### severity 说明

| 等级 | 含义 |
|------|------|
| `low` | 边缘问题，有 workaround |
| `medium` | 影响正常使用 |
| `high` | 严重影响开发流程 |
| `critical` | 完全无法使用 |

### tags 常用值

`import-error` · `breaking-change` · `memory` · `performance` · `tool-calling` · `agent-behavior` · `authentication` · `configuration` · `retrieval` · `general`

---

## 📂 目录结构 Directory Structure

```
cases/
├── langchain/
│   ├── import-error/
│   ├── breaking-change/
│   ├── memory/
│   ├── tool-calling/
│   └── ...
├── mcp/
├── crewai/
├── llamaindex/
├── openai-sdk/
└── ...
```

文件命名：`<简短描述>-<三位数编号>.md`，如 `chatmodel-import-001.md`。

---

## ✅ 提交前检查 Pre-submit Checklist

- [ ] 病例文件放在正确的 `cases/<framework>/<category>/` 目录下
- [ ] YAML front matter 包含所有必填字段
- [ ] framework 和 severity、complexity 使用了合法的枚举值
- [ ] id 全局唯一
- [ ] 本地校验通过：`python tools/validate.py`
- [ ] Markdown 正文包含：症状描述、错误信息、根因分析、药方 四个章节

---

## 🏅 贡献者荣誉 Contributor Recognition

- 每位贡献者都会在病例文件中署名
- 高质量贡献者将获得 **「神医」** 徽章
- 贡献排行榜在 [EPIDEMIC_REPORT.md](./EPIDEMIC_REPORT.md) 中更新

---

> *最伟大的医者从不将医术据为己有——他们行走于村落之间，救死扶伤，薪火相传。*
>
> *The greatest physicians didn't hoard knowledge — they traveled between villages, healing the sick and training the next generation.*
