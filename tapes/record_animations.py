"""
终端动画 → asciicast → GIF 录制器
Recording terminal animations as asciicast v2 format for GIF conversion.

用法:
    python tapes/record_animations.py boot     # 录制启动动画
    python tapes/record_animations.py effects  # 录制电影级特效
    python tapes/record_animations.py all      # 录制全部
"""

import io
import json
import sys
import time


def record_to_asciicast(output_path: str, func, width: int = 120, height: int = 40):
    """
    捕获函数的 stderr/stdout 输出并写为 asciicast v2 格式。

    asciicast v2 格式:
    - 第一行: JSON header
    - 后续行: [time, "o", data] 事件
    """
    events = []
    start_time = time.time()

    # 创建一个自定义的写入器来捕获输出和时间戳
    class TimestampWriter:
        def __init__(self, original):
            self.original = original

        def write(self, text):
            if text:
                elapsed = time.time() - start_time
                events.append((elapsed, text))
                # 也输出到真实终端以展示进度
                self.original.write(text)
                self.original.flush()
            return len(text) if text else 0

        def flush(self):
            self.original.flush()

        def isatty(self):
            return True  # 欺骗 _supports_color() 检查

    # 替换 stdout 和 stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    capture_out = TimestampWriter(old_stderr)  # 输出到原始 stderr 以展示进度
    sys.stdout = capture_out
    sys.stderr = capture_out

    try:
        func()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    total_duration = time.time() - start_time

    # 写入 asciicast v2 文件
    header = {
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(start_time),
        "duration": total_duration,
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
        "title": "CyberHuaTuo Terminal Animation",
    }

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for elapsed, text in events:
            event = [round(elapsed, 6), "o", text]
            f.write(json.dumps(event) + "\n")

    print(f"\n✅ 录制完成: {output_path}")
    print(f"   时长: {total_duration:.1f}s, 事件数: {len(events)}")


def record_boot():
    """录制启动动画"""
    from cyberhuatuo.banner import play_boot_animation

    print("🎬 正在录制启动动画...")
    record_to_asciicast(
        "assets/cli_boot_animation.cast",
        lambda: play_boot_animation(case_count=42, framework_count=50),
    )


def record_effects():
    """录制电影级特效"""
    from cyberhuatuo.cli_effects import demo

    print("🎬 正在录制电影级特效...")
    record_to_asciicast(
        "assets/cli_cinematic_effects.cast",
        demo,
        width=120,
        height=50,
    )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ("boot", "all"):
        record_boot()

    if target in ("effects", "all"):
        record_effects()

    if target == "all":
        print("\n🎉 全部录制完成！")
        print("下一步: 使用 agg 将 .cast 转为 .gif")
        print("  agg assets/cli_boot_animation.cast assets/cli_boot_animation.gif")
        print("  agg assets/cli_cinematic_effects.cast assets/cli_cinematic_effects.gif")
