<p align="center">
  <img src="assets/banner.png" alt="CyberHuaTuo Banner" width="100%"/>
</p>

<h1 align="center">🩺 CyberHuaTuo / 赛博华佗</h1>

<p align="center">
  <strong>The open-source diagnostic intelligence for AI agents.</strong><br>
  <strong>开源的 AI Agent 诊断智能体。</strong>
</p>

<p align="center">
  <em>Paste your error. Get a cure. In seconds, not hours.</em><br>
  <em>粘贴报错，获得药方。以秒计，非以时。</em>
</p>

<p align="center">
  <a href="https://github.com/JinNing6/CyberHuaTuo/stargazers"><img src="https://img.shields.io/github/stars/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00D09C" alt="Stars"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/network/members"><img src="https://img.shields.io/github/forks/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=00BFFF" alt="Forks"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/issues"><img src="https://img.shields.io/github/issues/JinNing6/CyberHuaTuo?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=FFD700" alt="Issues"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-FFD700?style=for-the-badge&labelColor=1a1a2e" alt="License"/></a>
  <a href="https://github.com/JinNing6/CyberHuaTuo/pulls"><img src="https://img.shields.io/badge/PRs-welcome-00FFFF?style=for-the-badge&labelColor=1a1a2e" alt="PRs Welcome"/></a>
</p>

<p align="center">
  <a href="#-try-it-now">⚡ Try It</a> •
  <a href="#-the-problem">The Problem</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-why-cyberhuatuo">Why Us</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-join-the-clinic">Join Us</a> •
  <a href="#-the-name">The Name</a>
</p>

<p align="center">
  <a href="./README_CN.md"><strong>🇨🇳 完整中文文档</strong></a>
</p>

---

## ⚡ Try It Now

```bash
# One command. One cure.
cyberhuatuo diagnose "ImportError: cannot import name 'ChatOpenAI' from 'langchain'"
```

```
🔍 望 (Look)    → Detected: LangChain, Python 3.11, import error
🔗 闻 (Listen)  → Matched: Breaking change in LangChain 0.2+ (package split)
💊 切 (Diagnose) → Prescription #1 (95% cure rate, 847 confirmations):

   pip install langchain-openai
   from langchain_openai import ChatOpenAI  # ✅ Fixed

   Root cause: LangChain 0.2 split into langchain-core, langchain-community,
   and langchain-openai. The old import path no longer exists.
```

> **3 seconds.** Not 3 hours. That's the difference.
>
> **三秒钟。** 不是三小时。这就是区别。

---

## 🩻 The Problem

Every day, thousands of developers stare at cryptic agent errors — copy-pasting stack traces across GitHub Issues, Discord threads, Reddit posts, and half-abandoned blog articles. **Hours evaporate. Frustration compounds.**

The fix is out there. Buried under seven layers of irrelevant search results.

<!-- 每天，成千上万的开发者面对 Agent 报错束手无策。答案就在某处，却被埋在七层无关搜索结果之下。 -->

**CyberHuaTuo is not a search box. It's a diagnostic intelligence — an agent that heals agents.**

---

## 🤔 Why CyberHuaTuo?

| | 🩺 CyberHuaTuo | 🔍 Stack Overflow | 🤖 ChatGPT | 📋 GitHub Issues |
|---|:---:|:---:|:---:|:---:|
| **Agent-specific knowledge** | ✅ Purpose-built | ⚠️ General | ⚠️ Generic | ⚠️ Scattered |
| **Version-aware diagnosis** | ✅ Auto-detect | ❌ Manual | ❌ Outdated cutoff | ❌ Manual |
| **Structured prescriptions** | ✅ Root cause + fix + verification | ⚠️ Varies | ⚠️ May hallucinate | ⚠️ Varies |
| **Cross-framework mapping** | ✅ LangChain ↔ LlamaIndex ↔ CrewAI | ❌ Siloed | ⚠️ Inconsistent | ❌ Siloed |
| **Community cure rate** | ✅ Verified & ranked | ⚠️ Vote-based | ❌ No tracking | ❌ No tracking |
| **Speed to cure** | ⚡ Seconds | 🕐 Hours/Days | ⚡ Fast but risky | 🕐 Hours/Days |

> *Stack Overflow waits for someone to answer. ChatGPT might hallucinate. GitHub Issues drown in duplicates.*
>
> ***CyberHuaTuo prescribes battle-tested cures.***

---

## 🔮 How It Works

Inspired by **望闻问切** — the 2,000-year-old four-step diagnosis of traditional Chinese medicine:

```
  Your Error
      │
      ▼
 ┌─────────┐
 │ 望 Look  │──→ Parse stack trace, detect framework & version
 └────┬────┘
      ▼
 ┌──────────┐
 │ 闻 Listen │──→ Correlate with known issues & breaking changes
 └─────┬────┘
      ▼
 ┌────────┐
 │ 问 Ask  │──→ Smart follow-up (only when critical info is missing)
 └───┬────┘
      ▼
 ┌───────────┐
 │ 切 Diagnose│──→ Semantic search → LLM reasoning → Ranked prescriptions
 └─────┬─────┘
      ▼
 💊 Top-5 Prescriptions (ranked by cure rate)
```

Every prescription includes:

- 🎯 **Root cause** — not just _what_ to do, but _why_ it broke
- 🔧 **Copy-paste fix** — step-by-step with ready-to-run code
- 📌 **Version-locked** — applies to your exact framework version
- 🔄 **Cross-framework map** — *"LangChain issue? Here's the LlamaIndex equivalent."*
- ✅ **Community-verified** — upvoted, tested, and marked **"Cured ✅"**

---

## 📊 Epidemic Report — Live Intelligence

<!-- 疫情通报 — 实时情报看板 -->

A living dashboard showing **what's breaking across the AI agent ecosystem right now**:

- 🔥 **Trending issues** and their cure rates
- 🗺️ **Heatmap** of problems across frameworks
- 📈 **Framework health scores** — know before you adopt

---

## 🚀 Quick Start

### Web

> Visit [**cyberhuatuo.dev**](https://cyberhuatuo.dev) and paste your error. That's it.

### CLI

```bash
pip install cyberhuatuo

# Diagnose — instant prescription
cyberhuatuo diagnose "your error message here"

# Search the knowledge base
cyberhuatuo search "LangChain memory not persisting"
```

### Self-Hosted

```bash
git clone https://github.com/JinNing6/CyberHuaTuo.git
cd CyberHuaTuo
docker compose up -d
# → http://localhost:3000
```

---

## 📋 Supported Frameworks

| Framework | Cases | Status | Help us grow 👇 |
|-----------|:-----:|--------|-----------------|
| LangChain | 1+ | 🟢 Seed data live | [Add a case →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| MCP (Anthropic) | 1+ | 🟢 Seed data live | [Add a case →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| CrewAI | 1+ | 🟢 Seed data live | [Add a case →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| LlamaIndex | — | 🟡 Accepting PRs | [Be the first →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| OpenAI SDK | — | 🟡 Accepting PRs | [Be the first →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| AutoGen | — | 🟡 Accepting PRs | [Be the first →](https://github.com/JinNing6/CyberHuaTuo/issues/new) |
| DSPy | — | 🔵 Planned | [Vote →](https://github.com/JinNing6/CyberHuaTuo/discussions) |
| Haystack | — | 🔵 Planned | [Vote →](https://github.com/JinNing6/CyberHuaTuo/discussions) |

> **Every framework starts with one case. Yours could be the first.**

---

## 🏥 Join the Clinic

### This isn't just a project. This is a movement.

> *The greatest physicians didn't hoard knowledge — they traveled between villages, healing the sick and training the next generation. CyberHuaTuo is that journey, for the age of AI.*
>
> *最伟大的医者从不将医术据为己有——他们行走于村落之间，救死扶伤，薪火相传。赛博华佗，便是这段旅程在 AI 时代的延续。*

---

### 👨‍⚕️ Become a Resident Doctor（成为坐堂医师）

Found a fix that saved your project? **Don't let it die in your commit history.**

1. 📝 **Submit a Prescription** — document your fix with error, version, env, and solution
2. ✅ **Community Verification** — other developers validate through real-world testing
3. 🏅 **Earn the "神医" Badge** — top contributors earn the **Divine Doctor（神医）** title

> *You don't need to be a 10x engineer. You just need to have solved one problem that someone else hasn't — yet.*

### 🧬 Contribute Cases（贡献病例）

Encountered a mind-bending agent bug? **Your suffering has value.**

- Error message + full stack trace
- Framework name & version, environment details
- Your debugging journey and final fix
- **Bonus**: reproduction steps

**Every case makes the engine smarter. You're not filing a bug report — you're training a digital physician.**

### 🛠️ Improve the Engine（改进引擎）

1. Fork & clone the repo
2. Check `CONTRIBUTING.md` for setup
3. Submit a PR — every improvement heals thousands

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI · PostgreSQL · Qdrant · Redis |
| **Frontend** | Next.js |
| **ML Pipeline** | text-embedding-3-small · LiteLLM |
| **Infrastructure** | Docker Compose |

---

## 🏛️ The Name

<blockquote>

**华佗**（约 145–208），字元化，东汉末年名医，中国"外科鼻祖"。

**Hua Tuo** (c. 145–208 AD) — the legendary physician of ancient China, revered as the "Father of Surgery."

</blockquote>

In an age of warlords and plague, while others sought power, Hua Tuo traveled across provinces with nothing but a medicine bag — healing the sick, asking for nothing in return. He invented **Ma Fei San（麻沸散）**, the world's first general anesthetic, **1,600 years before Western medicine**. He pioneered abdominal surgery when the rest of the world was still praying to gods.

在群雄割据、瘟疫横行的东汉末年，华佗没有选择仕途，而是背起药箱行走四方，悬壶济世。他发明的**麻沸散**是世界上最早的全身麻醉药——比西方早了 **1600 多年**。

When Cao Cao demanded he serve as a personal physician, Hua Tuo refused — and was executed. Legend says his life's medical knowledge, compiled in the *Book of the Azure Bag（青囊书）*, was burned with him. The greatest surgical wisdom of ancient China, lost to tyranny.

当曹操要他做私人医师时，华佗宁死不从。传说他毕生医术写成的《青囊书》随他一同被焚毁——中国医学史上最伟大的外科经验，就此失传。

> **But the spirit was never lost.**
>
> **但精神从未失传。**

Today, 1,800 years later, AI developers face their own scattered "ancient prescriptions" — buried in GitHub Issues, lost Discord threads, outdated Stack Overflow answers. **CyberHuaTuo gathers them all.**

今天，1800 年后，AI 开发者面对的"古方"同样散落各处。**赛博华佗，便是要把它们重新集结。**

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

## 📜 License

[Apache License 2.0](LICENSE) — Use it. Fork it. Build on it. Heal with it.

---

<p align="center">
  <br>
  <strong>🩺 Your Agent is sick?</strong><br>
  <strong>Walk in. We'll take it from here.</strong>
  <br><br>
  <strong>你的 Agent 病了？走进来，剩下的交给华佗。</strong>
  <br><br>
  <em>望闻问切，药到病除。</em><br>
  <em>古为今用，薪火相传。</em><br>
  <em>这是技术对文化的致敬，也是文化对技术的赋能。</em>
  <br><br>
  <a href="https://github.com/JinNing6/CyberHuaTuo">⭐ Star this repo</a> · 
  <a href="https://github.com/JinNing6/CyberHuaTuo/issues/new">🐛 Report a Bug</a> · 
  <a href="https://github.com/JinNing6/CyberHuaTuo/discussions">💬 Discussions</a> · 
  <a href="https://discord.gg/cyberhuatuo">🎮 Discord</a>
  <br><br>
  <sub>Named after 华佗, the divine physician of ancient China — in tribute to 5,000 years of Chinese medical wisdom.</sub><br>
  <sub>以华佗之名，致敬中华五千年医道传承。</sub>
</p>
