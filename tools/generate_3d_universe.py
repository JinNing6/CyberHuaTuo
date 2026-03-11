#!/usr/bin/env python3
"""
CyberHuaTuo 3D 药方宇宙生成器
扫描 cases/ 目录，自动生成：
  1. assets/prescription_universe.svg  — 嵌入 README 的 CSS 动画预览图
  2. docs/3d-universe/index.html       — 自包含 Three.js 交互式 3D 页面

用法:
    python tools/generate_3d_universe.py
"""

import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ 请安装 pyyaml: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent.resolve()
CASES_DIR = ROOT / "cases"
SVG_OUTPUT = ROOT / "assets" / "prescription_universe.svg"
HTML_DIR = ROOT / "docs" / "3d-universe"
HTML_OUTPUT = HTML_DIR / "index.html"

# ─── 框架配色方案 ───
FRAMEWORK_COLORS = {
    "langchain":    {"primary": "#00D09C", "glow": "rgba(0,208,156,0.5)"},
    "crewai":       {"primary": "#FF6B6B", "glow": "rgba(255,107,107,0.5)"},
    "mcp":          {"primary": "#60A5FA", "glow": "rgba(96,165,250,0.5)"},
    "llamaindex":   {"primary": "#A78BFA", "glow": "rgba(167,139,250,0.5)"},
    "openai-sdk":   {"primary": "#FFD700", "glow": "rgba(255,215,0,0.5)"},
    "_nourishing":  {"primary": "#2ED573", "glow": "rgba(46,213,115,0.5)"},
}

FRAMEWORK_ICONS = {
    "langchain":    "🔗",
    "crewai":       "🤖",
    "mcp":          "🔌",
    "llamaindex":   "📚",
    "openai-sdk":   "🧠",
    "_nourishing":  "🌿",
}

FRAMEWORK_DISPLAY_NAMES = {
    "langchain":    "LangChain",
    "crewai":       "CrewAI",
    "mcp":          "MCP",
    "llamaindex":   "LlamaIndex",
    "openai-sdk":   "OpenAI SDK",
    "_nourishing":  "养生药方",
}

SEVERITY_COLORS = {
    "critical": "#FF4757",
    "high":     "#FF6B6B",
    "medium":   "#FFD700",
    "low":      "#2ED573",
}


# ──────────────────────────────────────────────
# 1. 数据扫描
# ──────────────────────────────────────────────

def parse_front_matter(filepath: Path) -> dict | None:
    """解析 YAML front matter"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1].strip())
    except yaml.YAMLError:
        return None


def scan_all_cases() -> dict:
    """扫描 cases/ 目录，构建完整的数据结构"""
    case_files = sorted(CASES_DIR.rglob("*.md"))
    case_files = [f for f in case_files if f.name != "_index.md"]

    # 三级结构: framework -> category -> [cases]
    tree = defaultdict(lambda: defaultdict(list))
    all_cases = []

    for fp in case_files:
        meta = parse_front_matter(fp)
        if not meta:
            continue

        fw = meta.get("framework", "unknown")
        # 从目录结构推断 category
        rel = fp.relative_to(CASES_DIR)
        parts = rel.parts
        category = parts[-2] if len(parts) >= 2 else "general"

        case_info = {
            "id": meta.get("id", fp.stem),
            "title": meta.get("title", fp.stem),
            "title_en": meta.get("title_en", ""),
            "framework": fw,
            "category": category,
            "severity": meta.get("severity", "medium"),
            "complexity": meta.get("complexity", "moderate"),
            "tags": meta.get("tags", []),
            "filepath": str(rel),
        }
        tree[fw][category].append(case_info)
        all_cases.append(case_info)

    return {
        "tree": {fw: dict(cats) for fw, cats in tree.items()},
        "all_cases": all_cases,
        "total": len(all_cases),
        "frameworks": list(tree.keys()),
        "generated_at": datetime.now().isoformat(),
    }


# ──────────────────────────────────────────────
# 2. SVG 生成器
# ──────────────────────────────────────────────

def generate_svg(data: dict) -> str:
    """生成带 CSS 动画的 SVG 文件"""
    frameworks = data["tree"]
    total = data["total"]
    fw_count = len(frameworks)

    w, h = 900, 520
    cx, cy = w / 2, h / 2 - 20
    orbit_rx, orbit_ry = 280, 140  # 椭圆轨道半径

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    lines.append('<defs>')
    # 发光滤镜
    lines.append('''
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glow-strong" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glow-soft" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    ''')

    # 径向渐变 - 中心太极
    lines.append('''
    <radialGradient id="taichi-cyan" cx="50%" cy="50%">
      <stop offset="0%" stop-color="#00FFFF" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#00FFFF" stop-opacity="0.2"/>
    </radialGradient>
    <radialGradient id="taichi-green" cx="50%" cy="50%">
      <stop offset="0%" stop-color="#00D09C" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#00D09C" stop-opacity="0.2"/>
    </radialGradient>
    ''')
    lines.append('</defs>')

    # CSS 动画
    lines.append('<style>')
    lines.append('''
      @keyframes pulse-core {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.08); }
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      @keyframes float-y {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
      }
      @keyframes twinkle {
        0%, 100% { opacity: 0.2; }
        50% { opacity: 0.8; }
      }
      @keyframes dash-flow {
        to { stroke-dashoffset: -20; }
      }
      .core-glow { animation: pulse-core 3s ease-in-out infinite; transform-origin: center; }
      .orbit-line { fill: none; stroke-dasharray: 4 6; animation: dash-flow 2s linear infinite; }
      .star { animation: twinkle var(--dur) ease-in-out infinite; animation-delay: var(--delay); }
    ''')

    # 为每个框架生成轨道动画
    fw_list = list(frameworks.keys())
    for i, _fw in enumerate(fw_list):
        duration = 20 + i * 5  # 不同速度
        # 行星沿椭圆轨道运动的关键帧
        lines.append(f'''
      @keyframes orbit-{i} {{
        from {{ transform: rotate({i * (360 // max(fw_count, 1))}deg); }}
        to {{ transform: rotate({i * (360 // max(fw_count, 1)) + 360}deg); }}
      }}
      .planet-{i} {{
        animation: orbit-{i} {duration}s linear infinite;
        transform-origin: {cx}px {cy}px;
      }}
      .planet-label-{i} {{
        animation: float-y {2 + i * 0.5}s ease-in-out infinite;
      }}
    ''')

    lines.append('</style>')

    # ─── 背景 ───
    lines.append(f'<rect width="{w}" height="{h}" fill="#0A0E1A" rx="12"/>')

    # 背景网格
    lines.append('<g opacity="0.04">')
    for x in range(0, w, 40):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="#00D09C" stroke-width="0.5"/>')
    for y in range(0, h, 40):
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#00D09C" stroke-width="0.5"/>')
    lines.append('</g>')

    # 随机星星
    import random
    random.seed(42)  # 固定种子保证一致性
    lines.append('<g>')
    for _ in range(60):
        sx = random.randint(10, w - 10)
        sy = random.randint(10, h - 60)
        sr = random.uniform(0.3, 1.2)
        dur = random.uniform(2, 6)
        delay = random.uniform(0, 4)
        lines.append(
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" '
            f'class="star" style="--dur:{dur:.1f}s;--delay:{delay:.1f}s"/>'
        )
    lines.append('</g>')

    # ─── 八卦奇门轨道阵 ───
    for i in range(fw_count):
        scale = 0.6 + (i * 0.15)
        rx = orbit_rx * scale
        ry = orbit_ry * scale
        color = list(FRAMEWORK_COLORS.values())[i % len(FRAMEWORK_COLORS)]
        
        # 计算 8 个顶点构成带透视的八边形
        points = []
        offset_angle = math.pi / 8 if i % 2 == 1 else 0
        for j in range(8):
            a = (2 * math.pi / 8) * j + offset_angle
            px = cx + rx * math.cos(a)
            py = cy + ry * math.sin(a)
            points.append(f"{px},{py}")
            
        pts_str = " ".join(points)
        lines.append(
            f'<polygon points="{pts_str}" '
            f'class="orbit-line" stroke="{color["primary"]}" stroke-opacity="0.3" fill="none" stroke-width="1"/>'
        )

    # ─── 辐射状地支切割线 ───
    max_scale = 0.6 + ((fw_count - 1) * 0.15) if fw_count > 0 else 0.6
    max_rx = orbit_rx * max_scale + 20
    max_ry = orbit_ry * max_scale + 10
    for j in range(8):
        a = (2 * math.pi / 8) * j
        x1 = cx + (max_rx * 0.1) * math.cos(a)
        y1 = cy + (max_ry * 0.1) * math.sin(a)
        x2 = cx + max_rx * math.cos(a)
        y2 = cy + max_ry * math.sin(a)
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#00D09C" stroke-opacity="0.15" stroke-width="0.5" stroke-dasharray="2 4"/>')

    # ─── 中心太极光核 ───
    # 外围发光
    lines.append(f'<circle cx="{cx}" cy="{cy}" r="45" fill="none" stroke="#00D09C" stroke-width="1" stroke-opacity="0.5" class="core-glow" filter="url(#glow-strong)"/>')
    # 青蓝色半球 (上)
    lines.append(f'<path d="M {cx-22} {cy} A 22 22 0 0 1 {cx+22} {cy} Z" fill="url(#taichi-cyan)" filter="url(#glow)"/>')
    # 翠绿色半球 (下)
    lines.append(f'<path d="M {cx-22} {cy} A 22 22 0 0 0 {cx+22} {cy} Z" fill="url(#taichi-green)" filter="url(#glow)"/>')
    # 分界线
    lines.append(f'<line x1="{cx-24}" y1="{cy}" x2="{cx+24}" y2="{cy}" stroke="#0A0E1A" stroke-width="2"/>')
    
    # 中心文字
    lines.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="#0A0E1A" font-family="sans-serif" font-size="7" font-weight="800" letter-spacing="0.5">CYBER</text>')
    lines.append(f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" fill="#0A0E1A" font-family="sans-serif" font-size="6" font-weight="600">HUATUO</text>')

    # ─── 行星节点与经络连线 ───
    for i, fw in enumerate(fw_list):
        case_count = sum(len(cases) for cases in frameworks[fw].values())
        color_info = FRAMEWORK_COLORS.get(fw, {"primary": "#888", "glow": "rgba(136,136,136,0.5)"})
        color = color_info["primary"]
        icon = FRAMEWORK_ICONS.get(fw, "📦")
        display_name = FRAMEWORK_DISPLAY_NAMES.get(fw, fw)

        # 计算椭圆轨道上的初始位置
        angle = (2 * math.pi / fw_count) * i - math.pi / 2
        scale = 0.6 + (i * 0.15)
        px = cx + orbit_rx * scale * math.cos(angle)
        py = cy + orbit_ry * scale * math.sin(angle)

        node_r = 10 + case_count * 1.5  # 节点大小与案例数正比
        node_r = min(node_r, 30)

        # 折线经络连线 (中转点)
        mid_x = cx + (px - cx) * 0.5
        lines.append(
            f'<polyline points="{cx},{cy} {mid_x},{cy} {px},{py}" '
            f'stroke="{color}" stroke-opacity="0.25" fill="none" stroke-width="1" stroke-dasharray="2 3"'
            f' class="orbit-line"/>'
        )

        # 行星组
        lines.append(f'<g class="planet-label-{i}">')

        # 发光圈
        lines.append(
            f'<circle cx="{px}" cy="{py}" r="{node_r + 8}" fill="{color}" opacity="0.08" '
            f'filter="url(#glow-soft)"/>'
        )
        # 行星体
        lines.append(
            f'<circle cx="{px}" cy="{py}" r="{node_r}" fill="#0A0E1A" stroke="{color}" '
            f'stroke-width="1.5" filter="url(#glow)"/>'
        )
        # 行星图标
        lines.append(
            f'<text x="{px}" y="{py + 1}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="12">{icon}</text>'
        )
        # 框架名称
        lines.append(
            f'<text x="{px}" y="{py + node_r + 14}" text-anchor="middle" fill="{color}" '
            f'font-family="sans-serif" font-size="8" font-weight="600">{display_name}</text>'
        )
        # 案例数
        lines.append(
            f'<text x="{px}" y="{py + node_r + 24}" text-anchor="middle" fill="{color}" '
            f'font-family="monospace" font-size="7" opacity="0.7">{case_count} cases</text>'
        )
        lines.append('</g>')

    # ─── 底部统计条 ───
    bar_y = h - 38
    lines.append(f'<rect x="0" y="{bar_y - 5}" width="{w}" height="43" fill="#0A0E1A" fill-opacity="0.8"/>')
    lines.append(f'<line x1="60" y1="{bar_y}" x2="{w - 60}" y2="{bar_y}" stroke="#00D09C" stroke-opacity="0.15" stroke-width="1"/>')

    stats_text = f'{total} Prescriptions · {fw_count} Frameworks · 100% Open Source'
    lines.append(
        f'<text x="{cx}" y="{bar_y + 20}" text-anchor="middle" fill="#00D09C" '
        f'font-family="monospace" font-size="10" opacity="0.6" letter-spacing="1">'
        f'{stats_text}</text>'
    )

    # 左右装饰
    lines.append(f'<text x="30" y="{bar_y + 20}" fill="#00D09C" font-family="sans-serif" font-size="10" opacity="0.4">🩺</text>')
    lines.append(f'<text x="{w - 40}" y="{bar_y + 20}" fill="#00D09C" font-family="sans-serif" font-size="10" opacity="0.4">💊</text>')

    # 顶部标题
    lines.append(f'<text x="{cx}" y="25" text-anchor="middle" fill="#00D09C" font-family="monospace" font-size="9" font-weight="700" letter-spacing="2" opacity="0.5">PRESCRIPTION UNIVERSE</text>')
    lines.append(f'<text x="{cx}" y="37" text-anchor="middle" fill="#8892B0" font-family="sans-serif" font-size="8" opacity="0.5">药方宇宙 · 点击进入可交互 3D 版本</text>')

    lines.append('</svg>')
    return '\n'.join(lines)


# ──────────────────────────────────────────────
# 3. Three.js HTML 生成器
# ──────────────────────────────────────────────

def generate_html(data: dict) -> str:
    """生成自包含的 Three.js 交互式 3D HTML"""
    json_data = json.dumps(data, ensure_ascii=False, indent=2)

    # 框架配色 JSON
    colors_json = json.dumps(FRAMEWORK_COLORS, ensure_ascii=False)
    icons_json = json.dumps(FRAMEWORK_ICONS, ensure_ascii=False)
    names_json = json.dumps(FRAMEWORK_DISPLAY_NAMES, ensure_ascii=False)
    severity_colors_json = json.dumps(SEVERITY_COLORS, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CyberHuaTuo · 3D 药方宇宙 · Prescription Universe</title>
  <meta name="description" content="赛博华佗 3D 药方宇宙 — 可交互的处方知识图谱可视化">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Orbitron:wght@500;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      background: #0A0E1A;
      color: #E8E8F0;
      font-family: 'Inter', 'Noto Sans SC', sans-serif;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }}

    #canvas-container {{
      position: fixed;
      inset: 0;
      z-index: 1;
    }}

    /* ─── 顶部导航 ─── */
    .top-bar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 28px;
      background: linear-gradient(180deg, rgba(10,14,26,0.95) 0%, rgba(10,14,26,0.6) 60%, rgba(10,14,26,0) 100%);
      pointer-events: none;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .top-bar > * {{ pointer-events: auto; }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-icon {{ font-size: 1.3rem; }}

    .brand-text {{
      font-family: 'Orbitron', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      color: #00D09C;
      letter-spacing: 0.15em;
      text-shadow: 0 0 30px rgba(0,208,156,0.4);
    }}

    .brand-sub {{
      font-family: 'Noto Sans SC', sans-serif;
      font-size: 0.65rem;
      color: #4A5070;
      margin-top: 2px;
    }}

    .stats-bar {{
      display: flex;
      gap: 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      color: #4A5070;
    }}

    .stat-value {{
      color: #00D09C;
      font-weight: 600;
    }}

    /* ─── 框架过滤器 ─── */
    .filter-bar {{
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 100;
      display: flex;
      gap: 6px;
      padding: 8px 14px;
      background: rgba(26,31,46,0.88);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(42,48,80,0.6);
      border-radius: 30px;
      max-width: 95vw;
      overflow-x: auto;
      scrollbar-width: none;
    }}

    .filter-bar::-webkit-scrollbar {{ display: none; }}

    .filter-chip {{
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid rgba(42,48,80,0.8);
      background: transparent;
      color: #8892B0;
      font-family: 'Inter', sans-serif;
      font-size: 0.72rem;
      cursor: pointer;
      transition: all 0.25s;
      white-space: nowrap;
    }}

    .filter-chip:hover {{
      border-color: rgba(0,208,156,0.4);
      color: #E8E8F0;
    }}

    .filter-chip.active {{
      border-color: #00D09C;
      background: rgba(0,208,156,0.12);
      color: #00D09C;
    }}

    /* ─── 详情面板 ─── */
    .detail-panel {{
      position: fixed;
      top: 0;
      right: -420px;
      width: 400px;
      height: 100vh;
      z-index: 200;
      background: rgba(10,14,26,0.96);
      backdrop-filter: blur(20px);
      border-left: 1px solid rgba(0,208,156,0.2);
      transition: right 0.4s cubic-bezier(0.22,1,0.36,1);
      overflow-y: auto;
      padding: 28px 24px;
    }}

    .detail-panel.open {{
      right: 0;
    }}

    .detail-close {{
      position: absolute;
      top: 16px;
      right: 16px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 1px solid rgba(42,48,80,0.6);
      background: transparent;
      color: #8892B0;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }}

    .detail-close:hover {{
      border-color: #FF4757;
      color: #FF4757;
    }}

    .detail-fw-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.72rem;
      font-weight: 600;
      margin-bottom: 12px;
    }}

    .detail-title {{
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.5;
      margin-bottom: 6px;
    }}

    .detail-title-en {{
      font-size: 0.82rem;
      color: #4A5070;
      margin-bottom: 16px;
      line-height: 1.4;
    }}

    .detail-section {{
      margin-bottom: 16px;
    }}

    .detail-section-title {{
      font-size: 0.72rem;
      color: #4A5070;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 8px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .detail-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .detail-tag {{
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.68rem;
      font-weight: 500;
      border: 1px solid;
    }}

    .severity-badge {{
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.7rem;
      font-weight: 600;
    }}

    .cases-list {{
      list-style: none;
    }}

    .cases-list li {{
      padding: 12px 14px;
      border: 1px solid rgba(42,48,80,0.4);
      border-radius: 10px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .cases-list li:hover {{
      border-color: rgba(0,208,156,0.3);
      background: rgba(0,208,156,0.04);
    }}

    .case-title {{
      font-size: 0.82rem;
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .case-meta {{
      font-size: 0.68rem;
      color: #4A5070;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* ─── Tooltip ─── */
    .tooltip {{
      position: fixed;
      padding: 8px 14px;
      background: rgba(26,31,46,0.95);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(0,208,156,0.3);
      border-radius: 8px;
      font-size: 0.75rem;
      color: #E8E8F0;
      pointer-events: none;
      z-index: 300;
      opacity: 0;
      transition: opacity 0.15s;
      white-space: nowrap;
    }}

    .tooltip.visible {{
      opacity: 1;
    }}

    /* ─── 操作提示 ─── */
    .hint {{
      position: fixed;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 50;
      font-size: 0.72rem;
      color: #4A5070;
      font-family: 'JetBrains Mono', monospace;
      opacity: 0.5;
      pointer-events: none;
      white-space: nowrap;
      text-align: center;
      letter-spacing: 0.05em;
    }}

    @media (max-width: 768px) {{
      .top-bar {{ padding: 12px 16px; }}
      .brand-text {{ font-size: 0.8rem; }}
      .stats-bar {{ font-size: 0.65rem; gap: 12px; }}
      .hint {{ font-size: 0.6rem; bottom: 72px; }}
      .filter-chip {{ padding: 5px 10px; font-size: 0.65rem; }}
      .detail-panel {{ width: 85vw; right: -90vw; }}
    }}

    /* ─── 卷轴关闭按钮 ─── */
    .scroll-close-btn {{
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 300;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      border: 1px solid rgba(255,71,87,0.4);
      background: rgba(10,14,26,0.88);
      backdrop-filter: blur(12px);
      color: #FF4757;
      font-size: 1.3rem;
      cursor: pointer;
      display: none;
      align-items: center;
      justify-content: center;
      transition: all 0.25s;
      box-shadow: 0 0 20px rgba(255,71,87,0.15);
    }}

    .scroll-close-btn:hover {{
      border-color: #FF4757;
      background: rgba(255,71,87,0.18);
      transform: scale(1.12);
      box-shadow: 0 0 30px rgba(255,71,87,0.3);
    }}

    .scroll-hint {{
      position: fixed;
      bottom: 100px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 300;
      font-size: 0.72rem;
      color: #00D09C;
      font-family: 'JetBrains Mono', monospace;
      opacity: 0;
      pointer-events: none;
      white-space: nowrap;
      transition: opacity 0.4s;
      text-shadow: 0 0 15px rgba(0,208,156,0.3);
    }}

    .scroll-hint.visible {{
      opacity: 0.6;
    }}

    /* ─── 加载动画 ─── */
    .loader {{
      position: fixed;
      inset: 0;
      z-index: 1000;
      background: #0A0E1A;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.6s;
    }}

    .loader.hide {{
      opacity: 0;
      pointer-events: none;
    }}

    .loader-text {{
      font-family: 'Orbitron', sans-serif;
      font-size: 1rem;
      color: #00D09C;
      letter-spacing: 0.15em;
      margin-top: 20px;
      animation: pulse-load 1.5s ease-in-out infinite;
    }}

    @keyframes pulse-load {{
      0%, 100% {{ opacity: 0.4; }}
      50% {{ opacity: 1; }}
    }}

    .loader-ring {{
      width: 48px;
      height: 48px;
      border: 2px solid rgba(0,208,156,0.15);
      border-top-color: #00D09C;
      border-radius: 50%;
      animation: spin-load 1s linear infinite;
    }}

    @keyframes spin-load {{
      to {{ transform: rotate(360deg); }}
    }}
  </style>
</head>
<body>
  <!-- 加载动画 -->
  <div class="loader" id="loader">
    <div class="loader-ring"></div>
    <div class="loader-text">INITIALIZING UNIVERSE</div>
  </div>

  <!-- 3D 画布 -->
  <div id="canvas-container"></div>

  <!-- 顶部导航 -->
  <div class="top-bar">
    <div class="brand">
      <span class="brand-icon">🩺</span>
      <div>
        <div class="brand-text">CYBERHUATUO</div>
        <div class="brand-sub">3D 药方宇宙 · Prescription Universe</div>
      </div>
    </div>
    <div class="stats-bar">
      <span>💊 <span class="stat-value" id="stat-total">{data['total']}</span> prescriptions</span>
      <span>🔧 <span class="stat-value" id="stat-fw">{len(data['frameworks'])}</span> frameworks</span>
    </div>
  </div>

  <!-- 框架过滤器 -->
  <div class="filter-bar" id="filter-bar"></div>

  <!-- 操作提示 -->
  <div class="hint">拖拽旋转 · 滚轮缩放 · 点击节点查看详情</div>

  <!-- 详情面板 -->
  <div class="detail-panel" id="detail-panel">
    <button class="detail-close" id="detail-close">✕</button>
    <div id="detail-content"></div>
  </div>

  <!-- Tooltip -->
  <div class="tooltip" id="tooltip"></div>

  <!-- 卷轴关闭按钮 -->
  <button class="scroll-close-btn" id="scroll-close-btn">✕</button>
  <div class="scroll-hint" id="scroll-hint">ESC 关闭卷轴 · Press ESC to close</div>

  <!-- Three.js CDN -->
  <script type="importmap">
  {{
    "imports": {{
      "three": "https://unpkg.com/three@0.170.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.170.0/examples/jsm/"
    }}
  }}
  </script>

  <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
    import {{ UnrealBloomPass }} from 'three/addons/postprocessing/UnrealBloomPass.js';
    import {{ EffectComposer }} from 'three/addons/postprocessing/EffectComposer.js';
    import {{ RenderPass }} from 'three/addons/postprocessing/RenderPass.js';

    // ─── 数据注入 ───
    const DATA = {json_data};
    const FW_COLORS = {colors_json};
    const FW_ICONS = {icons_json};
    const FW_NAMES = {names_json};
    const SV_COLORS = {severity_colors_json};

    // ─── 场景初始化 ───
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(0, 6, 18);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);

    // 后处理 - Bloom
    const composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.2, 0.3, 0.75
    );
    composer.addPass(bloomPass);

    // 控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.3;
    controls.minDistance = 8;
    controls.maxDistance = 50;
    controls.maxPolarAngle = Math.PI * 0.85;

    // ─── 背景星空 ───
    const starGeom = new THREE.BufferGeometry();
    const starCount = 4000;
    const starPos = new Float32Array(starCount * 3);
    const starSizes = new Float32Array(starCount);
    for (let i = 0; i < starCount; i++) {{
      starPos[i * 3]     = (Math.random() - 0.5) * 200;
      starPos[i * 3 + 1] = (Math.random() - 0.5) * 200;
      starPos[i * 3 + 2] = (Math.random() - 0.5) * 200;
      starSizes[i] = Math.random() * 1.5 + 0.3;
    }}
    starGeom.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    starGeom.setAttribute('size', new THREE.BufferAttribute(starSizes, 1));
    const starMat = new THREE.PointsMaterial({{
      color: 0xffffff,
      size: 0.15,
      transparent: true,
      opacity: 0.7,
      sizeAttenuation: true,
    }});
    scene.add(new THREE.Points(starGeom, starMat));

    // ─── 节点存储 ───
    const nodeObjects = [];
    const nodeDataMap = new Map();       // mesh -> data
    const frameworkGroups = new Map();    // fw -> group
    let activeFilter = 'all';

    // ─── 创建中心太极节点 (Tai Chi Core) ───
    function createCore() {{
      const group = new THREE.Group();

      // 半球: Cyan (Tech)
      const half1Geom = new THREE.SphereGeometry(2.0, 32, 32, 0, Math.PI);
      const half1Mat = new THREE.MeshStandardMaterial({{
        color: 0x00FFFF, emissive: 0x00FFFF, emissiveIntensity: 0.6,
        transparent: true, opacity: 0.9, roughness: 0.1, metalness: 0.9,
      }});
      const half1 = new THREE.Mesh(half1Geom, half1Mat);
      
      // 半球: Green (TCM)
      const half2Geom = new THREE.SphereGeometry(2.0, 32, 32, Math.PI, Math.PI);
      const half2Mat = new THREE.MeshStandardMaterial({{
        color: 0x00D09C, emissive: 0x00D09C, emissiveIntensity: 0.6,
        transparent: true, opacity: 0.9, roughness: 0.1, metalness: 0.9,
      }});
      const half2 = new THREE.Mesh(half2Geom, half2Mat);

      const coreSphere = new THREE.Group();
      coreSphere.add(half1, half2);
      coreSphere.name = 'taiChiCore';
      group.add(coreSphere);

      // 八角形符文阵列占位 (Octagonal Rings)
      const ringGeom = new THREE.RingGeometry(3.2, 3.25, 8);
      const ringMat = new THREE.MeshBasicMaterial({{
        color: 0x00D09C, transparent: true, opacity: 0.5, side: THREE.DoubleSide
      }});
      const ring = new THREE.Mesh(ringGeom, ringMat);
      ring.rotation.x = Math.PI / 2;
      group.add(ring);

      const ring2Geom = new THREE.RingGeometry(4.0, 4.02, 8);
      const ring2 = new THREE.Mesh(ring2Geom, ringMat);
      ring2.rotation.x = Math.PI / 2;
      ring2.rotation.z = Math.PI / 8; // 交错
      group.add(ring2);

      scene.add(group);
      return group;
    }}

    // ─── 创建框架节点 ───
    function createFrameworkNode(fw, index, totalFw) {{
      const group = new THREE.Group();
      const colorStr = FW_COLORS[fw]?.primary || '#888888';
      const color = new THREE.Color(colorStr);
      const cases = DATA.tree[fw] || {{}};
      const caseCount = Object.values(cases).reduce((s, arr) => s + arr.length, 0);

      // 等角水平环形分布 — 避免聚集
      const angle = (2 * Math.PI / totalFw) * index;
      const radius = 10 + caseCount * 0.2;

      const x = radius * Math.cos(angle);
      const y = (Math.sin(index * 1.2) * 2.5);  // 微小 Y 偏移增加层次
      const z = radius * Math.sin(angle);

      group.position.set(x, y, z);

      // 节点球体 — 放大尺寸
      const size = 1.0 + caseCount * 0.12;
      const geom = new THREE.SphereGeometry(Math.min(size, 2.5), 32, 32);
      const mat = new THREE.MeshStandardMaterial({{
        color: color,
        emissive: color,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.9,
        roughness: 0.3,
        metalness: 0.6,
      }});
      const mesh = new THREE.Mesh(geom, mat);
      group.add(mesh);

      // 节点数据
      nodeObjects.push(mesh);
      nodeDataMap.set(mesh, {{
        type: 'framework',
        framework: fw,
        name: FW_NAMES[fw] || fw,
        icon: FW_ICONS[fw] || '📦',
        color: colorStr,
        caseCount,
        categories: cases,
      }});

      // 光环 — 放大
      const haloGeom = new THREE.RingGeometry(size + 0.4, size + 0.65, 32);
      const haloMat = new THREE.MeshBasicMaterial({{
        color: color,
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
      }});
      const halo = new THREE.Mesh(haloGeom, haloMat);
      halo.lookAt(camera.position);
      group.add(halo);

      // 赛博经络连线到中心 (Cyber Meridian Lines)
      const midRadius = radius * 0.4;
      const midX = midRadius * Math.cos(angle);
      const midZ = midRadius * Math.sin(angle);
      const linePoints = [
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(midX, 0, midZ),
        new THREE.Vector3(x, 0, z),
        new THREE.Vector3(x, y, z)
      ];
      const lineGeom = new THREE.BufferGeometry().setFromPoints(linePoints);
      const lineMat = new THREE.LineBasicMaterial({{
        color: color,
        transparent: true,
        opacity: 0.25,
      }});
      scene.add(new THREE.Line(lineGeom, lineMat));

      // ─── 创建分类子节点 ───
      const catKeys = Object.keys(cases);
      catKeys.forEach((cat, catIdx) => {{
        const catCases = cases[cat];
        const catAngle = (2 * Math.PI / catKeys.length) * catIdx;
        const catRadius = 3.0 + catCases.length * 0.4;
        const cx = catRadius * Math.cos(catAngle);
        const cy = (Math.sin(catIdx * 2.1) - 0.5) * 2.0;
        const cz = catRadius * Math.sin(catAngle);

        const catGeom = new THREE.SphereGeometry(0.35 + catCases.length * 0.08, 16, 16);
        const catMat = new THREE.MeshStandardMaterial({{
          color: color,
          emissive: color,
          emissiveIntensity: 0.3,
          transparent: true,
          opacity: 0.75,
        }});
        const catMesh = new THREE.Mesh(catGeom, catMat);
        catMesh.position.set(cx, cy, cz);
        group.add(catMesh);

        nodeObjects.push(catMesh);
        nodeDataMap.set(catMesh, {{
          type: 'category',
          framework: fw,
          category: cat,
          name: cat.replace(/-/g, ' '),
          icon: FW_ICONS[fw] || '📦',
          color: colorStr,
          cases: catCases,
        }});

        // 子节点赛博经络连线到框架节点
        const catMidX = cx * 0.5;
        const catMidZ = cz * 0.5;
        const catLinePoints = [
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(catMidX, 0, catMidZ),
          new THREE.Vector3(cx, 0, cz),
          new THREE.Vector3(cx, cy, cz)
        ];
        const catLineGeom = new THREE.BufferGeometry().setFromPoints(catLinePoints);
        const catLineMat = new THREE.LineBasicMaterial({{
          color: color,
          transparent: true,
          opacity: 0.15,
        }});
        group.add(new THREE.Line(catLineGeom, catLineMat));
      }});

      scene.add(group);
      frameworkGroups.set(fw, group);
      return group;
    }}

    // ─── 八卦奇门轨道阵 (Bagua Compass Orbits) ───
    function createBaguaCompass() {{
      const fws = Object.keys(DATA.tree);
      const compassGroup = new THREE.Group();
      compassGroup.name = 'baguaCompass';

      fws.forEach((fw, i) => {{
        const colorStr = FW_COLORS[fw]?.primary || '#888888';
        const radius = 10 + i * 2.5;
        
        // 八边形线框
        const circleGeom = new THREE.CircleGeometry(radius, 8);
        const edges = new THREE.EdgesGeometry(circleGeom);
        const lineMat = new THREE.LineBasicMaterial({{
          color: new THREE.Color(colorStr),
          transparent: true,
          opacity: 0.15 + (i % 2 === 0 ? 0.15 : 0), // 层次亮度差异
        }});
        const octagon = new THREE.LineSegments(edges, lineMat);
        octagon.rotation.x = Math.PI / 2;
        // 每层交错一个角度
        octagon.rotation.z = (i % 2 === 0) ? 0 : Math.PI / 8;
        compassGroup.add(octagon);
      }});

      // 添加辐射状地支分割线
      const maxRadius = 10 + (fws.length - 1) * 2.5 + 2;
      for (let i = 0; i < 8; i++) {{
        const angle = (Math.PI / 4) * i;
        const pts = [
           new THREE.Vector3(4.0 * Math.cos(angle), 0, 4.0 * Math.sin(angle)),
           new THREE.Vector3(maxRadius * Math.cos(angle), 0, maxRadius * Math.sin(angle))
        ];
        const geom = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({{ color: 0x00D09C, transparent: true, opacity: 0.1 }});
        compassGroup.add(new THREE.Line(geom, mat));
      }}

      scene.add(compassGroup);
    }}

    // ─── 粒子流 ───
    function createParticleStream() {{
      const particleCount = 300;
      const geom = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);
      const sizes = new Float32Array(particleCount);

      for (let i = 0; i < particleCount; i++) {{
        const theta = Math.random() * Math.PI * 2;
        const r = 3 + Math.random() * 15;
        positions[i * 3]     = r * Math.cos(theta);
        positions[i * 3 + 1] = (Math.random() - 0.5) * 6;
        positions[i * 3 + 2] = r * Math.sin(theta);

        const c = new THREE.Color(Math.random() > 0.5 ? 0x00D09C : 0x00FFFF);
        colors[i * 3] = c.r;
        colors[i * 3 + 1] = c.g;
        colors[i * 3 + 2] = c.b;
        sizes[i] = Math.random() * 0.08 + 0.02;
      }}

      geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      const mat = new THREE.PointsMaterial({{
        size: 0.06,
        vertexColors: true,
        transparent: true,
        opacity: 0.5,
        sizeAttenuation: true,
      }});
      const points = new THREE.Points(geom, mat);
      scene.add(points);
      return points;
    }}

    // ─── 环境光 ───
    scene.add(new THREE.AmbientLight(0x404050, 0.5));
    const pointLight = new THREE.PointLight(0x00D09C, 2, 50);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);
    const pointLight2 = new THREE.PointLight(0x00FFFF, 0.5, 30);
    pointLight2.position.set(10, -3, 5);
    scene.add(pointLight2);

    // ─── 构建场景 ───
    createCore();
    createBaguaCompass();
    const particles = createParticleStream();

    const fwKeys = Object.keys(DATA.tree);
    fwKeys.forEach((fw, i) => createFrameworkNode(fw, i, fwKeys.length));

    // ─── 过滤器 UI ───
    const filterBar = document.getElementById('filter-bar');
    const allChip = document.createElement('button');
    allChip.className = 'filter-chip active';
    allChip.textContent = '🌐 All';
    allChip.onclick = () => setFilter('all');
    filterBar.appendChild(allChip);

    fwKeys.forEach(fw => {{
      const chip = document.createElement('button');
      chip.className = 'filter-chip';
      chip.dataset.fw = fw;
      const icon = FW_ICONS[fw] || '📦';
      const name = FW_NAMES[fw] || fw;
      const count = Object.values(DATA.tree[fw]).reduce((s, a) => s + a.length, 0);
      chip.textContent = `${{icon}} ${{name}} (${{count}})`;
      chip.onclick = () => setFilter(fw);
      filterBar.appendChild(chip);
    }});

    function setFilter(fw) {{
      activeFilter = fw;
      document.querySelectorAll('.filter-chip').forEach(c => {{
        c.classList.toggle('active', (fw === 'all' && c.textContent.includes('All')) || c.dataset.fw === fw);
      }});
      frameworkGroups.forEach((group, key) => {{
        const visible = fw === 'all' || key === fw;
        group.visible = visible;
      }});
    }}

    // ─── 3D 书轴系统 ───
    let activeScroll = null;
    let scrollAnimState = null;
    const savedCamPos = new THREE.Vector3();
    const savedCamTarget = new THREE.Vector3();

    function easeOutCubic(t) {{ return 1 - Math.pow(1 - t, 3); }}
    function easeInCubic(t) {{ return t * t * t; }}

    // 离屏 Canvas 渲染药方内容
    function renderPrescriptionCanvas(nodeData) {{
      const cvs = document.createElement('canvas');
      const W = 3072, CH = 2048; // High resolution
      cvs.width = W; cvs.height = CH;
      const ctx = cvs.getContext('2d');

      // 纸面底色 — Dark Cyber Glass
      const grad = ctx.createLinearGradient(0, 0, W, CH);
      grad.addColorStop(0, '#090D14');
      grad.addColorStop(0.5, '#121A28');
      grad.addColorStop(1, '#090D14');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, W, CH);

      // Subtle cyber grid lines
      ctx.strokeStyle = '#ffffff04';
      ctx.lineWidth = 1;
      for(let i=0; i<W; i+=100) {{ ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, CH); ctx.stroke(); }}
      for(let j=0; j<CH; j+=100) {{ ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(W, j); ctx.stroke(); }}

      const fColor = nodeData.color || '#00D09C';

      // 外外边框 (Glowing Rim)
      ctx.strokeStyle = fColor + 'AA';
      ctx.lineWidth = 10;
      ctx.strokeRect(30, 30, W - 60, CH - 60);

      // 内边框 (Fine line)
      ctx.strokeStyle = fColor + '60';
      ctx.lineWidth = 2;
      ctx.strokeRect(50, 50, W - 100, CH - 100);

      // 顶部四角纹饰
      ctx.strokeStyle = fColor + '80';
      ctx.lineWidth = 4;
      [[60, 60], [W - 60, 60], [60, CH - 60], [W - 60, CH - 60]].forEach(([x, y]) => {{
        ctx.beginPath();
        const dx = x < W / 2 ? 1 : -1;
        const dy = y < CH / 2 ? 1 : -1;
        ctx.moveTo(x + dx * 50, y);
        ctx.lineTo(x, y);
        ctx.lineTo(x, y + dy * 50);
        ctx.stroke();
      }});

      // 标题 Icon + 名称
      ctx.fillStyle = fColor;
      ctx.font = 'bold 80px "Inter", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${{nodeData.icon || '📦'}} ${{nodeData.name || ''}}`, W / 2, 180);

      // 副标题
      ctx.fillStyle = '#8892B0';
      ctx.font = '36px "JetBrains Mono", monospace';
      if (nodeData.type === 'framework') {{
        const catCount = Object.keys(nodeData.categories || {{}}).length;
        ctx.fillText(`药方集 | Prescriptions: ${{nodeData.caseCount}} · 领域 | Domains: ${{catCount}}`, W / 2, 250);
      }} else {{
        ctx.fillText(`药方集 | Prescriptions: ${{(nodeData.cases || []).length}}`, W / 2, 250);
      }}

      // 分隔线
      ctx.strokeStyle = fColor + '50';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(150, 310);
      ctx.lineTo(W - 150, 310);
      ctx.stroke();

      // 内容
      let y = 400;
      ctx.textAlign = 'left';
      const svColors = {{ critical: '#FF4757', high: '#FF6B35', medium: '#FFA500', low: '#00D09C' }};

      if (nodeData.type === 'framework') {{
        Object.entries(nodeData.categories || {{}}).forEach(([cat, cases]) => {{
          if (y > CH - 200) return;
          ctx.fillStyle = fColor;
          ctx.font = 'bold 44px "Inter", sans-serif';
          ctx.fillText(`✦ ${{cat.replace(/-/g, ' ')}} (${{cases.length}})`, 120, y);
          y += 70;
          cases.forEach(c => {{
            if (y > CH - 150) return;
            // 中文行
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 38px "Inter", sans-serif';
            let title = c.title || '';
            if (title.length > 40) title = title.substring(0, 40) + '...';
            ctx.fillText(title, 160, y);
            y += 48;

            // 英文行 (Severity, Complexity, Tags)
            const svColor = svColors[c.severity] || '#888';
            ctx.fillStyle = svColor;
            ctx.font = '30px "JetBrains Mono", monospace';
            const engStr = `[${{c.severity.toUpperCase()}}] CPLX: ${{c.complexity}} | TAGS: ${{(c.tags || []).join(', ')}}`;
            ctx.fillText(engStr, 160, y);
            y += 70;
          }});
          y += 30; // 领域隔离
        }});
      }} else if (nodeData.type === 'category') {{
        (nodeData.cases || []).forEach(c => {{
          if (y > CH - 150) return;
          // 中文行
          ctx.fillStyle = '#FFFFFF';
          ctx.font = 'bold 40px "Inter", sans-serif';
          let title = c.title || '';
          if (title.length > 50) title = title.substring(0, 50) + '...';
          ctx.fillText(title, 120, y);
          y += 50;

          // 英文行
          const svColor = svColors[c.severity] || '#888';
          ctx.fillStyle = svColor;
          ctx.font = '32px "JetBrains Mono", monospace';
          const engStr = `[${{c.severity.toUpperCase()}}] LEVEL: ${{c.complexity}} | META: ${{(c.tags || []).join(', ')}}`;
          ctx.fillText(engStr, 120, y);
          y += 80;
        }});
      }}

      // 底部印章
      ctx.fillStyle = fColor + '80';
      ctx.font = '28px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('🩺 CyberHuaTuo · 赛博华佗 3D Prescription Scroll', W / 2, CH - 80);

      return cvs;
    }}

    // 创建 3D 卷轴模型
    function createScrollModel(nodeData) {{
      const group = new THREE.Group();
      const fColor = new THREE.Color(nodeData.color || '#00D09C');
      const scrollW = 10.0, scrollH = 6.6; // Wider for high res
      const rodR = 0.15, rodL = scrollH + 0.9;

      // 暗金卷轴木轴材质 (Cyber Obsidian)
      const rodMat = new THREE.MeshStandardMaterial({{
        color: 0x111622, roughness: 0.2, metalness: 0.8,
      }});

      // 轴头装饰球材质 (Cyber Glowing Jade)
      const knobMat = new THREE.MeshStandardMaterial({{
        color: fColor, emissive: fColor, emissiveIntensity: 0.8,
        roughness: 0.1, metalness: 0.9,
      }});
      const knobGeom = new THREE.SphereGeometry(0.25, 32, 32);

      // 左轴 Group
      const leftGroup = new THREE.Group();
      const leftRod = new THREE.Mesh(new THREE.CylinderGeometry(rodR, rodR, rodL, 32), rodMat);
      leftGroup.add(leftRod);
      const leftKnobTop = new THREE.Mesh(knobGeom, knobMat);
      leftKnobTop.position.y = rodL / 2;
      const leftKnobBot = new THREE.Mesh(knobGeom, knobMat);
      leftKnobBot.position.y = -rodL / 2;
      leftGroup.add(leftKnobTop, leftKnobBot);

      // 右轴 Group
      const rightGroup = leftGroup.clone();

      group.add(leftGroup, rightGroup);

      // 纸面（Canvas 贴图） -> 全息玻璃质感 (Glassmorphism)
      const canvasEl = renderPrescriptionCanvas(nodeData);
      const tex = new THREE.CanvasTexture(canvasEl);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.needsUpdate = true;
      const paperMat = new THREE.MeshPhysicalMaterial({{
        map: tex, side: THREE.DoubleSide, transparent: true,
        opacity: 0.95, roughness: 0.15, metalness: 0.1,
        clearcoat: 1.0, clearcoatRoughness: 0.1,
        transmission: 0.4, thickness: 0.1, // Glassmorphism
        emissive: fColor, emissiveMap: tex, emissiveIntensity: 0.6 // Text Glow
      }});
      const paper = new THREE.Mesh(new THREE.PlaneGeometry(scrollW, scrollH, 32, 32), paperMat);

      // 边缘背光辉光效果
      const edgeMat = new THREE.MeshBasicMaterial({{
        color: fColor, transparent: true, opacity: 0.15, side: THREE.DoubleSide,
      }});
      const edge = new THREE.Mesh(new THREE.PlaneGeometry(scrollW + 0.3, scrollH + 0.3), edgeMat);
      edge.position.z = -0.05;
      paper.add(edge);

      group.add(paper);

      // 初始状态: 收缩
      paper.scale.x = 0.001;
      leftGroup.position.x = 0;
      rightGroup.position.x = 0;

      // 通过 userData 传递给渲染循环作独立控制
      group.userData = {{ paper, leftGroup, rightGroup, targetW: scrollW }};
      return group;
    }}

    // 展开卷轴
    function showScrollDetail(nodeData) {{
      if (activeScroll) closeScrollDetail(false);

      savedCamPos.copy(camera.position);
      savedCamTarget.copy(controls.target);

      const scroll = createScrollModel(nodeData);

      // 定位：在摄像机正前方
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);
      const pos = camera.position.clone().add(dir.multiplyScalar(14));
      scroll.position.copy(pos);
      scroll.lookAt(camera.position);

      scene.add(scroll);
      activeScroll = scroll;

      scrollAnimState = {{
        phase: 'opening', progress: 0,
        startTime: performance.now(), duration: 900,
      }};

      document.getElementById('scroll-close-btn').style.display = 'flex';
      document.getElementById('scroll-hint').classList.add('visible');
      controls.autoRotate = false;
    }}

    // 收起卷轴
    function closeScrollDetail(restoreCam = true) {{
      if (!activeScroll) return;
      const scrollToRemove = activeScroll;
      activeScroll = null; // 立即分离以解除控制反馈

      scrollAnimState = {{
        phase: 'closing', progress: 0,
        startTime: performance.now(), duration: 500,
        scrollTarget: scrollToRemove // 存入引用以便动画循环继续渲染
      }};
      document.getElementById('scroll-close-btn').style.display = 'none';
      document.getElementById('scroll-hint').classList.remove('visible');

      setTimeout(() => {{
        scene.remove(scrollToRemove);
        if (restoreCam) controls.autoRotate = true;
      }}, 600);
    }}

    // 关闭按钮 + ESC
    document.getElementById('scroll-close-btn').onclick = () => closeScrollDetail();
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeScrollDetail();
    }});

    // showDetail 保留旧面板作为降级 + 触发3D卷轴
    const detailPanel = document.getElementById('detail-panel');
    function showDetail(data) {{
      showScrollDetail(data);
    }}

    // ─── 交互：点击 & Hover ───
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const tooltip = document.getElementById('tooltip');

    renderer.domElement.addEventListener('click', (e) => {{
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeObjects);
      if (intersects.length > 0) {{
        const data = nodeDataMap.get(intersects[0].object);
        if (data) showDetail(data);
      }}
    }});

    renderer.domElement.addEventListener('mousemove', (e) => {{
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeObjects);

      if (intersects.length > 0) {{
        const data = nodeDataMap.get(intersects[0].object);
        if (data) {{
          const label = data.type === 'framework'
            ? `${{data.icon}} ${{data.name}} · ${{data.caseCount}} 药方`
            : `${{data.icon}} ${{data.name}} · ${{data.cases.length}} 药方`;

          tooltip.textContent = label;
          tooltip.style.left = (e.clientX + 15) + 'px';
          tooltip.style.top = (e.clientY - 10) + 'px';
          tooltip.classList.add('visible');
          renderer.domElement.style.cursor = 'pointer';
        }}
      }} else {{
        tooltip.classList.remove('visible');
        renderer.domElement.style.cursor = 'grab';
      }}
    }});

    // ─── 动画循环 ───
    const clock = new THREE.Clock();

    function animate() {{
      requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      // 粒子缓旋
      if (particles) {{
        particles.rotation.y = t * 0.02;
        particles.rotation.x = Math.sin(t * 0.1) * 0.05;
      }}

      // 太极核心与八阵轨道缓旋 (Cyber TCM Dynamics)
      const taiChi = scene.getObjectByName('taiChiCore');
      if (taiChi) taiChi.rotation.y = t * 0.3;
      
      const compass = scene.getObjectByName('baguaCompass');
      if (compass) compass.rotation.y = t * -0.05;

      // 框架节点微浮
      frameworkGroups.forEach((group, fw) => {{
        const i = fwKeys.indexOf(fw);
        const offset = i * 0.7;
        group.position.y += Math.sin(t * 0.5 + offset) * 0.001;
      }});

      // 卷轴展开/收起动画
      if (scrollAnimState) {{
        const elapsed = (performance.now() - scrollAnimState.startTime) / scrollAnimState.duration;
        const progress = Math.min(elapsed, 1);
        const targetScroll = scrollAnimState.phase === 'opening' ? activeScroll : scrollAnimState.scrollTarget;

        if (targetScroll && targetScroll.userData) {{
          let easeVal = scrollAnimState.phase === 'opening' ? easeOutCubic(progress) : 1 - easeInCubic(progress);
          const ud = targetScroll.userData;

          // 画卷独立放缩，避免木轴被压缩
          ud.paper.scale.x = Math.max(0.001, easeVal);
          let yzScale = 0.8 + easeVal * 0.2;
          targetScroll.scale.set(1, yzScale, yzScale);

          // 木轴向两侧平移
          const maxW = ud.targetW;
          ud.leftGroup.position.x = (-maxW / 2) * easeVal - 0.18;
          ud.rightGroup.position.x = (maxW / 2) * easeVal + 0.18;

          targetScroll.lookAt(camera.position);
        }}

        if (progress >= 1) scrollAnimState = null;
      }}

      // 正常的跟随朝向 (当不在收起动画中时)
      if (activeScroll && !scrollAnimState) {{
        activeScroll.lookAt(camera.position);
      }}

      controls.update();
      composer.render();
    }}

    // ─── 启动 ───
    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      composer.setSize(window.innerWidth, window.innerHeight);
    }});

    // 隐藏加载动画
    setTimeout(() => {{
      document.getElementById('loader').classList.add('hide');
    }}, 800);

    animate();
  </script>
</body>
</html>'''

    return html


# ──────────────────────────────────────────────
# 4. 主入口
# ──────────────────────────────────────────────

def main():
    print("🩺 CyberHuaTuo 3D 药方宇宙生成器")
    print("=" * 50)

    # 1. 扫描案例
    print("📂 扫描 cases/ 目录 ...")
    data = scan_all_cases()
    print(f"   ✅ 发现 {data['total']} 个药方，{len(data['frameworks'])} 个框架")

    for fw in data["frameworks"]:
        case_count = sum(len(v) for v in data["tree"][fw].values())
        display = FRAMEWORK_DISPLAY_NAMES.get(fw, fw)
        icon = FRAMEWORK_ICONS.get(fw, "📦")
        cats = list(data["tree"][fw].keys())
        print(f"      {icon} {display}: {case_count} cases ({', '.join(cats)})")

    # 2. 生成 SVG
    print("\n🎨 生成 CSS 动画 SVG ...")
    svg_content = generate_svg(data)
    SVG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SVG_OUTPUT.write_text(svg_content, encoding="utf-8")
    print(f"   ✅ {SVG_OUTPUT}")

    # 3. 生成 HTML
    print("\n🌐 生成 Three.js 交互式 3D 页面 ...")
    html_content = generate_html(data)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUTPUT.write_text(html_content, encoding="utf-8")
    print(f"   ✅ {HTML_OUTPUT}")

    # 4. 完成
    print("\n" + "=" * 50)
    print("🎉 生成完成！")
    print(f"   📊 SVG 预览图:  {SVG_OUTPUT}")
    print(f"   🌐 3D 交互页面: {HTML_OUTPUT}")
    print("\n💡 直接在浏览器中打开 index.html 即可体验 3D 药方宇宙:")
    print(f"   file:///{HTML_OUTPUT.as_posix()}")


if __name__ == "__main__":
    main()
