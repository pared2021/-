# UV 项目设置脚本
# 用于快速设置和管理 UV 项目环境

param(
    [string]$Action = "help",
    [switch]$Force
)

# 设置 UV 路径
$env:Path = "C:\Users\Administrator\.local\bin;$env:Path"

function Show-Help {
    Write-Host "UV 项目管理脚本" -ForegroundColor Green
    Write-Host "用法: .\uv-setup.ps1 [action] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "可用操作:" -ForegroundColor Cyan
    Write-Host "  install     - 安装项目依赖"
    Write-Host "  install-dev - 安装开发依赖"
    Write-Host "  run         - 运行主程序"
    Write-Host "  test        - 运行测试"
    Write-Host "  lint        - 代码检查"
    Write-Host "  format      - 代码格式化"
    Write-Host "  clean       - 清理环境"
    Write-Host "  sync        - 同步依赖"
    Write-Host "  lock        - 更新锁定文件"
    Write-Host "  shell       - 激活虚拟环境"
    Write-Host "  info        - 显示项目信息"
    Write-Host "  help        - 显示此帮助"
    Write-Host ""
    Write-Host "选项:" -ForegroundColor Cyan
    Write-Host "  -Force      - 强制执行操作"
}

function Install-Dependencies {
    Write-Host "安装项目依赖..." -ForegroundColor Green
    uv sync
}

function Install-DevDependencies {
    Write-Host "安装开发依赖..." -ForegroundColor Green
    uv sync --extra dev
}

function Run-Main {
    Write-Host "运行主程序..." -ForegroundColor Green
    uv run python main.py
}

function Run-Tests {
    Write-Host "运行测试..." -ForegroundColor Green
    uv run --extra test pytest
}

function Run-Lint {
    Write-Host "运行代码检查..." -ForegroundColor Green
    uv run --extra lint flake8 src/
    uv run --extra lint mypy src/
    uv run --extra lint bandit -r src/
}

function Format-Code {
    Write-Host "格式化代码..." -ForegroundColor Green
    uv run --extra lint black src/
    uv run --extra lint isort src/
}

function Clean-Environment {
    Write-Host "清理环境..." -ForegroundColor Green
    if ($Force -or (Read-Host "确定要删除虚拟环境吗? (y/N)") -eq "y") {
        Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force .uv-cache -ErrorAction SilentlyContinue
        Write-Host "环境已清理" -ForegroundColor Yellow
    }
}

function Sync-Dependencies {
    Write-Host "同步依赖..." -ForegroundColor Green
    uv sync --all-extras
}

function Update-Lock {
    Write-Host "更新锁定文件..." -ForegroundColor Green
    uv lock --upgrade
}

function Enter-Shell {
    Write-Host "激活虚拟环境..." -ForegroundColor Green
    Write-Host "使用 'exit' 退出虚拟环境" -ForegroundColor Yellow
    uv shell
}

function Show-Info {
    Write-Host "项目信息:" -ForegroundColor Green
    Write-Host "UV 版本: $(uv --version)" -ForegroundColor Cyan
    Write-Host "Python 版本: $(uv run python --version)" -ForegroundColor Cyan
    Write-Host "项目路径: $(Get-Location)" -ForegroundColor Cyan
    
    if (Test-Path "uv.lock") {
        Write-Host "锁定文件: 存在" -ForegroundColor Green
    } else {
        Write-Host "锁定文件: 不存在" -ForegroundColor Red
    }
    
    if (Test-Path ".venv") {
        Write-Host "虚拟环境: 存在" -ForegroundColor Green
    } else {
        Write-Host "虚拟环境: 不存在" -ForegroundColor Red
    }
}

# 主逻辑
switch ($Action.ToLower()) {
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "run" { Run-Main }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "clean" { Clean-Environment }
    "sync" { Sync-Dependencies }
    "lock" { Update-Lock }
    "shell" { Enter-Shell }
    "info" { Show-Info }
    "help" { Show-Help }
    default {
        Write-Host "未知操作: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}