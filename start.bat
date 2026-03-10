@echo off
chcp 65001 >nul 2>&1
title CyberHuaTuo 赛博华佗

echo.
echo  🩺 CyberHuaTuo 赛博华佗
echo  ========================================
echo  望闻问切，药到病除。
echo  Diagnose. Prescribe. Cure.
echo  ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.9+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖是否安装
python -c "import fastapi, chromadb" >nul 2>&1
if errorlevel 1 (
    echo 📦 首次运行，正在安装依赖...
    pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
    echo.
)

:: 启动服务（自动打开浏览器）
echo 🚀 启动中...
python -m cyberhuatuo serve

pause
