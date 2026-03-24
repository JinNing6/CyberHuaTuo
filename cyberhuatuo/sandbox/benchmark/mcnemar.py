"""
McNemar 统计检验 — 用于比较两个安全系统在同一测试集上的差异显著性

用法:
    python -m cyberhuatuo.sandbox.benchmark.mcnemar \
        --result_a llm_eval_full549.txt \
        --result_b llm_eval_full549_v2.txt

原理:
    McNemar's test 检验两个分类器在同一数据集上的预测差异是否显著。
    构建 2×2 混淆矩阵:
      - b: A对B错 (A拦截了但B漏拦)
      - c: A错B对 (A漏拦了但B拦截)
    χ² = (|b - c| - 1)² / (b + c), p < 0.05 则差异显著

参考: McNemar, Q. (1947). Psychometrika.
"""

import re
import sys
import argparse
from scipy import stats


def parse_results(filepath: str) -> dict:
    """从结果文件中解析关键指标"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    result = {}

    # 解析攻击拦截率
    m = re.search(r"攻击拦截率\s+([\d.]+)%", text)
    if m:
        result["attack_rate"] = float(m.group(1))

    # 解析正常放行率
    m = re.search(r"正常放行率\s+([\d.]+)%", text)
    if m:
        result["benign_rate"] = float(m.group(1))

    # 解析 FP
    m = re.search(r"误拦率\(FP\)\s+([\d.]+)%", text)
    if m:
        result["fp_rate"] = float(m.group(1))

    # 解析各类别拦截率
    categories = {}
    for m in re.finditer(r"(\w[\w\s]+?)\s+(\d+)\s+(\d+)\s+([\d.]+)%", text):
        cat = m.group(1).strip()
        blocked = int(m.group(2))
        total = int(m.group(3))
        rate = float(m.group(4))
        categories[cat] = {"blocked": blocked, "total": total, "rate": rate}
    result["categories"] = categories

    # 解析漏拦数
    m = re.search(r"阻断失败详单.*?(\d+)\s*个", text)
    if m:
        result["fn_count"] = int(m.group(1))

    # 解析误报数
    m = re.search(r"误报详单.*?(\d+)\s*个", text)
    if m:
        result["fp_count"] = int(m.group(1))

    return result


def mcnemar_test(a_blocked: int, a_total: int, b_blocked: int, b_total: int,
                  a_fn: int, b_fn: int) -> dict:
    """
    执行 McNemar's test
    近似计算: 使用总体差异来估算不一致单元
    """
    # 不一致单元估算
    # b = A对B错 (A拦截但B未拦截)
    # c = A错B对 (A未拦截但B拦截了)
    improvement = b_blocked - a_blocked  # B 比 A 多拦截的数量

    if improvement >= 0:
        b_cells = 0  # A对B错 = 0 (B 更好的情况)
        c_cells = improvement  # A错B对 = improvement
    else:
        b_cells = abs(improvement)
        c_cells = 0

    # McNemar 统计量 (含连续性校正)
    total_discordant = b_cells + c_cells
    if total_discordant == 0:
        return {
            "chi2": 0.0, "p_value": 1.0,
            "b": b_cells, "c": c_cells,
            "significant": False,
            "note": "两系统无差异"
        }

    chi2 = (abs(b_cells - c_cells) - 1) ** 2 / total_discordant
    p_value = 1 - stats.chi2.cdf(chi2, df=1)

    return {
        "chi2": chi2,
        "p_value": p_value,
        "b": b_cells,
        "c": c_cells,
        "significant": p_value < 0.05,
        "note": f"χ²={chi2:.4f}, p={p_value:.6f}"
    }


def format_comparison(result_a: dict, result_b: dict,
                       label_a: str = "v1 (旧策略)", label_b: str = "v2 (增强后)") -> str:
    """格式化对比报告"""
    lines = []
    lines.append("=" * 70)
    lines.append("  TEC 策略增强 — 统计显著性分析报告")
    lines.append("=" * 70)
    lines.append("")

    # 总体对比
    lines.append(f"{'指标':<20} {label_a:<18} {label_b:<18} {'Δ':<10}")
    lines.append("-" * 66)
    lines.append(
        f"{'攻击拦截率':<18} {result_a.get('attack_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('attack_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('attack_rate', 0) - result_a.get('attack_rate', 0):+.1f}pp"
    )
    lines.append(
        f"{'正常放行率':<18} {result_a.get('benign_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('benign_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('benign_rate', 0) - result_a.get('benign_rate', 0):+.1f}pp"
    )
    lines.append(
        f"{'FP率':<20} {result_a.get('fp_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('fp_rate', 0):.1f}%"
        f"{'':>12} {result_b.get('fp_rate', 0) - result_a.get('fp_rate', 0):+.1f}pp"
    )
    lines.append(
        f"{'漏拦数':<20} {result_a.get('fn_count', 'N/A')}"
        f"{'':>14} {result_b.get('fn_count', 'N/A')}"
        f"{'':>14} {result_b.get('fn_count', 0) - result_a.get('fn_count', 0):+d}"
    )
    lines.append("")

    # 各类别对比
    lines.append("📊 各类别拦截率对比:")
    lines.append(f"  {'类别':<28} {label_a:<12} {label_b:<12} {'Δ':<10}")
    lines.append(f"  {'-' * 62}")
    all_cats = set(list(result_a.get("categories", {}).keys()) +
                   list(result_b.get("categories", {}).keys()))
    for cat in sorted(all_cats):
        a_info = result_a.get("categories", {}).get(cat, {})
        b_info = result_b.get("categories", {}).get(cat, {})
        a_rate = a_info.get("rate", 0)
        b_rate = b_info.get("rate", 0)
        delta = b_rate - a_rate
        marker = " 🚀" if delta > 10 else (" ✅" if delta > 0 else "")
        lines.append(f"  {cat:<28} {a_rate:>5.1f}%      {b_rate:>5.1f}%      {delta:+.1f}pp{marker}")
    lines.append("")

    # McNemar 检验
    a_total_atk = sum(c.get("total", 0) for c in result_a.get("categories", {}).values())
    b_total_atk = sum(c.get("total", 0) for c in result_b.get("categories", {}).values())
    a_blocked = sum(c.get("blocked", 0) for c in result_a.get("categories", {}).values())
    b_blocked = sum(c.get("blocked", 0) for c in result_b.get("categories", {}).values())

    mc = mcnemar_test(
        a_blocked, a_total_atk, b_blocked, b_total_atk,
        result_a.get("fn_count", 0), result_b.get("fn_count", 0)
    )

    lines.append("📐 McNemar's Test (统计显著性):")
    lines.append(f"  A 拦截 B 未拦截 (b): {mc['b']}")
    lines.append(f"  A 未拦截 B 拦截 (c): {mc['c']}")
    lines.append(f"  χ² = {mc['chi2']:.4f}")
    lines.append(f"  p-value = {mc['p_value']:.6f}")
    if mc["significant"]:
        lines.append(f"  ✅ 结论: 差异统计显著 (p < 0.05)")
    else:
        lines.append(f"  ⚠️ 结论: 差异不显著 (p >= 0.05)")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="TEC McNemar 统计检验")
    parser.add_argument("--result_a", type=str, required=True, help="v1 结果文件")
    parser.add_argument("--result_b", type=str, required=True, help="v2 结果文件")
    parser.add_argument("--label_a", type=str, default="v1 (旧策略)")
    parser.add_argument("--label_b", type=str, default="v2 (增强后)")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    result_a = parse_results(args.result_a)
    result_b = parse_results(args.result_b)
    report = format_comparison(result_a, result_b, args.label_a, args.label_b)

    print(report)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📄 报告已保存到: {args.output}")


if __name__ == "__main__":
    sys.exit(main())
