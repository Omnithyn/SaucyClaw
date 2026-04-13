#!/bin/bash
# darwin.sh - macOS 平台安装逻辑

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# ============================================================================
# macOS 平台特定函数
# ============================================================================

# 检查 Homebrew
check_brew() {
    if command -v brew &> /dev/null; then
        log_success "Homebrew 已安装"
        brew --version 2>/dev/null | head -1 | sed 's/^/  /'
        return 0
    else
        log_warning "Homebrew 未安装"
        return 1
    fi
}

# 安装 Homebrew
install_brew() {
    log_header "安装 Homebrew"

    if confirm "是否自动安装 Homebrew？" "n"; then
        log_info "下载并安装 Homebrew..."

        # 检查网络
        if ! curl -s https://www.google.com > /dev/null 2>&1; then
            log_error "无法连接网络"
            return 1
        fi

        # 安装 Command Line Tools
        if ! xcode-select -p &> /dev/null; then
            log_info "安装 Xcode Command Line Tools..."
            xcode-select --install || log_warning "Command Line Tools 安装被取消"
        fi

        # 安装 Homebrew
        if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
            log_success "Homebrew 安装成功"

            # 配置环境变量
            eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
            return 0
        else
            log_error "Homebrew 安装失败"
            return 1
        fi
    else
        log_info "请手动安装 Homebrew: https://brew.sh"
        return 1
    fi
}

# 安装依赖（macOS）
install_dependencies_darwin() {
    log_header "安装依赖（macOS）"

    local deps=("python3" "git" "curl")

    for dep in "${deps[@]}"; do
        if command -v "$dep" &> /dev/null; then
            log_success "$dep 已安装"
        else
            if command -v brew &> /dev/null; then
                log_info "安装 $dep..."
                brew install "$dep"
            else
                log_error "请先安装 Homebrew"
                return 1
            fi
        fi
    done

    log_success "所有依赖已安装"
    return 0
}

# 配置 macOS 环境
configure_macos() {
    log_header "配置 macOS 环境"

    # 配置 PATH
    local profile_file="$HOME/.zshrc"
    if [ -f "$profile_file" ]; then
        if ! grep -q "HOMEBREW" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            echo '# Homebrew 路径配置' >> "$profile_file"
            echo 'eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"' >> "$profile_file"
            log_success "已配置 Homebrew 路径"
        fi
    fi

    # 配置 Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        log_warning "Xcode Command Line Tools 未安装"
        if confirm "是否安装？" "y"; then
            xcode-select --install
        fi
    fi

    log_success "macOS 环境配置完成"
}

# 安装 OpenClaw（macOS）
install_openclaw_darwin() {
    log_header "安装 OpenClaw（macOS）"

    # 确保 Homebrew 存在
    if ! command -v brew &> /dev/null; then
        install_brew
    fi

    # 使用 pip 安装（推荐方式）
    log_info "使用 pip 安装 openclaw..."
    if pip3 install openclaw; then
        log_success "OpenClaw 安装成功"
        openclaw --version
        return 0
    else
        log_warning "pip 安装失败，尝试从源码安装"

        # 从源码安装
        local temp_dir="/tmp/openclaw-build"
        git clone https://github.com/openclaw/openclaw.git "$temp_dir" 2>/dev/null || {
            log_error "源码安装失败"
            return 1
        }

        cd "$temp_dir"
        pip3 install -e .
        cd - > /dev/null
        rm -rf "$temp_dir"

        if openclaw --version &> /dev/null; then
            log_success "OpenClaw 源码安装成功"
            return 0
        fi
    fi
}
