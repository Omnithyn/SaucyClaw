"""OpenHarness 宿主 Profile。

声明 OpenHarness runtime 的治理能力接入信息：
- 支持哪些模式
- 当前成熟度
- 推荐入口
- 哪些能力已确认，哪些待验证

M11 — OpenHarness Recon & Skeleton Profile
M12 — OpenHarness First Executable Path (hooks_live)
M13 — OpenHarness Live Validation & Reality Closure
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapters.host_protocols import (
    HostAdapterProfile,
    HostCapabilities,
    HostMode,
)


# OpenHarness 模式成熟度映射
_OPENHARNESS_MATURITY: dict[HostMode, str] = {
    HostMode.SHADOW: "概念验证（待实现）",
    HostMode.NOTIFICATION: "概念验证（待实现）",
    HostMode.HOOKS_LIVE: "MVP（已真实验证）",
}

# OpenHarness 模式入口模块映射
_OPENHARNESS_ENTRY_POINTS: dict[HostMode, str] = {
    HostMode.SHADOW: "adapters.openharness.shadow_runtime",
    HostMode.NOTIFICATION: "adapters.openharness.notification_adapter",
    HostMode.HOOKS_LIVE: "adapters.openharness.hooks_adapter",
}

# OpenHarness 真实验证状态
_OPENHARNESS_VALIDATED: dict[HostMode, bool] = {
    HostMode.SHADOW: False,
    HostMode.NOTIFICATION: False,
    HostMode.HOOKS_LIVE: True,
}


@dataclass(frozen=True)
class OpenHarnessProfile:
    """OpenHarness 宿主 Profile 实现。

    用法：
        profile = OpenHarnessProfile()
        print(profile.capabilities.modes)
        print(profile.get_entry_point(HostMode.HOOKS_LIVE))

    调研结论（M11）：
    - OpenHarness 有完整的 hooks 系统（4 种钩子类型：command/http/prompt/agent）
    - HTTP Hook 是最推荐的 hooks-live 接入方式
    - Channel 系统支持 notification 模式（10+ 消息通道）
    - engine/stream_events.py 提供了清晰的事件结构，适合 shadow mock

    M12 进展：
    - hooks_live 已进入最小可执行阶段（OpenHarnessHookReceiver + OpenHarnessHookProbe）
    - Block / Allow / failure 三类路径验证通过

    M13 进展：
    - hooks_live 完成真实验证，5/5 场景通过
    - Payload 格式与 OpenHarness 源码完全对齐（executor.py:148）
    - 响应结构与 OpenHarness 判断逻辑完全兼容（executor.py:151-159）
    """

    name: str = "openharness"

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
        )

    def get_entry_point(self, mode: HostMode) -> str | None:
        return _OPENHARNESS_ENTRY_POINTS.get(mode)

    def get_maturity(self, mode: HostMode) -> str:
        return _OPENHARNESS_MATURITY.get(mode, "未知")

    def is_validated(self, mode: HostMode) -> bool:
        return _OPENHARNESS_VALIDATED.get(mode, False)

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
