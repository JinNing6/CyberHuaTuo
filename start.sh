#!/bin/bash
# CyberHuaTuo 赛博华佗 — 一键启动脚本 (macOS/Linux)

echo ""
echo "  🩺 CyberHuaTuo 赛博华佗"
echo "  ========================================"
echo "  望闻问切，药到病除。"
echo "  Diagnose. Prescribe. Cure."
echo "  ========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查依赖
python3 -c "import fastapi, chromadb" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 首次运行，正在安装依赖..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
    echo ""
fi

echo "🚀 启动中..."
cd "$SCRIPT_DIR"
python3 -m cyberhuatuo serve
