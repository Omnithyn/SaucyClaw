"""OpenClaw 宿主适配器 — 外围接入包。

本包提供围绕 OpenClaw 的三种接入模式：

**Shadow Mode（正式工程面）**
- 基于 mock adapter 的本地测试和治理引擎外围接入
- 入口模块：ShadowRuntime

**Notification Mode（正式工程面）**
- 旧通知线兼容，使用 OpenClawPayload 格式
- 入口模块：OpenClawNotificationAdapter

**Hooks-Live Mode（MVP）**
- 真实 OpenClaw hooks 对接，使用 HookAgentPayload 格式
- 入口模块：OpenClawHooksAdapter

详细文档：docs/integration/openclaw_integration_modes.md
"""

from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import (
    AdapterExplainOutput,
    ExplainBridge,
)
from adapters.openclaw.shadow_runtime import (
    ShadowRuntime,
    ShadowRunResult,
)
from adapters.openclaw.runtime_trace import (
    RuntimeTrace,
    build_runtime_trace,
)
from adapters.openclaw.debug_render import (
    render_shadow_run,
)
from adapters.openclaw.hook_contract import (
    HostOutputSink,
    ExplainPayload,
    GovernanceProcessor,
    ShadowOutput,
)

# Notification Mode 适配器（正式工程面）
from adapters.openclaw.notification_adapter import (
    WakeResult,
    OpenClawNotificationAdapter,
    OpenClawCommandNotificationAdapter,
)

# Hooks-Live Mode 适配器（MVP）
from adapters.openclaw.hooks_adapter import (
    HooksWakeResult,
    OpenClawHooksAdapter,
)

__all__ = [
    # Shadow Mode（正式工程面）
    "OpenClawHostAdapter",
    "ExplainBridge",
    "AdapterExplainOutput",
    "ShadowRuntime",
    "ShadowRunResult",
    "RuntimeTrace",
    "build_runtime_trace",
    "render_shadow_run",
    # Hook Contract (Protocols)
    "HostOutputSink",
    "ExplainPayload",
    "GovernanceProcessor",
    "ShadowOutput",
    # Notification Mode（正式工程面）
    "WakeResult",
    "OpenClawNotificationAdapter",
    "OpenClawCommandNotificationAdapter",
    # Hooks-Live Mode（MVP）
    "HooksWakeResult",
    "OpenClawHooksAdapter",
]
