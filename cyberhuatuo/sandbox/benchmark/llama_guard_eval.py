"""
Llama Guard 3 真实基线评估器

Llama Guard 3 是 Meta 的安全分类模型，输入 user/agent 对话 → 输出 safe/unsafe。
我们将其作为 TEC 的真实基线对比：
- TEC: 运行时策略引擎，检测工具调用参数
- Llama Guard: 预检分类器，检测 prompt 本身是否恶意

评估方式：
1. 将每个场景的 user_prompt 发给 Llama Guard 3
2. 如果判定 unsafe → 视为"拦截"
3. 如果判定 safe → 视为"放行"
4. 对比 TEC 的拦截率

这是一种公平的对比，因为论文中 Llama Guard 被定位为"提示级防护"，
而 TEC 是"工具调用级防护"。

实验数据自动遵循三层安全架构（与 run_llm_eval.py 共享）。
"""

import json
import time
import logging
import urllib.request
import urllib.error

from cyberhuatuo.sandbox.benchmark.harness import (
    ScenarioResult, SystemResult, CategoryResult,
)

logger = logging.getLogger("tec.benchmark.llama_guard")

OLLAMA_BASE_URL = "http://localhost:11434"


class LlamaGuardEvaluator:
    """Llama Guard 3 真实基线评估器"""

    MAX_RETRIES = 5
    RETRY_DELAYS = [5, 10, 20, 40, 60]

    def __init__(self, model_name: str = "llama-guard3:latest",
                 base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.base_url = base_url
        self._warmed_up = False

    def _call_ollama(self, payload: dict, timeout: int = 120) -> str | None:
        """原生 HTTP 调用 Ollama /api/chat，返回文本内容"""
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"}
        )
        for attempt in range(self.MAX_RETRIES):
            try:
                r = urllib.request.urlopen(req, timeout=timeout)
                result = json.loads(r.read().decode("utf-8"))
                return result.get("message", {}).get("content", "")
            except Exception as e:
                wait = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                logger.warning(
                    f"Llama Guard 调用失败 (第{attempt+1}次): {e}，等待 {wait}s 重试..."
                )
                print(f"Llama Guard 调用失败 (第{attempt+1}次): {e}，等待 {wait}s 重试...")
                time.sleep(wait)
        return None

    def warmup(self):
        """预热 Llama Guard 模型"""
        if self._warmed_up:
            return
        print(f"  🔥 预热 {self.model_name}...")
        result = self._call_ollama({
            "model": self.model_name,
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "stream": False,
            "options": {"num_predict": 20}
        }, timeout=60)
        if result is not None:
            self._warmed_up = True
            print(f"  ✅ {self.model_name} 预热完成!")
        else:
            print(f"  ⚠️ 预热失败")

    def classify(self, user_prompt: str, system_prompt: str = "") -> dict:
        """
        将场景的 prompt 发给 Llama Guard 3 分类

        Returns:
            {
                "safe": bool,
                "categories": list[str],  # e.g. ["S2", "S7"]
                "raw_output": str,
                "latency_ms": float
            }
        """
        # 构建对话：system_prompt + user_prompt
        messages = []
        if system_prompt:
            messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "assistant", "content": "I'll help you with that."})

        messages.append({"role": "user", "content": user_prompt})

        t0 = time.perf_counter()
        raw = self._call_ollama({
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 50, "temperature": 0}
        })
        latency = (time.perf_counter() - t0) * 1000

        if raw is None:
            return {"safe": True, "categories": [], "raw_output": "ERROR",
                    "latency_ms": latency}

        raw = raw.strip().lower()

        # 解析输出: "safe" 或 "unsafe\nS2,S7"
        is_safe = raw.startswith("safe")
        categories = []
        if not is_safe:
            lines = raw.split("\n")
            if len(lines) > 1:
                categories = [c.strip().upper() for c in lines[1].split(",") if c.strip()]

        return {
            "safe": is_safe,
            "categories": categories,
            "raw_output": raw,
            "latency_ms": latency,
        }


def run_llama_guard_benchmark(scenarios) -> SystemResult:
    """在 TEC 场景集上运行 Llama Guard 3 评估，返回 SystemResult"""
    from collections import defaultdict

    evaluator = LlamaGuardEvaluator()
    evaluator.warmup()

    system_name = f"LlamaGuard3_{evaluator.model_name}"

    lines = []
    def log(msg=""):
        print(msg)
        lines.append(msg)

    log(f"\n{'='*70}")
    log(f"  Llama Guard 3 真实基线评估")
    log(f"  场景数: {len(scenarios)}")
    log(f"{'='*70}\n")

    attack_results: list[ScenarioResult] = []
    benign_results: list[ScenarioResult] = []
    cat_stats = defaultdict(lambda: {"total": 0, "blocked": 0})

    total = len(scenarios)
    for i, sc in enumerate(scenarios, 1):
        print(f"[{i}/{total}] 评估场景: {sc.id}")
        result = evaluator.classify(sc.user_prompt, sc.system_prompt)

        # Llama Guard 判 unsafe = 拦截
        blocked = not result["safe"]
        correct = blocked == sc.expected_blocked

        # 构建决策字符串
        if blocked:
            cats_str = ",".join(result["categories"]) if result["categories"] else "unsafe"
            decision_str = f"LlamaGuard→UNSAFE({cats_str})"
        else:
            decision_str = "LlamaGuard→SAFE"

        sr = ScenarioResult(
            scenario_id=sc.id,
            category=sc.category if hasattr(sc, "category") else "_benign",
            name=sc.name,
            system=system_name,
            blocked=blocked,
            expected_blocked=sc.expected_blocked,
            correct=correct,
            decisions=[decision_str],
            latency_ms=result["latency_ms"],
        )

        if sc.expected_blocked:
            attack_results.append(sr)
            cat_stats[sr.category]["total"] += 1
            if blocked:
                cat_stats[sr.category]["blocked"] += 1
        else:
            benign_results.append(sr)

    # 统计
    total_attack = len(attack_results) or 1
    total_benign = len(benign_results) or 1
    attack_blocked = sum(1 for r in attack_results if r.blocked)
    benign_passed = sum(1 for r in benign_results if not r.blocked)
    fp = total_benign - benign_passed

    atk_rate = attack_blocked / total_attack * 100
    ben_rate = benign_passed / total_benign * 100
    fp_rate = fp / total_benign * 100

    all_latencies = [r.latency_ms for r in attack_results + benign_results]
    avg_lat = sum(all_latencies) / len(all_latencies) if all_latencies else 0

    log("=" * 70)
    log("  Llama Guard 3 — 结果摘要")
    log("=" * 70)
    log(f"\n  攻击拦截率:  {atk_rate:.1f}% ({attack_blocked}/{total_attack})")
    log(f"  正常放行率:  {ben_rate:.1f}% ({benign_passed}/{total_benign})")
    log(f"  误拦率(FP):  {fp_rate:.1f}% ({fp}/{total_benign})")
    log(f"  平均延迟:    {avg_lat:.1f}ms")

    log(f"\n📊 各攻击类别拦截率:")
    log(f"  {'类别':<30} {'拦截':<8} {'总数':<8} {'拦截率':<10}")
    log(f"  {'-'*56}")
    for cat, stats in sorted(cat_stats.items()):
        rate = stats["blocked"] / stats["total"] * 100 if stats["total"] else 0
        log(f"  {cat:<30} {stats['blocked']:<8} {stats['total']:<8} {rate:.1f}%")

    # 漏拦详单
    fn_list = [r for r in attack_results if not r.correct]
    log(f"\n🧐 漏拦: {len(fn_list)} 个")
    for r in fn_list[:20]:
        log(f"  ❌ [{r.category}] {r.name[:70]} -> {r.decisions}")
    if len(fn_list) > 20:
        log(f"  ... 还有 {len(fn_list) - 20} 个未显示")

    # 误拦详单
    fp_list = [r for r in benign_results if not r.correct]
    log(f"\n🧐 误拦: {len(fp_list)} 个")
    for r in fp_list[:20]:
        log(f"  ❌ {r.name[:70]} -> {r.decisions}")

    log()

    # 构建 CategoryResult
    cat_results = {}
    for cat, stats in cat_stats.items():
        tp = stats["blocked"]
        fn = stats["total"] - tp
        cat_results[cat] = CategoryResult(
            category=cat, total=stats["total"], correct=tp,
            accuracy=tp / stats["total"] if stats["total"] else 0,
            true_positive=tp, false_negative=fn,
            true_negative=0, false_positive=0,
        )
    # benign 类别
    cat_results["_benign"] = CategoryResult(
        category="_benign", total=len(benign_results),
        correct=benign_passed,
        accuracy=benign_passed / total_benign if total_benign else 0,
        true_positive=0, false_negative=0,
        true_negative=benign_passed, false_positive=fp,
    )

    system_result = SystemResult(
        system=system_name,
        attack_results=attack_results,
        benign_results=benign_results,
        category_results=cat_results,
        attack_block_rate=attack_blocked / total_attack,
        benign_pass_rate=benign_passed / total_benign,
        false_positive_rate=fp / total_benign,
        false_negative_rate=1 - (attack_blocked / total_attack),
        avg_latency_ms=avg_lat,
    )

    # 附带文本报告供三层架构使用
    system_result._report_text = "\n".join(lines)

    return system_result


if __name__ == "__main__":
    import sys
    import random
    import argparse

    from cyberhuatuo.sandbox.benchmark.scenario_generator import ALL_GENERATED_SCENARIOS
    from cyberhuatuo.sandbox.benchmark.llm_scenarios import ALL_LLM_SCENARIOS
    from cyberhuatuo.sandbox.benchmark.run_llm_eval import save_experiment_data

    parser = argparse.ArgumentParser(description="Llama Guard 3 真实基线评估")
    parser.add_argument("--mode", choices=["core", "full", "sample"],
                        default="core")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--no-save", action="store_true",
                        help="跳过三层安全架构保存（仅用于调试）")
    args = parser.parse_args()

    if args.mode == "core":
        scenarios = ALL_LLM_SCENARIOS
    elif args.mode == "full":
        scenarios = ALL_GENERATED_SCENARIOS
    elif args.mode == "sample":
        random.seed(args.seed)
        pool = ALL_GENERATED_SCENARIOS
        n = min(args.count, len(pool))
        attacks = [s for s in pool if s.expected_blocked]
        benign = [s for s in pool if not s.expected_blocked]
        atk_n = int(n * len(attacks) / len(pool))
        ben_n = n - atk_n
        scenarios = random.sample(attacks, min(atk_n, len(attacks))) + \
                    random.sample(benign, min(ben_n, len(benign)))
    else:
        scenarios = ALL_LLM_SCENARIOS

    t0 = time.perf_counter()
    result = run_llama_guard_benchmark(scenarios)
    elapsed = time.perf_counter() - t0

    # ── 三层安全架构: 自动保存 ──
    if not args.no_save:
        total_attacks = len(result.attack_results)
        total_benign = len(result.benign_results)
        blocked_attacks = sum(1 for r in result.attack_results if r.correct)
        passed_benign = sum(1 for r in result.benign_results if r.correct)

        attack_rate = (blocked_attacks / total_attacks * 100) if total_attacks else 0
        benign_rate = (passed_benign / total_benign * 100) if total_benign else 0
        fp_rate = ((total_benign - passed_benign) / total_benign * 100) if total_benign else 0
        fn_count = sum(1 for r in result.attack_results if not r.correct)

        save_experiment_data(
            content=result._report_text,
            model="llama-guard3:latest",
            mode=args.mode,
            scenario_count=len(scenarios),
            attack_rate=attack_rate,
            benign_rate=benign_rate,
            fp_rate=fp_rate,
            fn_count=fn_count,
            elapsed=elapsed,
            extra_output=args.output,
            system_result=result,
        )
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result._report_text)
        print(f"\n📄 结果已保存到: {args.output} (⚠️ 未执行三层安全保存)")

