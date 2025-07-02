@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ================================================
:: 游戏自动化工具 - 智能启动器 v2.0
:: 功能: 自动管理Python环境，支持便携式安装
:: ================================================

echo.
echo ========================================
echo 🎮 游戏自动化工具 - Windows启动器 v2.0
echo ========================================
echo.

:: 设置项目路径
set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "PYTHON_PORTABLE=%PROJECT_ROOT%\python_portable\python.exe"
set "PYTHON_SETUP=%PROJECT_ROOT%\python_setup\setup_python.bat"
set "VENV_DIR=%PROJECT_ROOT%\venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

:: Python检测和安装
call :DetectPython
call :EnsureVirtualEnv
call :CheckDependencies
call :StartApplication

goto :EOF

:: ================================================
:: 函数: 检测Python环境
:: ================================================
:DetectPython
echo 🔍 检测Python环境...

:: 检查项目内便携式Python
if exist "%PYTHON_PORTABLE%" (
    echo ✅ 发现项目内便携式Python
    "%PYTHON_PORTABLE%" --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 便携式Python正常工作
        set "PYTHON_EXE=%PYTHON_PORTABLE%"
        goto :EOF
    ) else (
        echo ⚠️ 便携式Python可能已损坏
    )
)

:: 检查系统Python (多种可能的路径)
echo 🔍 检查系统Python...
set "SYSTEM_PYTHON_FOUND=0"

:: 尝试常见的Python命令
for %%i in (python py python3) do (
    %%i --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 找到系统Python: %%i
        set "PYTHON_EXE=%%i"
        set "SYSTEM_PYTHON_FOUND=1"
        goto :CheckPythonVersion
    )
)

:: 尝试常见安装路径
set "PYTHON_PATHS=C:\Python311\python.exe;C:\Python39\python.exe;%LOCALAPPDATA%\Programs\Python\Python311\python.exe;%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        "%%p" --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ 找到系统Python: %%p
            set "PYTHON_EXE=%%p"
            set "SYSTEM_PYTHON_FOUND=1"
            goto :CheckPythonVersion
        )
    )
)

:CheckPythonVersion
if %SYSTEM_PYTHON_FOUND% equ 1 (
    :: 检查Python版本
    for /f "tokens=2" %%v in ('"%PYTHON_EXE%" --version 2^>^&1') do (
        set "PYTHON_VERSION=%%v"
    )
    echo 📋 Python版本: !PYTHON_VERSION!
    
    :: 检查版本是否满足要求 (3.8+)
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        if %%a geq 3 (
            if %%b geq 8 (
                echo ✅ Python版本满足要求
                goto :EOF
            )
        )
    )
    echo ⚠️ Python版本过低，需要Python 3.8+
)

:: 没有找到合适的Python，提示安装
echo.
echo ❌ 未找到合适的Python环境！
echo.
echo 🤔 您希望如何解决这个问题？
echo    [1] 自动安装便携式Python （推荐）
echo    [2] 手动安装Python
echo    [3] 退出
echo.
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" goto :InstallPortablePython
if "%choice%"=="2" goto :ManualInstallGuide
if "%choice%"=="3" goto :ExitScript

echo ❌ 无效选择，默认进行自动安装...

:InstallPortablePython
echo.
echo 🚀 开始自动安装便携式Python...
if exist "%PYTHON_SETUP%" (
    call "%PYTHON_SETUP%"
    if !errorlevel! equ 0 (
        echo ✅ Python安装完成，重新检测...
        if exist "%PYTHON_PORTABLE%" (
            set "PYTHON_EXE=%PYTHON_PORTABLE%"
            goto :EOF
        )
    )
    echo ❌ 自动安装失败，请手动安装
    goto :ManualInstallGuide
) else (
    echo ❌ 安装脚本不存在: %PYTHON_SETUP%
    goto :ManualInstallGuide
)

:ManualInstallGuide
echo.
echo 📖 手动安装指南:
echo ================================
echo 1. 访问 https://www.python.org/downloads/
echo 2. 下载 Python 3.11+ for Windows
echo 3. 安装时勾选 "Add Python to PATH"
echo 4. 重新运行此脚本
echo.
pause
goto :ExitScript

:ExitScript
echo.
echo 👋 感谢使用游戏自动化工具！
pause
exit /b 1

:: ================================================
:: 函数: 确保虚拟环境
:: ================================================
:EnsureVirtualEnv
echo.
echo 🌟 检查虚拟环境...

:: 检查现有虚拟环境
if exist "%VENV_PYTHON%" (
    echo 📦 发现现有虚拟环境，验证完整性...
    "%VENV_PYTHON%" --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 虚拟环境正常工作
        set "ACTIVE_PYTHON=%VENV_PYTHON%"
        goto :EOF
    ) else (
        echo ⚠️ 虚拟环境已损坏，重新创建...
        rmdir /s /q "%VENV_DIR%" 2>nul
    )
)

:: 创建虚拟环境
echo 🔨 创建项目虚拟环境...
if not defined PYTHON_EXE (
    echo ❌ 未找到Python可执行文件
    goto :ExitScript
)

"%PYTHON_EXE%" -m venv "%VENV_DIR%"
if !errorlevel! neq 0 (
    echo ❌ 虚拟环境创建失败
    echo 💡 尝试升级Python或检查权限
    pause
    goto :ExitScript
)

:: 验证虚拟环境
if exist "%VENV_PYTHON%" (
    echo ✅ 虚拟环境创建成功
    set "ACTIVE_PYTHON=%VENV_PYTHON%"
) else (
    echo ❌ 虚拟环境验证失败
    pause
    goto :ExitScript
)

goto :EOF

:: ================================================
:: 函数: 检查依赖
:: ================================================
:CheckDependencies
echo.
echo 📋 检查项目依赖...

:: 设置环境变量
set "PYTHONPATH=%PROJECT_ROOT%\src;%PROJECT_ROOT%;%PYTHONPATH%"

:: 激活虚拟环境（设置PATH）
set "PATH=%VENV_DIR%\Scripts;%PATH%"

:: 升级pip
echo 📦 升级pip...
"%ACTIVE_PYTHON%" -m pip install --upgrade pip --quiet --no-warn-script-location

:: 检查依赖
echo 🔍 检查依赖完整性...
"%ACTIVE_PYTHON%" -c "import sys; sys.path.insert(0, '.'); from src.main import check_dependencies; deps = check_dependencies(); print('依赖检查完成' if not deps['missing'] else 'Missing dependencies: ' + str(deps['missing'])); exit(0 if not deps['missing'] else 1)" 2>nul

if !errorlevel! neq 0 (
    echo.
    echo 💾 安装缺少的依赖...
    echo 📦 正在安装必需的包，请稍候...
    
    :: 安装核心依赖
    "%ACTIVE_PYTHON%" -m pip install PyQt6 pywin32 psutil GPUtil mss keyboard mouse torch pyautogui jedi black isort yapf pyqtgraph --quiet --no-warn-script-location
    
    if !errorlevel! neq 0 (
        echo ❌ 依赖安装失败
        echo.
        echo 故障排除建议:
        echo    1. 检查网络连接
        echo    2. 尝试使用国内pip镜像源
        echo    3. 检查磁盘空间
        echo.
        pause
        goto :ExitScript
    )
    
    echo ✅ 依赖安装完成
) else (
    echo ✅ 所有依赖已满足
)

goto :EOF

:: ================================================
:: 函数: 启动应用程序
:: ================================================
:StartApplication
echo.
echo 🚀 启动游戏自动化工具...
echo ================================
echo 📊 运行环境信息:

:: 显示Python信息
"%ACTIVE_PYTHON%" --version
echo    Python路径: %ACTIVE_PYTHON%
echo    项目路径: %PROJECT_ROOT%
echo    虚拟环境: %VENV_DIR%
echo.

:: 启动主程序
echo 正在启动主程序...
"%ACTIVE_PYTHON%" -m src.main %*

:: 检查退出码
set "EXIT_CODE=!errorlevel!"
if !EXIT_CODE! neq 0 (
    echo.
    echo ❌ 程序异常退出 (退出码: !EXIT_CODE!)
    echo.
    echo 故障排除建议:
    echo    1. 检查是否有其他实例在运行
    echo    2. 检查防火墙和安全软件设置  
    echo    3. 查看错误日志获取详细信息
    echo    4. 尝试以管理员身份运行
    echo.
    pause
) else (
    echo.
    echo ✅ 程序正常退出
)

exit /b !EXIT_CODE! 