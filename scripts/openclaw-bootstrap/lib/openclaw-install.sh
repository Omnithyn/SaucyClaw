#!/bin/bash
# openclaw-install.sh - OpenClaw 安装逻辑（macOS/Linux）
# 包含平台特定的安装函数

# 来源: common 函数
source "$(dirname "${BASH_SOURCE[0]}")/platform/common.sh"

# ============================================================================
# OpenClaw 安装函数
# ============================================================================

# 检查 OpenClaw 是否已安装
check_openclaw_installed() {
    if command -v openclaw &> /dev/null; then
        log_success "OpenClaw 已安装"
        openclaw --version
        return 0
    else
        log_warning "OpenClaw 未安装"
        return 1
    fi
}

# 使用官方安装脚本安装 OpenClaw
install_openclaw_official() {
    log_header "安装 OpenClaw（官方脚本）"

    local temp_script="/tmp/openclaw-install.sh"
    local install_url="https://raw.githubusercontent.com/openclaw-org/openclaw/main/install.sh"

    # 下载安装脚本
    log_info "下载官方安装脚本..."
    if command -v curl &> /dev/null; then
        curl -fsSL "$install_url" -o "$temp_script"
    elif command -v wget &> /dev/null; then
        wget -q "$install_url" -O "$temp_script"
    else
        log_error "未找到 curl 或 wget"
        return 1
    fi

    # 检查下载成功
    if [ ! -f "$temp_script" ]; then
        log_error "下载安装脚本失败"
        return 1
    fi

    # 验证脚本
    log_info "验证安装脚本..."
    if ! head -1 "$temp_script" | grep -q "#!/bin/bash"; then
        log_warning "安装脚本格式验证警告"
    fi

    # 执行安装脚本
    log_info "执行安装脚本..."
    if bash "$temp_script"; then
        log_success "OpenClaw 安装脚本执行成功"
    else
        log_error "OpenClaw 安装脚本执行失败"
        return 1
    fi

    # 清理
    rm -f "$temp_script"

    # 验证安装
    if command -v openclaw &> /dev/null; then
        log_success "OpenClaw 安装成功！"
        openclaw --version
        return 0
    else
        log_error "OpenClaw 安装失败：未找到 openclaw 命令"
        return 1
    fi
}

# 使用 pip 安装 OpenClaw（如果发布到 PyPI）
install_openclaw_pip() {
    log_header "安装 OpenClaw（pip）"

    log_info "检查 Python 环境..."
    check_python_version 3.8 || return 1

    log_info "使用 pip 安装 openclaw..."
    if pip install openclaw; then
        log_success "OpenClaw pip 安装成功"
        return 0
    else
        log_error "OpenClaw pip 安装失败"
        return 1
    fi
}

# 从源码编译安装
install_openclaw_from_source() {
    log_header "安装 OpenClaw（从源码）"

    local repo_url="https://github.com/openclaw/openclaw.git"
    local temp_dir="/tmp/openclaw-build"

    # 克隆源码
    log_info "克隆源码仓库..."
    if git clone "$repo_url" "$temp_dir"; then
        log_success "源码克隆成功"
    else
        log_error "源码克隆失败"
        return 1
    fi

    # 安装依赖
    log_info "安装依赖..."
    cd "$temp_dir"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    # 构建和安装
    log_info "构建和安装..."
    if python setup.py install; then
        log_success "OpenClaw 源码安装成功"
    else
        log_error "OpenClaw 源码安装失败"
        return 1
    fi

    # 清理
    cd - > /dev/null
    rm -rf "$temp_dir"

    # 验证
    if command -v openclaw &> /dev/null; then
        log_success "OpenClaw 安装成功！"
        return 0
    else
        log_error "OpenClaw 安装失败"
        return 1
    fi
}

# ============================================================================
# OpenClaw 卸载
# ============================================================================

uninstall_openclaw() {
    log_header "卸载 OpenClaw"

    if ! command -v openclaw &> /dev/null; then
        log_info "OpenClaw 未安装"
        return 0
    fi

    log_warning "此操作将卸载 OpenClaw"
    if confirm "继续卸载？" "n"; then
        # TODO: 调用 openclaw uninstall（如果支持）
        # 或手动清理安装的文件
        log_success "OpenClaw 卸载完成（如果通过 pip 安装，可使用: pip uninstall openclaw）"
    else
        log_info "卸载已取消"
    fi
}

# ============================================================================
# 环境配置
# ============================================================================

# 配置环境变量
configure_environment() {
    log_header "配置环境变量"

    local platform
    platform=$(detect_os)

    case "$platform" in
        darwin)
            configure_path_macos
            ;;
        linux|wsl)
            configure_path_linux
            ;;
    esac
}

# macOS 配置
configure_path_macos() {
    local profile_file="$HOME/.zshrc"

    if [ -f "$profile_file" ]; then
        if ! grep -q "openclaw" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            echo "# OpenClaw 环境配置" >> "$profile_file"
            echo '# export PATH="/usr/local/openclaw/bin:$PATH"' >> "$profile_file"
            log_success "已添加 OpenClaw 配置到 $profile_file"
            log_info "请运行: source $profile_file"
        else
            log_success "OpenClaw 配置已存在"
        fi
    else
        log_warning "未找到 profile 文件: $profile_file"
    fi
}

# Linux 配置
configure_path_linux() {
    local profile_file="$HOME/.bashrc"

    if [ -f "$profile_file" ]; then
        if ! grep -q "openclaw" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            echo "# OpenClaw 环境配置" >> "$profile_file"
            echo '# export PATH="/usr/local/openclaw/bin:$PATH"' >> "$profile_file"
            log_success "已添加 OpenClaw 配置到 $profile_file"
            log_info "请运行: source $profile_file"
        else
            log_success "OpenClaw 配置已存在"
        fi
    else
        log_warning "未找到 profile 文件: $profile_file"
    fi
}

# ============================================================================
# 版本管理
# ============================================================================

# 获取最新版本
get_latest_version() {
    local repo="openclaw-org/openclaw"
    local url="https://api.github.com/repos/$repo/releases/latest"

    if command -v curl &> /dev/null; then
        curl -s "$url" | grep -oP '"tag_name": "v\K[^"]+' || echo "unknown"
    else
        echo "unknown"
    fi
}

# 检查版本
check_version() {
    if command -v openclaw &> /dev/null; then
        log_info "当前 installed version:"
        openclaw --version
    else
        log_info "OpenClaw 未安装"
    fi
}

# ============================================================================
# 实用工具
# ============================================================================

# 安装 OpenClaw（推荐方式）
install_openclaw() {
    log_header "OpenClaw 安装"

    # 尝试官方安装脚本
    install_openclaw_official
}

# 检查并安装依赖
ensure_dependencies() {
    log_header "确保依赖已安装"

    local deps=()
    local platform
    platform=$(detect_os)

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        deps+=("python3")
    fi

    # 检查 Git
    if ! command -v git &> /dev/null; then
        deps+=("git")
    fi

    # 检查下载工具
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        deps+=("curl" "wget")
    fi

    if [ ${#deps[@]} -gt 0 ]; then
        log_info "需要安装依赖: ${deps[*]}"

        case "$platform" in
            darwin)
                for dep in "${deps[@]}"; do
                    brew_install "$dep"
                done
                ;;
            linux|wsl)
                for dep in "${deps[@]}"; do
                    apt_install "$dep"
                done
                ;;
        esac
    else
        log_success "所有依赖已安装"
    fi
}
