"""SaucyClaw 配置加载器。

从用户目录下的配置文件加载私有配置，不泄露到源码中。

配置文件位置：
- ~/.saucyclaw/saucyclaw.json

配置结构：
{
  "notification": {
    "gateway_url": "http://your-gateway/hooks/agent",
    "hooks_token": "your-token",
    "timeout_ms": 10000
  }
}

环境变量覆盖（优先级更高）：
- SAUCYCLAW_GATEWAY_URL
- SAUCYCLAW_HOOKS_TOKEN
- SAUCYCLAW_TIMEOUT_MS
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_DIR = Path.home() / ".saucyclaw"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "saucyclaw.json"


@dataclass(frozen=True)
class NotificationConfig:
    """Notification 配置。"""
    gateway_url: str | None = None
    hooks_token: str | None = None
    timeout_ms: int = 10_000


@dataclass(frozen=True)
class SaucyClawConfig:
    """SaucyClaw 完整配置。"""
    notification: NotificationConfig = NotificationConfig()


def load_config_file(config_path: Path | None = None) -> dict[str, Any] | None:
    """加载配置文件。"""
    path = config_path or DEFAULT_CONFIG_FILE
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def load_notification_config(config_path: Path | None = None) -> NotificationConfig:
    """加载 notification 配置，优先使用环境变量。

    优先级：
    1. 环境变量 SAUCYCLAW_GATEWAY_URL / SAUCYCLAW_HOOKS_TOKEN
    2. 配置文件 ~/.saucyclaw/saucyclaw.json
    3. 默认值
    """
    # 环境变量优先
    env_gateway_url = os.environ.get("SAUCYCLAW_GATEWAY_URL")
    env_hooks_token = os.environ.get("SAUCYCLAW_HOOKS_TOKEN")
    env_timeout_ms = os.environ.get("SAUCYCLAW_TIMEOUT_MS")

    # 加载配置文件
    config_file = load_config_file(config_path)
    file_notification = config_file.get("notification", {}) if config_file else {}

    # 合并配置（环境变量优先）
    gateway_url = env_gateway_url or file_notification.get("gateway_url")
    hooks_token = env_hooks_token or file_notification.get("hooks_token")
    timeout_ms = (
        int(env_timeout_ms)
        if env_timeout_ms
        else file_notification.get("timeout_ms", 10_000)
    )

    return NotificationConfig(
        gateway_url=gateway_url,
        hooks_token=hooks_token,
        timeout_ms=timeout_ms,
    )


def load_config(config_path: Path | None = None) -> SaucyClawConfig:
    """加载完整配置。"""
    return SaucyClawConfig(
        notification=load_notification_config(config_path),
    )


def ensure_config_exists() -> Path:
    """确保配置目录存在，返回配置文件路径。

    如果配置文件不存在，创建默认模板。
    """
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not DEFAULT_CONFIG_FILE.exists():
        template = {
            "notification": {
                "gateway_url": None,
                "hooks_token": None,
                "timeout_ms": 10000,
            }
        }
        with open(DEFAULT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2)
        print(f"[config] Created config template at {DEFAULT_CONFIG_FILE}")
        print("[config] Please fill in gateway_url and hooks_token")

    return DEFAULT_CONFIG_FILE