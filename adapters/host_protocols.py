"""宿主无关接入抽象协议。

本模块定义 SaucyClaw 与外部 runtime 交互的上位抽象，
不依赖任何具体 runtime 实现。

M10 — Runtime-Neutral Host Abstraction
M14 — Hook Integration Pattern Refinement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class HostMode(Enum):
    """宿主接入模式。

    shadow: 本地 mock 测试，不依赖真实 runtime
    notification: 通过 runtime 通知通道发送治理决策
    hooks_live: 通过 runtime hooks API 发送真实消息
    """
    SHADOW = "shadow"
    NOTIFICATION = "notification"
    HOOKS_LIVE = "hooks_live"


class HookInteractionPattern(Enum):
    """Hook 交互形态。

    M14 引入：hooks_live 模式下，SaucyClaw 与宿主的交互方向不同。

    - outbound_hook_push: SaucyClaw 主动调用宿主 hooks API
      （如 OpenClaw POST /hooks/agent，SaucyClaw 发送治理决策通知）

    - inbound_hook_gatekeeping: 宿主在事件点 POST 到 SaucyClaw 端点
      （如 OpenHarness HTTP Hook，SaucyClaw 接收请求并返回阻断/放行响应）
    """
    OUTBOUND_HOOK_PUSH = "outbound_hook_push"
    INBOUND_HOOK_GATEKEEPING = "inbound_hook_gatekeeping"


@dataclass(frozen=True)
class HostWakeResult:
    """宿主 wake 调用统一结果。

    不同 runtime 的结果结构可映射到此统一类型：
    - OpenClaw notification → WakeResult
    - OpenClaw hooks → HooksWakeResult（含 run_id）
    - 其他 runtime → 适配到此结构
    """
    gateway: str
    success: bool
    error: str | None = None
    status_code: int | None = None
    run_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HostCapabilities:
    """宿主能力声明。

    声明某个 runtime 支持哪些接入模式。

    M14 增加 hook_pattern：
    - 仅当 supports_hooks_live=True 时有意义
    - 用于区分 outbound_hook_push 与 inbound_hook_gatekeeping
    """
    modes: list[HostMode]
    supports_shadow: bool = True
    supports_notification: bool = False
    supports_hooks_live: bool = False
    hook_pattern: HookInteractionPattern | None = None


class HostAdapterProfile(Protocol):
    """宿主接入 profile 协议。

    每个 runtime 实现此协议来声明自己的治理能力：
    - 支持哪些模式
    - 推荐入口
    - 成熟度信息
    """

    @property
    def name(self) -> str:
        """runtime 名称，如 'openclaw', 'openharness'。"""
        ...

    @property
    def capabilities(self) -> HostCapabilities:
        """声明支持的能力列表。"""
        ...

    def get_entry_point(self, mode: HostMode) -> str | None:
        """获取指定模式的入口模块路径。"""
        ...

    def get_maturity(self, mode: HostMode) -> str:
        """获取指定模式的成熟度描述。"""
        ...
