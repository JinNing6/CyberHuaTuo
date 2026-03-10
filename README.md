<p align="center">
  <img src="assets/banner.png" alt="CyberHuaTuo Banner" width="100%"/>
</p>

<h1 align="center">🩺 CyberHuaTuo / 赛博华佗</h1>

<p align="center">
  <strong>望闻问切，药到病除。</strong><br>
  <strong>Diagnose. Prescribe. Cure.</strong>
</p>

<p align="center">
  <em>Your Agent is sick? Walk in.</em><br>
  <em>你的 Agent 病了？华佗来了。</em>
</p>

<p align="center">
  <a href="#-the-problem">The Problem</a> •
  <a href="#-four-step-diagnosis">How It Works</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-join-the-clinic">Join Us</a> •
  <a href="#-license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-building-00D09C?style=flat-square&logo=statuspage&logoColor=white" alt="Status"/>
  <img src="https://img.shields.io/badge/license-Apache%202.0-FFD700?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/PRs-welcome-00FFFF?style=flat-square" alt="PRs Welcome"/>
</p>

---

## 🩻 The Problem

> *Every day, thousands of developers stare at cryptic agent errors — copy-pasting stack traces across GitHub Issues, Discord threads, Reddit posts, and half-abandoned blog articles. Hours evaporate. Frustration compounds. The fix was out there, buried under seven layers of irrelevant search results.*

**CyberHuaTuo exists because debugging AI agents shouldn't feel like archaeology.**

In the 2025–2026 wave of AI agent adoption, the problem density is exploding but solutions remain **scattered, fragmented, and slow**. Stack Overflow waits for human answers. GitHub Issues drown in duplicates. Discord threads vanish into the void.

**CyberHuaTuo is not a search box. It is a diagnostic intelligence — an agent that heals agents.**

Paste your error. Get a cure. In seconds, not hours.

---

## 🔮 Four-Step Diagnosis

Inspired by the 2,000-year-old wisdom of traditional Chinese medicine, CyberHuaTuo diagnoses with the precision of an ancient master and the speed of a modern machine:

```
  Your Error Message
         │
         ▼
   ┌──────────┐
   │  望 Look  │──→ Parse stack trace, detect framework & version
   └─────┬────┘
         ▼
   ┌───────────┐
   │ 闻 Listen  │──→ Correlate with known issues, breaking changes, env factors
   └──────┬────┘
         ▼
   ┌─────────┐
   │  问 Ask  │──→ Smart follow-up questions (only when critical info is missing)
   └────┬────┘
         ▼
   ┌────────────┐
   │ 切 Diagnose │──→ Semantic search → LLM reasoning → Ranked prescriptions
   └──────┬─────┘
         ▼
   💊 Top-5 Prescriptions (ranked by relevance & cure rate)
```

| Step | 中文 | What It Does |
|------|------|-------------|
| **👁️ Look** | 望 | Automatically parse your error stack trace — identify framework, version, and error type |
| **👂 Listen** | 闻 | Contextual analysis — correlate with known issues, breaking changes, and environmental factors |
| **🗣️ Ask** | 问 | Intelligently ask 1–3 follow-up questions only when critical context is missing |
| **🫀 Diagnose** | 切 | Semantic search + LLM reasoning to deliver ranked, battle-tested prescriptions |

---

## 💊 Smart Prescriptions

Every prescription is not a guess — it's a **battle-tested cure**:

- 🎯 **Root cause explanation** — not just _what_ to do, but _why_ it broke
- 🔧 **Step-by-step fix** with copy-paste-ready code snippets
- 📌 **Version-locked** — tells you if this fix applies to your exact framework version
- 🔄 **Cross-framework mapping** — *"This LangChain issue? Here's the LlamaIndex equivalent."*
- ✅ **Community-verified** — upvote, downvote, and the sacred **"Cured ✅"** confirmation

---

## 📊 Epidemic Report — Real-Time Intelligence

A living dashboard that shows **what's breaking across the AI agent ecosystem right now**:

- 🔥 Trending problems and their cure rates
- 🗺️ Heatmap of issues across frameworks
- 📈 Framework health scores — know before you adopt

---

## 🚀 Quick Start

### Web

> Visit [cyberhuatuo.dev](https://cyberhuatuo.dev) and paste your error. That's it.

### CLI

```bash
pip install cyberhuatuo

# Diagnose an error — instant prescription
cyberhuatuo diagnose "ImportError: cannot import name 'ChatOpenAI' from 'langchain'"

# Search the knowledge base
cyberhuatuo search "LangChain memory not persisting"
```

### Self-Hosted

```bash
git clone https://github.com/YourOrg/CyberHuaTuo.git
cd CyberHuaTuo
docker compose up -d
# Visit http://localhost:3000
```

---

## 📋 Supported Frameworks

| Framework | Cases | Status |
|-----------|-------|--------|
| LangChain | 🔴 Building | P0 |
| LlamaIndex | 🔴 Building | P0 |
| OpenAI SDK | 🔴 Building | P0 |
| CrewAI | 🟡 Planned | P1 |
| AutoGen | 🟡 Planned | P1 |
| MCP (Anthropic) | 🟡 Planned | P1 |
| DSPy | 🟢 Future | P2 |
| Haystack | 🟢 Future | P2 |

---

## 🏥 Join the Clinic

### 这不只是一个项目。这是一场运动。

> *In the ancient world, the greatest physicians didn't hoard their knowledge — they traveled between villages, healing the sick and training the next generation. CyberHuaTuo is that journey, for the age of AI.*

Every developer who has ever lost a day to a cryptic agent error is a potential healer. Every fix you've discovered through blood, sweat, and `print()` statements is a cure waiting to be shared.

**We're building the world's first open-source diagnostic intelligence for AI agents — and we need you.**

---

### 👨‍⚕️ Become a Resident Doctor（成为坐堂医师）

Found a fix that saved your project? **Don't let it die in your commit history.** Share your cure with the community:

1. 📝 **Submit a Prescription** — Document your fix with context: error message, framework version, environment, and solution
2. ✅ **Community Verification** — Other developers validate your cure through real-world testing
3. 🏅 **Earn the "神医" Badge** — Top contributors earn the legendary **Divine Doctor（神医）** title

> *You don't need to be a 10x engineer. You just need to have solved one problem that someone else hasn't — yet.*

### 🧬 Contribute Cases（贡献病例）

Encountered a mind-bending agent bug? **Your suffering has value.** Document it:

- Error message + full stack trace
- Framework name & version, environment details
- Your debugging journey and final fix
- **Bonus**: reproduction steps so others can learn

Every case you add makes the diagnostic engine smarter. You're not just filing a bug report — **you're training a digital physician.**

### 🛠️ Improve the Engine（改进引擎）

The diagnostic intelligence itself is open source. Help us make it sharper:

1. Fork & clone the repo
2. Check out `CONTRIBUTING.md` for development setup
3. Submit a PR — every improvement helps thousands of developers

---

### 🌍 Why This Matters

```
  2025: "My agent is broken. Let me search for 3 hours."

  2026: "My agent is broken. Let me ask CyberHuaTuo."
         — 3 seconds later —
         "Fixed."
```

The AI agent ecosystem is growing at breakneck speed. Frameworks release breaking changes weekly. New patterns emerge daily. **The knowledge gap between "it works in the tutorial" and "it works in production" is a canyon — and developers are falling into it every single day.**

CyberHuaTuo bridges that canyon. Not with another static FAQ. Not with another chatbot. With a **living, learning, community-powered diagnostic intelligence** that gets smarter with every cure.

**Every prescription you contribute doesn't just help one person. It heals the entire ecosystem.**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + PostgreSQL + Qdrant + Redis |
| **Frontend** | Next.js |
| **ML Pipeline** | text-embedding-3-small + LiteLLM |
| **Infrastructure** | Docker Compose |

---

## 📜 License

[Apache License 2.0](LICENSE) — Use it. Fork it. Build on it. Heal with it.

---

## 🙏 Acknowledgments

Named after [华佗 (Hua Tuo)](https://en.wikipedia.org/wiki/Hua_Tuo), the legendary physician of ancient China who invented surgical anesthesia (麻沸散) and pioneered the art of diagnosis over 1,800 years ago.

In his spirit, CyberHuaTuo brings the ancient art of healing into the digital age — **diagnosing the ailments of AI agents so developers can build the future without fear.**

---

<p align="center">
  <br>
  <strong>🩺 Your Agent is sick?</strong><br>
  <strong>Walk in. We'll take it from here.</strong>
  <br><br>
  <em>望闻问切，药到病除。</em>
  <br><br>
  <a href="https://github.com/YourOrg/CyberHuaTuo/issues">Report a Bug</a> •
  <a href="https://github.com/YourOrg/CyberHuaTuo/discussions">Discussions</a> •
  <a href="https://discord.gg/cyberhuatuo">Discord</a>
</p>
