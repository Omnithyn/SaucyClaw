"""SaucyClaw 配置模块。

提供私有配置加载能力，不从源码泄露敏感信息。
"""

from core.config.loader import (
    NotificationConfig,
    SaucyClawConfig,
    load_config,
    load_notification_config,
    ensure_config_exists,
    DEFAULT_CONFIG_FILE,
)

__all__ = [
    "NotificationConfig",
    "SaucyClawConfig",
    "load_config",
    "load_notification_config",
    "ensure_config_exists",
    "DEFAULT_CONFIG_FILE",
]
