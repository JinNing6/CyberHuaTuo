"""
CyberHuaTuo 测试 — 共享 fixtures
"""

import sys
from pathlib import Path

import pytest

# 确保项目根目录在 Python 路径中
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))
