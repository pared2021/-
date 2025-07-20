# PowerShell下载脚本 - Python便携式版本自动下载器
# 版本: 1.0
# 功能: 多源下载、完整性校验、进度显示、错误处理

param(
    [Parameter(Mandatory=$true)]
    [string]$Architecture,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false)]
    [string]$UrlsFile = "python_urls.txt"
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 全局变量
$PythonVersion = "3.11.9"
$MaxRetries = 3
$TimeoutSeconds = 300

# 函数: 写入彩色输出
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 函数: 显示进度
function Show-Progress {
    param(
        [string]$Activity,
        [string]$Status,
        [int]$PercentComplete = -1
    )
    if ($PercentComplete -ge 0) {
        Write-Progress -Activity $Activity -Status $Status -PercentComplete $PercentComplete
    } else {
        Write-Progress -Activity $Activity -Status $Status
    }
}

# 函数: 获取下载URL列表
function Get-DownloadUrls {
    param(
        [string]$Architecture,
        [string]$UrlsFile
    )
    
    $urls = @()
    
    if (Test-Path $UrlsFile) {
        Write-ColorOutput "📋 读取下载源配置文件..." "Cyan"
        $lines = Get-Content $UrlsFile
        foreach ($line in $lines) {
            if ($line -match "^$Architecture\|(.+)$") {
                $urls += $matches[1]
            }
        }
    }
    
    # 如果配置文件不存在或为空，使用默认URL
    if ($urls.Count -eq 0) {
        Write-ColorOutput "⚠️ 配置文件未找到或为空，使用默认下载源" "Yellow"
        if ($Architecture -eq "x64") {
            $urls += "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
            $urls += "https://mirrors.huaweicloud.com/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
        } else {
            $urls += "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-win32.zip"
            $urls += "https://mirrors.huaweicloud.com/python/$PythonVersion/python-$PythonVersion-embed-win32.zip"
        }
    }
    
    return $urls
}

# 函数: 下载文件
function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath,
        [int]$TimeoutSeconds = 300
    )
    
    try {
        Write-ColorOutput "🌐 正在从以下地址下载: $Url" "Green"
        
        # 创建WebClient实例
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "GameAutomation-PythonDownloader/1.0")
        
        # 注册进度事件
        Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -Action {
            $Global:DLProgress = $Event.SourceEventArgs.ProgressPercentage
            Show-Progress -Activity "下载Python便携版" -Status "正在下载... $($Global:DLProgress)%" -PercentComplete $Global:DLProgress
        } | Out-Null
        
        # 开始异步下载
        $Global:DLProgress = 0
        $downloadTask = $webClient.DownloadFileTaskAsync($Url, $OutputPath)
        
        # 等待下载完成或超时
        $timeout = New-TimeSpan -Seconds $TimeoutSeconds
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        while (-not $downloadTask.IsCompleted -and $stopwatch.Elapsed -lt $timeout) {
            Start-Sleep -Milliseconds 500
        }
        
        if ($downloadTask.IsCompleted) {
            Write-ColorOutput "✅ 下载完成!" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ 下载超时" "Red"
            $webClient.CancelAsync()
            return $false
        }
        
    } catch {
        Write-ColorOutput "❌ 下载失败: $($_.Exception.Message)" "Red"
        return $false
    } finally {
        if ($webClient) {
            $webClient.Dispose()
        }
        Write-Progress -Activity "下载Python便携版" -Completed
    }
}

# 函数: 验证文件完整性
function Test-FileIntegrity {
    param(
        [string]$FilePath
    )
    
    try {
        Write-ColorOutput "🔍 验证文件完整性..." "Cyan"
        
        if (-not (Test-Path $FilePath)) {
            Write-ColorOutput "❌ 文件不存在: $FilePath" "Red"
            return $false
        }
        
        $fileInfo = Get-Item $FilePath
        Write-ColorOutput "📊 文件大小: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" "Gray"
        
        # 基本大小检查 (Python嵌入版应该在10-30MB之间)
        if ($fileInfo.Length -lt 10MB -or $fileInfo.Length -gt 50MB) {
            Write-ColorOutput "⚠️ 文件大小异常，可能下载不完整" "Yellow"
            return $false
        }
        
        # 检查ZIP文件头
        $bytes = [System.IO.File]::ReadAllBytes($FilePath)
        if ($bytes.Length -ge 4 -and $bytes[0] -eq 0x50 -and $bytes[1] -eq 0x4B) {
            Write-ColorOutput "✅ ZIP文件格式验证通过" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ 文件格式验证失败" "Red"
            return $false
        }
        
    } catch {
        Write-ColorOutput "❌ 文件验证出错: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 主函数: 执行下载
function Start-Download {
    param(
        [string]$Architecture,
        [string]$OutputPath,
        [string]$UrlsFile
    )
    
    Write-ColorOutput "🚀 开始下载Python $PythonVersion 便携版 ($Architecture)" "Yellow"
    Write-ColorOutput "📁 目标路径: $OutputPath" "Gray"
    
    # 确保输出目录存在
    $outputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # 如果文件已存在且完整，跳过下载
    if (Test-Path $OutputPath) {
        Write-ColorOutput "📦 发现已存在的文件，验证完整性..." "Cyan"
        if (Test-FileIntegrity -FilePath $OutputPath) {
            Write-ColorOutput "✅ 文件已存在且完整，跳过下载" "Green"
            return $true
        } else {
            Write-ColorOutput "🗑️ 删除损坏的文件..." "Yellow"
            Remove-Item $OutputPath -Force
        }
    }
    
    # 获取下载URL列表
    $urls = Get-DownloadUrls -Architecture $Architecture -UrlsFile $UrlsFile
    Write-ColorOutput "🔗 找到 $($urls.Count) 个下载源" "Cyan"
    
    # 尝试从每个URL下载
    foreach ($url in $urls) {
        for ($retry = 1; $retry -le $MaxRetries; $retry++) {
            Write-ColorOutput "🔄 尝试下载 (源: $($urls.IndexOf($url) + 1)/$($urls.Count), 重试: $retry/$MaxRetries)" "Yellow"
            
            if (Download-File -Url $url -OutputPath $OutputPath -TimeoutSeconds $TimeoutSeconds) {
                if (Test-FileIntegrity -FilePath $OutputPath) {
                    Write-ColorOutput "🎉 Python便携版下载成功!" "Green"
                    return $true
                } else {
                    Write-ColorOutput "❌ 文件完整性验证失败，删除并重试..." "Red"
                    if (Test-Path $OutputPath) {
                        Remove-Item $OutputPath -Force
                    }
                }
            }
            
            if ($retry -lt $MaxRetries) {
                Write-ColorOutput "⏳ 等待 3 秒后重试..." "Yellow"
                Start-Sleep -Seconds 3
            }
        }
    }
    
    Write-ColorOutput "❌ 所有下载源均失败！" "Red"
    return $false
}

# 主执行逻辑
try {
    Write-ColorOutput "=" * 60 "Cyan"
    Write-ColorOutput "🐍 Python便携版自动下载器" "Yellow"
    Write-ColorOutput "=" * 60 "Cyan"
    
    $success = Start-Download -Architecture $Architecture -OutputPath $OutputPath -UrlsFile $UrlsFile
    
    if ($success) {
        Write-ColorOutput "🎊 下载任务完成!" "Green"
        exit 0
    } else {
        Write-ColorOutput "💥 下载任务失败!" "Red"
        Write-ColorOutput "请检查网络连接或手动下载Python便携版" "Yellow"
        exit 1
    }
    
} catch {
    Write-ColorOutput "💥 脚本执行出错: $($_.Exception.Message)" "Red"
    Write-ColorOutput "详细错误信息: $($_.Exception.StackTrace)" "Red"
    exit 1
} 