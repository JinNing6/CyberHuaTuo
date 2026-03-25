---
trigger: always_on
---

这个是一个需要花真金白银的科研项目，在测试阶段，我们只使用已经布置好的免费模型比如groq。测试达到了完美程度后我们才开始跑真实的模型来出数据。

每次跑完实验、确认数据有效后，必须做一次 Git commit，附带简单的实验描述（如模型名、参数变化、实验目的等）。实验脚本的输出文件（CSV/PNG等）采用覆盖模式是合理的，因为脚本间存在流水线依赖关系，下游脚本期望读取最新数据。历史数据通过 Git 版本控制回溯，不需要在文件名中加时间戳。

## 项目学术研究目录结构

```
CyberHuaTuo/
├── cyberhuatuo/sandbox/           # 🔬 核心学术研究代码（全部实验相关逻辑）
│   ├── policy.py                  #   PolicyEngine 策略引擎（核心防御系统）
│   ├── capsule.py                 #   瞬态隔离胶囊（TEC 核心概念实现）
│   ├── classifier.py              #   ToolDNA 分类器（工具安全性自动推导）
│   ├── schemas.py                 #   数据模型（ToolCall, PolicyDecision 等）
│   ├── journal.py                 #   审计日志
│   ├── proxy.py                   #   工具调用代理
│   └── benchmark/                 #   📊 评估基准套件
│       ├── scenario_generator.py  #     550 场景参数化生成器（400 攻击 + 150 正常）
│       ├── llm_driver.py          #     LLM 驱动（Ollama 本地 + OpenAI 兼容云端 API）
│       ├── llm_harness.py         #     LLM 端到端评估引擎
│       ├── llm_scenarios.py       #     10 个手工精选核心场景
│       ├── llama_guard_eval.py    #     Llama Guard 评估脚本
│       ├── run_llm_eval.py        #     CLI 入口（core/full/sample + 三层安全自动保存）
│       ├── mcnemar.py             #     McNemar 统计检验
│       ├── harness.py             #     模拟评估引擎（用于消融实验）
│       ├── attack_scenarios.py    #     模拟攻击场景库（174 场景）
│       ├── benign_scenarios.py    #     模拟正常场景库（50 场景）
│       ├── baselines.py           #     基线系统模拟器
│       ├── academic_eval.py       #     学术基线评估
│       ├── run_academic_eval.py   #     学术评估 CLI
│       ├── report.py              #     报告格式化
│       └── perf_bench.py          #     性能基准测试
│
├── data/                          # 📁 实验数据（三层安全架构）
│   ├── runs/                      #   层2: 不可变原始快照（每次实验独立子目录）
│   │   └── {YYYYMMDD_HHMMSS}_{model}_{场景数}/
│   │       ├── v1_baseline.txt
│   │       ├── v2_xxx_fix.txt
│   │       └── mcnemar_v1_v2.txt
│   ├── latest/                    #   层3a: 最新视图（下游脚本读取）
│   │   ├── llm_eval_full.txt      #     最新一轮全量结果
│   │   └── mcnemar_latest.txt     #     最新一轮统计检验
│   ├── history/                   #   层3b: 被覆盖文件的自动备份
│   └── experiment_ledger.csv      #   层1: Append-Only 全局账本
│
├── reports/                       # 📝 生成的学术报告
├── 设计/                          # 📐 设计文档
└── tests/                         # ✅ 单元测试
```

## 关键 CLI 命令速查

```bash
# 10 核心场景快测（~30s）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model qwen2.5:latest --mode core

# 50 场景分层抽样（~2.5min）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model qwen2.5:latest --mode sample --count 50

# 全量 550 场景（~25min，自动三层安全保存）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model qwen2.5:latest --mode full

# 云端 API — Groq 免费 70B（~15min，受限于 rate limit）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model groq:llama-3.3-70b-versatile --mode full

# 云端 API — Cerebras（~10min）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model cerebras:llama-3.3-70b --mode core

# 云端 API — SambaNova
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model sambanova:Meta-Llama-3.3-70B-Instruct --mode core

# McNemar 统计检验
python -m cyberhuatuo.sandbox.benchmark.mcnemar --result_a data/runs/.../v1.txt --result_b data/runs/.../v2.txt

# 模拟基线评估（无需 LLM/GPU）
python -m cyberhuatuo.sandbox.benchmark.run_academic_eval

# 调试模式（跳过自动保存）
python -m cyberhuatuo.sandbox.benchmark.run_llm_eval --model qwen3.5:9b --mode core --no-save
```

## 当前实验成绩档案

| 日期 | 模型 | 场景数 | 攻击拦截 | FP | 正常放行 | 版本 |
|------|------|--------|---------|------|---------|------|
| 2026-03-24 | qwen2.5:latest (7B) | 550 | 74.4% | 2.0% | 98.0% | v1 基线 |
| 2026-03-24 | qwen2.5:latest (7B) | 550 | 82.0% | 1.3% | 98.7% | v2 +批量破坏检测 |
| 2026-03-24 | qwen2.5:latest (7B) | 550 | **83.0%** | **0.0%** | **100%** | v3 最终 |
| 2026-03-24 | qwen3:14b | 50 | 100% | 0.0% | 100% | 14B 抽样 |
| 2026-03-24 | qwen2.5:latest (7B) | 550 | 83.0% | 0.0% | 100% | v3 消融 (TEC=97.3%) |
| 2026-03-24 | llama-guard3:latest | 550 | 89.8% | 3.3% | 96.7% | Guard3 真实基线 |
| 2026-03-25 | qwen3.5:9b | 550 | 74.2% | 0.0% | 100% | 9B 基线 |

McNemar v1→v2: χ²=29.03, p≈0（极显著）

## 实验数据安全规则（绝对不可违反）

实验数据是花真金白银跑出来的，**绝不允许丢失**。必须严格遵守以下三层安全架构：

### 层 1: Append-Only 全局账本 (`data/experiment_ledger.csv`)
- 每次实验完成后，**追加** 一行到账本（run_id + timestamp + model + 结果指标）
- **永不覆盖、永不删除** 账本中的任何已有行
- 论文写作时从账本按 `(model, attack_category)` 分组聚合统计

### 层 2: 不可变原始快照 (`data/runs/{timestamp}_{model}/`)
- 每次运行完自动保存到独立目录，**文件永不修改**
- 目录命名格式: `YYYYMMDD_HHMMSS_{model_name}_{scenario_count}{suffix}`
- 包含该次运行的所有原始输出文件

### 层 3: 最新视图 + 备份 (`data/latest/` + `data/history/`)
- `data/latest/` 中的文件可被下游脚本读取（固定文件名）
- 覆盖前旧文件**自动备份**到 `data/history/`（带时间戳后缀）

### 禁止行为
- ❌ **禁止** 用 `to_csv("固定文件名")` 直接覆盖 `data/` 下的数据文件
- ❌ **禁止** 手动删除 `data/` 目录下的任何文件
- ❌ **禁止** 修改 `data/runs/` 中的任何已有快照
- ❌ **禁止** 清空 `experiment_ledger.csv`
- ❌ **禁止** 将实验结果文件输出到项目根目录（必须输出到 `data/` 下）
- ✅ 每次跑完实验，结果必须存入 `data/runs/{timestamp}/` 和 `data/latest/`
- ✅ 每次确认数据有效后，必须 Git commit
- ✅ `run_llm_eval.py` 已内置三层安全自动保存（无需手动操作）

## 断点续跑规则

- ⚠️ 长时间实验（>100 场景）在运行日志中会定期输出进度
- 如实验中断（系统重启/网络断开），优先检查 `data/runs/` 和 `data/latest/` 是否有部分数据
- 中断的实验必须**完整重跑**，不接受拼接数据，确保统计显著性
- 使用 `--no-save` 参数可在调试时跳过三层安全保存

## 成本控制规则

- 🆓 **测试阶段**: 仅使用免费模型
  - 本地 Ollama: qwen2.5, qwen3, qwen3.5
  - 云端免费: Groq / Cerebras / SambaNova / Mistral / GitHub Models
  - 注意: GitHub Models 的 GPT-4o 通过 GITHUB_TOKEN 免费调用，定位为测试阶段使用
- 💰 **正式出数据**: 使用付费 API（OpenRouter: Claude-3.5-Sonnet），必须设置花费上限
- ⚠️ 每次调用付费 API 前，先用 `--mode sample --count 10` 确认脚本无 bug，再跑全量