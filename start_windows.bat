@echo off
chcp 65001 >nul
echo ========================================
echo 🎮 游戏自动化工具 - Windows启动器
echo ========================================

:: 检查Python是否存在
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 💡 请先安装Python 3.11+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "venv\" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

:: 添加项目根目录到Python路径
set PYTHONPATH=%~dp0;%PYTHONPATH%

:: 检查并安装依赖
echo 📋 检查依赖...
python -c "import sys; sys.path.insert(0, '.'); from src.main import check_dependencies; deps = check_dependencies(); print('✅ 依赖检查完成' if not deps['missing'] else f'❌ 缺少依赖: {deps[\"missing\"]}')"

if %errorlevel% neq 0 (
    echo 💾 安装缺少的依赖...
    pip install PyQt6 pywin32 psutil GPUtil mss keyboard mouse torch pyautogui jedi black isort yapf pyqtgraph
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

:: 启动应用
echo 🚀 启动游戏自动化工具...
python -m src.main %*

:: 保持窗口打开（如果有错误）
if %errorlevel% neq 0 (
    echo ❌ 程序异常退出
    pause
) 