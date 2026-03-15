"""启动动画录制入口 — stdout 版本"""
import sys

# 重定向 stderr 到 stdout，确保 VHS 能捕获所有输出
sys.stderr = sys.stdout

from cyberhuatuo.banner import play_boot_animation

play_boot_animation(case_count=42, framework_count=50)
