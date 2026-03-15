"""魂环全息投影 + 排名扫描 — 录制入口"""
import json
import sys
import time

# 录制为 asciicast v2 格式
events = []
start_time = time.time()


class TimestampWriter:
    def __init__(self, original):
        self.original = original

    def write(self, text):
        if text:
            elapsed = time.time() - start_time
            events.append((elapsed, text))
            self.original.write(text)
            self.original.flush()
        return len(text) if text else 0

    def flush(self):
        self.original.flush()

    def isatty(self):
        return True


old_stdout = sys.stdout
old_stderr = sys.stderr
capture = TimestampWriter(old_stderr)
sys.stdout = capture
sys.stderr = capture

try:
    from cyberhuatuo.cli_effects import (
        animate_ranking_scan,
        render_soul_rings,
    )

    # 模拟一个高级炼丹师的魂环展示
    demo_directions = [
        {
            "key": "soul", "emoji": "🔥", "name_cn": "炼魂",
            "name_en": "Soul Refining", "count": 15,
            "rings": "🟡🟡🟣🟣⚫", "ring_name": "五环", "ring_count": 5,
        },
        {
            "key": "thunder", "emoji": "⚡", "name_cn": "雷火",
            "name_en": "Thunder Fire", "count": 8,
            "rings": "🟡🟡🟣", "ring_name": "三环", "ring_count": 3,
        },
    ]
    render_soul_rings(demo_directions)

    # 排名全息扫描
    demo_profile = {
        "title_emoji": "💜", "title_cn": "丹王", "title_en": "Pill King",
        "global_rank": 3, "global_total": 42, "percentile": 85.0,
        "contribution_count": 18, "is_rank_one": False,
    }
    animate_ranking_scan("DemoAlchemist", demo_profile)

except KeyboardInterrupt:
    pass
finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr

total_duration = time.time() - start_time

header = {
    "version": 2,
    "width": 120,
    "height": 50,
    "timestamp": int(start_time),
    "duration": total_duration,
    "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    "title": "CyberHuaTuo Soul Ring Hologram",
}

output_path = "assets/cli_soul_ring.cast"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(header) + "\n")
    for elapsed, text in events:
        event = [round(elapsed, 6), "o", text]
        f.write(json.dumps(event) + "\n")

print(f"\n✅ 魂环动画录制完成: {output_path}")
print(f"   时长: {total_duration:.1f}s, 事件数: {len(events)}")
