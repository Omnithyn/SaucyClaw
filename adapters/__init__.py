"""SaucyClaw adapters。

宿主桥接层：
- openclaw/ — OpenClaw 适配器（第一个已落地的 host profile）
- host_protocols.py — 宿主无关抽象协议（M10）
"""

from adapters.host_protocols import (
    HostMode,
    HostWakeResult,
    HostCapabilities,
    HostAdapterProfile,
)

__all__ = [
    # Host Abstraction（M10）
    "HostMode",
    "HostWakeResult",
    "HostCapabilities",
    "HostAdapterProfile",
]
