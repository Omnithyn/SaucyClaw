# OpenClaw Bootstrap 工具

环境检查与项目初始化工具，用于快速验证环境并准备 OpenClaw 多智能体开发环境。

## 目录结构

```
scripts/openclaw-bootstrap/
├── bootstrap.sh         # macOS/Linux 环境检查脚本
├── bootstrap.ps1        # Windows 环境检查脚本
├── platform/            # 平台适配层
│   ├── common.sh        # 通用函数
│   ├── darwin.sh        # macOS 平台
│   ├── linux.sh         # Linux 平台
│   └── wsl.sh           # WSL2 平台
└── README.md            # 本文档
```

## 快速开始

### macOS / Linux

```bash
# 检查环境（不会安装任何东西）
./scripts/openclaw-bootstrap/bootstrap.sh check

# 查看帮助
./scripts/openclaw-bootstrap/bootstrap.sh help
```

### Windows (PowerShell)

```powershell
# 检查环境（不会安装任何东西）
.\scripts\openclaw-bootstrap\bootstrap.ps1 check

# 查看帮助
.\scripts\openclaw-bootstrap\bootstrap.ps1 help
```

## 检查项目

脚本会检查以下环境：

- **Python 3.8+**: OpenClaw 运行环境
- **Git**: 版本控制工具
- **curl 或 wget**: 下载工具
- **磁盘空间**: 至少 1GB 可用空间
- **权限**: 当前目录写权限

**重要**: 此工具只进行环境检查，不会自动安装任何软件。如需安装依赖，需手动安装。

## 使用示例

### 完整流程

```bash
# 1. 检查环境
./scripts/openclaw-bootstrap/bootstrap.sh check

# 2. 手动安装缺失的依赖（如果需要）
# macOS: brew install python@3.11 git
# Ubuntu: sudo apt install python3 python3-pip git

# 3. 验证安装
python3 --version
git --version

# 4. 继续使用 SaucyClaw 的其他脚本
./scripts/bootstrap/init_saucyclaw.sh my-project
```

## 平台支持

### macOS

- 检测 Homebrew 是否可用
- 提示安装命令（如未安装）

### Linux

- 支持 Debian/Ubuntu
- 支持 RHEL/CentOS/Fedora
- 支持 WSL2

### Windows

- 支持 PowerShell
- 检测 Windows Terminal
- 提示 Git for Windows

## 故障排查

### Python 版本过低

**问题**: `Python 版本过低: 3.7.12 (需要 >= 3.8)`

**解决方案**:

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv

# RHEL/CentOS/Fedora
sudo dnf install python3.11
```

### Git 未安装

**解决方案**:

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# 下载并安装 Git for Windows: https://git-scm.com/download/win
```

### 磁盘空间不足

**问题**: `磁盘空间不足 (512 MB, 需要 >= 1024 MB)`

**解决方案**: 清理磁盘空间或更换到空间充足的目录。

## 与现有脚本的关系

此工具**补充**而非替代现有的 SaucyClaw 脚本：

| 脚本 | 职责 |
|------|------|
| `bootstrap.sh/ps1` | 环境检查（本工具） |
| `scripts/bootstrap/init_saucyclaw.sh` | 初始化项目结构 |
| `scripts/validate/check_structure.sh` | 验证项目结构 |
| `scripts/demo/up_demo.sh` | 启动 Docker demo |

**推荐流程**:

```bash
# 1. 检查环境
./scripts/openclaw-bootstrap/bootstrap.sh check

# 2. 初始化项目
./scripts/bootstrap/init_saucyclaw.sh my-project

# 3. 验证结构
./scripts/validate/check_structure.sh

# 4. 启动 demo（可选）
./scripts/demo/up_demo.sh
```

## 安全说明

- 脚本**不会**自动安装任何软件
- 脚本**不会**修改系统配置
- 脚本**不会**下载外部文件（仅检查工具是否存在）

所有操作都是**只读检查**，确保安全使用。

## 贡献

该工具遵循 SaucyClaw 项目规范。贡献时请注意：

- 使用 Bash (macOS/Linux) 和 PowerShell (Windows)
- 详细的错误信息和修复建议
- 不自动安装依赖，只提供检查和提示

---

**提示**: 使用该工具前，请确保已阅读 SaucyClaw 项目的 [CLAUDE.md](../../CLAUDE.md) 了解项目规范。
