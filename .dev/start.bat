@echo off
:: 设置中文编码支持
chcp 65001 >nul
title 游戏自动操作工具
echo 正在启动游戏自动操作工具...

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python 3.8或更高版本
    echo 可以从 https://www.python.org/downloads/ 下载
    pause
    exit /b 1
)

:: 检查Python版本
python -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)"
if %errorlevel% neq 0 (
    echo Python版本过低，请安装Python 3.8或更高版本
    pause
    exit /b 1
)

:: 运行启动脚本
python ..\scripts\run_in_venv.py %*

if %errorlevel% neq 0 (
    echo 程序启动失败
    pause
)