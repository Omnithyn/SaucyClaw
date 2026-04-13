#!/bin/bash
# linux.sh - Linux 平台安装逻辑

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# ============================================================================
# Linux 平台特定函数
# ============================================================================

# 检测 Linux 发行版
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

# 检查包管理器
check_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v apt-get &> /dev/null; then
        echo "apt-get"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

# 检查 GCC
check_gcc() {
    if command -v gcc &> /dev/null; then
        log_success "GCC 已安装"
        gcc --version 2>/dev/null | head -1 | sed 's/^/  /'
        return 0
    else
        log_warning "GCC 未安装（某些包可能需要编译）"
        return 1
    fi
}

# 安装依赖（Debian/Ubuntu）
install_dependencies_debian() {
    log_header "安装依赖（Debian/Ubuntu）"

    log_info "更新包列表..."
    if sudo apt update -qq; then
        log_success "包列表已更新"
    else
        log_warning "包列表更新失败"
    fi

    local deps=("python3" "python3-pip" "git" "curl" "build-essential")

    for dep in "${deps[@]}"; do
        if dpkg -l | grep -q "^ii  $dep "; then
            log_success "$dep 已安装"
        else
            log_info "安装 $dep..."
            if sudo apt install -y "$dep"; then
                log_success "$dep 安装成功"
            else
                log_error "$dep 安装失败"
                return 1
            fi
        fi
    done

    log_success "所有依赖已安装"
    return 0
}

# 安装依赖（RHEL/CentOS）
install_dependencies_rhel() {
    log_header "安装依赖（RHEL/CentOS）"

    local deps=("python3" "git" "curl" "gcc" "gcc-c++")

    for dep in "${deps[@]}"; do
        if rpm -q "$dep" &> /dev/null; then
            log_success "$dep 已安装"
        else
            log_info "安装 $dep..."
            if sudo yum install -y "$dep"; then
                log_success "$dep 安装成功"
            else
                log_error "$dep 安装失败"
                return 1
            fi
        fi
    done

    log_success "所有依赖已安装"
    return 0
}

# 安装依赖（Fedora）
install_dependencies_fedora() {
    log_header "安装依赖（Fedora）"

    local deps=("python3" "python3-pip" "git" "curl" "gcc" "gcc-c++")

    for dep in "${deps[@]}"; do
        if rpm -q "$dep" &> /dev/null; then
            log_success "$dep 已安装"
        else
            log_info "安装 $dep..."
            if sudo dnf install -y "$dep"; then
                log_success "$dep 安装成功"
            else
                log_error "$dep 安装失败"
                return 1
            fi
        fi
    done

    log_success "所有依赖已安装"
    return 0
}

# 安装依赖（Arch Linux）
install_dependencies_arch() {
    log_header "安装依赖（Arch Linux）"

    local deps=("python" "python-pip" "git" "curl")

    for dep in "${deps[@]}"; do
        if pacman -Q "$dep" &> /dev/null; then
            log_success "$dep 已安装"
        else
            log_info "安装 $dep..."
            if sudo pacman -Sy --noconfirm "$dep"; then
                log_success "$dep 安装成功"
            else
                log_error "$dep 安装失败"
                return 1
            fi
        fi
    done

    log_success "所有依赖已安装"
    return 0
}

# 安装依赖（通用）
install_dependencies_linux() {
    local distro
    distro=$(detect_distro)

    case "$distro" in
        ubuntu|debian)
            install_dependencies_debian
            ;;
        centos|rhel)
            install_dependencies_rhel
            ;;
        fedora)
            install_dependencies_fedora
            ;;
        arch|manjaro)
            install_dependencies_arch
            ;;
        *)
            log_warning "未检测到已知发行版，尝试通用安装..."
            if command -v apt &> /dev/null; then
                install_dependencies_debian
            elif command -v yum &> /dev/null; then
                install_dependencies_rhel
            elif command -v dnf &> /dev/null; then
                install_dependencies_fedora
            else
                log_error "不支持的发行版"
                return 1
            fi
            ;;
    esac
}

# 配置 Linux 环境
configure_linux() {
    log_header "配置 Linux 环境"

    local profile_files=("$HOME/.bashrc" "$HOME/.zshrc")
    for profile in "${profile_files[@]}"; do
        if [ -f "$profile" ]; then
            echo "" >> "$profile"
            echo "# Python 环境配置" >> "$profile"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$profile"
            log_success "已配置 $profile"
        fi
    done

    log_success "Linux 环境配置完成"
}

# 安装 OpenClaw（Linux）
install_openclaw_linux() {
    log_header "安装 OpenClaw（Linux）"

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
