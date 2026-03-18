#!/usr/bin/env python3
"""
SaucyClaw CLI Tool
统一的命令行工具入口
"""

import sys
import os
import argparse
from pathlib import Path

from saucyclaw import __version__


def init_project(args):
    """初始化 SaucyClaw 项目"""
    TOOLS_DIR = Path(__file__).parent
    project_name = args.name
    print(f"正在初始化项目: {project_name}")
    # 调用脚本
    script_path = TOOLS_DIR.parent / "scripts" / "bootstrap" / "init_saucyclaw.sh"
    if script_path.exists():
        os.system(f"bash {script_path} {project_name}")
    else:
        print(f"错误: 脚本不存在: {script_path}")


def validate_structure(args):
    """验证项目结构"""
    TOOLS_DIR = Path(__file__).parent
    print("正在验证项目结构...")
    script_path = TOOLS_DIR.parent / "scripts" / "validate" / "check_structure.sh"
    if script_path.exists():
        os.system(f"bash {script_path}")
    else:
        print(f"错误: 脚本不存在: {script_path}")


def create_agent(args):
    """创建新的智能体角色"""
    TOOLS_DIR = Path(__file__).parent
    agent_name = args.name
    agent_type = args.type
    print(f"正在创建智能体: {agent_name} (type: {agent_type})")
    script_path = TOOLS_DIR.parent / "scripts" / "bootstrap" / "create_agent_role.sh"
    if script_path.exists():
        os.system(f"bash {script_path} {agent_name} {agent_type}")
    else:
        print(f"错误: 脚本不存在: {script_path}")


def start_demo(args):
    """启动 Docker demo 环境"""
    TOOLS_DIR = Path(__file__).parent
    print("正在启动 Docker demo...")
    script_path = TOOLS_DIR.parent / "scripts" / "demo" / "up_demo.sh"
    if script_path.exists():
        os.system(f"bash {script_path}")
    else:
        print(f"错误: 脚本不存在: {script_path}")


def stop_demo(args):
    """停止 Docker demo 环境"""
    TOOLS_DIR = Path(__file__).parent
    print("正在停止 Docker demo...")
    script_path = TOOLS_DIR.parent / "scripts" / "demo" / "down_demo.sh"
    if script_path.exists():
        os.system(f"bash {script_path}")
    else:
        print(f"错误: 脚本不存在: {script_path}")


def bundle_project(args):
    """打包项目为可分享的 bundle"""
    print("正在打包项目...")
    from saucyclaw.packagers.bundle import create_bundle
    output_path = create_bundle(output_dir=args.output)
    print(f"打包完成: {output_path}")


def show_version(args):
    """显示版本信息"""
    print(f"SaucyClaw CLI v{__version__}")
    print(f"Python: {sys.version}")


def main():
    parser = argparse.ArgumentParser(
        description="🦞 SaucyClaw - Multi-Agent Governance Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  saucyclaw init my-project           # 初始化新项目
  saucyclaw validate                  # 验证项目结构
  saucyclaw create-agent researcher   # 创建智能体
  saucyclaw demo start                # 启动 demo
  saucyclaw bundle -o my-bundle.zip   # 打包项目
        """
    )

    parser.add_argument('--version', action='store_true', help='显示版本信息')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化 SaucyClaw 项目')
    init_parser.add_argument('name', help='项目名称或路径')
    init_parser.set_defaults(func=init_project)

    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证项目结构合规性')
    validate_parser.set_defaults(func=validate_structure)

    # create-agent 命令
    create_parser = subparsers.add_parser('create-agent', help='创建新的智能体角色')
    create_parser.add_argument('name', help='智能体名称')
    create_parser.add_argument(
        '--type', '-t',
        choices=['specialist', 'general', 'reviewer'],
        default='specialist',
        help='智能体类型 (default: specialist)'
    )
    create_parser.set_defaults(func=create_agent)

    # demo 命令
    demo_parser = subparsers.add_parser('demo', help='管理 Docker demo 环境')
    demo_subparsers = demo_parser.add_subparsers(dest='demo_action')

    demo_start = demo_subparsers.add_parser('start', help='启动 demo')
    demo_start.set_defaults(func=start_demo)

    demo_stop = demo_subparsers.add_parser('stop', help='停止 demo')
    demo_stop.set_defaults(func=stop_demo)

    # bundle 命令
    bundle_parser = subparsers.add_parser('bundle', help='打包项目为可分享的 bundle')
    bundle_parser.add_argument(
        '--output', '-o',
        default='saucyclaw-bundle.zip',
        help='输出文件路径 (default: saucyclaw-bundle.zip)'
    )
    bundle_parser.set_defaults(func=bundle_project)

    # version 命令
    version_parser = subparsers.add_parser('version', help='显示版本信息')
    version_parser.set_defaults(func=show_version)

    # 解析参数
    args = parser.parse_args()

    # 处理 --version
    if args.version:
        show_version(args)
        return

    # 没有命令时显示帮助
    if not hasattr(args, 'func'):
        parser.print_help()
        return

    # 执行命令
    try:
        args.func(args)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
