## 📋 变更说明
<!-- 一句话描述你的改动 / Describe your changes in one sentence -->



## 🏥 变更类型
<!-- 勾选所有适用的选项 / Check all that apply -->

- [ ] 💊 新增药方/病例 (`cases/`)
- [ ] 🔧 引擎改进 (`cyberhuatuo/`)
- [ ] 🛠️ 工具改进 (`tools/`)
- [ ] 📝 文档更新
- [ ] 🐛 Bug 修复
- [ ] 🏗️ 基础设施 (CI/CD, 配置)

## 💊 如果是新增药方/病例，请填写

- **框架 Framework**: <!-- 如 langchain, crewai, mcp -->
- **严重程度 Severity**: <!-- low / medium / high / critical -->
- **涉及版本 Version**: <!-- 如 langchain >= 0.3.0 -->

## 🔗 关联 Issue
<!-- 填写关联的 Issue 编号 / Related issue number -->
Closes #

## 📸 截图/日志（如适用）
<!-- 粘贴相关截图或日志输出 -->



## ✅ 自查清单
<!-- 请在提交前逐项确认 / Please check before submitting -->

- [ ] 我的代码遵循本项目的[贡献指南](CONTRIBUTING.md)
- [ ] 如果是新增病例：YAML front matter 包含所有必填字段
- [ ] 如果是新增病例：Markdown 正文包含**症状描述/错误信息/根因分析/药方**四个章节
- [ ] 如果是新增病例：`id` 全局唯一，格式为 `<framework>-<category>-<name>-<number>`
- [ ] 本地校验已通过：`python tools/validate.py`
- [ ] 测试通过（如适用）：`pytest tests/ -v`
- [ ] 我同意以本项目的开源协议 (Apache 2.0) 贡献此内容

---

> 🩺 *感谢你为赛博华佗贡献药方！每一份贡献都在帮助无数 AI 开发者。*
>
> *Thank you for prescribing a cure! Every contribution heals the AI developer community.*
