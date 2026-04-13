# bootstrap.ps1 - OpenClaw 环境检查工具（Windows）
# 只检查环境，不会自动安装任何东西

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "help")]
    [string]$Command = "help"
)

# ============================================================================
# 配置
# ============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ============================================================================
# 彩色日志
# ============================================================================

function Log-Info { Write-Host "[ℹ️ ]" -ForegroundColor Cyan -NoNewline; Write-Host " $args" }
function Log-Success { Write-Host "[✅]" -ForegroundColor Green -NoNewline; Write-Host " $args" }
function Log-Warning { Write-Host "[⚠️ ]" -ForegroundColor Yellow -NoNewline; Write-Host " $args" }
function Log-Error { Write-Host "[❌]" -ForegroundColor Red -NoNewline; Write-Host " $args" -ForegroundColor Red }
function Log-Header { Write-Host ""; Write-Host "========================================" -ForegroundColor Cyan; Write-Host "$args" -ForegroundColor Cyan; Write-Host "========================================" -ForegroundColor Cyan }

# ============================================================================
# 平台检测
# ============================================================================

function Get-Platform {
    if ($IsWindows) { return "windows" }
    elseif ($IsLinux) { return "linux" }
    elseif ($IsMacOS) { return "darwin" }
    else { return "unknown" }
}

function Get-Arch {
    [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
}

# ============================================================================
# 环境检查
# ============================================================================

function Test-Environment {
    Log-Header "环境检查"

    $errors = 0
    $platform = Get-Platform

    Write-Host "平台: $platform"
    Write-Host "架构: $(Get-Arch)"
    Write-Host ""

    # 检查 Python
    Log-Info "检查 Python..."
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $version = python --version 2>&1
        Log-Success "Python $version"
    } else {
        Log-Warning "Python 未安装（需要 Python 3.8+）"
        $errors++
    }

    # 检查 Git
    Log-Info "检查 Git..."
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        Log-Success "Git"
    } else {
        Log-Warning "Git 未安装"
        $errors++
    }

    # 检查 curl/wget
    Log-Info "检查下载工具..."
    $curl = Get-Command curl -ErrorAction SilentlyContinue
    $wget = Get-Command wget -ErrorAction SilentlyContinue
    if ($curl -or $wget) {
        Log-Success "下载工具 (curl/wget)"
    } else {
        Log-Warning "下载工具未安装 (curl 或 wget)"
        $errors++
    }

    # 检查磁盘空间
    Log-Info "检查磁盘空间..."
    $drive = Get-PSDrive -Name $PWD.Path.Substring(0,1)
    $availableGB = [math]::Round($drive.Free / 1GB, 2)
    if ($availableGB -ge 1) {
        Log-Success "磁盘空间充足 (${availableGB}GB 可用)"
    } else {
        Log-Warning "磁盘空间不足 (${availableGB}GB 可用, 需要 >= 1GB)"
        $errors++
    }

    # 检查管理员权限
    Log-Info "检查权限..."
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($isAdmin) {
        Log-Success "管理员权限"
    } else {
        Log-Info "非管理员权限（正常）"
    }

    # 总结
    Write-Host ""
    if ($errors -eq 0) {
        Log-Success "环境检查通过！"
        return $true
    } else {
        Log-Warning "环境检查完成，发现 $errors 个问题（可选修复）"
        return $true
    }
}

# ============================================================================
# 主函数
# ============================================================================

function Main {
    switch ($Command) {
        "check" { Test-Environment }
        "help" {
            Write-Host @"
OpenClaw Bootstrap - 环境检查工具（只检查，不安装）

用法:
    .\scripts\openclaw-bootstrap\bootstrap.ps1 <command>

命令:
    check       检查环境（不会安装任何东西）
    help        显示帮助信息

平台支持:
    Windows

示例:
    .\scripts\openclaw-bootstrap\bootstrap.ps1 check

说明:
    此脚本只进行环境检查，不会自动安装任何软件。
    如需安装依赖，请手动安装。

"@
        }
    }
}

Main
