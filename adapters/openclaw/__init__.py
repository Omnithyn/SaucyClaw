"""OpenClaw 宿主适配器 — 外围接入包。

本包提供围绕 OpenClaw mock adapter 的最小可交付接入链路，包含：

- **adapter** — 宿主适配器 mock（Phase 0-1）
- **explain_bridge** — 解释桥接器，生成伴随输出（Phase 2.0）
- **shadow_runtime** — Shadow Mode 外围接入模板（Phase 2.2）
- **runtime_trace** — 运行链路最小摘要（Phase 2.5）
- **debug_render** — 调试输出渲染器（Phase 2.6）
- **hook_contract** — 外部接入契约 Protocol（Phase 2.3）

当前状态：基于 mock adapter 的最小闭环，尚未接入真实 OpenClaw hook。
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

__all__ = [
    # Adapter
    "OpenClawHostAdapter",
    # Explain Bridge
    "ExplainBridge",
    "AdapterExplainOutput",
    # Shadow Runtime
    "ShadowRuntime",
    "ShadowRunResult",
    # Runtime Trace
    "RuntimeTrace",
    "build_runtime_trace",
    # Debug Render
    "render_shadow_run",
    # Hook Contract (Protocols)
    "HostOutputSink",
    "ExplainPayload",
    "GovernanceProcessor",
    "ShadowOutput",
]
