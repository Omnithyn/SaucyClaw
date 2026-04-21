"""Hermes Agent 宿主 Profile。

声明 Hermes Agent runtime 的治理能力接入信息：
- 支持哪些模式
- 当前成熟度
- 推荐入口
- 哪些能力已确认，哪些待验证

M11 — Hermes Agent Recon & Skeleton Profile
M14 — Hook Integration Pattern Refinement
M15 — Inbound Hook Gatekeeping Base Package（预期复用）
M17 — Hermes First Executable Path on Inbound Base（已落地）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapters.host_protocols import (
    HostCapabilities,
    HostMode,
    HookInteractionPattern,
)


# Hermes 模式成熟度映射
_HERMES_MATURITY: dict[HostMode, str] = {
    HostMode.SHADOW: "概念验证（待实现）",
    HostMode.NOTIFICATION: "概念验证（待实现）",
    HostMode.HOOKS_LIVE: "最小可执行（M17 已落地）",
}

# Hermes 模式入口模块映射
_HERMES_ENTRY_POINTS: dict[HostMode, str] = {
    HostMode.SHADOW: "adapters.hermes.shadow_runtime",
    HostMode.NOTIFICATION: "adapters.hermes.notification_adapter",
    HostMode.HOOKS_LIVE: "adapters.hermes.hooks_adapter",
}

# Hermes 真实验证状态
_HERMES_VALIDATED: dict[HostMode, bool] = {
    HostMode.SHADOW: False,
    HostMode.NOTIFICATION: False,
    HostMode.HOOKS_LIVE: True,  # M17 已验证
}

# Hermes hook_pattern 映射
_HERMES_HOOK_PATTERN: dict[HostMode, HookInteractionPattern | None] = {
    HostMode.SHADOW: None,
    HostMode.NOTIFICATION: None,
    HostMode.HOOKS_LIVE: HookInteractionPattern.INBOUND_HOOK_GATEKEEPING,
}


@dataclass(frozen=True)
class HermesProfile:
    """Hermes Agent 宿主 Profile 实现。

    用法：
        profile = HermesProfile()
        print(profile.capabilities.modes)
        print(profile.get_entry_point(HostMode.HOOKS_LIVE))

    调研结论（M11）：
    - Hermes 有完整的 hook 系统（从 ~/.hermes/hooks/ 目录自动发现脚本）
    - 事件类型包括 agent:step/command:*/session:start 等
    - hooks-live 需要通过 hook 脚本 + HTTP 端点方式接入
    - Channel 系统支持 9+ 消息平台，适合 notification
    - AIAgent 回调体系清晰，适合 shadow mock

    M14 说明：
    - Hermes hooks-live 使用 INBOUND_HOOK_GATEKEEPING 模式
    - Hook 脚本 POST 到 SaucyClaw /governance 端点
    - 脚本返回非 0 值阻断 Hermes 操作

    M15 说明（预期复用）：
    - Hermes 预期可复用 inbound_hook_gatekeeping 公共基座

    M17 说明（已落地）：
    - Hermes 已真正复用 inbound_hook_gatekeeping 公共基座
    - HermesHookResult = InboundHookResult（直接复用）
    - build_hermes_hook_response 桥接公共 helper
    - HermesHookReceiver/HermesHookProbe 符合公共 Protocol
    - 25 单元测试 + 5 真实验证全部通过
    """

    name: str = "hermes"

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
            hook_pattern=HookInteractionPattern.INBOUND_HOOK_GATEKEEPING,
        )

    def get_entry_point(self, mode: HostMode) -> str | None:
        return _HERMES_ENTRY_POINTS.get(mode)

    def get_maturity(self, mode: HostMode) -> str:
        return _HERMES_MATURITY.get(mode, "未知")

    def is_validated(self, mode: HostMode) -> bool:
        return _HERMES_VALIDATED.get(mode, False)

    def get_hook_pattern(self, mode: HostMode) -> HookInteractionPattern | None:
        return _HERMES_HOOK_PATTERN.get(mode)

    def to_dict(self) -> dict[str, Any]:
        """导出为字典（用于序列化/日志）。"""
        return {
            "name": self.name,
            "capabilities": {
                mode.value: {
                    "entry_point": self.get_entry_point(mode),
                    "maturity": self.get_maturity(mode),
                    "validated": self.is_validated(mode),
                    "hook_pattern": self.get_hook_pattern(mode).value if self.get_hook_pattern(mode) else None,
                }
                for mode in self.capabilities.modes
            },
        }
