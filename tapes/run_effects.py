"""电影级特效 demo 录制入口 — stdout 版本"""
import sys

# 重定向 stderr 到 stdout，确保 VHS 能捕获所有输出
sys.stderr = sys.stdout

from cyberhuatuo.cli_effects import demo

demo()
