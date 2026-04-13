#!/bin/bash
# bootstrap.sh - OpenClaw 环境检查工具（macOS/Linux）
# 不会自动安装任何东西，只是检查环境

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$SCRIPT_DIR/platform"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Emoji
CHECK="✅"
WARN="⚠️"
ERROR="❌"
INFO="ℹ️"

# ============================================================================
# 日志函数
# ============================================================================

log_info() {
    echo -e "${BLUE}${INFO}${NC} $1"
}

log_success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}${WARN}${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR}${NC} $1" >&2
}

log_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# ============================================================================
# 平台检测
# ============================================================================

detect_platform() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "darwin"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -qi microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

detect_arch() {
    uname -m
}

# ============================================================================
# 环境检查
# ============================================================================

check_environment() {
    log_header "环境检查"

    local errors=0
    local platform
    platform=$(detect_platform)

    echo "平台: $platform"
    echo "架构: $(detect_arch)"
    echo ""

    # 检查必需工具
    log_info "检查必需工具..."

    if command -v python3 &> /dev/null; then
        local version
        version=$(python3 --version 2>&1 | awk '{print $2}')
        local major minor
        IFS='.' read -r major minor <<< "$version"
        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            log_success "Python $version (>= 3.8)"
        else
            log_warning "Python 版本过低: $version (需要 >= 3.8)"
            ((errors++))
        fi
    else
        log_warning "Python 3 未安装（需要 >= 3.8）"
        ((errors++))
    fi

    if command -v git &> /dev/null; then
        log_success "Git"
    else
        log_warning "Git 未安装"
        ((errors++))
    fi

    if command -v curl &> /dev/null || command -v wget &> /dev/null; then
        log_success "下载工具 (curl/wget)"
    else
        log_warning "下载工具未安装 (curl 或 wget)"
        ((errors++))
    fi

    # 检查磁盘空间
    local available_mb
    available_mb=$(df -m . 2>/dev/null | tail -1 | awk '{print $4}')
    if [ "$available_mb" -ge 1024 ]; then
        log_success "磁盘空间充足 ($available_mb MB)"
    else
        log_warning "磁盘空间不足 ($available_mb MB, 需要 >= 1024 MB)"
        ((errors++))
    fi

    # 检查权限
    if [ -w "$(pwd)" ]; then
        log_success "当前目录可写"
    else
        log_error "当前目录不可写"
        ((errors++))
    fi

    # 总结
    echo ""
    if [ $errors -eq 0 ]; then
        log_success "环境检查通过！"
        return 0
    else
        log_warning "环境检查完成，发现 $errors 个问题（可选修复）"
        return 0
    fi
}

# ============================================================================
# 命令处理
# ============================================================================

show_help() {
    cat <<EOFHELP
OpenClaw Bootstrap - 环境检查与初始化工具（只检查，不安装）

用法:
    $0 <command>

命令:
    check       检查环境（不会安装任何东西）
    help        显示帮助信息

平台支持:
    macOS (darwin)
    Linux (debian/ubuntu, rhel/centos, fedora)
    Windows WSL2

示例:
    $0 check        # 检查环境
    $0 help         # 显示帮助

说明:
    此脚本只进行环境检查，不会自动安装任何软件。
    如需安装依赖，请手动安装。

EOFHELP
}

# 主函数
main() {
    # 解析参数
    local command=""

    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    command=$1
    shift

    # 执行命令
    case "$command" in
        check)
            check_environment
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
