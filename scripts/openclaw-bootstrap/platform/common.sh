#!/bin/bash
# common.sh - 通用函数库

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

#日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# 检测操作系统类型
detect_os() {
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

# 获取系统架构
get_arch() {
    uname -m
}

# 检查命令是否存在
check_command() {
    local cmd=$1
    local name=${2:-$cmd}

    if command -v "$cmd" &> /dev/null; then
        log_success "$name 已安装"
        return 0
    else
        log_error "$name 未安装"
        return 1
    fi
}

# 检查 Python 版本
check_python_version() {
    local min_version="${1:-3.8}"

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        return 1
    fi

    local version
    version=$(python3 --version 2>&1 | awk '{print $2}')
    local major minor patch
    IFS='.' read -r major minor patch <<< "$version"
    local min_major min_minor
    IFS='.' read -r min_major min_minor <<< "$min_version"

    # 处理没有小版本号的情况（如 3.8）
    minor=${minor:-0}

    # 使用数值比较
    if [ "$major" -gt "$min_major" ]; then
        log_success "Python $version (>= $min_version)"
        return 0
    elif [ "$major" -eq "$min_major" ]; then
        if [ "$minor" -gt "$min_minor" ]; then
            log_success "Python $version (>= $min_version)"
            return 0
        elif [ "$minor" -eq "$min_minor" ]; then
            log_success "Python $version (>= $min_version)"
            return 0
        fi
    fi

    log_error "Python $version 版本过低（需要 >= $min_version）"
    return 1
}

# 检查磁盘空间
check_disk_space() {
    local required_mb="${1:-1024}"

    local available_mb
    available_mb=$(df -m . 2>/dev/null | tail -1 | awk '{print $4}')

    if [ "$available_mb" -ge "$required_mb" ]; then
        log_success "磁盘空间充足 ($available_mb MB)"
        return 0
    else
        log_error "磁盘空间不足 ($available_mb MB, 需要 >= $required_mb MB)"
        return 1
    fi
}

# 确认操作
confirm() {
    local prompt="${1:-确认操作？}"
    local default="${2:-y}"

    if [ "$SILENT_MODE" = true ]; then
        [ "$default" = "y" ]
        return $?
    fi

    read -p "${prompt} (y/n) [$default]: " response
    case "${response:-$default}" in
        [yY]*) return 0 ;;
        *) return 1 ;;
    esac
}

# 安装依赖（平台无关包装函数）
install_dependency() {
    local dep="$1"
    local platform
    platform=$(detect_os)

    case "$platform" in
        darwin)
            if command -v brew &> /dev/null; then
                if brew list --versions "$dep" &> /dev/null; then
                    log_success "$dep 已安装"
                else
                    brew install "$dep"
                fi
            else
                log_error "Homebrew 未安装"
                return 1
            fi
            ;;
        linux|wsl)
            if command -v apt &> /dev/null; then
                sudo apt update -qq && sudo apt install -y "$dep"
            elif command -v yum &> /dev/null; then
                sudo yum install -y "$dep"
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y "$dep"
            else
                log_error "未检测到包管理器"
                return 1
            fi
            ;;
        *)
            log_error "不支持的平台: $platform"
            return 1
            ;;
    esac
}

# 检查必需工具
check_requirements() {
    log_header "检查必需工具"

    local errors=0

    check_command "python3" "Python 3" || ((errors++))
    check_command "git" "Git" || ((errors++))
    check_command "curl" "curl" || check_command "wget" "wget" || ((errors++))

    if [ $errors -eq 0 ]; then
        log_success "所有必需工具已安装"
        return 0
    else
        log_error "发现 $errors 个缺失的工具"
        return 1
    fi
}

# 环境检查
check_environment() {
    log_header "环境检查"

    local platform
    platform=$(detect_os)

    echo "平台: $platform"
    echo "架构: $(get_arch)"
    echo ""

    check_requirements
    check_disk_space 1024

    # 检查权限
    if [ -w "$(pwd)" ]; then
        log_success "当前目录可写"
    else
        log_error "当前目录不可写"
        return 1
    fi

    echo ""
    log_success "环境检查通过！"
    return 0
}
