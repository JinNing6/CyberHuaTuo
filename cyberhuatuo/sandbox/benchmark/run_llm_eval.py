"""
TEC LLM 端到端测试入口 CLI

支持两种模式:
- core: 仅跑手工精选的 10 个核心场景（快速验证）
- full: 跑全部 549 个自动生成的场景（学术级评估）
- sample: 从 549 个场景中随机抽样 N 个
"""

import sys
import random
import argparse
import time

from cyberhuatuo.sandbox.benchmark.llm_driver import OllamaDriver
from cyberhuatuo.sandbox.benchmark.llm_harness import LLMBenchmarkHarness
from cyberhuatuo.sandbox.benchmark.llm_scenarios import ALL_LLM_SCENARIOS
from cyberhuatuo.sandbox.benchmark.scenario_generator import ALL_GENERATED_SCENARIOS
from cyberhuatuo.sandbox.benchmark.harness import BenchmarkHarness

def main():
    parser = argparse.ArgumentParser(description="TEC 真实 LLM 端到端 Benchmark 测试")
    parser.add_argument("--model", type=str, default="qwen3:14b", help="本地 Ollama 模型名称")
    parser.add_argument("--output", type=str, default=None, help="结果输出文件路径")
    parser.add_argument(
        "--mode", type=str, default="core",
        choices=["core", "full", "sample"],
        help="core=精选10场景, full=全部549场景, sample=随机抽样"
    )
    parser.add_argument("--count", type=int, default=50, help="sample 模式抽样数量")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（可复现）")
    args = parser.parse_args()

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

    driver = OllamaDriver(model_name=args.model)
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

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n📄 完整结果已保存到: {args.output}")

if __name__ == "__main__":
    sys.exit(main())
