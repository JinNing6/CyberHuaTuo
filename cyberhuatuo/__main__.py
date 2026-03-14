"""
CyberHuaTuo CLI 入口
python -m cyberhuatuo [command]

支持两种模式：
  · CLI 模式：python -m cyberhuatuo diagnose "你的报错"
  · MCP 模式：python -m cyberhuatuo.mcp_server（或 cyberhuatuo-mcp）
"""

from .cli import main

if __name__ == "__main__":
    main()
