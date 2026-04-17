"""OpenHarness 适配器包。

M11 — skeleton profile
M12 — hooks_live 最小可执行路径
"""

from adapters.openharness.profile import OpenHarnessProfile
from adapters.openharness.hooks_adapter import (
    OpenHarnessHookReceiver,
    OpenHarnessHookProbe,
    OpenHarnessHookResult,
    build_openharness_hook_response,
    parse_openharness_hook_payload,
)

__all__ = [
    "OpenHarnessProfile",
    "OpenHarnessHookReceiver",
    "OpenHarnessHookProbe",
    "OpenHarnessHookResult",
    "build_openharness_hook_response",
    "parse_openharness_hook_payload",
]
