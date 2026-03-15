"""
🎆 赛博华佗 · 电影级科幻终端动画引擎
CyberHuaTuo CLI Cinematic Sci-Fi Effects Engine

融合「斗罗大陆·魂环」×「赛博朋克·全息投影」×「古中医·经络脉象」三重美学，
在终端中呈现电影级的科幻视觉震撼。

使用方式：
    from .cli_effects import render_soul_rings, render_alchemy_hud, ...
"""

import math
import random
import time

# ============================================================
# 🎨 复用 banner.py 的色彩常量与辅助函数
# ============================================================
from .banner import (
    BOLD,
    CLEAR_LINE,
    CYAN,
    CYAN_BRIGHT,
    CYAN_DIM,
    DARK_GRAY,
    DIM,
    GOLD,
    GOLD_DIM,
    GRAY,
    PURPLE,
    PURPLE_DIM,
    RED,
    RED_DIM,
    RESET,
    WHITE,
    _get_term_width,
    _supports_color,
    _write,
)

# ============================================================
# 🌈 扩展科幻色板 — Cinema Grade Color Palette
# ============================================================

# 霓虹色
ORANGE = "\033[38;2;255;140;0m"
GREEN_BRIGHT = "\033[38;2;0;255;100m"
GREEN_DIM = "\033[38;2;0;140;60m"
GREEN_MATRIX = "\033[38;2;0;200;80m"
BLUE_BRIGHT = "\033[38;2;80;160;255m"
BLUE_DIM = "\033[38;2;40;80;160m"
PINK = "\033[38;2;255;100;200m"
PINK_DIM = "\033[38;2;180;60;140m"
BLACK_BRIGHT = "\033[38;2;80;80;100m"
YELLOW_BRIGHT = "\033[38;2;255;255;100m"
MAGENTA = "\033[38;2;220;50;255m"
MAGENTA_DIM = "\033[38;2;140;30;180m"

# 色彩渐变辅助
CYAN_GRADIENT = [
    "\033[38;2;0;80;80m",
    "\033[38;2;0;120;100m",
    "\033[38;2;0;160;130m",
    "\033[38;2;0;200;160m",
    "\033[38;2;0;230;185m",
    "\033[38;2;0;255;200m",
    "\033[38;2;80;255;220m",
    "\033[38;2;150;255;240m",
]

GOLD_GRADIENT = [
    "\033[38;2;120;80;20m",
    "\033[38;2;160;120;30m",
    "\033[38;2;200;160;40m",
    "\033[38;2;230;180;45m",
    "\033[38;2;255;200;50m",
    "\033[38;2;255;220;100m",
    "\033[38;2;255;240;150m",
    "\033[38;2;255;255;200m",
]

PURPLE_GRADIENT = [
    "\033[38;2;60;20;100m",
    "\033[38;2;90;30;140m",
    "\033[38;2;120;50;180m",
    "\033[38;2;150;65;220m",
    "\033[38;2;180;80;255m",
    "\033[38;2;200;120;255m",
    "\033[38;2;220;160;255m",
    "\033[38;2;240;200;255m",
]

RED_GRADIENT = [
    "\033[38;2;100;20;30m",
    "\033[38;2;140;30;40m",
    "\033[38;2;180;40;50m",
    "\033[38;2;210;50;65m",
    "\033[38;2;255;60;80m",
    "\033[38;2;255;100;110m",
    "\033[38;2;255;140;140m",
    "\033[38;2;255;180;180m",
]

# ============================================================
# 🔮 魂环颜色与品阶映射
# ============================================================

RING_COLORS = {
    "⚪": (GRAY, WHITE, "白环 · White Ring"),
    "🟡": (GOLD_DIM, GOLD, "黄环 · Yellow Ring"),
    "🟣": (PURPLE_DIM, PURPLE, "紫环 · Purple Ring"),
    "⚫": (DARK_GRAY, BLACK_BRIGHT, "黑环 · Black Ring"),
    "🔴": (RED_DIM, RED, "红环 · Red Ring"),
    "✨": (GOLD, YELLOW_BRIGHT, "金环 · Golden Ring"),
}

RING_TIER_NAMES = {
    1: ("白环初现", "First White Ring", "灵魂初现，通往炼丹之路"),
    2: ("双黄破晓", "Twin Yellow Dawn", "黄金双环，丹术初成"),
    3: ("三环紫韵", "Triple Purple Aura", "紫气东来，炼丹造诣渐深"),
    4: ("四环齐辉", "Quadruple Radiance", "四环齐鸣，丹火已通"),
    5: ("五环黑炎", "Five Rings Dark Flame", "黑暗之环，万年火候"),
    6: ("六环天象", "Hexagonal Celestial", "天象六环，丹道大成"),
    7: ("七环赤焰", "Septenary Scarlet", "赤焰降世，封号丹师"),
    8: ("八环至尊", "Octagonal Supreme", "至尊八环，纵横天地"),
    9: ("九环封神", "Nine Rings Apotheosis", "九环封神，万古长存"),
}

# 方向色系 (dim, bright, gradient)
DIRECTION_PALETTES = {
    "soul": (RED_DIM, RED, RED_GRADIENT),
    "thunder": (GOLD_DIM, YELLOW_BRIGHT, GOLD_GRADIENT),
    "shield": (GREEN_DIM, GREEN_BRIGHT, CYAN_GRADIENT),
    "detox": (BLUE_DIM, BLUE_BRIGHT, CYAN_GRADIENT),
    "craft": (GOLD_DIM, ORANGE, GOLD_GRADIENT),
    "genesis": (PURPLE_DIM, PURPLE, PURPLE_GRADIENT),
}


# ============================================================
# ⚡ 基础视觉特效引擎
# ============================================================


def _gradient_text(text: str, gradient: list[str]) -> str:
    """对文本逐字符应用渐变色"""
    result = []
    g_len = len(gradient)
    for i, ch in enumerate(text):
        color = gradient[min(i * g_len // max(len(text), 1), g_len - 1)]
        result.append(f"{color}{ch}")
    return "".join(result) + RESET


def _holographic_flicker(text: str, color: str, flickers: int = 3) -> None:
    """全息投影文字闪烁效果"""
    for _i in range(flickers):
        _write(f"{CLEAR_LINE}  {DIM}{color}{text}{RESET}")
        time.sleep(0.04)
        _write(f"{CLEAR_LINE}  {BOLD}{color}{text}{RESET}")
        time.sleep(0.06)
    _write(f"{CLEAR_LINE}")


def _particle_burst(width: int = 50, frames: int = 5, color: str = GOLD) -> None:
    """粒子爆炸效果"""
    particles = "·✦✧⁕⁑∗∘○◦◌◍◎●◉"
    for frame in range(frames):
        line = ""
        center = width // 2
        radius = (frame + 1) * 3
        for x in range(width):
            dist = abs(x - center)
            if dist <= radius and random.random() < (0.6 - frame * 0.1):
                p = random.choice(particles)
                brightness = color if dist < radius // 2 else DIM + color
                line += f"{brightness}{p}{RESET}"
            else:
                line += " "
        _write(f"  {line}\n")
        time.sleep(0.03)


def _data_stream_line(width: int, color: str = CYAN_DIM) -> str:
    """生成一行数据流装饰文字"""
    hex_chars = "0123456789ABCDEF"
    stream = ""
    for _ in range(width):
        if random.random() < 0.3:
            stream += f"{color}{random.choice(hex_chars)}"
        elif random.random() < 0.2:
            stream += f"{DARK_GRAY}·"
        else:
            stream += " "
    return stream + RESET


def _matrix_rain_short(width: int = 50, lines: int = 3) -> None:
    """短促矩阵雨效果"""
    chars = "01アイウエオカキ華佗望聞問切脈氣血藥方診炼丹魂环"
    for _ in range(lines):
        line = ""
        for _col in range(width):
            if random.random() < 0.12:
                c = random.choice(chars)
                brightness = random.choice([
                    CYAN_DIM, GREEN_DIM, GREEN_MATRIX,
                    CYAN, DARK_GRAY, GRAY,
                ])
                line += f"{brightness}{c}"
            else:
                line += f"{DARK_GRAY}·"
        _write(f"  {line}{RESET}\n")
        time.sleep(0.03)


def _radar_sweep(width: int = 40, sweeps: int = 1) -> None:
    """雷达扫描效果"""
    center = width // 2
    radius = width // 2 - 2

    for _sweep in range(sweeps):
        for angle_deg in range(0, 360, 15):
            angle = math.radians(angle_deg)
            line_chars = [" "] * width

            # 绘制圆周
            for a in range(0, 360, 5):
                r = math.radians(a)
                x = int(center + radius * math.cos(r) * 0.5)
                if 0 <= x < width:
                    line_chars[x] = f"{CYAN_DIM}·"

            # 绘制扫描线
            for r_len in range(1, radius):
                x = int(center + r_len * math.cos(angle) * 0.5)
                if 0 <= x < width:
                    intensity = r_len / radius
                    if intensity > 0.7:
                        line_chars[x] = f"{GREEN_BRIGHT}█"
                    elif intensity > 0.4:
                        line_chars[x] = f"{GREEN_MATRIX}▓"
                    else:
                        line_chars[x] = f"{GREEN_DIM}░"

            # 中心点
            line_chars[center] = f"{GREEN_BRIGHT}◉"

            _write(f"{CLEAR_LINE}  {''.join(line_chars)}{RESET}")
            time.sleep(0.02)

    _write(f"{CLEAR_LINE}")


def _energy_charge_bar(
    label: str,
    color: str,
    gradient: list[str],
    width: int = 30,
    duration: float = 0.5,
) -> None:
    """能量充能进度条（带渐变和脉冲效果）"""
    for i in range(width + 1):
        bar_parts = []
        for j in range(i):
            g_idx = min(j * len(gradient) // max(width, 1), len(gradient) - 1)
            bar_parts.append(f"{gradient[g_idx]}█")
        bar_str = "".join(bar_parts)
        empty = f"{DARK_GRAY}{'░' * (width - i)}"
        pct = int(i / width * 100)
        # 脉冲字符
        pulse = "▸" if i % 3 == 0 else "▹"
        _write(f"{CLEAR_LINE}  {GRAY}[{bar_str}{empty}{GRAY}]{RESET} "
               f"{color}{pct:3d}%{RESET} {color}{pulse}{RESET} {GRAY}{label}{RESET}")
        time.sleep(duration / width)
    _write(f"{CLEAR_LINE}  {GRAY}[{gradient[-1]}{'█' * width}{GRAY}]{RESET} "
           f"{GREEN_BRIGHT}100% ✓{RESET} {WHITE}{label}{RESET}\n")


# ============================================================
# 🔮 电影级魂环 ASCII Art 渲染器
# ============================================================


def _build_cinematic_ring_art(
    ring_count: int,
    ring_emojis: str,
) -> list[tuple[str, str]]:
    """
    构建电影级的魂环同心环 ASCII Art。

    使用数学圆方程绘制精确的同心圆，配合丰富的字符渐变和光晕效果。
    """
    if ring_count <= 0:
        return []

    # 解析环的颜色（dim, bright 两色）
    ring_chars = [c for c in ring_emojis if c in "⚪🟡🟣⚫🔴✨"]
    ring_palette = []
    for rc in ring_chars:
        dim_c, bright_c, _ = RING_COLORS.get(rc, (GRAY, WHITE, ""))
        ring_palette.append((dim_c, bright_c))

    # 核心参数
    base_radius = 3
    ring_gap = 2.0
    total_radius = base_radius + ring_count * ring_gap + 1
    canvas_h = int(total_radius * 2) + 1
    canvas_w = int(total_radius * 4) + 2  # 宽度加倍补偿终端字符宽高比

    center_y = total_radius
    center_x = total_radius * 2

    # 逐像素绘制
    lines = []
    for y in range(canvas_h):
        line = ""
        for x in range(canvas_w):
            dx = (x - center_x) / 2.0  # 补偿宽高比
            dy = y - center_y
            dist = math.sqrt(dx * dx + dy * dy)

            placed = False

            # 中心太极符号
            if dist < 1.2:
                line += f"{GOLD}{BOLD}☯{RESET}"
                placed = True
            elif dist < base_radius - 0.5:
                # 中心区域——微弱能量场
                if random.random() < 0.08:
                    line += f"{GOLD_DIM}·"
                else:
                    line += " "
                placed = True

            if not placed:
                # 检查每个环
                for ring_idx in range(ring_count):
                    ring_radius = base_radius + (ring_idx + 1) * ring_gap
                    ring_dist = abs(dist - ring_radius)

                    if ring_dist < 0.7:
                        dim_c, bright_c = ring_palette[min(ring_idx, len(ring_palette) - 1)]

                        # 根据距离选择字符和颜色
                        if ring_dist < 0.25:
                            # 环的核心 — 最亮
                            symbols = "█▓▓█"
                            line += f"{bright_c}{BOLD}{random.choice(symbols)}{RESET}"
                        elif ring_dist < 0.5:
                            # 环的边缘 — 中等亮度
                            symbols = "▓░▒"
                            line += f"{bright_c}{random.choice(symbols)}{RESET}"
                        else:
                            # 光晕区域
                            symbols = "░·"
                            line += f"{dim_c}{random.choice(symbols)}{RESET}"
                        placed = True
                        break

                    # 环间能量涟漪
                    if ring_idx < ring_count - 1:
                        next_radius = base_radius + (ring_idx + 2) * ring_gap
                        mid_point = (ring_radius + next_radius) / 2
                        if abs(dist - mid_point) < 0.3 and random.random() < 0.05:
                            line += f"{DARK_GRAY}∙"
                            placed = True
                            break

            if not placed:
                # 外围暗能量粒子
                if dist < total_radius and dist > total_radius - 2 and random.random() < 0.03:
                    line += f"{DARK_GRAY}·"
                else:
                    line += " "

        stripped = line.rstrip()
        if stripped.strip():
            lines.append((WHITE, stripped))

    return lines


def render_soul_rings(
    directions: list[dict],
    animate: bool = True,
) -> None:
    """
    渲染电影级魂环全息投影动画。

    Args:
        directions: get_alchemy_profile()["directions"] 返回的方向列表
        animate: 是否播放动画效果
    """
    if not _supports_color() or not directions:
        return

    width = min(_get_term_width(), 72)

    # ─── 序幕：矩阵雨 ───
    if animate:
        _matrix_rain_short(width - 4, lines=2)
        time.sleep(0.1)

    # ─── 标题（全息闪烁） ───
    title_text = "◆ 魂 环 全 息 投 影 · SOUL RING HOLOGRAM ◆"
    if animate:
        _holographic_flicker(title_text, PURPLE, flickers=3)
        time.sleep(0.08)

    _write(f"\n  {PURPLE}{BOLD}{title_text}{RESET}\n")
    _write(f"  {_gradient_text('━' * (width - 4), PURPLE_GRADIENT)}\n\n")

    for d in directions:
        ring_count = d.get("ring_count", 0)
        rings_emoji = d.get("rings", "")
        name_cn = d.get("name_cn", "")
        name_en = d.get("name_en", "")
        emoji = d.get("emoji", "")
        count = d.get("count", 0)
        dir_key = d.get("key", "")

        if ring_count <= 0:
            continue

        tier_info = RING_TIER_NAMES.get(ring_count, (f"{ring_count}环", f"{ring_count} Rings", ""))
        _, dir_bright, dir_grad = DIRECTION_PALETTES.get(dir_key, (CYAN_DIM, CYAN, CYAN_GRADIENT))

        # ── 方向标题（雷达扫描 → 揭示） ──
        if animate:
            _radar_sweep(width - 4, sweeps=1)
            _write("\n")

        # 方向名称：渐变显示
        dir_title = f"  {emoji} {name_cn}丹师 · {name_en} Alchemist"
        if animate:
            # 逐字渐现
            for i in range(len(dir_title)):
                partial = dir_title[:i+1]
                _write(f"{CLEAR_LINE}{dir_bright}{BOLD}{partial}{RESET}")
                time.sleep(0.01)
            _write("\n")
        else:
            _write(f"  {dir_bright}{BOLD}{dir_title}{RESET}\n")

        _write(f"  {GRAY}   贡献 {WHITE}{count}{GRAY} 方 │ {GOLD}{tier_info[0]}{GRAY} · {tier_info[1]}{RESET}\n")
        if tier_info[2]:
            _write(f"  {CYAN_DIM}   「{tier_info[2]}」{RESET}\n")
        _write("\n")

        # ── 充能动画 → 魂环绘制 ──
        if animate:
            _energy_charge_bar(
                label="魂环投影充能 · Ring Projection",
                color=dir_bright,
                gradient=dir_grad,
                width=28,
                duration=0.4,
            )
            time.sleep(0.1)
            _write("\n")

        # ── 绘制魂环 ASCII Art ──
        ring_art = _build_cinematic_ring_art(ring_count, rings_emoji)
        for _color, line in ring_art:
            if animate:
                time.sleep(0.008)
            _write(f"  {line}\n")

        # ── 粒子爆炸收尾 ──
        if animate:
            _particle_burst(width - 4, frames=3, color=dir_bright)

        # ── 环型标注面板 ──
        _write(f"\n  {GRAY}   ┌─ 魂环构成 ─────────────────────────┐{RESET}\n")
        ring_chars = [c for c in rings_emoji if c in "⚪🟡🟣⚫🔴✨"]
        if ring_chars:
            _write(f"  {GRAY}   │{RESET} {rings_emoji}                          {GRAY}│{RESET}\n")
            _write(f"  {GRAY}   │{RESET} ")
            for i, rc in enumerate(ring_chars):
                _, bright_c, label = RING_COLORS.get(rc, (GRAY, WHITE, ""))
                short_label = label.split("·")[0].strip()
                if animate:
                    time.sleep(0.03)
                _write(f"{bright_c}第{i+1}环:{short_label} ")
            _write(f"{GRAY}│{RESET}\n")
        _write(f"  {GRAY}   └──────────────────────────────────────┘{RESET}\n")

        _write(f"\n  {_gradient_text('─' * (width - 4), dir_grad)}\n\n")


def _get_direction_color(key: str) -> str:
    """获取丹术方向对应的终端颜色"""
    _, bright, _ = DIRECTION_PALETTES.get(key, (CYAN_DIM, CYAN, CYAN_GRADIENT))
    return bright


# ============================================================
# 🖥️ 电影级丹术方向 HUD 面板
# ============================================================


def render_alchemy_hud(
    directions: list[dict],
    username: str = "",
    animate: bool = True,
) -> None:
    """
    渲染电影级赛博朋克 HUD 仪表盘。
    """
    if not _supports_color() or not directions:
        return

    width = min(_get_term_width(), 68)
    inner = width - 6

    # ─── HUD 启动 ───
    if animate:
        _holographic_flicker("⚗️  HUD SYSTEM ONLINE", CYAN, flickers=2)
        _write("\n")

    # ─── 外框 ───
    top_border = _gradient_text("╔" + "═" * inner + "╗", CYAN_GRADIENT)
    bot_border = _gradient_text("╚" + "═" * inner + "╝", CYAN_GRADIENT)
    mid_border = _gradient_text("╠" + "═" * inner + "╣", CYAN_GRADIENT)

    _write(f"  {top_border}\n")

    # 标题区
    _write(f"  {CYAN}║{RESET} {GOLD}{BOLD}⚗️  丹 术 修 为 总 览{RESET}")
    _write(f"{' ' * max(0, inner - 22)}{CYAN}║{RESET}\n")
    _write(f"  {CYAN}║{RESET} {GRAY}ALCHEMY CULTIVATION OVERVIEW{RESET}")
    _write(f"{' ' * max(0, inner - 30)}{CYAN}║{RESET}\n")

    if username:
        user_line = f"@{username}"
        # 数据流背景装饰
        bg_stream = _data_stream_line(inner - len(user_line) - 4)
        _write(f"  {CYAN}║{RESET} {CYAN_BRIGHT}{user_line}{RESET} {bg_stream}{CYAN}║{RESET}\n")

    _write(f"  {mid_border}\n")

    if animate:
        time.sleep(0.15)

    # ─── 各方向进度条 ───
    max_count = max((d.get("count", 0) for d in directions), default=1)
    bar_width = inner - 34
    if bar_width < 12:
        bar_width = 12

    for d in directions:
        name_cn = d.get("name_cn", "")
        emoji = d.get("emoji", "")
        count = d.get("count", 0)
        rings = d.get("rings", "")
        dir_key = d.get("key", "")

        _, dir_bright, dir_grad = DIRECTION_PALETTES.get(dir_key, (CYAN_DIM, CYAN, CYAN_GRADIENT))

        # 渐变进度条
        ratio = count / max_count if max_count > 0 else 0
        filled = int(ratio * bar_width)
        empty = bar_width - filled

        bar_parts = []
        for j in range(filled):
            g_idx = min(j * len(dir_grad) // max(bar_width, 1), len(dir_grad) - 1)
            bar_parts.append(f"{dir_grad[g_idx]}█")
        bar_str = "".join(bar_parts)
        empty_str = f"{DARK_GRAY}{'░' * empty}"

        label = f"{emoji} {name_cn}"
        count_str = f"{count:>3}方"

        if animate:
            time.sleep(0.08)

        _write(f"  {CYAN}║{RESET} {dir_bright}{label:<7}{RESET} "
               f"{bar_str}{empty_str}{RESET} "
               f"{WHITE}{count_str}{RESET} {rings}\n")

    _write(f"  {bot_border}\n")


# ============================================================
# 📡 电影级排名全息扫描动画
# ============================================================


def animate_ranking_scan(
    username: str,
    profile: dict,
    animate: bool = True,
) -> None:
    """
    电影级排名查询全息扫描动画。
    """
    if not _supports_color():
        return

    width = min(_get_term_width(), 68)

    if animate:
        # ─── Phase 0: 矩阵雨序幕 ───
        _matrix_rain_short(width - 4, lines=3)
        time.sleep(0.1)

        # ─── Phase 1: 全息扫描协议 ───
        protocol_text = "⟨ 全息扫描协议启动 · HOLOGRAPHIC SCAN INITIATED ⟩"
        _holographic_flicker(protocol_text, CYAN_DIM, flickers=4)
        _write(f"\n  {CYAN}{BOLD}{protocol_text}{RESET}\n\n")
        time.sleep(0.15)

        # 目标锁定
        _write(f"  {GRAY}TARGET ▸ {RESET}")
        target_str = f"@{username}"
        for ch in target_str:
            _write(f"{CYAN_BRIGHT}{BOLD}{ch}{RESET}")
            time.sleep(0.03)
        _write("\n\n")

        # 扫描子系统（带四通道进度条）
        scan_channels = [
            ("神经网络连接", "NEURAL LINK", CYAN, CYAN_GRADIENT),
            ("修为数据索引", "CULTIVATION INDEX", PURPLE, PURPLE_GRADIENT),
            ("全球排名计算", "GLOBAL RANKING", GOLD, GOLD_GRADIENT),
            ("魂环投影校准", "SOUL RING CAL.", RED, RED_GRADIENT),
        ]

        for phase_cn, phase_en, color, grad in scan_channels:
            _energy_charge_bar(
                label=f"{phase_cn} · {phase_en}",
                color=color,
                gradient=grad,
                width=22,
                duration=0.25,
            )

        _write(f"\n  {_gradient_text('━' * (width - 4), CYAN_GRADIENT)}\n")
        time.sleep(0.15)

    # ─── Phase 2: 排名面板 ───
    title_emoji = profile.get("title_emoji", "🌱")
    title_cn = profile.get("title_cn", "实习药童")
    title_en = profile.get("title_en", "Intern")
    rank = profile.get("global_rank", 0)
    total = profile.get("global_total", 0)
    percentile = profile.get("percentile", 0.0)
    contribution_count = profile.get("contribution_count", 0)

    inner = width - 6

    # 双色渐变边框
    _write(f"\n  {_gradient_text('╔' + '═' * inner + '╗', CYAN_GRADIENT)}\n")

    _write(f"  {CYAN}║{RESET}  {_gradient_text('🌐 全 球 炼 丹 师 排 行', GOLD_GRADIENT)}")
    _write(f"{' ' * max(0, inner - 24)}{CYAN}║{RESET}\n")
    _write(f"  {CYAN}║{RESET}  {GRAY}GLOBAL ALCHEMIST RANKING{RESET}")
    _write(f"{' ' * max(0, inner - 26)}{CYAN}║{RESET}\n")
    _write(f"  {_gradient_text('╠' + '═' * inner + '╣', CYAN_GRADIENT)}\n")

    # 数据行（带微动画）
    data_rows = [
        ("炼丹师", f"{CYAN_BRIGHT}@{username}{RESET}"),
        ("修  为", f"{GOLD}{title_emoji} {title_cn} · {title_en}{RESET}"),
        ("印  痕", f"{CYAN_BRIGHT}{contribution_count}{WHITE} 段药方{RESET}"),
        ("排  位", f"{GOLD}#{rank}{WHITE} / {total}{RESET}"),
        ("超  越", f"{GREEN_BRIGHT}{percentile:.0f}%{WHITE} 炼丹师{RESET}"),
    ]

    for label, value in data_rows:
        if animate:
            time.sleep(0.06)
        # 数据流背景
        bg = _data_stream_line(max(0, inner - 28))
        _write(f"  {CYAN}║{RESET}  {WHITE}{label}  {value} {bg}{CYAN}║{RESET}\n")

    _write(f"  {_gradient_text('╚' + '═' * inner + '╝', CYAN_GRADIENT)}\n")


# ============================================================
# 🏆 电影级封神榜揭榜动画
# ============================================================


def animate_leaderboard(
    sorted_stats: list[tuple[str, int]],
    total: int,
    display_count: int,
    calculate_title_fn,
    animate: bool = True,
) -> None:
    """电影级封神榜逐行揭榜动画。"""
    if not _supports_color():
        _print_leaderboard_plain(sorted_stats, total, display_count, calculate_title_fn)
        return

    width = min(_get_term_width(), 72)
    inner = width - 6

    # ─── 序幕 ───
    if animate:
        _matrix_rain_short(width - 4, lines=2)
        time.sleep(0.1)

        summon_text = "⟨ 正在召唤封神榜 · SUMMONING APOTHEOSIS BOARD ⟩"
        _holographic_flicker(summon_text, GOLD_DIM, flickers=3)
        _write(f"\n  {GOLD}{BOLD}{summon_text}{RESET}\n\n")

        # 闪电暴风
        for _burst in range(3):
            bolt = "".join(random.choice("⚡✦✧") + " " * random.randint(0, 3)
                          for _ in range(random.randint(4, 10)))
            _write(f"  {GOLD}{BOLD}{bolt}{RESET}")
            time.sleep(0.04)
            _write(f"{CLEAR_LINE}")
        _write("\n")

        # 充能
        _energy_charge_bar("封神之力凝聚 · Apotheosis Charge", GOLD, GOLD_GRADIENT, 30, 0.5)
        _write("\n")

    # ─── 榜单 ───
    _write(f"  {_gradient_text('╔' + '═' * inner + '╗', GOLD_GRADIENT)}\n")
    _write(f"  {GOLD}║{RESET}  {_gradient_text('🏆 赛 博 华 佗 · 全 球 封 神 榜', GOLD_GRADIENT)}")
    _write(f"{' ' * max(0, inner - 32)}{GOLD}║{RESET}\n")
    _write(f"  {GOLD}║{RESET}  {GRAY}CYBERHUATUO · GLOBAL APOTHEOSIS BOARD{RESET}")
    _write(f"{' ' * max(0, inner - 39)}{GOLD}║{RESET}\n")
    _write(f"  {GOLD}║{RESET}  {WHITE}总注册医师: {CYAN_BRIGHT}{total}{WHITE} 人{RESET}")
    _write(f"{' ' * max(0, inner - 18)}{GOLD}║{RESET}\n")
    _write(f"  {_gradient_text('╠' + '═' * inner + '╣', GOLD_GRADIENT)}\n")

    # 表头
    _write(f"  {GOLD}║{RESET}  {GRAY}{'排位':<6} {'炼丹师':<16} {'称号':<16} {'药方':>6}{RESET}")
    _write(f"{' ' * max(0, inner - 48)}{GOLD}║{RESET}\n")
    _write(f"  {GOLD}╠{'─' * inner}╣{RESET}\n")

    if animate:
        time.sleep(0.15)

    # ─── 逐行揭榜 ───
    medals = {1: "👑", 2: "🥈", 3: "🥉"}

    for i in range(display_count):
        username, count = sorted_stats[i]
        rank = i + 1
        is_r1 = (rank == 1)

        pct = (100.0 if is_r1 else 0.0) if total <= 1 else round((total - rank) / (total - 1) * 100, 1)

        emoji, title_cn, _ = calculate_title_fn(pct, is_r1)
        medal = medals.get(rank, f"#{rank}")

        # 行色彩方案
        if rank == 1:
            row_color, _row_grad = GOLD, GOLD_GRADIENT
        elif rank == 2:
            row_color, _row_grad = WHITE, CYAN_GRADIENT
        elif rank == 3:
            row_color, _row_grad = ORANGE, GOLD_GRADIENT
        else:
            row_color, _row_grad = GRAY, CYAN_GRADIENT

        if animate:
            delay = 0.4 if rank <= 3 else 0.06
            time.sleep(delay)

            if rank <= 3:
                # 前三名——粒子爆炸 + 数据流背景
                _particle_burst(inner, frames=2, color=row_color)

        row_text = f"{medal:<6} @{username:<14} {emoji} {title_cn:<12} {count:>6}"

        if rank <= 3 and animate:
            _write(f"  {GOLD}║{RESET}  {row_color}{BOLD}{row_text}{RESET}")
        else:
            _write(f"  {GOLD}║{RESET}  {row_color}{row_text}{RESET}")

        _write(f"{' ' * max(0, 2)}{GOLD}║{RESET}\n")

    _write(f"  {_gradient_text('╚' + '═' * inner + '╝', GOLD_GRADIENT)}\n")


def _print_leaderboard_plain(sorted_stats, total, display_count, calculate_title_fn):
    """非 TTY 环境的纯文本封神榜"""
    print("\n🏆 赛博华佗 · 全球封神榜")
    print(f"总注册医师: {total} 人\n")
    print(f"{'排位':<6} {'炼丹师':<20} {'称号':<20} {'药方':>6}")
    print("-" * 55)

    medals = {1: "👑", 2: "🥈", 3: "🥉"}
    for i in range(display_count):
        username, count = sorted_stats[i]
        rank = i + 1
        is_r1 = (rank == 1)
        pct = (100.0 if is_r1 else 0.0) if total <= 1 else round((total - rank) / (total - 1) * 100, 1)
        emoji, title_cn, _ = calculate_title_fn(pct, is_r1)
        medal = medals.get(rank, f"#{rank}")
        print(f"{medal:<6} @{username:<18} {emoji} {title_cn:<14} {count:>6}")


# ============================================================
# 📋 电影级分享卡片生成动画
# ============================================================


def animate_card_generation(
    username: str,
    animate: bool = True,
) -> None:
    """电影级分享卡片生成动画。"""
    if not _supports_color() or not animate:
        return

    width = min(_get_term_width(), 68)

    # 矩阵雨序幕
    _matrix_rain_short(width - 4, lines=2)
    time.sleep(0.1)

    forge_text = "⟨ 正在铸造修为档案 · FORGING CULTIVATION ARCHIVE ⟩"
    _holographic_flicker(forge_text, CYAN_DIM, flickers=3)
    _write(f"\n  {CYAN}{BOLD}{forge_text}{RESET}\n\n")

    steps = [
        ("修为数据采集", "Gathering cultivation data", CYAN, CYAN_GRADIENT),
        ("魂环图谱生成", "Generating soul ring chart", PURPLE, PURPLE_GRADIENT),
        ("生命体征编码", "Encoding vital signs", RED, RED_GRADIENT),
        ("档案卡片渲染", "Rendering archive card", GOLD, GOLD_GRADIENT),
    ]

    for step_cn, step_en, color, grad in steps:
        _energy_charge_bar(
            label=f"{step_cn} · {step_en}",
            color=color,
            gradient=grad,
            width=24,
            duration=0.35,
        )

    # DNA 螺旋展示
    _write("\n")
    dna_frames = [
        f"  {CYAN}╔═══╗{RESET}   {PURPLE}╔═══╗{RESET}   {GOLD}╔═══╗{RESET}",
        f"  {CYAN}║╲ ╱║{RESET}   {PURPLE}║╲ ╱║{RESET}   {GOLD}║╲ ╱║{RESET}",
        f"  {CYAN}║ ╳ ║{RESET}   {PURPLE}║ ╳ ║{RESET}   {GOLD}║ ╳ ║{RESET}",
        f"  {CYAN}║╱ ╲║{RESET}   {PURPLE}║╱ ╲║{RESET}   {GOLD}║╱ ╲║{RESET}",
        f"  {CYAN}╚═══╝{RESET}   {PURPLE}╚═══╝{RESET}   {GOLD}╚═══╝{RESET}",
    ]
    for frame in dna_frames:
        _write(f"{frame}\n")
        time.sleep(0.04)

    _write(f"\n  {_gradient_text('✦ 修 为 档 案 已 铸 就 · Archive Forged ✦', GOLD_GRADIENT)}\n\n")
    time.sleep(0.1)


# ============================================================
# 🧪 演示预览
# ============================================================


def demo():
    """
    运行所有电影级科幻动画效果的演示预览。

    使用方式:
        python -c "from cyberhuatuo.cli_effects import demo; demo()"
    """
    if not _supports_color():
        print("终端不支持彩色输出，无法预览动画效果。")
        return

    _write(f"\n{_gradient_text('═══ CyberHuaTuo · Cinematic Effects Demo ═══', GOLD_GRADIENT)}\n")

    # ─── 1. 魂环演示 ───
    _write(f"\n{PURPLE}{BOLD}▸ 魂环全息投影演示{RESET}\n")
    demo_directions = [
        {
            "key": "soul", "emoji": "🔥", "name_cn": "炼魂",
            "name_en": "Soul Refining", "count": 15,
            "rings": "🟡🟡🟣🟣⚫", "ring_name": "五环", "ring_count": 5,
        },
        {
            "key": "thunder", "emoji": "⚡", "name_cn": "雷火",
            "name_en": "Thunder Fire", "count": 5,
            "rings": "🟡🟡🟣", "ring_name": "三环", "ring_count": 3,
        },
    ]
    render_soul_rings(demo_directions)

    # ─── 2. HUD 面板演示 ───
    _write(f"\n{PURPLE}{BOLD}▸ 丹术方向 HUD 面板演示{RESET}\n")
    render_alchemy_hud(demo_directions, username="DemoAlchemist")

    # ─── 3. 排名扫描演示 ───
    _write(f"\n{PURPLE}{BOLD}▸ 排名全息扫描演示{RESET}\n")
    demo_profile = {
        "title_emoji": "💜", "title_cn": "丹王", "title_en": "Pill King",
        "global_rank": 3, "global_total": 42, "percentile": 85.0,
        "contribution_count": 18, "is_rank_one": False,
    }
    animate_ranking_scan("DemoAlchemist", demo_profile)

    # ─── 4. 封神榜揭榜演示 ───
    _write(f"\n{PURPLE}{BOLD}▸ 封神榜揭榜演示{RESET}\n")
    demo_stats = [
        ("AlchemistKing", 42),
        ("PillMaster", 35),
        ("CodeHealer", 28),
        ("BugSlayer", 15),
        ("DebugDragon", 8),
    ]

    def _demo_title(pct, is_r1):
        if is_r1:
            return "🩺", "华佗再世", "Hua Tuo Reborn"
        if pct >= 85:
            return "💜", "丹王", "Pill King"
        if pct >= 50:
            return "🌟", "六星炼丹师", "Six-Star"
        return "⭐", "一星炼丹师", "One-Star"

    animate_leaderboard(demo_stats, 5, 5, _demo_title)

    # ─── 5. 卡片生成演示 ───
    _write(f"\n{PURPLE}{BOLD}▸ 分享卡片生成演示{RESET}\n")
    animate_card_generation("DemoAlchemist")

    _write(f"\n{_gradient_text('═══ Cinematic Demo Complete ═══', GOLD_GRADIENT)}\n\n")


if __name__ == "__main__":
    demo()
