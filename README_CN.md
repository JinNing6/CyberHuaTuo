<p align="center">
  <img src="assets/banner.png" alt="赛博华佗 Banner" width="100%"/>
</p>

<h1 align="center">🩺 赛博华佗 / CyberHuaTuo</h1>

<p align="center">
  <strong>开源的 AI Agent 诊断智能体。</strong><br>
  <strong>望闻问切，药到病除。</strong>
</p>

<p align="center">
  <em>粘贴报错，获得药方。以秒计，非以时。</em>
</p>

<p align="center">
  <a href="https://github.com/JinNing6/CyberHuaTuo/stargazers"><img src="https://img.shields.io/github/stars/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00D09C" alt="Stars"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/network/members"><img src="https://img.shields.io/github/forks/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00BFFF" alt="Forks"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/issues"><img src="https://img.shields.io/github/issues/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=FFD700" alt="Issues"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/许可证-Apache%202.0-FFD700?style=for-the-badge&labelColor=1a1a2e" alt="许可证"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/pulls"><img src="https://img.shields.io/badge/PRs-欢迎-00FFFF?style=for-the-badge&labelColor=1a1a2e" alt="欢迎 PR"/></a>
</p>

<p align="center">
  <a href="#-立即体验">⚡ 立即体验</a> •
  <a href="#-痛点">痛点</a> •
  <a href="#-望闻问切">诊断流程</a> •
  <a href="#-为什么选择赛博华佗">为什么选我们</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-加入诊所">加入我们</a> •
  <a href="#-华佗">华佗</a>
</p>

<p align="center">
  <a href="./README_CN.md"><strong>🇨🇳 中文</strong></a> •
  <a href="./README.md"><strong>🇬🇧 English</strong></a>
</p>

---

## ⚡ 立即体验

```bash
# 一条命令，一张药方。
cyberhuatuo diagnose "ImportError: cannot import name 'ChatOpenAI' from 'langchain'"
```

```
🔍 望    → 检测到: LangChain, Python 3.11, 导入错误
🔗 闻    → 匹配: LangChain 0.2+ 破坏性变更（包拆分）
💊 切    → 药方 #1（95% 治愈率，847 次确认）:

   pip install langchain-openai
   from langchain_openai import ChatOpenAI  # ✅ 已修复

   根因: LangChain 0.2 拆分为 langchain-core、langchain-community
   和 langchain-openai。旧导入路径已不存在。
```

> **3 秒钟。** 不是 3 小时。这就是区别。

---

## 🩻 痛点

每天，成千上万的开发者面对着 Agent 的神秘报错——在 GitHub Issues、Discord 频道、Reddit 帖子之间反复搜索。**时间在流逝，挫败感在累积。**

答案明明就在某处，却被埋在七层无关搜索结果之下。

**赛博华佗不是一个搜索框。它是一个诊断智能体——一个为 Agent 治病的 Agent。**

---

## 🤔 为什么选择赛博华佗？

| | 🩺 赛博华佗 | 🔍 Stack Overflow | 🤖 ChatGPT | 📋 GitHub Issues |
|---|:---:|:---:|:---:|:---:|
| **Agent 专属知识** | ✅ 专为 Agent 打造 | ⚠️ 通用 | ⚠️ 泛泛而谈 | ⚠️ 零散分布 |
| **版本感知诊断** | ✅ 自动检测 | ❌ 手动 | ❌ 知识截止 | ❌ 手动 |
| **结构化药方** | ✅ 根因 + 修复 + 验证 | ⚠️ 质量参差 | ⚠️ 可能幻觉 | ⚠️ 质量参差 |
| **跨框架映射** | ✅ LangChain ↔ LlamaIndex ↔ CrewAI | ❌ 信息孤岛 | ⚠️ 不一致 | ❌ 信息孤岛 |
| **社区治愈率** | ✅ 验证并排序 | ⚠️ 投票制 | ❌ 无追踪 | ❌ 无追踪 |
| **治愈速度** | ⚡ 秒级 | 🕐 小时/天 | ⚡ 快但有风险 | 🕐 小时/天 |

> *Stack Overflow 等人来答。ChatGPT 可能胡编。GitHub Issues 淹没在重复中。*
>
> ***赛博华佗开出经过实战检验的药方。***

---

## 🔮 望闻问切

传承两千年中医智慧——**望、闻、问、切**四步诊断法：

```
  你的报错信息
      │
      ▼
 ┌─────────┐
 │   望     │──→ 解析堆栈跟踪，识别框架与版本
 └────┬────┘
      ▼
 ┌─────────┐
 │   闻     │──→ 关联已知问题与破坏性变更
 └────┬────┘
      ▼
 ┌─────────┐
 │   问     │──→ 智能追问（仅在关键信息缺失时）
 └────┬────┘
      ▼
 ┌─────────┐
 │   切     │──→ 语义检索 → 大模型推理 → 排序药方
 └────┬────┘
      ▼
 💊 五大药方（按治愈率排序）
```

每张药方包含：

- 🎯 **根因分析** — 不仅告诉你怎么修，更告诉你为什么坏
- 🔧 **即用代码** — 逐步指引，可直接复制粘贴
- 📌 **版本锁定** — 确认此修复适用于你的框架版本
- 🔄 **跨框架映射** — *"LangChain 的问题？这是 LlamaIndex 的等效方案"*
- ✅ **社区验证** — 点赞、测试、标记**"已治愈 ✅"**

---

## 📊 疫情通报 — 实时情报

一个实时动态看板，展示**当前 AI Agent 生态中正在爆发的问题**：

- 🔥 **热门问题**及其治愈率
- 🗺️ 跨框架问题**热力图**
- 📈 **框架健康评分** — 在采用之前先了解

---

## 🚀 快速开始

### 网页端

> 访问 [**cyberhuatuo.dev**](https://cyberhuatuo.dev)，粘贴你的报错，就这么简单。

### 命令行

```bash
pip install cyberhuatuo

# 诊断——即时获得药方
cyberhuatuo diagnose "你的错误信息"

# 搜索知识库
cyberhuatuo search "LangChain memory not persisting"
```

### 自部署

```bash
git clone https://github.com/JinNing6/CyberHuaTuo.git
cd CyberHuaTuo
docker compose up -d
# → http://localhost:3000
```

---

## 📋 支持的框架

| 框架 | 病例数 | 状态 | 参与 👇 |
|-----------|:-----:|--------|--------|
| LangChain | 1+ | 🟢 种子数据已上线 | [贡献病例 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| MCP (Anthropic) | 1+ | 🟢 种子数据已上线 | [贡献病例 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| CrewAI | 1+ | 🟢 种子数据已上线 | [贡献病例 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| LlamaIndex | — | 🟡 接受 PR | [成为第一人 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| OpenAI SDK | — | 🟡 接受 PR | [成为第一人 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| AutoGen | — | 🟡 接受 PR | [成为第一人 →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| DSPy | — | 🔵 已规划 | [投票 →](https://github.com/JinNing6/CyberHuaTuo/discussions) |
| Haystack | — | 🔵 已规划 | [投票 →](https://github.com/JinNing6/CyberHuaTuo/discussions) |

> **每个框架都从一个病例开始。你的，可能就是第一个。**

---

## 🏥 加入诊所

### 这不只是一个项目。这是一场运动。

> *最伟大的医者从不将医术据为己有——他们行走于村落之间，救死扶伤，薪火相传。*
>
> *赛博华佗，便是这段旅程在 AI 时代的延续。*

---

### 👨‍⚕️ 成为坐堂医师

找到了拯救你项目的修复方案？**别让它埋没在你的 commit 记录里。**

1. 📝 **提交药方** — 记录你的修复：错误信息、框架版本、运行环境和解决方案
2. ✅ **社区验证** — 其他开发者通过真实测试验证你的药方
3. 🏅 **获得"神医"徽章** — 顶级贡献者将获得传奇的**神医**称号

> *你不需要是 10x 工程师。你只需要解决过一个别人还没解决的问题——就够了。*

### 🧬 贡献病例

遇到了让人抓狂的 Agent Bug？**你的痛苦是有价值的。**

- 错误信息 + 完整堆栈跟踪
- 框架名称和版本、环境详情
- 你的调试过程和最终修复
- **加分项**：复现步骤

**你贡献的每一个病例，都让诊断引擎更聪明。你不是在提 Bug 报告——你在训练一位数字医师。**

### 🛠️ 改进引擎

1. Fork 并克隆仓库
2. 查阅 `CONTRIBUTING.md` 了解开发配置
3. 提交一个 PR——每一次改进都将帮助成千上万的开发者

---

## 🛠️ 技术栈

| 层 | 技术 |
|-------|-----------|
| **后端** | FastAPI · PostgreSQL · Qdrant · Redis |
| **前端** | Next.js |
| **ML 流水线** | text-embedding-3-small · LiteLLM |
| **基础设施** | Docker Compose |

---

## 🏛️ 华佗

> **华佗**（约 145–208），字元化，东汉末年沛国谯县（今安徽亳州）人。
>
> 与董奉、张仲景并称为**"建安三神医"**，被誉为中国**"外科鼻祖"**。

在群雄割据、瘟疫横行的东汉末年，华佗没有选择仕途与安逸，而是背起药箱行走于安徽、河南、山东、江苏之间——为苍生治病，分文不取。他精通内科、外科、妇科、儿科与针灸，当时的人们称他为**"神医"**。

他最具开创性的贡献，是发明了**麻沸散（Ma Fei San）**——世界上最早的全身麻醉药方，比西方使用化学麻醉剂进行外科手术**早了整整 1600 多年**。据《后汉书》记载，华佗让患者饮用以酒调服的麻沸散，待患者失去知觉后，便可进行腹部手术——切除病灶、缝合创口，四五日即愈。

他还创编了**五禽戏**——模仿虎、鹿、熊、猿、鸟五种动物动作的健身术，已被列为**国家级非物质文化遗产**。他的理念超越治病本身——**预防胜于治疗**。

华佗最终因拒绝成为曹操的私人医师而被下狱处死。传说他临终前将毕生医术写成《**青囊书**》交付狱卒，但狱卒不敢接收，医书被焚毁——中国医学史上最伟大的外科经验就此失传。

> **但华佗的精神从未失传。**

今天，1800 年后，AI 开发者面对的"疑难杂症"同样散落各处——GitHub Issues 的角落、Discord 消失的对话、Stack Overflow 过时的回答。**赛博华佗，便是要把这些散落的"古方"重新集结，让集体智慧惠及每一个人。**

---

## ⭐ Star History

<a href="https://star-history.com/#JinNing6/CyberHuaTuo&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=JinNing6/CyberHuaTuo&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=JinNing6/CyberHuaTuo&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=JinNing6/CyberHuaTuo&type=Date" />
 </picture>
</a>

---

## 📜 许可协议

[Apache License 2.0](LICENSE) — 使用它。Fork 它。基于它构建。用它治愈。

---

<p align="center">
  <br>
  <strong>🩺 你的 Agent 病了？</strong><br>
  <strong>走进来，剩下的交给华佗。</strong>
  <br><br>
  <em>望闻问切，药到病除。</em><br>
  <em>古为今用，薪火相传。</em><br>
  <em>这是技术对文化的致敬，也是文化对技术的赋能。</em>
  <br><br>
  <a href="https://github.com/JinNing6/CyberHuaTuo">⭐ 点个 Star</a> · 
  <a href="https://github.com/JinNing6/CyberHuaTuo/issues/new">🐛 报告问题</a> · 
  <a href="https://github.com/JinNing6/CyberHuaTuo/discussions">💬 讨论</a> · 
  <a href="https://discord.gg/cyberhuatuo">🎮 Discord</a>
  <br><br>
  <sub>以华佗之名，致敬中华五千年医道传承。</sub><br>
  <sub>Named after 华佗, the divine physician of ancient China — in tribute to 5,000 years of Chinese medical wisdom.</sub>
</p>
