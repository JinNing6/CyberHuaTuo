"""
TEC LLM 端到端测试入口 CLI

支持三种模式:
- core: 仅跑手工精选的 10 个核心场景（快速验证）
- full: 跑全部 550 个自动生成的场景（学术级评估）
- sample: 从 550 个场景中随机抽样 N 个

实验数据自动遵循三层安全架构:
- 层1: Append-Only 全局账本 (data/experiment_ledger.csv)
- 层2: 不可变原始快照 (data/runs/{timestamp}_{model}/)
- 层3: 最新视图 + 备份 (data/latest/ + data/history/)
"""

import csv
import os
import re
import shutil
import subprocess
import sys
import random
import argparse
import time
from datetime import datetime
from pathlib import Path

from cyberhuatuo.sandbox.benchmark.llm_driver import create_driver
from cyberhuatuo.sandbox.benchmark.llm_harness import LLMBenchmarkHarness
from cyberhuatuo.sandbox.benchmark.llm_scenarios import ALL_LLM_SCENARIOS
from cyberhuatuo.sandbox.benchmark.scenario_generator import ALL_GENERATED_SCENARIOS
from cyberhuatuo.sandbox.benchmark.harness import BenchmarkHarness

# 项目根目录（相对于本文件向上 4 级: benchmark/ -> sandbox/ -> cyberhuatuo/ -> project/）
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = DATA_DIR / "runs"
LATEST_DIR = DATA_DIR / "latest"
HISTORY_DIR = DATA_DIR / "history"
LEDGER_PATH = DATA_DIR / "experiment_ledger.csv"

# Ledger CSV 表头
LEDGER_FIELDS = [
    "run_id", "timestamp", "model", "scenario_count", "mode",
    "attack_rate", "benign_rate", "fp_rate", "fn_count",
    "version", "notes",
]


def _sanitize_model_name(model: str) -> str:
    """将模型名中的特殊字符转换为文件名安全格式 (冒号→下划线, 斜杠→横杠)"""
    return re.sub(r"[:/\\]", "_", model)


def _validate_output_path(output_path: str | None) -> None:
    """P0 修复: 验证 --output 路径是否在 data/ 目录下"""
    if output_path is None:
        return
    abs_output = Path(output_path).resolve()
    abs_data = DATA_DIR.resolve()
    if not str(abs_output).startswith(str(abs_data)):
        print(
            f"\n⚠️  警告: --output 路径 '{output_path}' 不在 data/ 目录下。\n"
            f"   根据实验数据安全规则，建议输出到 data/latest/ 或 data/runs/。\n"
            f"   当前仍会写入指定路径，但三层安全架构将额外保存一份到标准位置。\n"
        )


def save_experiment_data(
    content: str,
    model: str,
    mode: str,
    scenario_count: int,
    attack_rate: float,
    benign_rate: float,
    fp_rate: float,
    fn_count: int,
    elapsed: float,
    version: str = "",
    notes: str = "",
    extra_output: str | None = None,
) -> str:
    """三层安全架构: 自动保存实验数据

    返回 run_dir 路径字符串。

    层1: 追加到 experiment_ledger.csv（永不覆盖）
    层2: 保存到 data/runs/{timestamp}_{model}_{count}/ （不可变快照）
    层3: 写入 data/latest/ 并在覆盖前备份到 data/history/
    最后: 自动 Git commit
    """
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    iso_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    safe_model = _sanitize_model_name(model)

    # ── 确保目录存在 ──
    for d in [RUNS_DIR, LATEST_DIR, HISTORY_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    # ── 层 2: 不可变原始快照 ──
    run_dirname = f"{timestamp_str}_{safe_model}_{scenario_count}"
    run_dir = RUNS_DIR / run_dirname
    run_dir.mkdir(parents=True, exist_ok=True)
    run_file = run_dir / "llm_eval_full.txt"
    run_file.write_text(content, encoding="utf-8")
    print(f"\n📦 层2 快照已保存: {run_file}")

    # ── 层 3: 最新视图 + 历史备份 ──
    if mode == "full":
        latest_name = f"llm_eval_{safe_model}_full.txt"
    elif mode == "core":
        latest_name = f"llm_eval_{safe_model}_core{scenario_count}.txt"
    else:
        latest_name = f"llm_eval_{safe_model}_{mode}{scenario_count}.txt"

    latest_file = LATEST_DIR / latest_name
    # 如果已有同名文件，先备份到 history/
    if latest_file.exists():
        backup_name = latest_file.stem + f"_{timestamp_str}" + latest_file.suffix
        backup_dest = HISTORY_DIR / backup_name
        shutil.copy2(str(latest_file), str(backup_dest))
        print(f"📜 层3 历史备份: {backup_dest}")

    latest_file.write_text(content, encoding="utf-8")
    print(f"📋 层3 最新视图: {latest_file}")

    # ── 额外 --output 路径（如果用户指定了）──
    if extra_output:
        extra_path = Path(extra_output)
        extra_path.parent.mkdir(parents=True, exist_ok=True)
        extra_path.write_text(content, encoding="utf-8")
        print(f"📄 额外输出: {extra_path}")

    # ── 层 1: Append-Only 全局账本 ──
    run_id = f"{now.strftime('%Y%m%d')}_{safe_model}_{mode}{scenario_count}"
    if not version:
        version = f"{safe_model}_{mode}"
    if not notes:
        notes = (
            f"{model} {scenario_count}场景{mode}"
            f"-{attack_rate:.1f}%拦截 {fp_rate:.1f}%FP {fn_count}漏拦"
        )

    ledger_exists = LEDGER_PATH.exists()
    with open(LEDGER_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if not ledger_exists:
            writer.writeheader()
        writer.writerow({
            "run_id": run_id,
            "timestamp": iso_timestamp,
            "model": model,
            "scenario_count": scenario_count,
            "mode": mode,
            "attack_rate": f"{attack_rate:.1f}",
            "benign_rate": f"{benign_rate:.1f}",
            "fp_rate": f"{fp_rate:.1f}",
            "fn_count": fn_count,
            "version": version,
            "notes": notes,
        })
    print(f"📒 层1 账本已追加: {LEDGER_PATH}")

    # ── Git 自动 commit ──
    try:
        subprocess.run(
            ["git", "add", "data/"],
            cwd=str(PROJECT_ROOT),
            capture_output=True, timeout=10,
        )
        commit_msg = (
            f"data: {model} {scenario_count}场景{mode}评估"
            f" - {attack_rate:.1f}%拦截 {fp_rate:.1f}%FP"
        )
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(PROJECT_ROOT),
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            print(f"✅ Git 自动提交: {commit_msg}")
        else:
            # 可能无变更需要提交
            stderr = result.stderr.strip()
            if "nothing to commit" in stderr or "nothing to commit" in result.stdout:
                print("ℹ️  Git: 无新变更需要提交")
            else:
                print(f"⚠️  Git commit 返回非零: {result.stdout.strip()}")
    except Exception as e:
        print(f"⚠️  Git 自动提交失败（数据已安全保存）: {e}")

    return str(run_dir)


def main():
    parser = argparse.ArgumentParser(description="TEC 真实 LLM 端到端 Benchmark 测试")
    parser.add_argument(
        "--model", type=str, default="qwen3.5:9b",
        help="模型名. 本地: qwen3.5:9b | 云端: groq:llama-3.3-70b-versatile, cerebras:llama-3.3-70b, github:gpt-4o"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="额外结果输出路径（三层安全架构会自动保存，此参数为可选的额外副本）"
    )
    parser.add_argument(
        "--mode", type=str, default="core",
        choices=["core", "full", "sample"],
        help="core=精选10场景, full=全部550场景, sample=随机抽样"
    )
    parser.add_argument("--count", type=int, default=50, help="sample 模式抽样数量")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（可复现）")
    parser.add_argument(
        "--no-save", action="store_true",
        help="跳过三层安全架构保存（仅用于调试）"
    )
    args = parser.parse_args()

    # P0 修复: 验证 --output 路径
    _validate_output_path(args.output)

    lines = []
    def log(msg=""):
        print(msg)
        lines.append(msg)

    # 选择场景集
    if args.mode == "core":
        scenarios = ALL_LLM_SCENARIOS
        mode_desc = f"核心精选 ({len(scenarios)} 场景)"
    elif args.mode == "full":
        scenarios = ALL_GENERATED_SCENARIOS
        mode_desc = f"全量生成 ({len(scenarios)} 场景)"
    elif args.mode == "sample":
        random.seed(args.seed)
        pool = ALL_GENERATED_SCENARIOS
        n = min(args.count, len(pool))
        # 按类别分层抽样，确保每类都有代表
        attacks = [s for s in pool if s.expected_blocked]
        benign = [s for s in pool if not s.expected_blocked]
        atk_n = int(n * len(attacks) / len(pool))
        ben_n = n - atk_n
        scenarios = random.sample(attacks, min(atk_n, len(attacks))) + \
                    random.sample(benign, min(ben_n, len(benign)))
        random.shuffle(scenarios)
        mode_desc = f"分层抽样 ({len(scenarios)} / {len(pool)} 场景, seed={args.seed})"
    else:
        scenarios = ALL_LLM_SCENARIOS
        mode_desc = "default"

    log(f"\n{'='*70}")
    log(f"  TEC LLM 端到端安全评估")
    log(f"  模型: {args.model} | 模式: {mode_desc}")
    log(f"{'='*70}\n")

    driver = create_driver(args.model)
    harness = LLMBenchmarkHarness(driver=driver)

    t0 = time.perf_counter()
    result = harness.run_benchmark(scenarios)
    elapsed = time.perf_counter() - t0

    log("\n✅ 运行完成！结果如下：\n")

    # 复用报告格式化逻辑
    results_map = {result.system: result}
    summary = BenchmarkHarness.format_summary(results_map)
    log(summary)

    # 打印详细延迟
    log(f"\n⏱ 总耗时: {elapsed:.2f}s, LLM 平均端到端延迟: {result.avg_latency_ms:.2f}ms")

    # 统计各攻击类别的拦截率
    from collections import Counter, defaultdict
    atk_by_cat = defaultdict(lambda: {"total": 0, "blocked": 0})
    for r in result.attack_results:
        atk_by_cat[r.category]["total"] += 1
        if r.correct:
            atk_by_cat[r.category]["blocked"] += 1

    log("\n📊 各攻击类别拦截率:")
    log(f"  {'类别':<30} {'拦截':<8} {'总数':<8} {'拦截率':<10}")
    log(f"  {'-'*56}")
    for cat, stats in sorted(atk_by_cat.items()):
        rate = stats["blocked"] / stats["total"] * 100 if stats["total"] else 0
        log(f"  {cat:<30} {stats['blocked']:<8} {stats['total']:<8} {rate:.1f}%")

    # ── 消融统计: TEC 策略拦截 vs LLM 自行拒绝 ──
    tec_policy_blocks = 0
    llm_self_refuses = 0
    tec_by_cat = defaultdict(lambda: {"tec": 0, "llm": 0, "total": 0})

    for r in result.attack_results:
        if r.correct:  # 成功拦截的攻击
            dec_str = ", ".join(r.decisions)
            tec_by_cat[r.category]["total"] += 1
            if "LLM_REFUSED_OR_NO_TOOLS" in dec_str:
                llm_self_refuses += 1
                tec_by_cat[r.category]["llm"] += 1
            else:
                tec_policy_blocks += 1
                tec_by_cat[r.category]["tec"] += 1

    total_intercepted = tec_policy_blocks + llm_self_refuses
    log(f"\n🔬 消融分析 (Ablation): TEC 策略引擎 vs LLM 安全对齐")
    log(f"  {'来源':<25} {'数量':<8} {'占比':<10}")
    log(f"  {'-'*43}")
    if total_intercepted > 0:
        log(f"  {'TEC 策略拦截':<23} {tec_policy_blocks:<8} {tec_policy_blocks/total_intercepted*100:.1f}%")
        log(f"  {'LLM 自行拒绝':<23} {llm_self_refuses:<8} {llm_self_refuses/total_intercepted*100:.1f}%")
    log(f"  {'合计拦截':<25} {total_intercepted:<8}")

    log(f"\n  按类别消融:")
    log(f"  {'类别':<28} {'TEC拦截':<10} {'LLM自拒':<10} {'合计':<8}")
    log(f"  {'-'*56}")
    for cat, stats in sorted(tec_by_cat.items()):
        log(f"  {cat:<28} {stats['tec']:<10} {stats['llm']:<10} {stats['total']:<8}")

    # 错误详单（限制显示数量）
    fn_list = [r for r in result.attack_results if not r.correct]
    fp_list = [r for r in result.benign_results if not r.correct]

    log(f"\n🧐 阻断失败详单（漏拦）: {len(fn_list)} 个")
    for r in fn_list[:20]:  # 最多显示 20 个
        log(f"  ❌ [{r.category}] {r.name[:80]} -> {r.decisions}")
    if len(fn_list) > 20:
        log(f"  ... 还有 {len(fn_list) - 20} 个未显示")

    log(f"\n🧐 误报详单（误拦）: {len(fp_list)} 个")
    for r in fp_list[:20]:
        log(f"  ❌ [{r.category}] {r.name[:80]} -> {r.decisions}")
    if len(fp_list) > 20:
        log(f"  ... 还有 {len(fp_list) - 20} 个未显示")

    log()

    # ── 三层安全架构: 自动保存实验数据 ──
    if not args.no_save:
        # 计算指标
        total_attacks = len(result.attack_results)
        total_benign = len(result.benign_results)
        blocked_attacks = sum(1 for r in result.attack_results if r.correct)
        passed_benign = sum(1 for r in result.benign_results if r.correct)

        attack_rate = (blocked_attacks / total_attacks * 100) if total_attacks else 0
        benign_rate = (passed_benign / total_benign * 100) if total_benign else 0
        fp_rate = ((total_benign - passed_benign) / total_benign * 100) if total_benign else 0

        content = "\n".join(lines)
        save_experiment_data(
            content=content,
            model=args.model,
            mode=args.mode,
            scenario_count=len(scenarios),
            attack_rate=attack_rate,
            benign_rate=benign_rate,
            fp_rate=fp_rate,
            fn_count=len(fn_list),
            elapsed=elapsed,
            extra_output=args.output,
        )
    elif args.output:
        # --no-save 模式下仅写到 --output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n📄 完整结果已保存到: {args.output} (⚠️ 未执行三层安全保存)")


if __name__ == "__main__":
    sys.exit(main())
