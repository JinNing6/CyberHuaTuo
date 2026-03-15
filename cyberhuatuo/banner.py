"""
🩺 赛博华佗 · 命令行启动动画
CyberHuaTuo CLI Boot Animation

融合赛博朋克美学与华佗救死扶伤精神的终端启动序列。
"""

import random
import shutil
import sys
import time

# ============================================================
# 🎨 色彩常量 (ANSI 256-color / True Color)
# ============================================================

# 赛博青色系
CYAN = "\033[38;2;0;255;200m"
CYAN_DIM = "\033[38;2;0;180;140m"
CYAN_BRIGHT = "\033[38;2;100;255;230m"
# 赛博紫色系
PURPLE = "\033[38;2;180;80;255m"
PURPLE_DIM = "\033[38;2;120;50;180m"
# 金色 (华佗经典)
GOLD = "\033[38;2;255;200;50m"
GOLD_DIM = "\033[38;2;200;160;40m"
# 红色 (心跳/生命)
RED = "\033[38;2;255;60;80m"
RED_DIM = "\033[38;2;180;40;50m"
# 白色 / 灰色
WHITE = "\033[38;2;230;230;240m"
GRAY = "\033[38;2;100;110;120m"
DARK_GRAY = "\033[38;2;50;55;60m"
# 格式
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CLEAR_LINE = "\033[2K\r"

# ============================================================
# 🔤 赛博华佗 ASCII Art
# ============================================================

BANNER_ART = f"""{CYAN}
    ╔══════════════════════════════════════════════════════════════╗
    ║{CYAN_BRIGHT}  ██████╗██╗   ██╗██████╗ ███████╗██████╗                    {CYAN}║
    ║{CYAN_BRIGHT}  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗                   {CYAN}║
    ║{CYAN_BRIGHT}  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝                   {CYAN}║
    ║{CYAN_BRIGHT}  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗                   {CYAN}║
    ║{CYAN_BRIGHT}  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║                   {CYAN}║
    ║{CYAN_BRIGHT}   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝                   {CYAN}║
    ║{GOLD}  ██╗  ██╗██╗   ██╗ █████╗ ████████╗██╗   ██╗ ██████╗       {CYAN}║
    ║{GOLD}  ██║  ██║██║   ██║██╔══██╗╚══██╔══╝██║   ██║██╔═══██╗      {CYAN}║
    ║{GOLD}  ███████║██║   ██║███████║   ██║   ██║   ██║██║   ██║      {CYAN}║
    ║{GOLD}  ██╔══██║██║   ██║██╔══██║   ██║   ██║   ██║██║   ██║      {CYAN}║
    ║{GOLD}  ██║  ██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚██████╔╝      {CYAN}║
    ║{GOLD}  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝       {CYAN}║
    ╚══════════════════════════════════════════════════════════════╝{RESET}
"""

# ============================================================
# 🩺 DNA / 经络 装饰
# ============================================================

DNA_HELIX_FRAMES = [
    "  ╔═══╗   ╔═══╗   ╔═══╗",
    "  ║╲ ╱║   ║╲ ╱║   ║╲ ╱║",
    "  ║ ╳ ║   ║ ╳ ║   ║ ╳ ║",
    "  ║╱ ╲║   ║╱ ╲║   ║╱ ╲║",
    "  ╚═══╝   ╚═══╝   ╚═══╝",
]

HEARTBEAT_FRAMES = [
    "  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    "  ░░░░░░░░░░░░░▓░░░░░░░░░░░░░░░░░░",
    "  ░░░░░░░░░░░░▓█▓░░░░░░░░░░░░░░░░░",
    "  ░░░░░░░░░░░▓███▓░░░░░░░░░░░░░░░░",
    "  ░░░░░░░░░░▓█████▓░░░░░░░░░░░░░░░",
    "  ░░░░░░░░░▓█▓░░▓██▓░░░░░░░░░░░░░░",
    "  ░░░░░░░░▓█▓░░░░▓██▓░░░░░░░░░░░░░",
    "  ░░░░░░░▓█▓░░░░░░░█▓░░░░░░░░░░░░░",
    "  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
]


# ============================================================
# ⚡ 动画函数
# ============================================================


def _supports_color() -> bool:
    """检测终端是否支持彩色输出"""
    return not (not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty())


def _get_term_width() -> int:
    """获取终端宽度"""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def _write(text: str) -> None:
    """写入并刷新"""
    sys.stderr.write(text)
    sys.stderr.flush()


def _type_text(text: str, color: str = WHITE, delay: float = 0.02) -> None:
    """逐字打印效果"""
    for char in text:
        _write(f"{color}{char}{RESET}")
        if char not in (" ", "\n"):
            time.sleep(delay)
    _write("\n")


def _progress_bar(label: str, color: str = CYAN, duration: float = 0.6, width: int = 30) -> None:
    """带脉冲效果的进度条"""
    for i in range(width + 1):
        filled = "█" * i
        empty = "░" * (width - i)
        percent = int(i / width * 100)
        _write(f"{CLEAR_LINE}  {GRAY}[{color}{filled}{DARK_GRAY}{empty}{GRAY}]{WHITE} {percent:3d}% {GRAY}{label}{RESET}")
        time.sleep(duration / width)
    _write(f"{CLEAR_LINE}  {GRAY}[{color}{'█' * width}{GRAY}]{WHITE} 100% {CYAN}✓ {label}{RESET}\n")


def _matrix_rain(lines: int = 4, duration: float = 0.8) -> None:
    """Matrix 风格数字雨"""
    width = min(_get_term_width(), 64)
    chars = "01アイウエオカキクケコサシスセソ華佗望聞問切脈氣血經絡穴藥方診"
    steps = int(duration / 0.05)

    for _ in range(steps):
        line = ""
        for _col in range(width):
            if random.random() < 0.15:
                c = random.choice(chars)
                brightness = random.choice([CYAN_DIM, CYAN, CYAN_BRIGHT, GOLD_DIM])
                line += f"{brightness}{c}"
            else:
                line += f"{DARK_GRAY}·"
        _write(f"  {line}{RESET}\n")
        time.sleep(0.05)


def _heartbeat_pulse(beats: int = 3) -> None:
    """心电图脉冲动画"""
    ecg_patterns = [
        "─", "─", "─", "╲", "╱", "─", "─", "╲", "╱", "▲",
        "█", "▼", "╲", "╱", "─", "─", "─", "─", "─", "─",
    ]
    for _ in range(beats):
        line = "  "
        for _i, p in enumerate(ecg_patterns):
            if p in ("▲", "█"):
                line += f"{RED}{BOLD}{p}{RESET}"
            elif p in ("▼",):
                line += f"{RED_DIM}{p}{RESET}"
            elif p in ("╲", "╱"):
                line += f"{CYAN_DIM}{p}{RESET}"
            else:
                line += f"{GRAY}{p}{RESET}"
            _write(f"{CLEAR_LINE}{line}")
            time.sleep(0.04)
        _write("\n")
        time.sleep(0.1)


def _boot_subsystem(name: str, name_cn: str, icon: str, delay: float = 0.15) -> None:
    """单个子系统启动行"""
    _write(f"  {GRAY}├─ {icon} {CYAN}{name:<28}{RESET}")
    time.sleep(delay)
    _write(f" {GOLD}⟫ {WHITE}{name_cn}{RESET}")
    time.sleep(delay * 0.5)
    _write(f"  {CYAN_BRIGHT}[ONLINE]{RESET}\n")
    time.sleep(0.05)


# ============================================================
# 🚀 主动画序列
# ============================================================


def play_boot_animation(
    case_count: int = 0,
    framework_count: int = 0,
    transport: str = "stdio",
) -> None:
    """
    播放赛博华佗 MCP Server 启动动画

    Args:
        case_count: 知识库病例数量
        framework_count: 支持的框架数量
        transport: 传输协议 (stdio/streamable-http)
    """
    if not _supports_color():
        # 无颜色支持时简洁输出
        _write("🩺 CyberHuaTuo MCP Server — Ready\n")
        return

    try:
        _play_full_boot(case_count, framework_count, transport)
    except KeyboardInterrupt:
        _write(f"\n{RESET}")


def _play_full_boot(
    case_count: int,
    framework_count: int,
    transport: str,
) -> None:
    """完整启动动画序列"""

    width = min(_get_term_width(), 66)

    # ─── Phase 0: 清屏 + 数字雨前奏 ───
    _write("\n")
    _matrix_rain(lines=3, duration=0.5)

    # ─── Phase 1: 主 Banner ───
    _write(BANNER_ART)
    time.sleep(0.3)

    # ─── Phase 2: 标语 ───
    tagline_cn = "望 闻 问 切 ， 药 到 病 除 。"
    tagline_en = "Diagnose. Prescribe. Cure."
    center_pad = " " * max(0, (width - len(tagline_cn)) // 4)

    _write(f"\n{center_pad}")
    _type_text(tagline_cn, color=GOLD, delay=0.04)
    _write(f"{center_pad}")
    _type_text(tagline_en, color=GRAY, delay=0.02)

    # ─── Phase 3: 心电图脉冲 ───
    _write("\n")
    _heartbeat_pulse(beats=2)
    _write("\n")

    # ─── Phase 4: 系统启动序列 ───
    _write(f"  {PURPLE}{BOLD}◆ 诊断系统初始化 · DIAGNOSTIC SYSTEMS INITIALIZING{RESET}\n")
    _write(f"  {GRAY}{'─' * (width - 4)}{RESET}\n")
    time.sleep(0.2)

    # 子系统启动
    _boot_subsystem("Meridian Neural Network", "经络神经网络", "🧠")
    _boot_subsystem("Pulse Vector Engine", "脉象向量引擎", "💉")
    _boot_subsystem("Herb Knowledge Graph", "本草知识图谱", "🌿")
    _boot_subsystem("Qi Flow Analyzer", "气血流量分析", "🔬")
    _boot_subsystem("Prescription Generator", "药方生成器", "💊")
    _boot_subsystem("Six Meridian Security", "六经脉安全防护", "🛡️")

    _write(f"  {GRAY}{'─' * (width - 4)}{RESET}\n\n")

    # ─── Phase 5: 知识库加载进度条 ───
    _progress_bar("知识库索引构建 · Building Knowledge Index", CYAN, 0.8)
    if framework_count:
        _progress_bar(f"框架文档扫描 · {framework_count} Frameworks", PURPLE, 0.4)
    _write("\n")

    # ─── Phase 6: 状态面板 ───
    _write(f"  {CYAN}╭─────────────────────────────────────────────╮{RESET}\n")
    _write(f"  {CYAN}│{RESET}  {GOLD}⚡{WHITE} 赛博华佗 MCP Server         {CYAN_BRIGHT}[ACTIVATED]{RESET} {CYAN}│{RESET}\n")
    _write(f"  {CYAN}├─────────────────────────────────────────────┤{RESET}\n")

    if case_count:
        _write(f"  {CYAN}│{RESET}  {GRAY}📦 知识库病例  {WHITE}{case_count:>5} cases{GRAY}              {CYAN}│{RESET}\n")
    if framework_count:
        _write(f"  {CYAN}│{RESET}  {GRAY}🔧 覆盖框架    {WHITE}{framework_count:>5} frameworks{GRAY}          {CYAN}│{RESET}\n")

    transport_display = "🔌 STDIO (本地管道)" if transport == "stdio" else "🌐 HTTP (远程直连)"
    _write(f"  {CYAN}│{RESET}  {GRAY}📡 传输协议    {WHITE}{transport_display}{GRAY}      {CYAN}│{RESET}\n")
    _write(f"  {CYAN}╰─────────────────────────────────────────────╯{RESET}\n")

    # ─── Phase 7: 就绪宣言 ───
    _write("\n")
    _write(f"  {CYAN_BRIGHT}{BOLD}「 悬 壶 济 世 · 普 度 苍 生 」{RESET}\n")
    _write(f"  {GRAY}   Healing the Digital World, One Bug at a Time.{RESET}\n")
    _write(f"\n  {GOLD}⚕{RESET} {WHITE}赛博华佗已就绪，等待望闻问切 ...{RESET}\n")
    _write(f"  {GRAY}  CyberHuaTuo is ready. Awaiting diagnosis requests ...{RESET}\n\n")


# ============================================================
# 🧪 直接运行预览
# ============================================================


if __name__ == "__main__":
    play_boot_animation(case_count=42, framework_count=50, transport="stdio")
