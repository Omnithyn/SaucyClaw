"""OpenClaw 宿主 Profile。

声明 OpenClaw runtime 的治理能力接入信息：
- 支持哪些模式
- 哪些模式是正式工程面
- 哪些模式是 MVP
- 哪些模式已完成真实验证
- 当前推荐入口

M10 — Runtime-Neutral Host Abstraction
M14 — Hook Integration Pattern Refinement
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapters.host_protocols import (
    HostCapabilities,
    HookInteractionPattern,
    HostMode,
)


# OpenClaw 模式成熟度映射
_OPENCLAW_MATURITY: dict[HostMode, str] = {
    HostMode.SHADOW: "正式工程面",
    HostMode.NOTIFICATION: "正式工程面",
    HostMode.HOOKS_LIVE: "MVP（最小可用）",
}

# OpenClaw 模式入口模块映射
_OPENCLAW_ENTRY_POINTS: dict[HostMode, str] = {
    HostMode.SHADOW: "adapters.openclaw.shadow_runtime",
    HostMode.NOTIFICATION: "adapters.openclaw.notification_adapter",
    HostMode.HOOKS_LIVE: "adapters.openclaw.hooks_adapter",
}

# OpenClaw 真实验证状态
_OPENCLAW_VALIDATED: dict[HostMode, bool] = {
    HostMode.SHADOW: True,
    HostMode.NOTIFICATION: True,
    HostMode.HOOKS_LIVE: True,
}


@dataclass(frozen=True)
class OpenClawProfile:
    """OpenClaw 宿主 Profile 实现。

    用法：
        profile = OpenClawProfile()
        print(profile.capabilities.modes)
        print(profile.get_entry_point(HostMode.HOOKS_LIVE))

    M14 说明：
    - hooks_live 属于 outbound_hook_push（SaucyClaw 主动调用宿主 hooks API）
    - OpenClaw 的 hooks API 是 POST /hooks/agent，由 SaucyClaw 发送治理决策通知
    """

    name: str = "openclaw"

    @property
    def capabilities(self) -> HostCapabilities:
        return HostCapabilities(
            modes=[
                HostMode.SHADOW,
                HostMode.NOTIFICATION,
                HostMode.HOOKS_LIVE,
            ],
            supports_shadow=True,
            supports_notification=True,
            supports_hooks_live=True,
            hook_pattern=HookInteractionPattern.OUTBOUND_HOOK_PUSH,
        )

    def get_entry_point(self, mode: HostMode) -> str | None:
        return _OPENCLAW_ENTRY_POINTS.get(mode)

    def get_maturity(self, mode: HostMode) -> str:
        return _OPENCLAW_MATURITY.get(mode, "未知")

    def is_validated(self, mode: HostMode) -> bool:
        return _OPENCLAW_VALIDATED.get(mode, False)

    def to_dict(self) -> dict[str, Any]:
        """导出为字典（用于序列化/日志）。"""
        return {
            "name": self.name,
            "capabilities": {
                mode.value: {
                    "entry_point": self.get_entry_point(mode),
                    "maturity": self.get_maturity(mode),
                    "validated": self.is_validated(mode),
                }
                for mode in self.capabilities.modes
            },
        }
