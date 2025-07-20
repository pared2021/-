@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ================================================
:: Python便携版环境安装脚本
:: 版本: 1.0
:: 功能: 自动检测系统架构并安装Python便携版
:: ================================================

echo.
echo ========================================
echo 🐍 Python便携版环境安装器
echo ========================================
echo.

:: 设置变量
set "PYTHON_VERSION=3.11.9"
set "PROJECT_ROOT=%~dp0.."
set "PYTHON_PORTABLE_DIR=%PROJECT_ROOT%\python_portable"
set "DOWNLOAD_DIR=%PROJECT_ROOT%\python_setup"
set "TEMP_ZIP=%DOWNLOAD_DIR%\python_portable.zip"

:: 检测系统架构
echo 🔍 检测系统架构...
set "ARCH=x64"
if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    if not defined PROCESSOR_ARCHITEW6432 (
        set "ARCH=x86"
    )
)
echo ✅ 检测到系统架构: %ARCH%

:: 设置下载文件名
if "%ARCH%"=="x64" (
    set "PYTHON_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip"
) else (
    set "PYTHON_ZIP=python-%PYTHON_VERSION%-embed-win32.zip"
)

echo 📋 安装信息:
echo    - Python版本: %PYTHON_VERSION%
echo    - 系统架构: %ARCH%
echo    - 安装目录: %PYTHON_PORTABLE_DIR%
echo    - 下载文件: %PYTHON_ZIP%
echo.

:: 检查是否已经安装
if exist "%PYTHON_PORTABLE_DIR%\python.exe" (
    echo 📦 检测到已安装的Python便携版...
    "%PYTHON_PORTABLE_DIR%\python.exe" --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Python便携版已正常安装，跳过安装步骤
        goto :create_venv
    ) else (
        echo ⚠️ 现有安装可能已损坏，重新安装...
        rmdir /s /q "%PYTHON_PORTABLE_DIR%" 2>nul
    )
)

:: 创建必要目录
echo 📁 创建安装目录...
if not exist "%PYTHON_PORTABLE_DIR%" mkdir "%PYTHON_PORTABLE_DIR%"
if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%"

:: 检查PowerShell可用性
echo 🔧 检查PowerShell环境...
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PowerShell不可用，无法自动下载
    echo 💡 请手动下载Python %PYTHON_VERSION% 嵌入版并解压到: %PYTHON_PORTABLE_DIR%
    echo 📥 下载地址: https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_ZIP%
    pause
    exit /b 1
)

:: 下载Python便携版
echo 📥 开始下载Python便携版...
cd /d "%PROJECT_ROOT%"
powershell -ExecutionPolicy Bypass -File "python_setup\download_python.ps1" -Architecture "%ARCH%" -OutputPath "%TEMP_ZIP%" -UrlsFile "python_setup\python_urls.txt"

if %errorlevel% neq 0 (
    echo ❌ 下载失败！
    echo 💡 请检查网络连接或手动下载
    pause
    exit /b 1
)

:: 检查下载的文件
if not exist "%TEMP_ZIP%" (
    echo ❌ 下载文件不存在: %TEMP_ZIP%
    pause
    exit /b 1
)

:: 解压Python便携版
echo 📦 解压Python便携版...
powershell -Command "try { Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%PYTHON_PORTABLE_DIR%' -Force; Write-Host '✅ 解压完成' -ForegroundColor Green } catch { Write-Host '❌ 解压失败: ' + $_.Exception.Message -ForegroundColor Red; exit 1 }"

if %errorlevel% neq 0 (
    echo ❌ 解压失败！
    pause
    exit /b 1
)

:: 清理下载文件
echo 🗑️ 清理临时文件...
del "%TEMP_ZIP%" 2>nul

:: 验证Python安装
echo 🔍 验证Python安装...
if not exist "%PYTHON_PORTABLE_DIR%\python.exe" (
    echo ❌ Python可执行文件未找到！
    pause
    exit /b 1
)

:: 测试Python运行
"%PYTHON_PORTABLE_DIR%\python.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python无法正常运行！
    pause
    exit /b 1
)

echo ✅ Python便携版安装成功！

:: 配置Python环境
echo 🔧 配置Python环境...

:: 创建pth文件以支持pip
echo python%PYTHON_VERSION:~0,4%.zip > "%PYTHON_PORTABLE_DIR%\python%PYTHON_VERSION:~0,4%._pth"
echo . >> "%PYTHON_PORTABLE_DIR%\python%PYTHON_VERSION:~0,4%._pth"
echo >> "%PYTHON_PORTABLE_DIR%\python%PYTHON_VERSION:~0,4%._pth"
echo # 启用site-packages >> "%PYTHON_PORTABLE_DIR%\python%PYTHON_VERSION:~0,4%._pth"
echo import site >> "%PYTHON_PORTABLE_DIR%\python%PYTHON_VERSION:~0,4%._pth"

:: 下载并安装pip
echo 📦 安装pip...
if not exist "%PYTHON_PORTABLE_DIR%\Scripts\pip.exe" (
    echo 📥 下载get-pip.py...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_PORTABLE_DIR%\get-pip.py'; Write-Host '✅ get-pip.py下载完成' -ForegroundColor Green } catch { Write-Host '❌ get-pip.py下载失败' -ForegroundColor Red; exit 1 }"
    
    if !errorlevel! equ 0 (
        echo 🔧 安装pip...
        "%PYTHON_PORTABLE_DIR%\python.exe" "%PYTHON_PORTABLE_DIR%\get-pip.py" --no-warn-script-location
        del "%PYTHON_PORTABLE_DIR%\get-pip.py" 2>nul
        
        if exist "%PYTHON_PORTABLE_DIR%\Scripts\pip.exe" (
            echo ✅ pip安装成功！
        ) else (
            echo ⚠️ pip安装可能未完全成功，但可以继续
        )
    )
)

:create_venv
:: 创建虚拟环境
echo 🌟 创建项目虚拟环境...
set "VENV_DIR=%PROJECT_ROOT%\venv"

if exist "%VENV_DIR%" (
    echo 📦 发现现有虚拟环境，验证完整性...
    "%VENV_DIR%\Scripts\python.exe" --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 虚拟环境已存在且正常
        goto :finish
    ) else (
        echo ⚠️ 现有虚拟环境可能已损坏，重新创建...
        rmdir /s /q "%VENV_DIR%" 2>nul
    )
)

:: 创建新的虚拟环境
echo 🔨 创建新的虚拟环境...
"%PYTHON_PORTABLE_DIR%\python.exe" -m venv "%VENV_DIR%"

if %errorlevel% neq 0 (
    echo ❌ 虚拟环境创建失败！
    pause
    exit /b 1
)

:: 验证虚拟环境
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo ✅ 虚拟环境创建成功！
) else (
    echo ❌ 虚拟环境验证失败！
    pause
    exit /b 1
)

:: 升级虚拟环境中的pip
echo 📦 升级虚拟环境中的pip...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --no-warn-script-location >nul 2>&1

:finish
echo.
echo ========================================
echo 🎉 Python环境安装完成！
echo ========================================
echo.
echo 📊 安装信息:
"%PYTHON_PORTABLE_DIR%\python.exe" --version
echo    - 便携版位置: %PYTHON_PORTABLE_DIR%
echo    - 虚拟环境位置: %VENV_DIR%
echo.
echo ✅ 现在可以使用 start_windows.bat 启动应用程序
echo.

exit /b 0 