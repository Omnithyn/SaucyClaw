"""OpenHarness 适配器包（skeleton）。

M11 — 只定义 profile，adapter 实现待后续阶段完成。

当前已确认能力：
- shadow: 可通过 mock engine 事件实现（待实现）
- notification: 可通过 Channel / MessageBus 实现（待实现）
- hooks_live: 可通过 HTTP Hook (pre_tool_use) 实现（待实现）
"""

from adapters.openharness.profile import OpenHarnessProfile

__all__ = ["OpenHarnessProfile"]
