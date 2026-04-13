#!/bin/bash
# wsl.sh - WSL2 平台安装逻辑

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# ============================================================================
# WSL2 平台特定函数
# ============================================================================

# 检测 WSL 版本
detect_wsl_version() {
    if grep -q "Microsoft" /proc/version 2>/dev/null; then
        if uname -r | grep -q "microsoft"; then
            echo "wsl2"
        else
            echo "wsl1"
        fi
    else
        echo "none"
    fi
}

# 检查 Windows 版本
check_windows_version() {
    if command -v wsl.exe &> /dev/null; then
        wsl.exe -l -v 2>/dev/null | grep -i "running" | awk '{print $4}'
    else
        cat /proc/version 2>/dev/null | grep -oP "Microsoft.*WSL" | head -1
    fi
}

# 检查 WSL 配置
check_wsl_config() {
    log_header "检查 WSL 配置"

    local wsl_version
    wsl_version=$(detect_wsl_version)

    echo "WSL 版本: $wsl_version"

    if [ "$wsl_version" = "wsl1" ]; then
        log_warning "检测到 WSL1，建议升级到 WSL2"
        echo "  升级方法: wsl --update && wsl --shutdown"
    else
        log_success "使用 WSL2（推荐）"
    fi

    # 检查挂载点
    if [ -d "/mnt/c" ]; then
        log_success "Windows 分区已挂载"
    else
        log_warning "未检测到 Windows 分区挂载点"
        echo "  Windows 文件系统可能未自动挂载"
    fi
}

# 性能优化建议
provide_wsl_tips() {
    log_header "WSL2 性能优化建议"

    echo ""
    echo -e "${CYAN}建议:${NC}"
    echo "  1. 将项目文件放在 Linux 文件系统中（/home），而不是 /mnt/c"
    echo "     - Windows 文件系统访问较慢"
    echo "     - 可能导致 npm、git 等工具性能问题"
    echo ""
    echo "  2. 配置 .wslconfig（Windows 用户）"
    echo "     位置: C:\\Users\\<用户名>\\.wslconfig"
    echo ""
    echo "     示例配置:"
    echo "     [wsl2]"
    echo "     memory=8GB"
    echo "     processors=4"
    echo "     swap=8GB"
    echo ""
    echo "  3. 定期清理 WSL"
    echo "     - wsl --shutdown"
    echo "     - wsl --update"
}

# 配置 WSL 环境
configure_wsl() {
    log_header "配置 WSL 环境"

    # 检查 /etc/wsl.conf
    if [ -f "/etc/wsl.conf" ]; then
        log_success "检测到 WSL 配置文件"
    else
        log_info "建议创建 /etc/wsl.conf 配置文件"
    fi

    # 检查 Windows path
    if grep -q " diagnosing" /proc/version 2>/dev/null; then
        log_warning "检测到 Windows 路径可能未正确配置"
    fi

    provide_wsl_tips
    log_success "WSL 环境检查完成"
}

# 安装 OpenClaw（WSL）
install_openclaw_wsl() {
    log_header "安装 OpenClaw（WSL）"

    # 使用 Linux 安装逻辑
    source "$(dirname "${BASH_SOURCE[0]}")/linux.sh"
    install_dependencies_linux

    log_info "使用 pip 安装 openclaw..."
    if pip3 install openclaw; then
        log_success "OpenClaw 安装成功"
        openclaw --version
        return 0
    else
        log_error "pip 安装失败"
        return 1
    fi
}
